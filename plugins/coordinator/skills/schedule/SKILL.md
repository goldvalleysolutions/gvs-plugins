---
name: schedule
description: Produce the "needs you" list (due today, overdue, and upcoming meetings), set it up as a scheduled run on Pro or higher, or draft a Slack or Teams post of the list for approval. Use when the user says "needs you list", "every weekday at 8", "remind me each morning", or asks to post the list to Slack or Teams.
---

# "Needs you" list, schedule, and posts

Read `memory/coordinator/` first (`tasks.md`, `people.md`, `rules.md`) and know today's date. Calendar rules are the same as in the `tasks` skill: use the connected Google Calendar, or a file or pasted events, or say the calendar is not connected. Never invent meetings.

## The list (any plan, by hand)

Build the "needs you" list in this order, one line per item, with the assignee on every task. Include only these three sections — not later-week tasks, not completed work, not any other meetings:

1. **Overdue:** open tasks due before today, oldest first.
2. **Due today:** open tasks due today.
3. **Coming up:** meetings today and tomorrow, with times.

If a section is empty, say "none". Personal appointments are shown in this chat list unless `rules.md` says otherwise, except when the user asked you to post the list to Slack or Teams: then the reply carries no chat list at all (see the hard rule below). Say which dates you used. The user can ask for the list by hand at any time on any plan, including Free.

## Scheduling it (Pro or higher)

Scheduled tasks need a Pro, Max, Ultra, Team or Enterprise plan. A Free account has no scheduled tasks.

1. If the user asks for a recurring run ("every weekday at 8 AM"), ask which plan they are on if you do not know.
2. You cannot create the scheduled task for them on any plan. Give them the exact prompt (for example "Run the Coordinator needs-you list and show it.") and the exact schedule, and tell them where to paste it in their own Claude account (Cowork scheduled tasks, or Claude Code scheduled tasks). Do not say that a schedule exists, was set up, was created, or has been scheduled, until they confirm they pasted it. Never write "I've set it up" or "it's been scheduled."
3. On Free: also say plainly that Free does not have scheduled tasks, that they can ask for the list by hand, and that Pro or higher is needed for a schedule.
4. On Pro or higher: still only give the prompt and schedule to paste; wait until they confirm it exists before saying it does.
5. A scheduled run only builds the list and shows it as its result. It never posts anywhere.

## Slack or Teams post (only after a yes)

A post sends something to other people, so it needs explicit approval every time.

Hard rule, for the whole reply, not just the draft: a team post only carries work items for the named person or team the user asked to post about. Personal or private entries are always left out, including their titles (calendar "Personal", for example a private appointment). That title must not appear anywhere in your reply when the user asks you to post to Slack or Teams: not in the draft, not in a chat-only list, not in a summary or note, and not in the question around the draft. Do not show the user's own needs-you list first and then a "cleaned" draft; the reply holds only the team draft and the approval question. Rebuild the draft from work items only, never by copying the chat list. You may say that personal or private items were left out, but do not name those appointments. If the user wants to see their own full list, they can ask for it in a separate message.

1. When the user asks to post the list, **draft the post and stop.** Show the exact text and the exact channel or chat ("#office on Slack"). Ask: "Post this to #office? Say yes to send."
2. The draft is not a copy of the chat list, and the reply does not include the chat list. Include only overdue tasks, tasks due today, and work meetings today and tomorrow. Leave out personal appointments even if they appear on the user's own needs-you list, and leave out anything you are unsure the whole office should see. If you mention the omission, write only that personal items were left out — never the appointment title, in the draft or anywhere else in the reply.
3. Do not call any Slack, Teams or other send tool in the same turn as the draft. Send only after the user replies with a clear yes to that exact text and channel. A change to the text or channel needs a new yes.
4. When the user says yes: if Slack or Teams is not connected, say so, send nothing, and give them the text to copy.
5. A yes covers one post. The next post asks again. A scheduled run never posts.

## Scope notes

The same rule as in the `tasks` skill applies to every reply: never name, number or describe an item that was left out on purpose because it is out of scope or private (no title, id, project or client, date, assignee, or reason). A general line such as "Personal items were left out." is allowed.

## Not in v1

Real push alerts (phone notifications) are not part of this plugin. Say so if asked.
