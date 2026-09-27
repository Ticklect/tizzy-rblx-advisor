import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "tizzy-advisor" / "SKILL.md"


def frontmatter():
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("SKILL.md is missing YAML frontmatter")
    end = lines.index("---", 1)
    data = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


class DistributionTests(unittest.TestCase):
    def test_claude_frontmatter_meets_current_limits(self):
        meta = frontmatter()
        self.assertEqual(meta.get("name"), "tizzy-advisor")
        self.assertLessEqual(len(meta.get("name", "")), 64)
        self.assertLessEqual(len(meta.get("description", "")), 200)

    def test_plugin_manifest_versions_match(self):
        paths = [
            ROOT / "plugin.json",
            ROOT / ".codex-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "plugin.json",
        ]
        versions = {json.loads(p.read_text(encoding="utf-8-sig"))["version"] for p in paths}
        self.assertEqual(len(versions), 1, versions)

    def test_packager_normalizes_text_bytes_for_cross_platform_builds(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "tizzy_packager", ROOT / "scripts" / "package.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            path.write_bytes(b"\xef\xbb\xbfa\r\nb\r\n")
            _, data = module.file_entry(path, "sample.md")
            self.assertEqual(data, b"a\nb\n")

    def test_zip_metadata_is_os_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "package.py"), "--output", tmp],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for archive in Path(tmp).glob("*.zip"):
                with zipfile.ZipFile(archive) as zf:
                    self.assertEqual({info.create_system for info in zf.infolist()}, {3})
    def test_packager_builds_platform_specific_archives(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "package.py"), "--output", tmp],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            out = Path(tmp)
            chatgpt = out / "tizzy-rblx-advisor-chatgpt.zip"
            claude = out / "tizzy-rblx-advisor-claude.zip"
            universal = out / "tizzy-rblx-advisor-universal.zip"
            for archive in (chatgpt, claude, universal):
                self.assertTrue(archive.is_file(), archive)

            with zipfile.ZipFile(chatgpt) as zf:
                names = set(zf.namelist())
                self.assertIn("plugin.json", names)
                self.assertIn("skills/tizzy-advisor/SKILL.md", names)
                self.assertIn(".codex-plugin/plugin.json", names)

            with zipfile.ZipFile(claude) as zf:
                names = set(zf.namelist())
                self.assertIn("tizzy-advisor/skill.md", names)
                self.assertIn("tizzy-advisor/references/game-design.md", names)
                self.assertNotIn("skill.md", names)

            with zipfile.ZipFile(universal) as zf:
                names = set(zf.namelist())
                self.assertIn("README.md", names)
                self.assertIn("plugin.json", names)
                self.assertIn(".claude-plugin/plugin.json", names)
                self.assertIn(".agents/plugins/marketplace.json", names)

            sums = (out / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(sums), 3)

    def test_packager_check_mode_matches_committed_dist(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()