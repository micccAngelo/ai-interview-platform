$taskRoot = Split-Path $PSScriptRoot -Parent
$env:PATH = "$taskRoot\.runtime\rubyinstaller-3.3.2-1-x64\bin;$taskRoot\.runtime\msys64\ucrt64\bin;$taskRoot\.runtime\msys64\usr\bin;" + $env:PATH
$env:MSYS2_PATH = "$taskRoot\.runtime\msys64"
$env:BUNDLE_USER_HOME = "$taskRoot\.runtime\bundle-user"
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '54329'
$env:DB_USERNAME = 'postgres'
$env:ALLOWED_ORIGINS = 'http://localhost:5173,http://127.0.0.1:5173'
$env:WEB_CONCURRENCY = '0'
$env:PLAYWRIGHT_BROWSERS_PATH = "$taskRoot\.runtime\playwright"
$taskSecretPath = Join-Path $taskRoot '.runtime/local-env.json'
if (-not (Test-Path -LiteralPath $taskSecretPath)) {
  $taskBytes = New-Object byte[] 48
  $taskGenerator = [Security.Cryptography.RandomNumberGenerator]::Create()
  $taskGenerator.GetBytes($taskBytes)
  @{ SecretKeyBase = [Convert]::ToBase64String($taskBytes) } | ConvertTo-Json | Set-Content -LiteralPath $taskSecretPath -Encoding utf8
  $taskGenerator.Dispose()
}
$env:SECRET_KEY_BASE = (Get-Content -LiteralPath $taskSecretPath -Raw | ConvertFrom-Json).SecretKeyBase
