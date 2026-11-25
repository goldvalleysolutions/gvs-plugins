---
name: schedule
description: Produce the "needs you" list (due today, overdue, and upcoming meetings), set it up as a scheduled run on Pro or higher, or offer a Slack or Teams post of the list. Use when the user says "needs you list", "every weekday at 8", "remind me each morning", or asks to post the list to Slack or Teams.
---

# "Needs you" list and schedule

> Scaffold only. The full instructions are written in the Coordinator build.

## Outline

1. The list: due today, overdue, and meetings coming up in the next day or two, from the notes and the calendar. Short. Names the assignee on each line.
2. By hand (all plans, including Free): show the list in chat whenever asked.
3. Scheduled (Pro or higher only): help the user create a scheduled task in their own Claude account that runs this skill at the time they choose (for example every weekday at 8 AM). Free accounts have no scheduled tasks. Say so plainly and keep the by-hand path.
4. Slack or Teams post (optional): only after the user approves the exact text and the exact channel in this chat. A scheduled run never posts without a previously approved standing instruction, and the first post of any new channel always asks.
5. Real push alerts are not part of v1 (they belong to the GVS bot). Say so if asked.

## Rules

- Nothing is posted or sent without an explicit yes in chat.
- Never claim a schedule exists until the user has confirmed it was created.
