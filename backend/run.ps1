# Inicia o backend PayGuard
$root = Split-Path -Parent $PSScriptRoot
& "$PSScriptRoot\venv_mba\Scripts\uvicorn.exe" app.main:app --reload --port 8000
