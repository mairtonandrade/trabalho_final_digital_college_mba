# Regenera PNGs em docs/assets a partir dos SVGs (UTF-8 com entidades XML)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$assets = Join-Path $root "docs\assets"
$frontend = Join-Path $root "frontend"

Push-Location $frontend
$svgs = @("01-home", "02-analista", "03-gerente-ia", "04-diretoria", "05-fluxo-ia")
foreach ($name in $svgs) {
  $in = Join-Path $assets "$name.svg"
  $out = Join-Path $assets "$name.png"
  npx --yes @resvg/resvg-js-cli --fit-width 1200 $in $out 2>&1 | Out-Null
  Write-Host "OK $name.png"
}
Pop-Location

Write-Host "PNGs atualizados em docs/assets"
