# Coordinator

Basic task and calendar coordination for a small office, on personal Claude (Free or Pro). It keeps a task list in your own notes: to-dos, who they are assigned to (including other staff), due dates, and meetings from your Google Calendar. Then you just ask.

**Status: 0.1.0, built, waiting for review.** Not yet reviewed by the developer and prospect panels.

## What you can ask

| You type | What comes back |
| --- | --- |
| "Set me up." | Short setup: creates your notes (after you say yes), learns who you assign work to, ends with a finished first task. |
| "What's on today?" | Today's tasks (with who they are assigned to), overdue tasks, and today's meetings. |
| "What does my week look like?" / "What do I have on Tuesday?" | The rest of the week, or that day (a bare weekday means the next one), with the date it used. |
| "What got completed this week so far?" | Tasks marked done since Monday, any assignee. |
| "What did Bob accomplish last week?" | Bob's tasks logged as completed last week. If none were logged, it says so. |
| "Add a task: Bob to finish the Woodstock estimate, due Thursday." | Saved with an absolute due date, read back to you. |
| "Mark the tile samples done." | Marks it done. If two tasks match, it asks which. |
| "Add a rule: don't show personal appointments in the week view." | Saved to your notes. This is how you teach it: by chat. |
| "Give me my needs-you list." | Overdue, due today, and meetings today and tomorrow. |
| "Post my needs-you list to #office on Slack." | A draft and the question "Post this?". It sends only after you say yes. |
| "Run the Coordinator self-test." | Sample questions answered from your notes, which you mark right or wrong. |

## What it will not do

- It knows about other people's work only from what you (or Inbox) log. Bob updating his own tasks, and a list the whole office shares, are not part of this plugin.
- It never sends, posts or pays without your yes in chat. A Slack or Teams post is drafted first and sent only after you approve that exact text and channel. A scheduled run never posts.
- No phone alerts. Reminders appear in chat, or in a list a scheduled run saves.
- It does not read other plugins' notes.

## Plans

Works on Claude Free. Free's limits: one custom connector and no scheduled tasks. Coordinator keeps its notes in local files and needs no custom connector. A scheduled "needs you" list needs Pro or higher; on Free you ask for the list by hand.

## Where your notes live

Coordinator writes plain files in your working folder under `memory/coordinator/` (`tasks.md`, `people.md`, `rules.md`, `tests.md`, `CLAUDE.md`). You can open and edit them. The plugin's own files are read-only. Saving files needs a session that has a working folder (Cowork project or Claude Code). In a plain chat with no folder, Coordinator says so and shows you the file text to save yourself.

## Install

```bash
claude plugin marketplace add goldvalleysolutions/gvs-plugins
claude plugin install coordinator@goldvalleysolutions
```

On claude.ai or the desktop app: Customize > Plugins > Add > Add marketplace > `goldvalleysolutions/gvs-plugins`, then add Coordinator. Or upload a zip: from the repository root run `cd plugins && zip -r coordinator.zip coordinator -x "coordinator/evals/*"`, then Customize > Plugins > Add > Upload plugin.

## Install-and-use test (for a person to run)

About 20 minutes. Use a scratch folder and invented tasks. Tick each box; write down anything surprising.

1. [ ] Add the marketplace and install Coordinator (above). Expected: Coordinator is listed with four skills (setup, tasks, schedule, self-test).
2. [ ] Open a new empty folder in Claude Code or a Cowork project. Type "Set me up."
   Expected: a short explanation, then it asks before creating a `memory/coordinator/` folder, and asks about Google Calendar and who you assign work to.
3. [ ] Say yes. Name one person (for example Bob). Skip the calendar, or connect Google Calendar from Customize > Connectors if you want to test it.
   Expected: notes created; it never invents meetings.
4. [ ] Type "Add a task: Bob to finish the Woodstock estimate, due Thursday."
   Expected: saved as T-001, assigned to Bob, with the real date of the coming Thursday read back. Open `memory/coordinator/tasks.md` and check the line.
5. [ ] Add one task for yourself due today and one due last week (say the dates). Type "What's on today?"
   Expected: today's task, the overdue one marked overdue, and today's meetings if the calendar is connected (or a plain note that it is not).
6. [ ] Type "What does my week look like?" then "What do I have on Tuesday?"
   Expected: both name the dates they used.
7. [ ] Type "Mark the Woodstock estimate done." then "What got completed this week so far?" then "What did Bob accomplish last week?"
   Expected: the first two show the estimate; the last says nothing is logged for last week (it does not guess).
8. [ ] Type "Add a rule: put Bob's tasks first in every list." Open `rules.md`.
   Expected: the rule is there in plain words.
9. [ ] Type "Give me my needs-you list."
   Expected: overdue, due today, then meetings today and tomorrow.
10. [ ] Type "Post my needs-you list to #office on Slack."
    Expected: a draft with the channel and the question "Post this?". Nothing is sent. Answer "no" and check that nothing was posted.
11. [ ] Type "Run the Coordinator self-test." Mark the first answer right or wrong.
    Expected: it shows the answer and the rule or note it used, waits for your mark, and saves the mark in `tests.md`.
12. [ ] Type "Every weekday at 8 AM, give me the needs-you list."
    - On Free: expected a plain "Free doesn't have scheduled tasks" with the by-hand option and "Pro or higher". It must not say a schedule exists.
    - On Pro or higher: it gives you the exact prompt and schedule to paste into a scheduled task. After you create it, confirm it ran once and produced the list.

Pass: every box ticked, nothing sent anywhere, and no file written before you said yes. Send the results to the maintainers.

## Testing the plugin itself

See `evals/README.md`. `python3 plugins/coordinator/evals/run_evals.py check` runs the offline checks from the repository root.
