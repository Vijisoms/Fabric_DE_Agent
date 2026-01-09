param(
  [Parameter(Mandatory=$false)]
  [string]$EnvironmentName = "fabde"
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

. "$PSScriptRoot\Load-AzdEnv.ps1" -EnvironmentName $EnvironmentName

if (-not $env:AZURE_AI_PROJECT_ENDPOINT) {
  throw "AZURE_AI_PROJECT_ENDPOINT is not set."
}
if (-not $env:AZURE_AI_MODEL_DEPLOYMENT_NAME) {
  throw "AZURE_AI_MODEL_DEPLOYMENT_NAME is not set."
}
if (-not $env:MCP_SERVER_URL) {
  throw "MCP_SERVER_URL is not set (expected https://<fqdn>/mcp)."
}

& "$repoRoot\.venv\Scripts\python.exe" "src\Agents\Fabric-de.py"