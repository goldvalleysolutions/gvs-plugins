# Coordinator eval plan

Status: written and runnable offline; the model run is waiting for a maintainer with a Claude login. See `README.md` in this folder for commands.

## What is tested

Given the notes and a calendar, Claude following the Coordinator skills gives the right answer, saves the right thing, and never sends or posts without a yes.

## Fixtures

`fixtures/` holds filled-in notes (people, rules, tasks) and a sample calendar, all invented. Eval "today" is Wednesday 2026-12-02. The data gives each query type a distinct answer: an overdue task, a personal appointment the week-view rule hides, a "Tuesday" that means next Tuesday, work done last week by three people, and a person (Carlos) with nothing logged.

## Cases (17, in `cases.json`)

Queries: today-snapshot, week-view, day-tuesday, completed-this-week, bob-last-week, unlogged-person, needs-you-list. Changes: add-task-relative-date, complete-task, complete-ambiguous, add-rule. Gates and limits: approval-gate-slack, approval-gate-teams, schedule-free-plan, calendar-not-connected. Flows: setup-first-run, self-test-run.

## Checks

- Deterministic: golden ids hand-written in `cases.json`, checked against the fixtures by a small reference implementation (`run_evals.py check`). Model answers are graded with regexes over the reply and over the saved notes (`tasks.md`, `rules.md`), plus "no Slack or Teams send tool was called" and "nothing written before a yes".
- No LLM judges. Every grader is a regex, file or tool check, so scores do not drift with a judge model.
- Every case also records whether the right skill ran (indicator only).

## Run paths

1. Offline, in CI: `run_evals.py check` (and the unit tests).
2. Offline grading of answers collected by hand: `run_evals.py grade`.
3. Model eval by a maintainer: `claude plugin eval . --scaffold --allow-tools Write Edit --no-publish --runs 3`. Needs a login and uses that account's plan usage.
4. Human install-and-use test: steps in the plugin README.

## Pass bar (proposed)

Each case 3 runs at 1.0. The gate cases pass 100%. A failure is fixed in the skill text and the whole suite is rerun.

## Known limits

- Calendar events come as a file, not through a Google Calendar connector. The connector path is covered only by the human test.
- Single-turn evals: setup and self-test stop at their first question. The back-and-forth is covered by the human test.
- Scheduled runs cannot be evaluated here; the by-hand list is.
