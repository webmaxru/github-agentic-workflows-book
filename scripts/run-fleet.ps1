#!/usr/bin/env pwsh
# Launches the GitHub Agentic Workflows book agent fleet autonomously (headless).
# Runs the master orchestrator prompt to completion via Copilot CLI, then exits.
#
# Usage:
#   ./scripts/run-fleet.ps1                # run the full pipeline
#   ./scripts/run-fleet.ps1 -DryRun        # print the command without running
#
# Notes:
#   - Run from the repo root (the script cd's there itself).
#   - --allow-all-tools grants Copilot the same access you have. For isolation,
#     run inside a sandbox/container, or use `copilot --cloud`.

[CmdletBinding()]
param(
    [switch]$DryRun,
    [string]$PromptPath = ".github/prompts/run-playbook.prompt.md"
)

$ErrorActionPreference = "Stop"

# Move to repo root (parent of this script's folder)
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not (Test-Path $PromptPath)) {
    throw "Orchestrator prompt not found: $PromptPath"
}

if (-not (Get-Command copilot -ErrorAction SilentlyContinue)) {
    throw "Copilot CLI ('copilot') not found on PATH. Install it first: https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli"
}

$prompt = Get-Content -Raw $PromptPath

Write-Host "Launching GitHub Agentic Workflows book fleet from '$PromptPath'..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[DryRun] Would run: copilot -p <orchestrator-prompt> --allow-all-tools" -ForegroundColor Yellow
    return
}

# Headless run: orchestrator drives the whole fleet and exits when done.
copilot -p $prompt --allow-all-tools
