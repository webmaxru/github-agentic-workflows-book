import json
import os
import shutil
import subprocess
import unittest

from helpers import ROOT, SourceTest


PWSH = shutil.which("pwsh")
NO_COPILOT = "function global:copilot { throw 'A real Copilot invocation is forbidden in tests.' }\n"


@unittest.skipUnless(PWSH, "PowerShell is not installed")
class LauncherTests(SourceTest):
    def setUp(self):
        super().setUp()
        self.launcher = self.put(
            "scripts/run-fleet.ps1", (ROOT / "run-fleet.ps1").read_text(encoding="utf-8")
        )
        for name in ("update-book", "run-playbook", "release-content"):
            self.put(f".github/prompts/{name}.prompt.md", f"Fixture {name} prompt.\n")
        self.put("custom.prompt.md", "A custom fixture prompt.\n")

    def invoke(self, arguments, prefix=NO_COPILOT, **environment):
        return subprocess.run(
            [PWSH, "-NoProfile", "-NonInteractive", "-Command",
             prefix + f"& $env:LAUNCHER_PATH {arguments}"],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "LAUNCHER_PATH": str(self.launcher), **environment},
        )

    def test_launcher_parses_without_executing_it(self):
        command = r"""
        $tokens = $null
        $parseErrors = $null
        [System.Management.Automation.Language.Parser]::ParseFile(
            $env:LAUNCHER_PATH, [ref]$tokens, [ref]$parseErrors
        ) | Out-Null
        if ($parseErrors.Count -gt 0) {
            throw ($parseErrors | Out-String)
        }
        """
        result = subprocess.run(
            [PWSH, "-NoProfile", "-NonInteractive", "-Command", command],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "LAUNCHER_PATH": str(self.launcher)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_default_is_update_and_dry_run_never_requires_copilot(self):
        result = self.invoke(
            "-DryRun",
            prefix=NO_COPILOT + "function global:Get-Command { throw 'Dry run looked up Copilot.' }\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("update-book.prompt.md", result.stdout)
        self.assertIn("[DryRun]", result.stdout)

    def test_explicit_update_target_dry_run_never_resolves_copilot(self):
        result = self.invoke(
            "-Mode Update -TargetVersion v0.88.7 -DryRun",
            prefix=NO_COPILOT + "function global:Get-Command { throw 'Dry run looked up Copilot.' }\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("update-book.prompt.md", result.stdout)
        self.assertIn("Fixed framework target: v0.88.7", result.stdout)
        self.assertIn("[DryRun]", result.stdout)

    def test_target_override_rejects_non_exact_stable_tags(self):
        for version in (
            "", "0.88.7", "V0.88.7", "v0.88", "v0.88.7.1", "v0.88.7-rc.1",
            "v0.88.7+build", "v00.88.7", " v0.88.7", "v0.88.7 ",
        ):
            with self.subTest(version=version):
                result = self.invoke(
                    "-TargetVersion $env:LAUNCHER_TEST_TARGET -DryRun",
                    LAUNCHER_TEST_TARGET=version,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_target_override_rejects_terminal_newline_and_unicode_digits(self):
        for version in ("v0.88.7\n", "v0.8\u0668.7"):
            with self.subTest(version=version):
                result = self.invoke(
                    "-TargetVersion $env:LAUNCHER_TEST_TARGET -DryRun",
                    LAUNCHER_TEST_TARGET=version,
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_bootstrap_and_release_are_explicit_modes(self):
        for mode, name in (("Bootstrap", "run-playbook"), ("Release", "release-content")):
            with self.subTest(mode=mode):
                result = self.invoke(f"-Mode {mode} -DryRun")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"{name}.prompt.md", result.stdout)
                result = self.invoke(f"-Mode {mode} -TargetVersion v0.88.7 -DryRun")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("supported only with -Mode Update", result.stderr)

    def test_update_passes_exact_target_and_original_cli_arguments(self):
        result = self.invoke(
            "-TargetVersion v0.88.7",
            prefix="function global:copilot { ConvertTo-Json -InputObject @($args) -Compress; "
                   "$global:LASTEXITCODE = 0 }\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        arguments = json.loads(next(line for line in result.stdout.splitlines() if line.startswith("[")))
        self.assertEqual(arguments[0], "-p")
        self.assertEqual(arguments[2:], ["--allow-all-tools"])
        self.assertIn("Fixture update-book prompt.", arguments[1])
        self.assertIn("Invocation target: v0.88.7.", arguments[1])
        self.assertIn("do not resolve latest", arguments[1])
        result = self.invoke("-TargetVersion latest -DryRun")
        self.assertNotEqual(result.returncode, 0)

    def test_custom_prompt_is_exclusive_with_mode_and_target(self):
        result = self.invoke("-PromptPath custom.prompt.md -DryRun")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("custom.prompt.md", result.stdout)
        for extra in ("-Mode Update", "-TargetVersion v0.88.7"):
            with self.subTest(extra=extra):
                result = self.invoke(f"-PromptPath custom.prompt.md {extra} -DryRun")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Use -PromptPath alone", result.stderr)

    def test_missing_prompt_fails_without_falling_back_to_update(self):
        result = self.invoke("-PromptPath missing.prompt.md -DryRun")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Book prompt not found", result.stderr)

    def test_nonzero_copilot_exit_is_not_reported_as_success(self):
        result = self.invoke(
            "", prefix="function global:copilot { $global:LASTEXITCODE = 17 }\n"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Copilot failed with exit code 17", result.stderr)


if __name__ == "__main__":
    unittest.main()
