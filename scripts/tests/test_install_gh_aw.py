import os
import shutil
import subprocess
import unittest

from helpers import ROOT, SourceTest


PWSH = shutil.which("pwsh")


@unittest.skipUnless(PWSH, "PowerShell is not installed")
class InstallerTests(SourceTest):
    def invoke(self, command, **environment):
        return subprocess.run(
            [PWSH, "-NoProfile", "-NonInteractive", "-Command", command],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "INSTALLER_PATH": str(ROOT / "install-gh-aw.ps1"), **environment},
        )

    def test_latest_and_empty_overrides_fail_before_any_download(self):
        for version in ("latest", ""):
            with self.subTest(version=version):
                result = self.invoke(
                    "& $env:INSTALLER_PATH -Version $env:TEST_VERSION",
                    TEST_VERSION=version,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Invalid framework version", result.stderr)

    def test_explicit_tags_reject_case_unicode_digits_and_terminal_newlines(self):
        for version in ("V0.88.7", "v0.8\u0668.7", "v0.88.7\n", "v0.88.7\r\n"):
            with self.subTest(version=version):
                result = self.invoke(
                    "function global:gh { throw 'Installer must reject the tag before GitHub access.' }\n"
                    "& $env:INSTALLER_PATH -Version $env:TEST_VERSION",
                    TEST_VERSION=version,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Invalid framework version", result.stderr)

    def test_missing_default_pin_never_falls_back_to_latest(self):
        installer = self.put("scripts/install-gh-aw.ps1", (ROOT / "install-gh-aw.ps1").read_text())
        (self.root / "content/FRAMEWORK_VERSION").unlink()
        result = self.invoke("& $env:INSTALLER_PATH", INSTALLER_PATH=str(installer))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing framework pin", result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows installer download path")
    def test_bad_hash_cleans_staging_and_preserves_existing_executable(self):
        target = self.root / "build/compiler"
        self.put("build/compiler/gh-aw.exe", "untouched existing executable")
        command = r'''
        function global:gh {
            $global:LASTEXITCODE = 0
            if ($args[1] -eq "view") {
                '{"tagName":"v0.81.6","assets":[{"name":"windows-amd64.exe"},{"name":"windows-arm64.exe"},{"name":"checksums.txt"}]}'
            } else {
                $destination = $args[[array]::IndexOf($args, "--dir") + 1]
                [IO.File]::WriteAllText((Join-Path $destination "windows-amd64.exe"), "bad download")
                [IO.File]::WriteAllText((Join-Path $destination "windows-arm64.exe"), "bad download")
                $zeros = "0" * 64
                [IO.File]::WriteAllText((Join-Path $destination "checksums.txt"),
                    "$zeros  windows-amd64.exe`n$zeros  windows-arm64.exe`n")
            }
        }
        & $env:INSTALLER_PATH -Version v0.81.6 -InstallDir $env:TARGET_DIR
        '''
        result = self.invoke(command, TARGET_DIR=str(target))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHA256 mismatch", result.stderr)
        self.assertEqual((target / "gh-aw.exe").read_text(), "untouched existing executable")
        self.assertEqual([path.name for path in target.iterdir()], ["gh-aw.exe"])


if __name__ == "__main__":
    unittest.main()
