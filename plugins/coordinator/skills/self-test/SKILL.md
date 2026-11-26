---
name: self-test
description: Run Coordinator's self-test: sample questions answered from the user's notes, with the rule or note used, which the user marks right or wrong, and add or change tests. Use when the user says "run the Coordinator self-test", "test yourself", or "add a test".
---

# Self-test

Read `memory/coordinator/tests.md`, `tasks.md`, `rules.md` and `people.md`, and know today's date. If the notes do not exist, offer `/coordinator:setup` and stop.

## Run

1. If `tests.md` has no tests, start from the sample questions in this plugin's `memory-templates/memory/tests.md`.
2. For each test, answer it the way the `tasks` or `schedule` skill would, from the user's real notes. Show: the question, your answer, and the rule or note you used ("rules.md: no personal appointments in the week view", "tasks.md T-101").
3. After each answer, ask: "Right or wrong? Add a comment if you like." Wait for the user. Never mark a test right or wrong yourself. In a one-message conversation, show the first answer or two and stop at that question.
4. Save the user's mark and comment next to the test in `tests.md`, with today's date.
5. If a test is marked wrong, ask what the right answer is, offer to add or fix a rule in `rules.md`, and rerun that test.
6. Finish with a one-line score ("4 right, 1 wrong") and one suggested next step.

## Add a test

"Add a test: ..." adds the question to `tests.md` with the expected answer. Ask for the expected answer if the user did not give one, and read the test back before saving.

## Rules

- Tests live in the user's `memory/coordinator/tests.md`, never in the plugin folder.
- If you cannot write files in this session, show the updated test lines for the user to paste, and say nothing was saved.
