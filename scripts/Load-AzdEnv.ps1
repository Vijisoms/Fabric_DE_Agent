param(
  [Parameter(Mandatory=$false)]
  [string]$EnvironmentName
)

$ErrorActionPreference = 'Stop'

$azdArgs = @('env','get-values')
if ($EnvironmentName) {
  $azdArgs += @('-e', $EnvironmentName)
}

# azd prints .env formatted lines: KEY="VALUE"
$lines = & azd @azdArgs
if ($LASTEXITCODE -ne 0) {
  throw "azd env get-values failed (exit=$LASTEXITCODE)"
}

foreach ($line in $lines) {
  if (-not $line) { continue }
  if ($line.TrimStart().StartsWith('#')) { continue }

  $parts = $line.Split('=', 2)
  if ($parts.Count -ne 2) { continue }

  $key = $parts[0].Trim()
  $raw = $parts[1].Trim()

  # Strip surrounding quotes if present
  if ($raw.Length -ge 2 -and $raw.StartsWith('"') -and $raw.EndsWith('"')) {
    $value = $raw.Substring(1, $raw.Length - 2)
  } else {
    $value = $raw
  }

  if ($key) {
    Set-Item -Path "Env:$key" -Value $value
  }
}

Write-Host "Loaded azd env values into current session."