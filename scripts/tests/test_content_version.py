import unittest

from helpers import SourceTest

import content_version


class VersionTests(SourceTest):
    def test_valid_two_and_three_component_versions(self):
        for version in ("0.0", "1.1", "1.1.1", "12.100.3"):
            with self.subTest(version=version):
                self.assertEqual(content_version.validate_version(version), version)
                self.assertEqual(content_version.tag_for(version), f"content-v{version}")

    def test_invalid_versions_cannot_become_release_tags(self):
        for version in ("", "v1.1", "V1.1", "1", "1.2.3.4", "01.1", "1.02", "1.2.03",
                        "-1.1", "1.1-beta", "1.1+build", "1.1\nbad", " 1.1", "1.1 "):
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    content_version.tag_for(version)

    def test_missing_or_empty_version_never_defaults(self):
        path = self.root / "content" / "VERSION"
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing required"):
            content_version.read_version(path)
        self.put("content/VERSION", "\n")
        with self.assertRaisesRegex(ValueError, "Invalid content version"):
            content_version.read_version(path)

    def test_crlf_and_surrounding_file_whitespace(self):
        path = self.put("content/VERSION", "1.2.3\r\n")
        self.assertEqual(content_version.read_version(path), "1.2.3")

    def test_framework_reader_requires_a_separate_exact_pin(self):
        path = self.put("content/FRAMEWORK_VERSION", "v0.88.7\r\n")
        self.assertEqual(content_version.read_framework_version(path), "v0.88.7")
        for version in ("", "latest", "0.88.7", "v0.88", "v00.88.7", "v0.88.7-rc.1"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                content_version.validate_framework_version(version)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing required framework"):
            content_version.read_framework_version(path)

    def test_existing_changelog_parser_is_preserved(self):
        path = self.put(
            "content/CHANGELOG.md",
            "## [1.2] - 2026-09-15\n\nSummary.\n\n### Changed\n\n"
            "- First line\n  continued.\n\n## [1.1] - 2026-07-08\n\nEarlier.\n",
        )
        releases = content_version.parse_changelog(path)
        self.assertEqual([release.version for release in releases], ["1.2", "1.1"])
        self.assertEqual(releases[0].summary, "Summary.")
        self.assertEqual(releases[0].groups[0].items, ["First line continued."])


if __name__ == "__main__":
    unittest.main()
