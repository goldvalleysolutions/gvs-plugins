---
name: setup
description: Set up Coordinator for this office. Use when the user says "set me up", "set up Coordinator", "get started", or has just installed the plugin and asks what to do first.
---

# Coordinator setup

> Scaffold only. The full instructions are written in the Coordinator build. This outline fixes what the skill must do.

## Goal

End the first conversation with a finished first task, so the user never wonders "now what".

## Outline

1. Say in two sentences what Coordinator does and does not do (tasks, assignees, due dates, Google Calendar meetings; it knows about other people's work only from what the user logs; nothing is sent, posted or paid without a yes).
2. Create the notes folder `memory/coordinator/` in the user's working folder from this plugin's `memory-templates/`. Ask before writing. Never write inside the plugin's own folder.
3. Ask whether Google Calendar is connected. If not, explain how to connect it from the Connectors page, and offer to carry on without it (tasks only, or pasted calendar text).
4. Ask who the user assigns work to. Save names to `people.md`.
5. Ask for standing preferences (how a today snapshot should look, what counts as completed, whether personal appointments are shown). Save to `rules.md`.
6. First pass: add two or three real tasks, one assigned to someone else, then answer "what does my week look like?". Let the user correct it and update the notes.
7. Offer the self-test (`/coordinator:self-test`) and, on Pro or higher, a scheduled "needs you" list (`/coordinator:schedule`).
8. Finish with a short welcome note listing the first jobs and the phrases that run them.

## Rules

- Replies appear in chat first. Nothing leaves the chat without an explicit yes.
- Plain language, short answers.
