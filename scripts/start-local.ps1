$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/runtime-env.ps1"
$taskRoot = Split-Path $PSScriptRoot -Parent
& "$taskRoot/.runtime/postgres/pgsql/bin/pg_ctl.exe" -D "$taskRoot/.runtime/pgdata" status | Out-Null
if ($LASTEXITCODE -ne 0) {
  & "$taskRoot/.runtime/postgres/pgsql/bin/pg_ctl.exe" -D "$taskRoot/.runtime/pgdata" -l "$taskRoot/.runtime/postgres.log" -o '-h 127.0.0.1 -p 54329' start
}
Push-Location "$taskRoot/api"
try {
  $env:RAILS_ENV = 'development'
  bundle exec rails db:prepare
  if ($LASTEXITCODE -ne 0) { throw 'Database preparation failed. See the terminal output.' }
  bundle exec rails runner db/evidence_demo.rb
  if ($LASTEXITCODE -ne 0) { throw 'Synthetic seed failed. See the terminal output.' }
  $taskDemo = Get-Content tmp/evidence-demo.json -Raw | ConvertFrom-Json
} finally { Pop-Location }
@("VITE_API_BASE_URL=http://127.0.0.1:3001/api/v1", "VITE_WS_BASE_URL=ws://127.0.0.1:3001", "VITE_DEV_TOKEN=$($taskDemo.token)", "VITE_DEV_TENANT_NAME=Synthetic Evidence Demo") | Set-Content "$taskRoot/web/.env.local" -Encoding utf8
if (-not (Get-NetTCPConnection -State Listen -LocalPort 3001 -ErrorAction SilentlyContinue)) {
  Start-Process -FilePath "$taskRoot/.runtime/rubyinstaller-3.3.2-1-x64/bin/ruby.exe" -ArgumentList 'bin/rails','server','-b','127.0.0.1','-p','3001' -WorkingDirectory "$taskRoot/api" -WindowStyle Hidden -RedirectStandardOutput "$taskRoot/.runtime/api-server.log" -RedirectStandardError "$taskRoot/.runtime/api-server-error.log"
}
if (-not (Get-NetTCPConnection -State Listen -LocalPort 5173 -ErrorAction SilentlyContinue)) {
  Start-Process -FilePath (Get-Command node).Source -ArgumentList 'node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','5173' -WorkingDirectory "$taskRoot/web" -WindowStyle Hidden -RedirectStandardOutput "$taskRoot/.runtime/web-server.log" -RedirectStandardError "$taskRoot/.runtime/web-server-error.log"
}
Write-Output ('Open the synthetic review: http://127.0.0.1:5173' + $taskDemo.path)
Write-Output 'API and web logs are in .runtime. No live Gemini call is made by this demo seed.'
