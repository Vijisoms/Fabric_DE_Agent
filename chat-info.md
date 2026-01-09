*****
I have turned on ability to edit files

*****
I am trying to create fabric pipelines using code do research with #microsoft_docs_search to see what options are available like rest api, sdk and best practices for acomplishing this. Improve or rewrite #file:create_pipeline.py
******
Quick use: python [create_pipeline.py](http://_vscodecontentref_/4) --workspace <wsId> --token <bearer> --definition pipeline.json --name my-pipeline --retries 3 --backoff 0.5 --timeout 30 --verbose.
********************
create a definition of the pipeline with 2 wait activity waiting for 1 minute and 2 minute
***************
I can run it, but I need two inputs you haven’t provided:

Workspace ID (GUID)
A valid Fabric bearer token with Workspace.ReadWrite.All or Item.ReadWrite.All
*************
use default credentials for authentication reference #microsoft_docs_search , workspace id is cda8958f-d52a-4361-91af-6fb46017a40b
**************************************
Convert current CLI tools (#sym:create_pipeline , #file:create_lakehouse.py ) into one singular Streamable MCP. Reference Model Context Protocol Python SDK using #io.github.upstash/context7 . Then Provide me the instructions on how to run the streamable MCP as a local service for testing before I deploy and publish . Name our brand new MCP as FAB_DE