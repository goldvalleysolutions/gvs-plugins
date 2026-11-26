#!/bin/bash
set -e
mkdir -p memory/coordinator
cat > memory/coordinator/CLAUDE.md <<'EVAL_FIXTURE_EOF'
# Coordinator notes (hot cache)

- People I assign work to: Bob (estimates, site visits), Priya (office, customers). Everything else is me.
- Today snapshot: tasks due today and overdue (with assignee), then today's meetings.
- Completed means: marked done in tasks.md.
- "On <day>" means the next occurrence of that day on or after today, unless I say "last".
- Nothing is sent, posted or paid without an explicit yes in chat.
EVAL_FIXTURE_EOF
cat > memory/coordinator/people.md <<'EVAL_FIXTURE_EOF'
# People

| Name | Role or notes |
| --- | --- |
| Bob | Estimates, site visits |
| Priya | Office, customer calls, newsletter |
EVAL_FIXTURE_EOF
cat > memory/coordinator/rules.md <<'EVAL_FIXTURE_EOF'
# Rules

- Do not include personal appointments in the week view, or in Slack or Teams drafts. (Today, the needs-you list in chat, and single-day views still show them.)
- A task counts as completed when it is marked done in tasks.md.
- Weeks run Monday to Sunday.
EVAL_FIXTURE_EOF
cat > memory/coordinator/tasks.md <<'EVAL_FIXTURE_EOF'
# Tasks

## Open

- [ ] T-101 | Finish the Woodstock estimate | assignee: Bob | due: 2026-12-03 | logged: 2026-11-30
- [ ] T-102 | Order tile samples | assignee: me | due: 2026-12-02 | logged: 2026-11-27
- [ ] T-103 | Call the Alvarez family back | assignee: Priya | due: 2026-12-01 | logged: 2026-11-25
- [ ] T-104 | Renew the van insurance | assignee: me | due: 2026-12-04 | logged: 2026-11-20
- [ ] T-105 | Send the December newsletter | assignee: Priya | due: 2026-12-08 | logged: 2026-11-30
- [ ] T-106 | Send the Alvarez paint invoice | assignee: me | due: 2026-12-05 | logged: 2026-12-01

## Completed

- [x] T-090 | Quote for the Maple Street job | assignee: Bob | due: 2026-11-25 | logged: 2026-11-18 | completed: 2026-11-24 |
- [x] T-091 | Site visit, Oak Lane | assignee: Bob | due: 2026-11-26 | logged: 2026-11-19 | completed: 2026-11-26 |
- [x] T-092 | Reconcile October receipts | assignee: Priya | due: 2026-11-27 | logged: 2026-11-19 | completed: 2026-11-25 |
- [x] T-093 | Book the dumpster | assignee: me | due: 2026-12-01 | logged: 2026-11-28 | completed: 2026-12-01 |
- [x] T-094 | Paint samples for the Alvarez job | assignee: Bob | due: 2026-12-01 | logged: 2026-11-27 | completed: 2026-11-30 |
EVAL_FIXTURE_EOF
cat > memory/coordinator/tests.md <<'EVAL_FIXTURE_EOF'
# Self-tests

(Empty on purpose: the self-test starts from the sample questions in the plugin's memory template.)
EVAL_FIXTURE_EOF
