# Coordinator

Basic task and calendar coordination for a small office, on personal Claude (Free or Pro). It keeps a task list in your own notes: to-dos, who they are assigned to (including other staff), due dates, and meetings from your Google Calendar. Then you just ask.

**Status: 0.1.0.** Ready to try, and free under the [MIT License](../../LICENSE). A full install test by a person, and a model eval, are still outstanding.

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

The Claude desktop app and claude.ai **Add marketplace** field accepts a GitHub `owner/repo` or a full Git URL only, for example `goldvalleysolutions/gvs-plugins` or `https://github.com/goldvalleysolutions/gvs-plugins`. Those use the default branch (`main`). A branch suffix such as `#coordinator-pilot` is rejected there ("Marketplace source format is invalid"). See [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) and the [Plugins overview](https://claude.com/docs/plugins/overview).

Until Coordinator is on `main`, install it in the desktop app by uploading the zip below, or add this branch from the Claude Code CLI.

### 1. On claude.ai or the Claude desktop app: upload the zip (the path that works today)

From a checkout of the `coordinator-pilot` branch, at the repository root:

```bash
mkdir -p dist-pilot
rm -f dist-pilot/coordinator-0.1.0.zip
( cd plugins && zip -r ../dist-pilot/coordinator-0.1.0.zip coordinator \
    -x 'coordinator/evals/*' \
    -x 'coordinator/evals/*/*' \
    -x 'coordinator/evals/*/*/*' \
    -x 'coordinator/evals/*/*/*/*' \
    -x 'coordinator/evals/*/*/*/*/*' \
    -x '*__pycache__*' )
```

The archive can hold the `coordinator` folder as its single top-level entry (this command does that) or the folder's contents directly. Either works as long as there is one `.claude-plugin/plugin.json` at the zip root or one folder down ([plugin structure](https://claude.com/docs/plugins/build)). Then:

1. Open **Customize > Plugins**.
2. Choose **Add > Upload plugin**.
3. Select `dist-pilot/coordinator-0.1.0.zip`.
4. Confirm Coordinator is listed with four skills: setup, tasks, schedule, and self-test.

A plugin package may be up to 200 MB and 5,000 files ([platform limits](https://claude.com/docs/plugins/platform-support)); this zip is far under both. Coordinator is skills-only; skills load in chat, Cowork, and Claude Code.

Once Coordinator is on `main`, you can instead choose **Add > Add marketplace**, enter `goldvalleysolutions/gvs-plugins`, and add Coordinator from the list.

### 2. Claude Code CLI (fallback, works on this branch today)

The `#ref` suffix is documented for Claude Code ([Install plugins](https://code.claude.com/docs/en/plugins/install)), not for the desktop Add marketplace field:

```bash
claude plugin marketplace add goldvalleysolutions/gvs-plugins#coordinator-pilot
claude plugin install coordinator@goldvalleysolutions
```

The same `#coordinator-pilot` suffix also works on the full Git URL: `https://github.com/goldvalleysolutions/gvs-plugins.git#coordinator-pilot`. Once `main` has this code, drop the `#coordinator-pilot` and use `goldvalleysolutions/gvs-plugins`.

Questions? Use the contact form on our website: [goldvalleysolutions.com/#contact](https://goldvalleysolutions.com/#contact).

## Install-and-use test (for a person to run)

About 20 minutes. Use a scratch folder and invented tasks. Tick each box; write down anything surprising.

1. [ ] Install Coordinator with the zip upload in Customize > Plugins (recommended), or with the Claude Code CLI command above. Expected: Coordinator is listed with four skills (setup, tasks, schedule, self-test).
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

Pass: every box ticked, nothing sent anywhere, and no file written before you said yes. Send the results with the contact form at [goldvalleysolutions.com/#contact](https://goldvalleysolutions.com/#contact).

## Testing the plugin itself

See `evals/README.md`. `python3 plugins/coordinator/evals/run_evals.py check` runs the offline checks from the repository root (no login).

**Pass bar (approved):** every case scores 1.0 in all 3 runs. The four gate cases (`approval-gate-slack`, `approval-gate-teams`, `schedule-free-plan`, `setup-first-run`) must pass at 100%. Fix the skill text and rerun the whole suite if a case fails.

The model eval (`claude plugin eval`) uses the signed-in Claude account's plan usage. It is capped with `--max-cost-usd 5` and should not be run until a maintainer says yes.
