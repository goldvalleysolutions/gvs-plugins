---
name: tasks
description: Add, change, complete and look up tasks, assignees and due dates, and answer "what's on today", "what does my week look like", "what do I have on Tuesday", "what got completed this week", and "what did Bob do last week". Use for any question or request about to-dos, who is doing what, or what is due.
---

# Tasks and questions

> Scaffold only. The full instructions are written in the Coordinator build.

## Reads and writes

- Tasks live in `memory/coordinator/tasks.md`; people in `people.md`; the user's standing preferences in `rules.md`. Read the notes first, every time.
- Calendar meetings come from the user's connected Google Calendar. If it is not connected, say so and answer from tasks only.

## Request types this skill must handle (each has an eval case)

| User says | Result |
| --- | --- |
| "Add a task: Bob to finish the Woodstock estimate, due Thursday." | Saves the task with assignee and an absolute due date; repeats the date back. |
| "What's on today?" | Today's tasks (with assignee) and today's meetings. |
| "What does my week look like?" | The week's tasks and meetings. |
| "What do I have on Tuesday?" | That day's tasks and meetings. |
| "What got completed this week so far?" | Tasks marked completed this week, any assignee. |
| "What did Bob accomplish last week?" | Bob's tasks logged as completed last week. If nothing is logged, say so; never guess. |
| "Mark the estimate done." | Marks it completed with today's date. Asks if more than one task matches. |
| "Add a rule: don't show personal appointments." | Updates `rules.md` and confirms. |

## Rules

- Convert "Thursday", "next Friday" and similar to an absolute date before saving, and say the date.
- Honest limit: Coordinator knows only what the user (or Inbox) logged. Say so when an answer depends on work that was never logged.
- Never send, post or message anyone from this skill.
