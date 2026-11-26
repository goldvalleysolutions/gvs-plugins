# Changelog

## 0.1.2

- Hard rule on Slack and Teams drafts: only work items for the named person or team, and personal or private entries (including their titles) stay out of the draft and the question around it.
- Tighter last-week scoping, and a required "nothing is logged for <person> last week" sentence when nothing is logged.
- Offline leak-answer fixtures cover naming a personal appointment in the omission note, last-week answers that include this week's work, and an unlogged-person paraphrase that never says nothing was logged.


## 0.1.1

- Tighten skills so Slack/Teams drafts leave out personal appointments, a needs-you list stays in scope, person and date-range answers do not invent or borrow work, a missing calendar never invents meetings, and no reply claims a schedule was set up.
- Same rules noted in the memory templates. Offline leak-answer fixtures cover the model-eval failures.

## 0.1.0

- Skills written: setup, tasks, schedule, self-test.
- Local notes templates (people, rules, tasks, tests).
- Evals: fixtures, deterministic checks (`evals/run_evals.py`), and a model-eval spec for `claude plugin eval`.
- Local reviews done. Human install test and model eval still outstanding.

## 0.0.1

- Scaffold.
