#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Download and checksum-verify an exact Windows gh-aw release without modifying
    the user's gh extension. The only pipeline output is the executable path.
.EXAMPLE
    $compiler = .\scripts\install-gh-aw.ps1 -Version v0.88.7
    python .\scripts\verify_examples.py --compiler $compiler --version v0.88.7
#>
[CmdletBinding()]
param(
    [string]$Version,
    [string]$InstallDir
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not $PSBoundParameters.ContainsKey("Version")) {
    $pin = Join-Path $root "content\FRAMEWORK_VERSION"
    if (-not (Test-Path -LiteralPath $pin -PathType Leaf)) {
        throw "Missing framework pin: $pin. Supply -Version with an exact tag."
    }
    $Version = (Get-Content -LiteralPath $pin -Raw -Encoding UTF8).Trim()
}
if ($Version -cnotmatch '\Av(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\z') {
    throw "Invalid framework version '$Version'. Expected an exact stable tag such as v0.88.7."
}
if ($env:OS -ne "Windows_NT") {
    throw "This installer supports Windows only. On Linux use gh extension install github/gh-aw --pin $Version."
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required. Install it and authenticate before retrying."
}
$architecture = if ($env:PROCESSOR_ARCHITEW6432) {
    $env:PROCESSOR_ARCHITEW6432
} else {
    $env:PROCESSOR_ARCHITECTURE
}
$assetName = switch ($architecture) {
    "AMD64" { "windows-amd64.exe" }
    "ARM64" { "windows-arm64.exe" }
    default { throw "Unsupported Windows architecture: $architecture. Use x64 or ARM64." }
}
if (-not $PSBoundParameters.ContainsKey("InstallDir")) {
    $InstallDir = Join-Path $root "build\tools\gh-aw\$Version"
}
if ([string]::IsNullOrWhiteSpace($InstallDir)) {
    throw "-InstallDir cannot be empty."
}
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)

Write-Host "Resolving github/gh-aw $Version ($assetName)"
$metadata = & gh release view $Version --repo github/gh-aw --json tagName,assets
if ($LASTEXITCODE -ne 0) {
    throw "Cannot read the pinned release. Check network and gh authentication; no anonymous or latest-release fallback is used."
}
$release = ($metadata -join "`n") | ConvertFrom-Json
if ($release.tagName -cne $Version) {
    throw "Release tag mismatch: requested $Version, received $($release.tagName)."
}
foreach ($required in @($assetName, "checksums.txt")) {
    $assets = @($release.assets | Where-Object { $_.name -ceq $required })
    if ($assets.Count -ne 1) {
        throw "Release $Version must contain exactly one '$required' asset."
    }
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
$stage = Join-Path $InstallDir (".download-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $stage | Out-Null
try {
    & gh release download $Version --repo github/gh-aw --pattern $assetName --pattern checksums.txt --dir $stage
    if ($LASTEXITCODE -ne 0) {
        throw "Pinned release download failed. The existing executable has not been changed."
    }
    $binary = Join-Path $stage $assetName
    $checksums = Join-Path $stage "checksums.txt"
    if (-not (Test-Path -LiteralPath $binary -PathType Leaf) -or
        -not (Test-Path -LiteralPath $checksums -PathType Leaf)) {
        throw "Download did not produce both required release assets."
    }
    $pattern = '^([A-Fa-f0-9]{64})\s+\*?' + [regex]::Escape($assetName) + '$'
    $hashLines = @(Get-Content -LiteralPath $checksums -Encoding UTF8 |
        Where-Object { $_ -cmatch $pattern })
    if ($hashLines.Count -ne 1) {
        throw "checksums.txt must contain exactly one valid SHA256 for $assetName."
    }
    $expected = [regex]::Match($hashLines[0], $pattern).Groups[1].Value.ToLowerInvariant()
    $actual = (Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($expected -cne $actual) {
        throw "SHA256 mismatch for $assetName. The existing executable has not been changed."
    }
    $versionOutput = & $binary version 2>&1
    $versionExitCode = $LASTEXITCODE
    if ($versionExitCode -ne 0) {
        throw "The downloaded compiler failed its version check."
    }
    $versions = @([regex]::Matches(
        ($versionOutput -join "`n"),
        '(?<![\w.-])v[0-9]+\.[0-9]+\.[0-9]+(?:[-+][\w.-]+)?(?![\w.-])'
    ) | ForEach-Object { $_.Value } | Select-Object -Unique)
    if ($versions.Count -ne 1 -or $versions[0] -cne $Version) {
        throw "Downloaded compiler version mismatch; expected $Version, received: $versionOutput"
    }
    $destination = Join-Path $InstallDir "gh-aw.exe"
    Move-Item -LiteralPath $binary -Destination $destination -Force
    Write-Host "Verified SHA256 and compiler version: $Version"
    Write-Output $destination
} finally {
    if (Test-Path -LiteralPath $stage) {
        Remove-Item -LiteralPath $stage -Recurse -Force
    }
}
