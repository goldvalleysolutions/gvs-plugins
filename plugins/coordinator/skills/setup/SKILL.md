---
name: setup
description: Set up Coordinator for this office. Use when the user says "set me up", "set up Coordinator", "get started", or has just installed the plugin and asks what to do first.
---

# Coordinator setup

Coordinator keeps a small task list and answers schedule questions. Setup creates its notes, learns who the user assigns work to, and ends with a finished first task.

## Notes folder

Coordinator keeps everything it learns as plain files in the user's working folder, under `memory/coordinator/`: `CLAUDE.md` (short hot cache), `people.md`, `rules.md`, `tasks.md`, `tests.md`. Starter copies are in this plugin's `memory-templates/` folder. The plugin's own files are read-only: never write inside them, and never read another plugin's notes.

If this session cannot read or write files in a working folder (for example a plain chat with no folder), say so in one sentence. Keep the notes as text in the chat, show the user the finished file contents after each change, and suggest Cowork or Claude Code for saving them. Do not pretend a file was saved.

## Steps

1. **Say what this is, in two or three sentences.** Coordinator keeps tasks, who they are assigned to (including other staff) and due dates; it reads meetings from Google Calendar; it answers "today", "this week", "on Tuesday", "completed" and "what did Bob do". It knows about other people's work only from what the user (or Inbox) logs. It never sends, posts or pays without a yes.
2. **Ask before writing.** If `memory/coordinator/` does not exist, ask: "May I create a `memory/coordinator/` folder here for my notes?" Do not create anything until the user says yes. In a one-message conversation, stop after asking.
3. **Create the notes** from `memory-templates/` once the user agrees. Remove the placeholder example lines.
4. **Calendar.** Ask whether Google Calendar is connected. If not, tell them it connects from Customize > Connectors. Offer to carry on without it: tasks only, or a calendar export or pasted events. Never invent meetings.
5. **People.** Ask who they assign work to (for example Bob). Save names and a few words on each in `people.md`.
6. **Standing preferences.** Ask what a today snapshot should show, whether personal appointments belong in the week view, and anything else they want always done. Save each as one line in `rules.md`. Keep the defaults in `CLAUDE.md` in step.
7. **First pass.** Ask for two or three real tasks, one assigned to someone else, with due dates. Add them with the rules in the `tasks` skill, then answer "what does my week look like?" and let the user correct it. Update the notes when they do.
8. **Offer next steps.** The self-test (`/coordinator:self-test`). A "needs you" list by hand now, and on Pro or higher a scheduled one (`/coordinator:schedule`).
9. **Welcome note.** Finish with a short list of the first jobs and the phrases that run them, for example: "What's on today?", "What does my week look like?", "Add a task: Bob to ... due Thursday.", "What did Bob accomplish last week?", "Give me my needs-you list.", "Run the Coordinator self-test."

## Rules

- Replies appear in chat first. Nothing leaves the chat without an explicit yes.
- Short, plain language for a small-office reader.
- If setup was already done (notes exist), say so and offer to review the people and rules instead of starting over.
