# Coordinator evals

Everything here uses invented data (`fixtures/`). Two layers.

## 1. Offline, no model, no login (runs in CI)

```bash
python3 plugins/coordinator/evals/run_evals.py check
```

Confirms that the fixtures still give the hand-written golden answers in `cases.json` (today, week, a named day, completed, per person, needs-you), that every case is well formed, and that `model-eval/` matches `cases.json`. If you change a fixture or a case, run `python3 plugins/coordinator/evals/run_evals.py generate` to rewrite `model-eval/`.

To grade answers you collected by hand in any Claude chat, with no login on this machine:

```bash
python3 plugins/coordinator/evals/run_evals.py grade ANSWERS_DIR
```

Put each final reply in `ANSWERS_DIR/<case-id>.txt`. For cases that change notes, also copy the folder the run left behind to `ANSWERS_DIR/<case-id>/` (it holds `memory/coordinator/...`). Checks that need the run transcript are listed as NOT CHECKED.

## 2. Model eval (needs a Claude login; a maintainer runs it)

`model-eval/` is a `claude plugin eval` suite: one folder per case with `prompt.md`, `case.yaml`, a `setup.sh` that writes the fixture notes into the empty run folder, and `graders/*.md`. Calendar events are given as a `calendar.json` file because the run has no Google Calendar connector; the real connector is covered by the human test in the plugin README.

From `plugins/coordinator/`:

```bash
claude plugin eval . --scaffold --allow-tools Write Edit --no-publish --runs 3 --max-cost-usd 5
```

- This makes real model calls on the signed-in account and counts against that account's plan usage (or API bill). Pick the account on purpose. `--max-cost-usd` is a ceiling on the cost estimate; lower it if you like.
- `--scaffold` runs our own `setup.sh` files; use it only on this suite. `--no-publish` keeps reports local (they would otherwise be published to a claude.ai link). Results go to `evals/results/` (git-ignored).
- Add `--case <name>` to run one case, and `--runs 1 --ablation none` for a quick pass.
- Pass bar (approved): every case scores 1.0 in all 3 runs. The four gate cases (`approval-gate-slack`, `approval-gate-teams`, `schedule-free-plan`, `setup-first-run`) must pass at 100%. Fix the skill text and rerun the whole suite.
- Without a login the command loads the suite and stops with "Not logged in". That was checked.
