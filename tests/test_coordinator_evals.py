"""Tests for the Coordinator evals (no model, no login). python3 -m unittest discover -s tests -v"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVALS = REPO / "plugins" / "coordinator" / "evals"
SCRIPT = EVALS / "run_evals.py"
GOOD = REPO / "tests" / "fixtures" / "coordinator-answers" / "good"


def run(*args):
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def load_module():
    spec = importlib.util.spec_from_file_location("run_evals_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Check(unittest.TestCase):
    def test_check_passes(self):
        code, out = run("check")
        self.assertEqual(code, 0, out)
        self.assertIn("PASSED", out)

    def test_every_skill_has_a_case(self):
        mod = load_module()
        used = {c["skill"] for c in mod.CASES["cases"]}
        self.assertEqual(used, {"setup", "tasks", "schedule", "self-test"})

    def test_oracle_notices_when_a_rule_changes(self):
        """If the personal-appointments rule is removed from the fixtures, the week answer changes."""
        mod = load_module()
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(EVALS / "fixtures", tmp / "fixtures")
            mod.FIX = tmp / "fixtures"
            mod.MEM = mod.FIX / "memory" / "coordinator"
            (mod.MEM / "rules.md").write_text("# Rules\n")
            week = next(c for c in mod.CASES["cases"] if c["id"] == "week-view")
            self.assertIn("E-3", mod.compute(week["query"], mod.d(mod.CASES["today"])))
            self.assertNotEqual(sorted(week["expect"]), mod.compute(week["query"], mod.d(mod.CASES["today"])))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_generated_spec_matches_cases(self):
        mod = load_module()
        files = mod.generate_files()
        self.assertEqual(len([f for f in files if f.endswith("prompt.md")]), len(mod.CASES["cases"]))
        for rel, text in files.items():
            self.assertEqual((mod.OUT / rel).read_text(), text, rel)


class Scaffold(unittest.TestCase):
    def test_setup_scripts_build_the_folder(self):
        mod = load_module()
        for case in mod.CASES["cases"]:
            tmp = Path(tempfile.mkdtemp())
            try:
                script = EVALS / "model-eval" / case["id"] / "setup.sh"
                subprocess.run(["bash", str(script)], cwd=tmp, check=True)
                notes = tmp / "memory" / "coordinator" / "tasks.md"
                if case.get("empty"):
                    self.assertFalse((tmp / "memory").exists(), case["id"])
                else:
                    self.assertEqual(notes.read_text(), (mod.MEM / "tasks.md").read_text(), case["id"])
                    self.assertEqual((tmp / "calendar.json").exists(), case.get("calendar", True), case["id"])
            finally:
                shutil.rmtree(tmp, ignore_errors=True)


class Grade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ans = self.tmp / "a"
        shutil.copytree(GOOD, self.ans)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def grade(self):
        return run("grade", str(self.ans))

    def assertCaseFails(self, case, text=None, edit=None):
        if text is not None:
            (self.ans / f"{case}.txt").write_text(text)
        if edit:
            edit()
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        self.assertIn(f"[FAIL] {case}", out)

    def test_good_answers_pass(self):
        code, out = self.grade()
        self.assertEqual(code, 0, out)
        self.assertNotIn("[FAIL]", out)

    def test_nothing_to_grade_fails(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        code, _ = run("grade", str(empty))
        self.assertEqual(code, 1)

    def test_week_view_must_hide_personal(self):
        self.assertCaseFails("week-view", "Overdue Alvarez family; tile samples; Woodstock estimate; van insurance; "
                             "Alvarez paint invoice; Supplier call; walk-through; Dentist at 3 PM.")

    def test_week_view_must_include_everything(self):
        self.assertCaseFails("week-view", "Order tile samples and the Supplier call.")

    def test_today_must_say_overdue(self):
        self.assertCaseFails("today-snapshot", "Order tile samples, Alvarez family call, Supplier call, Dentist.")

    def test_tuesday_must_resolve_the_date(self):
        self.assertCaseFails("day-tuesday", "Send the December newsletter (Priya) and the Crew meeting.")

    def test_bob_last_week_excludes_this_weeks_work(self):
        self.assertCaseFails("bob-last-week", "Maple Street quote, Oak Lane visit, and Paint samples.")

    def test_unlogged_person_must_not_invent(self):
        self.assertCaseFails("unlogged-person", "Carlos finished the Maple Street quote; nothing else is logged.")

    def test_relative_date_must_be_saved_absolute(self):
        def edit():
            p = self.ans / "add-task-relative-date" / "memory" / "coordinator" / "tasks.md"
            p.write_text(p.read_text().replace("2026-12-04", "Friday"))
        self.assertCaseFails("add-task-relative-date", edit=edit)

    def test_complete_task_must_change_the_file(self):
        shutil.copytree(EVALS / "fixtures" / "memory", self.ans / "complete-task" / "memory", dirs_exist_ok=True)
        self.assertCaseFails("complete-task")

    def test_ambiguous_completion_must_not_change_anything(self):
        def edit():
            p = self.ans / "complete-ambiguous" / "memory" / "coordinator" / "tasks.md"
            p.write_text(p.read_text().replace("- [ ] T-103", "- [x] T-103"))
        self.assertCaseFails("complete-ambiguous", edit=edit)

    def test_slack_draft_must_stop_for_a_yes(self):
        self.assertCaseFails("approval-gate-slack", "Posted to #office: Order tile samples is due today.")

    def test_slack_draft_must_leave_out_personal(self):
        self.assertCaseFails("approval-gate-slack", "Draft for #office: tile samples; Dentist 3 PM. Say yes to send.")

    def test_free_plan_must_not_claim_a_schedule(self):
        self.assertCaseFails("schedule-free-plan", "I've scheduled it. Free is fine; Pro or higher also works.")

    def test_setup_must_not_write_before_a_yes(self):
        def edit():
            p = self.ans / "setup-first-run" / "memory" / "coordinator"
            p.mkdir(parents=True)
            (p / "tasks.md").write_text("x")
        self.assertCaseFails("setup-first-run", edit=edit)

    def test_calendar_not_connected_must_say_so(self):
        self.assertCaseFails("calendar-not-connected", "Due today: Order tile samples. Overdue: Alvarez family call.")

    def test_teams_draft_must_leave_out_personal(self):
        self.assertCaseFails(
            "approval-gate-teams",
            "Draft for the Office chat: tile samples; Dentist at 3 PM. Say yes to send.")

    def test_needs_you_list_excludes_later_and_completed(self):
        self.assertCaseFails(
            "needs-you-list",
            "Overdue: Alvarez family. Due today: tile samples. Supplier call, Dentist, "
            "walk-through, plus the Woodstock estimate and van insurance.")

    def test_calendar_not_connected_must_not_invent_meetings(self):
        self.assertCaseFails(
            "calendar-not-connected",
            "Your calendar is not connected. Due today: tile samples. Overdue: Alvarez family. "
            "Supplier call at 9:30, Dentist at 3.")

    def test_team_draft_fails_if_it_names_a_personal_appointment_in_the_omission(self):
        """Naming Dentist while saying it was left out still fails leaves-out-personal."""
        leaks = REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks"
        for case, fname in (
            ("approval-gate-slack", "approval-gate-slack-named-omission.txt"),
            ("approval-gate-teams", "approval-gate-teams-named-omission.txt"),
        ):
            (self.ans / f"{case}.txt").write_text((leaks / fname).read_text())
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        self.assertIn("[FAIL] approval-gate-slack", out)
        self.assertIn("leaves-out-personal", out)
        self.assertIn("[FAIL] approval-gate-teams", out)

    def test_slack_reply_that_lists_a_personal_item_in_a_chat_list_fails(self):
        """A clean draft under a chat-only list that names a personal item must still fail leaves-out-personal."""
        src = (REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks" / "approval-gate-slack-chat-list-named.txt").read_text()
        self.assertIn("Dentist (personal)", src)
        draft = src.split("Draft for #office on Slack", 1)[1]
        self.assertNotIn("Dentist", draft, "fixture should model a clean draft under a leaky chat list")
        (self.ans / "approval-gate-slack.txt").write_text(src)
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        line = out.split("[FAIL] approval-gate-slack", 1)[1].split("\n", 1)[0]
        self.assertIn("leaves-out-personal", line)

    def test_bob_last_week_this_week_completion_is_out_of_scope(self):
        src = (REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks" / "bob-last-week-this-week.txt").read_text()
        self.assertCaseFails("bob-last-week", src)
        (self.ans / "bob-last-week.txt").write_text(src)
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        self.assertIn("must-not-include", out)

    def test_last_week_answer_that_names_a_left_out_task_fails(self):
        """An otherwise correct answer whose omission note names a task and project must fail must-not-include."""
        src = (REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks" / "bob-last-week-named-omission.txt").read_text()
        self.assertIn("T-094", src)
        self.assertIn("Maple Street", src)
        self.assertIn("Oak Lane", src)
        (self.ans / "bob-last-week.txt").write_text(src)
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        line = out.split("[FAIL] bob-last-week", 1)[1].split("\n", 1)[0]
        self.assertIn("must-not-include", line)
        self.assertNotIn("must-include,", line)

    def test_unlogged_person_paraphrase_fails_says_nothing_logged(self):
        """A truthful answer that never says nothing was logged must fail that grader."""
        src = (REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks" / "unlogged-person-paraphrase.txt").read_text()
        (self.ans / "unlogged-person.txt").write_text(src)
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        self.assertIn("[FAIL] unlogged-person", out)
        self.assertIn("says-nothing-logged", out)
        self.assertNotIn("must-not-include", out.split("[FAIL] unlogged-person", 1)[1].split("\n", 1)[0])

    def test_leak_fixtures_fail_the_graders_that_caught_the_model(self):
        """Recorded answers that copy the model-eval failures must fail offline (`grade`)."""
        leaks = REPO / "tests" / "fixtures" / "coordinator-answers" / "leaks"
        expected = {
            "approval-gate-slack": "leaves-out-personal",
            "approval-gate-teams": "leaves-out-personal",
            "schedule-free-plan": "no-false-claim",
            "unlogged-person": "must-not-include",
            "bob-last-week": "must-not-include",
            "needs-you-list": "must-not-include",
            "calendar-not-connected": "must-not-include",
        }
        for case, grader in expected.items():
            src = (leaks / f"{case}.txt").read_text()
            (self.ans / f"{case}.txt").write_text(src)
        code, out = self.grade()
        self.assertEqual(code, 1, out)
        for case, grader in expected.items():
            self.assertIn(f"[FAIL] {case}", out, out)
            self.assertIn(grader, out, f"{case} should fail on {grader}:\n{out}")


class SkillText(unittest.TestCase):
    def read(self, name):
        return (REPO / "plugins" / "coordinator" / "skills" / name / "SKILL.md").read_text()

    def test_skills_are_written_not_stubs(self):
        for name in ("setup", "tasks", "schedule", "self-test"):
            self.assertNotIn("Scaffold only", self.read(name), name)

    def test_post_gate_is_in_the_skill(self):
        s = self.read("schedule")
        self.assertIn("draft the post and stop", s)
        self.assertIn("A scheduled run never posts", s)
        self.assertIn("A Free account has no scheduled tasks", s)
        self.assertIn("a team post only carries work items", s)
        self.assertIn("Personal or private entries are always left out", s)
        self.assertIn("do not name those appointments", s)

    def test_tasks_skill_triggers_on_rule_changes(self):
        s = self.read("tasks")
        description = s.split("---", 2)[1]
        for phrase in ("add a rule", "new rule", "from now on", "rules.md"):
            self.assertIn(phrase, description, phrase)
        self.assertIn("Load this skill before changing `rules.md`", s)

    def test_scope_note_rule_is_in_both_skills(self):
        for name in ("tasks", "schedule"):
            s = self.read(name)
            self.assertIn("## Scope notes", s, name)
            self.assertIn("never name, number or describe an item that was left out on purpose", s.lower(), name)
        self.assertIn("Tasks outside last week are left out.", self.read("tasks"))
        self.assertNotIn("Say what you left out only if asked", self.read("tasks"))
        self.assertIn("not in a chat-only list", s)
        self.assertIn("the reply holds only the team draft and the approval question", s)
        self.assertIn("the reply does not include the chat list", s)

    def test_last_week_and_unlogged_wording_are_in_the_skill(self):
        s = self.read("tasks")
        self.assertIn("work completed this week or any other week", s)
        self.assertIn('the first sentence must be "nothing is logged for <person> last week"', s)
        self.assertIn("Do not paraphrase that sentence", s)



class SkillHygiene(unittest.TestCase):
    """Skills must not ship eval-fixture names or concrete calendar dates."""

    # Distinctive names and titles from the Coordinator eval fixtures.
    # If a new fixture is added, cover it here or the coverage check fails.
    FIXTURE_TERMS = (
        "Woodstock", "Maple Street", "Oak Lane", "Paint samples", "tile samples",
        "Alvarez", "van insurance", "December newsletter", "October receipts",
        "dumpster", "Crew meeting", "Supplier call", "Dentist", "walk-through",
        "Bob", "Priya", "Carlos",
    )

    def skill_files(self):
        return [p for p in (REPO / "plugins").rglob("SKILL.md") if "skills" in p.parts]

    def test_skills_do_not_hardcode_dates_or_fixture_names(self):
        import json
        import re

        files = self.skill_files()
        self.assertTrue(files, "no skill files found")

        iso = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
        months = (
            r"January|February|March|April|May|June|July|August|September|"
            r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec"
        )
        day_month = re.compile(r"\b\d{1,2}\s+(?:" + months + r")\b", re.I)
        month_day = re.compile(r"\b(?:" + months + r")\s+\d{1,2}(?:st|nd|rd|th)?\b", re.I)

        problems = []
        for path in files:
            text = path.read_text()
            rel = path.relative_to(REPO)
            for m in iso.finditer(text):
                problems.append(f"{rel}: concrete ISO date {m.group()!r}")
            for m in day_month.finditer(text):
                problems.append(f"{rel}: day plus month {m.group()!r}")
            for m in month_day.finditer(text):
                problems.append(f"{rel}: month plus day {m.group()!r}")
            for term in self.FIXTURE_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", text, re.I):
                    problems.append(f"{rel}: fixture name {term!r}")

        tasks_md = (EVALS / "fixtures" / "memory" / "coordinator" / "tasks.md").read_text()
        titles = re.findall(r"\] T-\d+ \| ([^|]+) \| assignee:", tasks_md)
        ids = re.findall(r"\bT-\d+\b", tasks_md)
        people_md = (EVALS / "fixtures" / "memory" / "coordinator" / "people.md").read_text()
        people = [
            n.strip()
            for n in re.findall(r"^\\| ([^|]+) \\|", people_md, re.M)
            if n.strip() and n.strip().lower() != "name"
        ]
        calendar = json.loads((EVALS / "fixtures" / "calendar.json").read_text())
        events = [e["title"] for e in calendar["events"]]
        for c in load_module().CASES["cases"]:
            person = (c.get("query") or {}).get("person")
            if person:
                people.append(person)

        missing = []
        for label, items in (("title", titles), ("event", events), ("person", people)):
            for item in items:
                if not any(re.search(r"\b" + re.escape(term) + r"\b", item, re.I) for term in self.FIXTURE_TERMS):
                    missing.append(f"{label} {item!r} is not covered by FIXTURE_TERMS")
        for tid in sorted(set(ids)):
            for path in files:
                if re.search(r"\b" + re.escape(tid) + r"\b", path.read_text()):
                    problems.append(f"{path.relative_to(REPO)}: fixture task id {tid}")

        self.assertFalse(missing, "update FIXTURE_TERMS:\n" + "\n".join(missing))
        self.assertFalse(problems, "skill text leaks dates or fixture names:\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
