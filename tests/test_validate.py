"""Tests for scripts/validate.py. Standard library only: python3 -m unittest discover -s tests -v"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "validate.py"
FIXTURES = REPO / "tests" / "fixtures"


def run(root, *args, env=None, path_override=None):
    e = dict(os.environ)
    e.pop("CLAUDE_BIN", None)
    if path_override is not None:
        e["PATH"] = path_override
    if env:
        e.update(env)
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True, env=e)
    return proc.returncode, proc.stdout + proc.stderr


def read(p):
    return json.loads(Path(p).read_text())


def write(p, data):
    Path(p).write_text(json.dumps(data, indent=2) + "\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gvs-validate-"))
        self.root = self.tmp / "m"
        shutil.copytree(FIXTURES / "good", self.root)
        self.plugin = self.root / "plugins" / "demo-plugin"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def assertFails(self, expected_text, *args):
        code, out = run(self.root, "--no-cli", *args)
        self.assertEqual(code, 1, out)
        self.assertIn("[FAIL]", out)
        self.assertIn(expected_text, out)
        self.assertIn("FAILED", out)


class PassingCases(unittest.TestCase):
    def test_repository_itself_passes(self):
        code, out = run(REPO, "--no-cli")
        self.assertEqual(code, 0, out)
        self.assertIn("PASSED", out)
        self.assertNotIn("[FAIL]", out)

    def test_good_fixture_passes(self):
        code, out = run(FIXTURES / "good", "--no-cli")
        self.assertEqual(code, 0, out)

    def test_no_cli_prints_skipped_line(self):
        code, out = run(FIXTURES / "good", "--no-cli")
        self.assertIn("[SKIPPED] claude-cli", out)
        self.assertIn("NOT run", out)


class BrokenManifest(unittest.TestCase):
    """The deliberately broken fixture must fail loudly."""

    def test_broken_fixture_fails(self):
        code, out = run(FIXTURES / "broken-manifest", "--no-cli")
        self.assertEqual(code, 1, out)
        self.assertIn("FAILED", out)
        self.assertIn("`description` is required", out)
        self.assertIn("`version` differs across manifests", out)
        self.assertIn("SKILL.md has no frontmatter", out)


class Mutations(Base):
    def test_invalid_json(self):
        (self.plugin / ".claude-plugin" / "plugin.json").write_text("{ not json")
        self.assertFails("is not valid JSON")

    def test_missing_manifest(self):
        (self.plugin / ".cursor-plugin" / "plugin.json").unlink()
        self.assertFails("missing file plugin.json")

    def test_marketplace_name_wrong(self):
        p = self.root / ".claude-plugin" / "marketplace.json"
        d = read(p); d["name"] = "someoneelse"; write(p, d)
        self.assertFails("must be 'goldvalleysolutions'")

    def test_marketplace_names_differ_between_surfaces(self):
        p = self.root / ".cursor-plugin" / "marketplace.json"
        d = read(p); d["name"] = "other"; write(p, d)
        self.assertFails("name differs")

    def test_reserved_marketplace_name(self):
        for surface in (".claude-plugin", ".cursor-plugin"):
            p = self.root / surface / "marketplace.json"
            d = read(p); d["name"] = "claude-plugins-official"; write(p, d)
        self.assertFails("is reserved")

    def test_missing_owner(self):
        p = self.root / ".claude-plugin" / "marketplace.json"
        d = read(p); del d["owner"]; write(p, d)
        self.assertFails("`owner.name` is required")

    def test_plugins_not_array(self):
        p = self.root / ".cursor-plugin" / "marketplace.json"
        d = read(p); d["plugins"] = {}; write(p, d)
        self.assertFails("`plugins` must be an array")

    def test_plugin_lists_differ(self):
        p = self.root / ".cursor-plugin" / "marketplace.json"
        d = read(p); d["plugins"] = []; write(p, d)
        self.assertFails("plugin lists differ")

    def test_source_with_dotdot(self):
        p = self.root / ".claude-plugin" / "marketplace.json"
        d = read(p); d["plugins"][0]["source"] = "./../elsewhere"; write(p, d)
        self.assertFails('contains ".."')

    def test_source_missing_folder(self):
        for surface, src in ((".claude-plugin", "./plugins/nope"), (".cursor-plugin", "plugins/nope")):
            p = self.root / surface / "marketplace.json"
            d = read(p); d["plugins"][0]["source"] = src; write(p, d)
        self.assertFails("source does not exist")

    def test_entry_name_differs_from_manifest_name(self):
        for surface in (".claude-plugin", ".cursor-plugin"):
            p = self.root / surface / "marketplace.json"
            d = read(p); d["plugins"][0]["name"] = "renamed"; write(p, d)
        self.assertFails("must equal the marketplace entry name")

    def test_unlisted_plugin_folder(self):
        shutil.copytree(self.plugin, self.root / "plugins" / "orphan")
        self.assertFails("plugins/orphan is not listed")

    def test_version_mismatch(self):
        p = self.plugin / ".cursor-plugin" / "plugin.json"
        d = read(p); d["version"] = "2.0.0"; write(p, d)
        self.assertFails("`version` differs across manifests")

    def test_description_mismatch(self):
        p = self.plugin / "plugin.json"
        d = read(p); d["description"] = "Something else"; write(p, d)
        self.assertFails("`description` differs across manifests")

    def test_agent_plugin_missing_schema(self):
        p = self.plugin / "plugin.json"
        d = read(p); del d["$schema"]; write(p, d)
        self.assertFails("`$schema` must be")

    def test_agent_plugin_extra_key(self):
        p = self.plugin / "plugin.json"
        d = read(p); d["skills"] = "./skills"; write(p, d)
        self.assertFails("keys not allowed by the Agent Plugins schema")

    def test_referenced_path_missing(self):
        p = self.plugin / ".claude-plugin" / "plugin.json"
        d = read(p); d["commands"] = "./commands/"; write(p, d)
        self.assertFails("does not exist")

    def test_referenced_path_escapes(self):
        p = self.plugin / ".cursor-plugin" / "plugin.json"
        d = read(p); d["logo"] = "../logo.png"; write(p, d)
        self.assertFails('contains ".."')

    def test_skill_without_frontmatter(self):
        (self.plugin / "skills" / "hello" / "SKILL.md").write_text("Just text.\n")
        self.assertFails("has no frontmatter")

    def test_skill_missing_description(self):
        (self.plugin / "skills" / "hello" / "SKILL.md").write_text("---\nname: hello\n---\nBody\n")
        self.assertFails("`description` is missing")

    def test_skill_name_must_match_folder(self):
        (self.plugin / "skills" / "hello" / "SKILL.md").write_text("---\nname: other\ndescription: x\n---\nBody\n")
        self.assertFails("must match the folder name")

    def test_skill_folder_without_skill_md(self):
        (self.plugin / "skills" / "empty").mkdir()
        self.assertFails("missing SKILL.md")

    def test_plugin_without_skills(self):
        shutil.rmtree(self.plugin / "skills")
        self.assertFails("missing skills/ directory")

    def test_mcp_files_must_match(self):
        write(self.plugin / ".mcp.json", {"mcpServers": {"a": {"command": "x"}}})
        write(self.plugin / "mcp.json", {"mcpServers": {"b": {"command": "y"}}})
        self.assertFails("must hold the same servers")

    def test_mcp_file_alone_fails(self):
        write(self.plugin / ".mcp.json", {"mcpServers": {}})
        self.assertFails("missing file mcp.json")

    def test_missing_template(self):
        shutil.rmtree(self.root / "templates")
        self.assertFails("templates/plugin is missing")

    def test_missing_marketplace_file(self):
        (self.root / ".cursor-plugin" / "marketplace.json").unlink()
        self.assertFails("missing file marketplace.json")


class CliHandling(Base):
    def fake_cli(self, exit_code, text):
        d = self.tmp / "bin"
        d.mkdir(exist_ok=True)
        exe = d / "claude"
        exe.write_text(f"#!/bin/sh\necho '{text}'\nexit {exit_code}\n")
        exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
        return str(d)

    def empty_path(self):
        d = self.tmp / "empty"
        d.mkdir(exist_ok=True)
        return str(d)

    def test_missing_cli_is_skipped_not_silent(self):
        code, out = run(self.root, path_override=self.empty_path())
        self.assertEqual(code, 0, out)
        self.assertIn("[SKIPPED] claude-cli", out)
        self.assertIn("claude CLI not found", out)

    def test_require_cli_fails_when_missing(self):
        code, out = run(self.root, "--require-cli", path_override=self.empty_path())
        self.assertEqual(code, 1, out)
        self.assertIn("--require-cli", out)

    def test_require_cli_with_no_cli_is_rejected(self):
        code, out = run(self.root, "--require-cli", "--no-cli")
        self.assertEqual(code, 1, out)

    def test_explicit_cli_path_that_does_not_exist_fails(self):
        code, out = run(self.root, "--cli", "/nonexistent/claude")
        self.assertEqual(code, 1, out)
        self.assertIn("was not found", out)

    def test_cli_failure_fails_validate(self):
        bin_dir = self.fake_cli(1, "Validation failed")
        code, out = run(self.root, path_override=bin_dir)
        self.assertEqual(code, 1, out)
        self.assertIn("claude plugin validate exited 1", out)

    def test_cli_exit_zero_but_failed_text_still_fails(self):
        bin_dir = self.fake_cli(0, "Validation failed")
        code, out = run(self.root, path_override=bin_dir)
        self.assertEqual(code, 1, out)

    def test_cli_pass_is_reported(self):
        bin_dir = self.fake_cli(0, "Validation passed")
        code, out = run(self.root, path_override=bin_dir)
        self.assertEqual(code, 0, out)
        self.assertIn("[PASS]    claude-cli marketplace", out)
        self.assertIn("[PASS]    claude-cli plugin demo-plugin", out)
        self.assertIn("[PASS]    claude-cli template", out)
        self.assertNotIn("SKIPPED", out)


if __name__ == "__main__":
    unittest.main()
