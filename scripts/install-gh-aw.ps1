# Manually installs the gh-aw binary extension when `gh extension install github/gh-aw`
# is blocked by org SAML enforcement on the authenticated token. The repo is public, so we
# download the release asset anonymously and verify its SHA256 against published checksums.
#
# NOTE: use curl.exe (not Invoke-WebRequest) for the binary download — Windows PowerShell 5.1's
# IWR truncated the ~31 MB binary to ~9 MB, producing a "not a valid Win32 application" error.
$ErrorActionPreference = "Stop"
$hdr = @{ "User-Agent" = "gh-aw-book"; "Accept" = "application/vnd.github+json" }
$rel = Invoke-RestMethod -Uri "https://api.github.com/repos/github/gh-aw/releases/latest" -Headers $hdr
$tag = $rel.tag_name
$arch = if ($env:PROCESSOR_ARCHITECTURE -eq "ARM64") { "windows-arm64.exe" } else { "windows-amd64.exe" }
$asset = $rel.assets | Where-Object { $_.name -eq $arch }
$checks = $rel.assets | Where-Object { $_.name -eq "checksums.txt" }
Write-Host "Installing gh-aw $tag ($arch)"
$extDir = Join-Path $env:LOCALAPPDATA "GitHub CLI\extensions\gh-aw"
New-Item -ItemType Directory -Force -Path $extDir | Out-Null
$binPath = Join-Path $extDir "gh-aw.exe"
curl.exe -sSL -o $binPath $asset.browser_download_url
if ($LASTEXITCODE -ne 0) { throw "curl download failed (exit $LASTEXITCODE)" }
$sumPath = Join-Path $env:TEMP "gh-aw-checksums.txt"
curl.exe -sSL -o $sumPath $checks.browser_download_url
$expected = (Select-String -Path $sumPath -Pattern ([regex]::Escape($arch)) | Select-Object -First 1).Line.Split(' ')[0].Trim()
$actual = (Get-FileHash -Path $binPath -Algorithm SHA256).Hash.ToLower()
if ($expected -ne $actual) { throw "Checksum mismatch! expected=$expected actual=$actual" }
Write-Host "Checksum OK: $actual"
$manifest = "owner: github`nname: gh-aw`nhost: github.com`ntag: $tag`nispinned: false`npath: $binPath`n"
Set-Content -Path (Join-Path $extDir "manifest.yml") -Value $manifest -Encoding utf8
Write-Host "--- gh aw version ---"
gh aw version
