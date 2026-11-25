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
    def test_setup_scripts_build_the_workspace(self):
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


if __name__ == "__main__":
    unittest.main()
