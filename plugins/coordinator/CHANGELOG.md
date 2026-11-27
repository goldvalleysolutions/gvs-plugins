# Changelog

## 0.1.6

- `tasks` skill trigger is stronger for rule changes: the description now names "add a rule", "new rule", "from now on", "always" and "never", and the body says to load the skill before changing `rules.md`. In the 0.1.5 model eval the `add-rule` case saved the rule correctly but skipped the skill on 2 of 3 runs.
- No grader and no safety gate changed.

## 0.1.5

- New "Scope notes" rule in the `tasks` and `schedule` skills: never name, number or describe an item that was left out on purpose because it is out of scope or private, even when explaining the omission. A general line such as "Tasks outside last week are left out." is allowed. The week view no longer lists what it left out.
- Offline leak fixture for a last-week answer whose omission note names a task and its project, with a unit test that requires `must-not-include` to fail it. No grader was changed.

## 0.1.4

- Hard rule on Slack and Teams drafts now covers the whole reply: when the user asks to post, a private or personal item's title appears nowhere (not in the draft, a chat-only list, a summary, or the question around the draft). The reply holds only the team draft and the approval question. Saying that personal items were left out is fine; naming them is not.
- Offline leak fixture for a reply that shows a chat list naming a personal appointment above a clean Slack draft, with a unit test that requires `leaves-out-personal` to fail it. No grader was changed.

## 0.1.3

- Example task lines and weekday examples in the skills use placeholders, not eval-fixture names or concrete dates. Every date range is relative to the user's current date.
- Unit test fails if a skill ships a concrete calendar date or a fixture-only name.


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
