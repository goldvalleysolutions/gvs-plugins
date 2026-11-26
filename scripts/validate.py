#!/usr/bin/env python3
"""Validate the Gold Valley plugin marketplace and every plugin folder.

What it checks
--------------
1. Marketplace: `.claude-plugin/marketplace.json` and `.cursor-plugin/marketplace.json`
   (required fields, name rules, same name on both surfaces, same plugin list,
   every plugin source exists and resolves to the same folder on both surfaces).
2. Plugin folders: every `plugins/*` folder plus `templates/plugin`:
   three manifests (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`,
   root `plugin.json` for Agent Plugins) that agree on name, version and
   description; paths referenced by a manifest exist; every skill has a
   `SKILL.md` with frontmatter (`name`, `description`); optional MCP files agree.
3. When the `claude` CLI is available, also runs `claude plugin validate`
   on the marketplace root and on every plugin folder.

It never passes silently: any failed check exits 1. A missing CLI prints a
SKIPPED line, and `--require-cli` turns that into a failure.

Formats (checked against the docs in 2026-11; they are still moving):
  Claude marketplace  https://code.claude.com/docs/en/plugins/marketplace-reference
  Claude plugin       https://code.claude.com/docs/en/plugins/manifest-reference
  Cursor plugins      https://cursor.com/docs/reference/plugins
  Agent Plugins       https://agent-plugins.org/plugin-authors/manifest
  Agent Skills        https://agentskills.io/specification

Standard library only. Python 3.9 or newer.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MARKETPLACE_NAME = "goldvalleysolutions"
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

# Claude marketplace/plugin entry names: letters, digits, '.', '_', '-', start with a letter or digit, no '..'.
CLAUDE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
# Agent Plugins name: 1-64 chars, lowercase letters, digits, hyphens, periods; no '--' or '..'.
# We hold every plugin name to this stricter rule so all three surfaces accept it.
PLUGIN_NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
# Agent Skills name: lowercase letters, digits, hyphens; no leading, trailing or double hyphen.
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Subset of the reserved Claude marketplace names (full list in the marketplace reference).
RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "anthropic-marketplace", "anthropic-plugins", "agent-skills", "anthropic-agent-skills",
    "knowledge-work-plugins", "claude-plugins-community", "inline", "builtin", "skills-dir", "synced",
}

# Top-level keys the Agent Plugins schema allows (the schema is closed).
AGENT_PLUGIN_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
# Manifest keys whose string values are paths inside the plugin.
PATH_KEYS = ("skills", "commands", "agents", "rules", "hooks", "mcpServers",
             "outputStyles", "lspServers", "logo")
# Fields that must be identical across the three plugin manifests.
SHARED_FIELDS = ("name", "version", "description")


class Report:
    def __init__(self, verbose: bool = False) -> None:
        self.failures = 0
        self.skipped = 0
        self.passed = 0
        self.verbose = verbose

    def ok(self, scope: str, msg: str) -> None:
        self.passed += 1
        print(f"[PASS]    {scope}: {msg}")

    def fail(self, scope: str, msg: str) -> None:
        self.failures += 1
        print(f"[FAIL]    {scope}: {msg}")

    def skip(self, scope: str, msg: str) -> None:
        self.skipped += 1
        print(f"[SKIPPED] {scope}: {msg}")


def load_json(path: Path, scope: str, rep: Report):
    """Return parsed JSON object, or None after reporting a failure."""
    if not path.is_file():
        rep.fail(scope, f"missing file {path.name}")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        rep.fail(scope, f"{path} is not valid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        rep.fail(scope, f"{path} must contain a JSON object")
        return None
    return data


def is_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def clean_rel(value: str) -> str:
    """Normalize './a/b' and 'a/b' to 'a/b'."""
    v = value.replace("\\", "/")
    while v.startswith("./"):
        v = v[2:]
    return v.rstrip("/")


def path_problem(value: str) -> str | None:
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return "absolute path"
    if ".." in value.replace("\\", "/").split("/"):
        return 'contains ".."'
    if "\\" in value:
        return "contains a backslash"
    return None


# ---------------------------------------------------------------- marketplace

def check_marketplace_file(path: Path, surface: str, rep: Report):
    """Common checks. Returns (data, {entry name: source string}) or (None, None)."""
    scope = f"marketplace/{surface}"
    data = load_json(path, scope, rep)
    if data is None:
        return None, None
    before = rep.failures
    name = data.get("name")
    if not is_str(name):
        rep.fail(scope, "`name` is required")
    else:
        if not CLAUDE_NAME_RE.match(name) or ".." in name:
            rep.fail(scope, f"`name` {name!r} is not a valid marketplace name")
        if name != MARKETPLACE_NAME:
            rep.fail(scope, f"`name` must be {MARKETPLACE_NAME!r}, found {name!r}")
        if name.lower() in RESERVED_MARKETPLACE_NAMES:
            rep.fail(scope, f"`name` {name!r} is reserved")
    owner = data.get("owner")
    if not isinstance(owner, dict) or not is_str(owner.get("name")):
        rep.fail(scope, "`owner.name` is required")
    plugins = data.get("plugins")
    entries: dict = {}
    if not isinstance(plugins, list):
        rep.fail(scope, "`plugins` must be an array (it may be empty)")
    else:
        for i, entry in enumerate(plugins):
            where = f"plugins[{i}]"
            if not isinstance(entry, dict):
                rep.fail(scope, f"{where} must be an object")
                continue
            ename, source = entry.get("name"), entry.get("source")
            if not is_str(ename):
                rep.fail(scope, f"{where}.name is required")
                continue
            if not CLAUDE_NAME_RE.match(ename) or ".." in ename or not PLUGIN_NAME_RE.match(ename):
                rep.fail(scope, f"{where}.name {ename!r} must be lowercase kebab-case")
            if ename in entries:
                rep.fail(scope, f"duplicate plugin name {ename!r}")
            if not is_str(source):
                rep.fail(scope, f"{where} ({ename}): `source` must be a relative path string")
                continue
            problem = path_problem(source)
            if problem:
                rep.fail(scope, f"{where} ({ename}): source {source!r}: {problem}")
            entries[ename] = source
    if rep.failures == before:
        rep.ok(scope, f"{path.name} fields OK ({len(entries)} plugin(s) listed)")
    return data, entries


def resolve_source(root: Path, surface: str, data: dict, source: str) -> Path:
    base = root
    if surface == "cursor":
        pr = (data.get("metadata") or {}).get("pluginRoot")
        if is_str(pr):
            base = root / clean_rel(pr)
    return base / clean_rel(source)


def check_marketplaces(root: Path, rep: Report):
    """Returns the list of plugin folders (as Paths) that the marketplaces list."""
    claude, c_entries = check_marketplace_file(root / ".claude-plugin" / "marketplace.json", "claude", rep)
    cursor, u_entries = check_marketplace_file(root / ".cursor-plugin" / "marketplace.json", "cursor", rep)
    if claude is None or cursor is None:
        return None
    scope = "marketplace"
    before = rep.failures
    if claude.get("name") != cursor.get("name"):
        rep.fail(scope, f"name differs: claude={claude.get('name')!r}, cursor={cursor.get('name')!r}")
    if set(c_entries) != set(u_entries):
        only_c = sorted(set(c_entries) - set(u_entries))
        only_u = sorted(set(u_entries) - set(c_entries))
        rep.fail(scope, f"plugin lists differ: only in claude {only_c}, only in cursor {only_u}")
    folders = []
    for ename in sorted(set(c_entries) & set(u_entries)):
        c_dir = resolve_source(root, "claude", claude, c_entries[ename])
        u_dir = resolve_source(root, "cursor", cursor, u_entries[ename])
        for surface, d in (("claude", c_dir), ("cursor", u_dir)):
            if not d.is_dir():
                rep.fail(scope, f"{ename}: {surface} source does not exist: {d.relative_to(root) if d.is_relative_to(root) else d}")
        if c_dir.is_dir() and u_dir.is_dir():
            if c_dir.resolve() != u_dir.resolve():
                rep.fail(scope, f"{ename}: claude and cursor sources point to different folders")
            folders.append((ename, c_dir))
    # Every folder under plugins/ must be listed.
    listed = {d.resolve() for _, d in folders}
    plugins_dir = root / "plugins"
    if plugins_dir.is_dir():
        for child in sorted(plugins_dir.iterdir()):
            if child.is_dir() and not child.name.startswith(".") and child.resolve() not in listed:
                rep.fail(scope, f"plugins/{child.name} is not listed in both marketplace files")
    if rep.failures == before:
        rep.ok(scope, "both marketplaces agree")
    return folders


# --------------------------------------------------------------------- plugin

def parse_frontmatter(text: str):
    """Tiny frontmatter reader (stdlib only): returns dict of top-level keys or None.

    Handles `key: value`, quoted values and folded/literal block values. It is a
    presence check, not a YAML parser; `claude plugin validate` does the rest.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    fm: dict = {}
    key = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m and not line[0].isspace():
            key = m.group(1)
            val = m.group(2).strip()
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                val = ""
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            fm[key] = val
        elif key is not None and line[0].isspace():
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def check_skills(folder: Path, scope: str, rep: Report):
    skills_dir = folder / "skills"
    if not skills_dir.is_dir():
        rep.fail(scope, "missing skills/ directory")
        return
    subdirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    if not subdirs:
        rep.fail(scope, "skills/ has no skill folders")
        return
    before = rep.failures
    for sd in subdirs:
        sk = f"{scope} skill {sd.name}"
        md = sd / "SKILL.md"
        if not md.is_file():
            rep.fail(sk, "missing SKILL.md")
            continue
        fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        if fm is None:
            rep.fail(sk, "SKILL.md has no frontmatter (the file must start with --- and close with ---)")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if not name:
            rep.fail(sk, "frontmatter `name` is missing")
        else:
            if not SKILL_NAME_RE.match(name) or len(name) > 64:
                rep.fail(sk, f"frontmatter name {name!r} must be lowercase letters, digits and single hyphens (max 64)")
            if name != sd.name:
                rep.fail(sk, f"frontmatter name {name!r} must match the folder name {sd.name!r}")
        if not desc:
            rep.fail(sk, "frontmatter `description` is missing or empty")
        elif len(desc) > 1024:
            rep.fail(sk, f"frontmatter description is {len(desc)} characters (max 1024)")
    if rep.failures == before:
        rep.ok(scope, f"{len(subdirs)} skill(s) have valid frontmatter")


def referenced_paths(manifest: dict):
    for key in PATH_KEYS:
        v = manifest.get(key)
        vals = [v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else []
        for s in vals:
            if not s.startswith(("http://", "https://")):
                yield key, s


def check_plugin(folder: Path, root: Path, rep: Report, expect_name: str | None = None, is_template: bool = False):
    rel = folder.relative_to(root).as_posix() if folder.is_relative_to(root) else str(folder)
    scope = f"plugin {rel}"
    before = rep.failures
    claude = load_json(folder / ".claude-plugin" / "plugin.json", scope, rep)
    cursor = load_json(folder / ".cursor-plugin" / "plugin.json", scope, rep)
    agent = load_json(folder / "plugin.json", scope, rep)
    manifests = [("claude", claude), ("cursor", cursor), ("agent", agent)]
    present = [(s, m) for s, m in manifests if m is not None]

    for surface, m in present:
        sc = f"{scope} [{surface}]"
        name = m.get("name")
        if not is_str(name):
            rep.fail(sc, "`name` is required")
        elif not PLUGIN_NAME_RE.match(name) or len(name) > 64:
            rep.fail(sc, f"`name` {name!r} must be lowercase kebab-case (max 64)")
        for field in ("version", "description"):
            if not is_str(m.get(field)):
                rep.fail(sc, f"`{field}` is required here so all three manifests can agree")
        author = m.get("author")
        if author is not None and (not isinstance(author, dict) or not is_str(author.get("name"))):
            rep.fail(sc, "`author` must be an object with a `name`")
        for key, p in referenced_paths(m):
            problem = path_problem(p)
            if problem:
                rep.fail(sc, f"`{key}` path {p!r}: {problem}")
            elif not (folder / clean_rel(p)).exists():
                rep.fail(sc, f"`{key}` path {p!r} does not exist")
        if surface == "agent":
            if m.get("$schema") != AGENT_PLUGINS_SCHEMA:
                rep.fail(sc, f"`$schema` must be {AGENT_PLUGINS_SCHEMA}")
            extra = sorted(set(m) - AGENT_PLUGIN_KEYS)
            if extra:
                rep.fail(sc, f"keys not allowed by the Agent Plugins schema: {extra} (client data goes under `extensions`)")

    # Agreement across surfaces.
    if len(present) == 3:
        for field in SHARED_FIELDS:
            values = {s: m.get(field) for s, m in present}
            if len({v for v in values.values()}) > 1:
                rep.fail(scope, f"`{field}` differs across manifests: {values}")
    if expect_name and claude and agent and claude.get("name") != expect_name:
        rep.fail(scope, f"manifest name {claude.get('name')!r} must equal the {('marketplace entry' if not is_template else 'expected')} name {expect_name!r}")

    check_skills(folder, scope, rep)

    # Optional MCP files: both or neither, and identical.
    a, b = folder / ".mcp.json", folder / "mcp.json"
    if a.exists() or b.exists():
        ja, jb = load_json(a, scope, rep), load_json(b, scope, rep)
        if ja is not None and jb is not None and ja != jb:
            rep.fail(scope, ".mcp.json and mcp.json must hold the same servers")

    if rep.failures == before:
        rep.ok(scope, "manifests agree and skills are valid")
    return claude


# ------------------------------------------------------------------------ CLI

def find_cli(explicit: str | None):
    """Return (path or None, error message or None)."""
    cand = explicit or os.environ.get("CLAUDE_BIN")
    if cand:
        found = shutil.which(cand)
        if found:
            return found, None
        return None, f"claude CLI {cand!r} (from --cli or CLAUDE_BIN) was not found"
    return shutil.which("claude"), None


def run_cli(cli: str, target: Path, strict: bool, scope: str, rep: Report):
    cmd = [cli, "plugin", "validate", str(target)] + (["--strict"] if strict else [])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as exc:
        rep.fail(scope, f"claude plugin validate could not run: {exc}")
        return
    out = (proc.stdout or "") + (proc.stderr or "")
    lines = [ln for ln in out.splitlines() if ln.strip()]
    verdict = lines[-1].strip() if lines else "(no output)"
    failed = proc.returncode != 0 or "Validation failed" in out
    if failed:
        rep.fail(scope, f"claude plugin validate exited {proc.returncode}: {verdict}")
        for ln in lines:
            print(f"            | {ln}")
    else:
        rep.ok(scope, f"claude plugin validate: {verdict}")
        if rep.verbose:
            for ln in lines:
                print(f"            | {ln}")


# ----------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate the plugin marketplace and every plugin folder.")
    ap.add_argument("--root", default=None, help="marketplace root (default: the repository containing this script)")
    ap.add_argument("--require-cli", action="store_true", help="fail (instead of SKIPPED) when the claude CLI is missing")
    ap.add_argument("--no-cli", action="store_true", help="do not run the claude CLI check (prints SKIPPED; incompatible with --require-cli)")
    ap.add_argument("--cli", default=None, help="path or name of the claude CLI (default: CLAUDE_BIN env var, then `claude` on PATH)")
    ap.add_argument("-v", "--verbose", action="store_true", help="print full claude CLI output")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    rep = Report(args.verbose)
    print(f"Validating {root}")

    if args.no_cli and args.require_cli:
        rep.fail("cli", "--no-cli and --require-cli cannot be used together")

    if not root.is_dir():
        rep.fail("root", f"{root} is not a directory")
    else:
        listed = check_marketplaces(root, rep)
        targets = []  # (scope, folder)
        for ename, folder in (listed or []):
            check_plugin(folder, root, rep, expect_name=ename)
            if folder.name != ename:
                rep.fail(f"plugin {folder.name}", f"folder name must equal the plugin name {ename!r}")
            targets.append((f"plugin {ename}", folder))
        template = root / "templates" / "plugin"
        if template.is_dir():
            check_plugin(template, root, rep, is_template=True)
            targets.append(("template", template))
        else:
            rep.fail("template", "templates/plugin is missing")

        # claude CLI
        if args.no_cli:
            rep.skip("claude-cli", "skipped by --no-cli; `claude plugin validate` NOT run")
        else:
            cli, err = find_cli(args.cli)
            if err:
                rep.fail("claude-cli", err)
            elif cli is None:
                if args.require_cli:
                    rep.fail("claude-cli", "claude CLI not found on PATH and --require-cli was given")
                else:
                    rep.skip("claude-cli", "claude CLI not found; `claude plugin validate` NOT run (install @anthropic-ai/claude-code, or pass --require-cli to make this a failure)")
            else:
                has_plugins = bool(listed)
                run_cli(cli, root, strict=has_plugins, scope="claude-cli marketplace", rep=rep)
                for scope, folder in targets:
                    run_cli(cli, folder, strict=True, scope=f"claude-cli {scope}", rep=rep)

    print("-" * 60)
    status = "FAILED" if rep.failures else "PASSED"
    print(f"{status}: {rep.passed} passed, {rep.failures} failed, {rep.skipped} skipped")
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
