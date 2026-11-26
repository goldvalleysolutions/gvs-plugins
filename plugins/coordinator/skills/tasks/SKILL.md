---
name: tasks
description: Add, change, complete and look up tasks, assignees and due dates, and answer "what's on today", "what does my week look like", "what do I have on Tuesday", "what got completed this week", and "what did Sam do last week". Use for any question or request about to-dos, who is doing what, or what is due.
---

# Tasks and questions

Read `memory/coordinator/` first, every time: `tasks.md` (the task list), `people.md`, `rules.md`, `CLAUDE.md`. If the notes do not exist, offer `/coordinator:setup` and stop.

Know today's date before answering. Use the date the session gives you (the user's current date); if you do not have one, ask. Weeks run Monday to Sunday unless `rules.md` says otherwise. Every date range is relative to that current date: this week is the Monday-to-Sunday week that contains today; last week is the Monday to Sunday before the current week.

## Task file format

One line per task in `tasks.md`, under `## Open` or `## Completed`. Dates are always absolute (`YYYY-MM-DD`). `me` means the user.

```
- [ ] T-001 | Example: Call the supplier | assignee: Sam | due: YYYY-MM-DD | logged: YYYY-MM-DD
- [x] T-002 | Example: Send the weekly report | assignee: Sam | due: YYYY-MM-DD | logged: YYYY-MM-DD | completed: YYYY-MM-DD | note
```

New ids continue from the highest existing id (`T-014` after `T-013`, or `T-001` for an empty list). Keep the file's other lines exactly as they are.

## Calendar

Meetings come from the user's Google Calendar connector when it is connected. Otherwise use a calendar file the user names or events they paste. If there is none of these, say plainly that the calendar is not connected and answer from open tasks only (due today and overdue). Do not mention meetings, event names, or times in that case. Never invent meetings. An event whose calendar is "Personal" is a personal appointment.

## Answering

Always say which dates you used (for example "Wednesday <date>"). Name the assignee on every task. Keep it short: one line per item.

- **"What's on today?" / today snapshot.** Open tasks due today, then open tasks overdue (due before today, marked overdue), then today's meetings with times. Show personal appointments here unless `rules.md` says otherwise for today.
- **"What does my week look like?"** From today through Sunday: open tasks by due date, overdue tasks flagged as overdue, and meetings by day. Apply `rules.md` (for example leave out personal appointments if told to). Say what you left out only if asked.
- **"What do I have on Tuesday?" / "on <day>".** Resolve a bare weekday name to the next such day on or after today, and say the date you resolved to ("Tuesday <date>"). "Last Tuesday" means the one before today. List that day's open tasks and meetings.
- **"What got completed this week so far?"** Tasks marked completed from Monday of this week through today, any assignee, with who did them.
- **"What did <person> accomplish last week?"** Only that person, and only tasks assigned to them with a `completed` date in last week (the Monday to Sunday before the current week). Say those two dates. Do not include other people, open tasks, meetings, or work completed this week or any other week, even if it is assigned to them. If none are logged, the first sentence must be "nothing is logged for <person> last week", then that Coordinator only knows what the user (or Inbox) has logged, then stop. Do not paraphrase that sentence, invent work, or mention someone else's tasks to fill the gap. If the name is not in `people.md` and has no tasks, still lead with that sentence, then say you have no record of that person.
- Other questions about the list ("what's overdue?", "what's Sam got open?"): answer the same way, from the notes only.

## Changing the list

- **Add.** "Add a task: Sam to send the invoice, due Friday." Convert relative dates ("Friday", "next Tuesday", "tomorrow") to an absolute date, add the line to `## Open`, then read back the id, title, assignee and date. If the assignee is not in `people.md`, add them there and say so. If no due date was given, save `due: none` and say so. If a date is ambiguous, ask.
- **Complete.** "Mark the weekly report done." Find the matching open task. If exactly one matches, move it to `## Completed` as `- [x]` with `completed: <today>` (or the date the user gives). If more than one task could match, list them with ids and ask which; change nothing until the user answers.
- **Change.** Reassign, retitle or move a due date on request, and read the change back.
- **Rules.** "Add a rule: ..." appends one plain line to `rules.md` and reads it back. Change `CLAUDE.md` only if the rule belongs in the short summary.
- If you cannot write files in this session, show the changed lines for the user to paste into `tasks.md` and say that nothing was saved.

## Never

- Never send, post or message anyone from this skill. Slack and Teams posts belong to the `schedule` skill and only after a yes.
- Never claim to know work that was not logged.
