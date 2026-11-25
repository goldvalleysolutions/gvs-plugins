#!/usr/bin/env python3
"""Coordinator evals: deterministic checks that need no model and no login.

  python3 run_evals.py check              fixtures still give the hand-written golden answers,
                                          and model-eval/ is in sync with cases.json
  python3 run_evals.py generate           (re)write model-eval/ from cases.json and fixtures/
  python3 run_evals.py grade ANSWERS_DIR  grade recorded answers offline (see below)

`check` is the offline part (it runs in CI). It parses fixtures/ with a small reference
implementation of the rules the skills describe (weeks run Monday to Sunday, a bare weekday
means the next one on or after today, the "no personal appointments in the week view" rule,
overdue = open and due before today) and compares the result with the golden ids in cases.json.

`generate` writes one folder per case under model-eval/ in the layout `claude plugin eval`
reads (prompt.md, case.yaml, setup.sh, graders/*.md). Running them needs a Claude login and
uses the signed-in account's plan usage; see README.md in this folder.

`grade` scores model answers you saved by hand, with no login here: put the final reply in
ANSWERS_DIR/<case-id>.txt, and optionally the folder the run left behind in
ANSWERS_DIR/<case-id>/ (so file checks like tasks.md can run). Checks that need the run
transcript are listed as NOT CHECKED. Exit 1 if anything fails.

Standard library only. Python 3.9 or newer.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
MEM = FIX / "memory" / "coordinator"
OUT = HERE / "model-eval"
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SEND_TOOL = "mcp__[A-Za-z0-9_-]*(slack|teams)[A-Za-z0-9_-]*(send|post|message)"


# ----------------------------------------------------------------- reference rules

def d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def load_tasks():
    tasks = {}
    section = None
    for line in (MEM / "tasks.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        m = re.match(r"^- \[( |x)\] (T-\d+) \| (.*)$", line)
        if not m:
            continue
        fields = [f.strip() for f in m.group(3).split("|")]
        t = {"id": m.group(2), "done": m.group(1) == "x", "title": fields[0], "section": section}
        for f in fields[1:]:
            if ":" in f:
                k, v = f.split(":", 1)
                t[k.strip()] = v.strip()
        tasks[t["id"]] = t
    return tasks


def load_events():
    data = json.loads((FIX / "calendar.json").read_text(encoding="utf-8"))
    return {e["id"]: {**e, "date": e["start"][:10]} for e in data["events"]}


def hides_personal_in_week() -> bool:
    return bool(re.search(r"do not include personal appointments in the week view",
                          (MEM / "rules.md").read_text(encoding="utf-8"), re.I))


def week_bounds(day: dt.date):
    mon = day - dt.timedelta(days=day.weekday())
    return mon, mon + dt.timedelta(days=6)


def compute(query: dict, today: dt.date) -> list:
    """Return the ids a correct answer must contain, sorted."""
    tasks, events = load_tasks(), load_events()
    opn = [t for t in tasks.values() if not t["done"]]
    done = [t for t in tasks.values() if t["done"]]
    kind = query["kind"]
    ids = set()
    overdue = [t for t in opn if d(t["due"]) < today]
    if kind in ("today", "today_tasks_only"):
        ids |= {t["id"] for t in opn if d(t["due"]) == today} | {t["id"] for t in overdue}
        if kind == "today":
            ids |= {e["id"] for e in events.values() if d(e["date"]) == today}
    elif kind == "week":
        _, sun = week_bounds(today)
        ids |= {t["id"] for t in opn if today <= d(t["due"]) <= sun} | {t["id"] for t in overdue}
        for e in events.values():
            if today <= d(e["date"]) <= sun and not (hides_personal_in_week() and e["calendar"] == "Personal"):
                ids.add(e["id"])
    elif kind == "day":
        target = today + dt.timedelta(days=(WEEKDAYS.index(query["weekday"]) - today.weekday()) % 7)
        ids |= {t["id"] for t in opn if d(t["due"]) == target}
        ids |= {e["id"] for e in events.values() if d(e["date"]) == target}
    elif kind == "completed_week":
        mon, _ = week_bounds(today)
        ids |= {t["id"] for t in done if mon <= d(t["completed"]) <= today}
    elif kind == "person_last_week":
        mon, sun = week_bounds(today - dt.timedelta(days=7))
        ids |= {t["id"] for t in done if t["assignee"].lower() == query["person"].lower()
                and mon <= d(t["completed"]) <= sun}
    elif kind == "needs_you":
        ids |= {t["id"] for t in opn if d(t["due"]) == today} | {t["id"] for t in overdue}
        ids |= {e["id"] for e in events.values() if today <= d(e["date"]) <= today + dt.timedelta(days=1)}
    else:
        raise ValueError(f"unknown query kind {kind!r}")
    return sorted(ids)


# --------------------------------------------------------------------- graders

def alt(words):
    return "|".join(re.escape(w) for w in words)


def include_all(words):
    return "".join(f"(?=[\\s\\S]*{re.escape(w)})" for w in words)


def build_graders(case: dict) -> list:
    """Graders for a case: dicts with name, type and the claude plugin eval grader keys."""
    keys = CASES["keys"]
    g = []
    if "expect" in case:
        want = [keys[i] for i in case["expect"]]
        # Items that must not appear: every known item that is not expected and whose phrase is not expected.
        other = sorted({keys[i] for i in keys if i not in case["expect"]} - set(want))
        if want:
            g.append({"name": "must-include", "type": "regex", "pattern": include_all(want), "flags": "i"})
        if other:
            g.append({"name": "must-not-include", "type": "regex", "pattern": alt(other),
                      "flags": "i", "match": "not_contains"})
    for x in case.get("extra", []):
        g.append({"type": "regex", **x})
    if case.get("no_send_tool"):
        g.append({"name": "no-send-tool-called", "type": "regex", "target": "trace",
                  "pattern": SEND_TOOL, "flags": "i", "match": "not_contains"})
    if case.get("file_absent"):
        g.append({"name": "nothing-written-without-a-yes", "type": "file_exists",
                  "path": case["file_absent"], "exists": False})
    g.append({"name": "skill-fired", "type": "tool_used", "tool": "Skill", "arm": "with-only",
              "input_match": '"skill"\\s*:\\s*"(?:[\\w-]+:)?' + case["skill"] + '"'})
    return g


# ------------------------------------------------------------------- generation

def prompt_text(case: dict) -> str:
    today = d(CASES["today"])
    head = f"Today is {WEEKDAYS[today.weekday()]} {today.isoformat()} (America/New_York)."
    if case.get("calendar", True) and not case.get("empty"):
        head += " Google Calendar is not connected; my calendar export is the file calendar.json."
    return f"{head} {case['prompt']}\n"


def setup_script(case: dict) -> str:
    """Bash that writes the fixture notes (and calendar) into the empty eval folder."""
    if case.get("empty"):
        return "#!/bin/bash\nset -e\n# Empty folder on purpose: first run.\n"
    lines = ["#!/bin/bash", "set -e", "mkdir -p memory/coordinator"]
    files = [(p, f"memory/coordinator/{p.name}") for p in sorted(MEM.glob("*.md"))]
    if case.get("calendar", True):
        files.append((FIX / "calendar.json", "calendar.json"))
    for src, dest in files:
        lines.append(f"cat > {dest} <<'EVAL_FIXTURE_EOF'")
        lines.append(src.read_text(encoding="utf-8").rstrip("\n"))
        lines.append("EVAL_FIXTURE_EOF")
    return "\n".join(lines) + "\n"


def yaml_value(v):
    return json.dumps(v, ensure_ascii=False)  # JSON scalars and flow maps are valid YAML


def grader_md(g: dict) -> str:
    front = "\n".join(f"{k}: {yaml_value(v)}" for k, v in g.items() if k != "name")
    return f"---\n{front}\n---\n"


def generate_files() -> dict:
    """Return {relative path: text} for the whole model-eval/ tree."""
    files = {}
    for case in CASES["cases"]:
        base = f"{case['id']}"
        files[f"{base}/prompt.md"] = (
            "---\nmax_turns: 12\ntimeout_seconds: 300\n"
            "allowed_tools: [Read, Write, Edit, Glob, Grep, Skill]\n"
            f"tags: [coordinator, {case['skill']}]\n---\n\n" + prompt_text(case))
        files[f"{base}/case.yaml"] = (
            'schema_version: "1.1"\n'
            f"name: {case['id']}\n"
            f"description: {yaml_value(case['prompt'])}\n"
            "context:\n  scaffold_script: setup.sh\n")
        files[f"{base}/setup.sh"] = setup_script(case)
        for g in build_graders(case):
            files[f"{base}/graders/{g['name']}.md"] = grader_md({k: v for k, v in g.items()})
    return files


def cmd_generate() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    for rel, text in generate_files().items():
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"wrote {len(list(OUT.glob('*/prompt.md')))} cases to {OUT.name}/")
    return 0


# ------------------------------------------------------------------------ check

def cmd_check() -> int:
    problems = []
    today = d(CASES["today"])
    ids = [c["id"] for c in CASES["cases"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate case ids")
    tasks, events = load_tasks(), load_events()
    for k in CASES["keys"]:
        if k not in tasks and k not in events:
            problems.append(f"key {k} is not in the fixtures")
    for i in list(tasks) + list(events):
        if i not in CASES["keys"]:
            problems.append(f"fixture item {i} has no phrase in cases.json keys")
    for c in CASES["cases"]:
        for i in c.get("expect", []):
            if i not in CASES["keys"]:
                problems.append(f"{c['id']}: expected id {i} unknown")
        if "query" in c:
            got = compute(c["query"], today)
            if got != sorted(c["expect"]):
                problems.append(f"{c['id']}: fixtures give {got}, golden says {sorted(c['expect'])}")
        if c["skill"] not in ("setup", "tasks", "schedule", "self-test"):
            problems.append(f"{c['id']}: unknown skill {c['skill']}")
        for g in build_graders(c):
            if g["type"] == "regex":
                try:
                    re.compile(g["pattern"])
                except re.error as exc:
                    problems.append(f"{c['id']}/{g['name']}: bad pattern: {exc}")
    # Generated spec must be current.
    want = generate_files()
    have = {str(p.relative_to(OUT)): p.read_text(encoding="utf-8") for p in OUT.rglob("*") if p.is_file()} if OUT.exists() else {}
    if want != have:
        stale = sorted(set(want) ^ set(have) | {k for k in want if k in have and want[k] != have[k]})
        problems.append(f"model-eval/ is out of date ({len(stale)} files differ); run: python3 run_evals.py generate")
    for p in problems:
        print(f"[FAIL] {p}")
    n = len(CASES["cases"])
    if problems:
        print(f"FAILED: {len(problems)} problem(s) in {n} cases")
        return 1
    print(f"PASSED: {n} cases; fixtures match the golden answers; model-eval/ is current")
    return 0


# ------------------------------------------------------------------------ grade

def cmd_grade(answers: Path) -> int:
    failed = 0
    graded = 0
    for case in CASES["cases"]:
        f = answers / f"{case['id']}.txt"
        if not f.exists():
            print(f"[SKIP] {case['id']}: no {f.name}")
            continue
        graded += 1
        reply = f.read_text(encoding="utf-8")
        work = answers / case["id"]
        results = []
        for g in build_graders(case):
            if g["type"] == "tool_used" or g.get("target") == "trace":
                results.append((g["name"], None))
                continue
            if g["type"] == "file_exists":
                if not work.is_dir():
                    results.append((g["name"], None))
                    continue
                found = [p for p in work.glob(g["path"]) if p.is_file()]
                results.append((g["name"], (not found) if g.get("exists") is False else bool(found)))
                continue
            target = g.get("target", "last_message")
            if isinstance(target, dict):
                p = work / target["path"]
                if not p.is_file():
                    results.append((g["name"], None))
                    continue
                text = p.read_text(encoding="utf-8")
            else:
                text = reply
            hit = re.search(g["pattern"], text, re.I if "i" in g.get("flags", "") else 0) is not None
            results.append((g["name"], (not hit) if g.get("match") == "not_contains" else hit))
        bad = [n for n, ok in results if ok is False]
        unchecked = [n for n, ok in results if ok is None]
        print(f"[{'FAIL' if bad else 'PASS'}] {case['id']}" + (f"  failed: {', '.join(bad)}" if bad else "")
              + (f"  NOT CHECKED offline: {', '.join(unchecked)}" if unchecked else ""))
        failed += bool(bad)
    print(f"{graded} graded, {failed} failed")
    return 1 if failed or graded == 0 else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("generate")
    g = sub.add_parser("grade")
    g.add_argument("answers", type=Path)
    a = ap.parse_args(argv)
    return {"check": cmd_check, "generate": cmd_generate}.get(a.cmd, lambda: cmd_grade(a.answers))()


if __name__ == "__main__":
    sys.exit(main())
