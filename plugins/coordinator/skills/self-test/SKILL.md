---
name: self-test
description: Run Coordinator's self-test: sample questions with the expected answer and the rule used, which the user marks right or wrong, and add or change tests. Use when the user says "run the Coordinator self-test", "test yourself", or "add a test".
---

# Self-test

> Scaffold only. The full instructions are written in the Coordinator build.

## Outline

1. Read `memory/coordinator/tests.md`. If it is empty, start from the sample questions shipped in `memory-templates/memory/tests.md`.
2. For each test, answer it from the user's real notes, show the answer and the rule from `rules.md` or the note that was used, and ask the user to mark it right or wrong with an optional comment.
3. Save each mark and comment back to `tests.md`. On a wrong mark, offer to update `rules.md` and re-run that test.
4. "Add a test: ..." appends a new test with its expected answer after the user confirms.
5. End with a one-line score and the next suggested step.

## Rules

- Tests are saved in the user's notes, never in the plugin folder.
- Never mark a test right on the user's behalf.
