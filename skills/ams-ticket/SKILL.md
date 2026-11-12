---
name: ams-ticket
description: "Work AMS support tickets that a customer helpdesk mail creates on a monday.com ticket board: list the open unassigned tickets to pick one, read the item, investigate the root cause in the customer's production Salesforce org, re-classify it (type, area, environment), assign it, and draft the reply as formatted text on the clipboard ready to paste into monday. TRIGGER when: user pastes a link to the project's ticket board (monday.com/boards/<ticket_board>/pulses/<id>), says 'ticket', 'segnalazione', 'prendi in carico', 'analizza il ticket', 'rispondi al ticket', 'ticket non assegnati', 'quali ticket ci sono', 'elenca i ticket', 'unassigned tickets', '/ams-ticket'. DO NOT TRIGGER for project task boards or for DevOps Center work items (use dc-work-item)."
---

# AMS ticket — pick, investigate, classify, reply

Customer helpdesk mails land as items on a monday ticket board, usually with a wrong or generic
type / area. This skill turns one item into: a root cause backed by evidence from the org, a
corrected classification, an assignee, and a reply the user pastes into monday.

The skill is board-agnostic: every column title, label and group name comes from the project
configuration below. Never hard-code or guess them.

## 0. Parameters (read first)

Read the `## Ticket AMS` section of the project `CLAUDE.md`:

| Key | Meaning |
|---|---|
| `ticket_board` | monday board id |
| `client_filter` | `Column=Value` identifying this project's tickets on a shared board (optional) |
| `prod_org` | sf alias of the customer production org — **read-only** for this skill |
| `assignee_column` / `assignee` | people column for the owner; `me` (token owner) or a monday user id |
| `type_column` + labels | type column and which label means *defect*, *support*, *enhancement*, *integration* |
| `area_columns` | area column(s) to fill (generic area, client-specific area) |
| `environment_column` + label | environment column and the production label |
| `status_column` + label | status column and the "in progress" label |
| `priority_column` + order | priority column and its labels from highest to lowest |
| `in_progress_group` | group to move the item to when taking charge |
| `exclude_groups` | substrings of group titles to skip when listing (closed, archive) |
| `list_columns` | extra columns to show when listing (customer ticket #, company, reporter, …) |
| `protected_columns` | columns the skill never writes |
| `reply_language` | language of the reply to the customer |
| `token` | where `MONDAY_TOKEN` lives (default: `.env` in the main checkout root, gitignored) |

Missing section or key → ask the user and propose adding it. Never guess an org alias or a label.

## HARD RULES

- **The production org is read-only.** Queries, describes, Setup inspection only. Any change in prod
  (user change, sending a verification mail, config, data) needs an explicit go from the user for
  *that* action — taking charge of the ticket is not a go.
- **Nothing customer-facing is sent by the skill.** The reply goes to the clipboard; the user pastes
  it. No monday updates, mails or helpdesk replies unless explicitly asked.
- **Every claim in the reply is backed by evidence** gathered in step 2 (record, query, doc link).
  What could not be verified is reported to the user, never stated as fact to the customer.
  Never promise as done an action that has not been done or approved.
- Never write `protected_columns`; the priority is proposed, not changed.
- Before telling a customer something is not supported: retrieve the metadata, look for similar
  patterns in the repo, read the official docs.

## 1. No ticket given → list and let the user pick

```bash
python3 -I <skill_dir>/scripts/monday_ticket.py list <ticket_board> \
  --where "<client_filter>" --unassigned "<assignee_column>" \
  --exclude-groups "<exclude_groups>" --priority "<priority_column>=<order>" \
  --show "<list_columns>"
#   drop --unassigned to include assigned tickets; add --json for machine-readable output
```

Show the result as a compact table (id, priority, group, created, list columns, subject) with a
one-line first guess of the area for each; flag oddities (e.g. "in progress" with no assignee).
Ask which one to take (AskUserQuestion, top ones by priority; the rest via "Other").
Do not take charge of anything until the user picks.

## 2. Read the ticket

```bash
python3 -I <skill_dir>/scripts/monday_ticket.py get <item_id>
```

Output: columns by title, the helpdesk mail (usually the first update), later updates/replies,
attachments, and the board schema (titles, allowed labels, groups). Extract: reporter, affected
user(s), exact error text, record ids, time of the event (helpdesk times are usually local, monday
timestamps are UTC), company/site. If `client_filter` does not match → stop: wrong project.

## 3. Investigate in `prod_org`

Use the Salesforce skills for each operation (SOQL → `platform-soql-query`, logs →
`platform-apex-logs-debug`, docs → `sf-docs` / salesforce-docs MCP). Typical first checks:

- the **user**: `User` (profile, role, IsActive, CreatedDate, LastLoginDate, LastModifiedDate),
  `LoginHistory` (SSO vs password), permission set / group assignments when it smells like access;
- **what they were doing** around the event time: records with `LastModifiedById = <user>`,
  `EmailMessage` / `Task` created by the user, the records named in the error;
- **automation in play**: `FlowDefinitionView` (active flows on the object), flow source in the repo,
  validation rules, sharing;
- **same pattern on other users** — one user or everybody? This decides the structural-fix part of
  the reply;
- **official docs** for platform errors before concluding anything.

Write down: root cause, evidence (queries + results, doc links), workaround available now,
definitive fix, who must act (us / customer IT / Salesforce), other users exposed.

## 4. Classify and take charge

Pick values only from the labels returned by `get`, mapped through the configured meanings:

| Column | How to choose |
|---|---|
| type | *defect* = our config/code is wrong · *support* = works as designed; user, how-to or setup issue · *enhancement* = new requirement (→ change request) · *integration* = only if an external integration is really involved, not because the text names the external system |
| area(s) | functional area matching the root cause, not the wording of the mail |
| environment | where it happened (normally production) |
| status | the "in progress" label |
| assignee | `assignee` |
| group | `in_progress_group` |

Show before → after and apply only once the user asked to take charge / update monday:

```bash
python3 -I <skill_dir>/scripts/monday_ticket.py set <item_id> \
  "<type_column>=<label>" "<area column>=<label>" "<environment_column>=<label>" \
  "<status_column>=<in progress label>" "<assignee_column>=<assignee>"
python3 -I <skill_dir>/scripts/monday_ticket.py move <item_id> "<in_progress_group>"
python3 -I <skill_dir>/scripts/monday_ticket.py get <item_id>   # verify
```

`set` rejects labels that do not exist on the board and lists the allowed ones.

## 5. Draft the reply (clipboard, formatted)

Write the reply in `reply_language` as HTML in the session scratchpad (`<scratchpad>/reply-<id>.html`):

```bash
bash <skill_dir>/scripts/clip_html.sh <scratchpad>/reply-<id>.html
```

The user pastes it with ⌘V into the monday update (bold/italic/lists kept, plain-text fallback
included). "Put it back on the clipboard" → re-run `clip_html.sh`. macOS only (`osascript`, `textutil`).

Reply structure (short, for business users, little platform jargon):

1. Greeting to the reporter; one sentence with the cause in plain words.
2. **Immediate workaround** — step by step, with button/field names as the user sees them.
3. **Definitive fix** — what will be done and by whom; only state as done what is done.
4. Optional **note** — other users exposed, structural proposal needing customer action, what we need from them.
5. Closing + the user's signature.

Section headings in `reply_language`.

## 6. Report to the user

Root cause + evidence, monday changes applied (before → after), reply on the clipboard, and the
**open actions that need their go** (prod changes, mails to users, change requests, entries for the
project's open-points log if it keeps one).
