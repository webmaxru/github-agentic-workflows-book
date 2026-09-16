#!/usr/bin/env pwsh
# Launches a book maintenance, bootstrap, or release-preparation prompt headlessly.
#
# Usage:
#   .\scripts\run-fleet.ps1                           # incremental update
#   .\scripts\run-fleet.ps1 -Mode Bootstrap            # explicit full-book build
#   .\scripts\run-fleet.ps1 -TargetVersion v0.88.7 -DryRun
#
# Notes:
#   - Run from the repo root (the script cd's there itself).
#   - --allow-all-tools grants Copilot the same access you have. For isolation,
#     run inside a sandbox/container, or use `copilot --cloud`.

[CmdletBinding()]
param(
    [switch]$DryRun,
    [ValidateSet("Update", "Bootstrap", "Release")]
    [string]$Mode = "Update",
    [string]$PromptPath,
    [ValidatePattern('\Av(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\z', Options = 'None')]
    [string]$TargetVersion
)

$ErrorActionPreference = "Stop"

# Move to repo root (parent of this script's folder)
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if ($PromptPath -and ($PSBoundParameters.ContainsKey("Mode") -or $TargetVersion)) {
    throw "Use -PromptPath alone, or select -Mode with an optional -TargetVersion."
}

if ($TargetVersion -and $Mode -ne "Update") {
    throw "-TargetVersion is supported only with -Mode Update."
}

if (-not $PromptPath) {
    $promptNames = @{
        Update = "update-book.prompt.md"
        Bootstrap = "run-playbook.prompt.md"
        Release = "release-content.prompt.md"
    }
    $PromptPath = Join-Path (Join-Path $repoRoot ".github\prompts") $promptNames[$Mode]
}

if (-not (Test-Path -LiteralPath $PromptPath -PathType Leaf)) {
    throw "Book prompt not found: $PromptPath"
}

$prompt = Get-Content -LiteralPath $PromptPath -Raw -Encoding utf8
if ($TargetVersion) {
    $prompt += "`n`nInvocation target: $TargetVersion. Use this exact framework target; do not resolve latest."
}

Write-Host "Book prompt: $PromptPath" -ForegroundColor Cyan
if ($TargetVersion) {
    Write-Host "Fixed framework target: $TargetVersion"
}
if ($DryRun) {
    Write-Host "[DryRun] Would run: copilot -p <orchestrator-prompt> --allow-all-tools" -ForegroundColor Yellow
    return
}

if (-not (Get-Command copilot -ErrorAction SilentlyContinue)) {
    throw "Copilot CLI ('copilot') not found on PATH. Install it first: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli"
}

copilot -p $prompt --allow-all-tools
if ($LASTEXITCODE -ne 0) {
    throw "Copilot failed with exit code $LASTEXITCODE."
}
