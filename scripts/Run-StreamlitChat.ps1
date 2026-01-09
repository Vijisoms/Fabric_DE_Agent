param(
  [Parameter(Mandatory=$false)]
  [string]$EnvironmentName = "fabde"
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Load azd env vars (includes MCP_SERVER_URL)
. "$PSScriptRoot\Load-AzdEnv.ps1" -EnvironmentName $EnvironmentName

if (-not $env:AZURE_AI_PROJECT_ENDPOINT) {
  Write-Warning "AZURE_AI_PROJECT_ENDPOINT is not set. Set it before running, e.g.:"
  Write-Warning "  `$env:AZURE_AI_PROJECT_ENDPOINT='https://<resource>.services.ai.azure.com/api/projects/<project>'"
}
if (-not $env:AZURE_AI_MODEL_DEPLOYMENT_NAME) {
  Write-Warning "AZURE_AI_MODEL_DEPLOYMENT_NAME is not set (needed for agent creation/versioning scripts)."
}
if (-not $env:MCP_SERVER_URL) {
  Write-Warning "MCP_SERVER_URL is not set. Deploy first (azd deploy) or set it manually."
}

& "$repoRoot\.venv\Scripts\python.exe" -m streamlit run "apps\streamlit_chat.py"