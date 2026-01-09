from __future__ import annotations

import os

import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Fabric DE Agent", page_icon="🧩", layout="centered")

st.title("Fabric DE Agent")
st.caption("Chat with your Azure AI Foundry agent (with MCP tools).")

with st.sidebar:
    st.subheader("Configuration")
    project_endpoint = st.text_input(
        "Project endpoint",
        value=os.getenv("AZURE_AI_PROJECT_ENDPOINT", ""),
        placeholder="https://<resource>.services.ai.azure.com/api/projects/<project>",
    )
    agent_name = st.text_input("Agent name", value=os.getenv("AGENT_NAME", "Fabric-DE-Agent"))

    st.text_input(
        "MCP server URL (informational)",
        value=os.getenv("MCP_SERVER_URL", ""),
        disabled=True,
        help="This is registered on the agent. The chat uses agent_reference.",
    )

    stream = st.toggle("Stream responses", value=True)

if not project_endpoint:
    st.info("Set AZURE_AI_PROJECT_ENDPOINT to start chatting.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


def _stream_response(openai_client, *, conversation_id: str, user_text: str, agent: str):
    events = openai_client.responses.create(
        stream=True,
        conversation=conversation_id,
        input=user_text,
        extra_body={"agent": {"name": agent, "type": "agent_reference"}},
    )

    for event in events:
        if getattr(event, "type", None) == "response.output_text.delta":
            yield event.delta


with DefaultAzureCredential() as credential, AIProjectClient(
    endpoint=project_endpoint, credential=credential
) as project_client:
    openai_client = project_client.get_openai_client()

    if st.session_state.conversation_id is None:
        conversation = openai_client.conversations.create()
        st.session_state.conversation_id = conversation.id

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about creating Fabric items…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if stream:
                streamed_text = st.write_stream(
                    _stream_response(
                        openai_client,
                        conversation_id=st.session_state.conversation_id,
                        user_text=prompt,
                        agent=agent_name,
                    )
                )
                assistant_text = streamed_text or ""
            else:
                resp = openai_client.responses.create(
                    conversation=st.session_state.conversation_id,
                    input=prompt,
                    extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
                )
                assistant_text = resp.output_text
                st.markdown(assistant_text)

        st.session_state.messages.append({"role": "assistant", "content": assistant_text})
