---
name: sf-save-memory
description: "Persist analysis results to docs/memory/ in the repo so they survive across conversations and can be committed. TRIGGER when: completing any analysis, investigation, or architectural review of components, classes, or features. Also triggers after sf-analyze-story and sf-implement-story phases."
---

# Salesforce Project Memory — Persist Analysis to Repo

## Role
Ensure every significant analysis is saved inside the project repository (committable, shareable) rather than only in Claude's ephemeral memory.

## When to trigger (AUTOMATIC)

Save a memory file after ANY of these:
1. **Component analysis** — reading and understanding LWC/Apex architecture
2. **Bug investigation** — root cause analysis, gap identification
3. **Story analysis** — output of sf-analyze-story
4. **Post-implementation** — summary of what was built, why, and gotchas
5. **Architecture review** — data flow, integration points, dependencies
6. **Client feedback** — requirements, decisions, change requests

## Where to save

- **Path**: `docs/memory/<topic>.md`
- **Index**: `docs/memory/README.md` — one-line entry per file
- Create the directory if it doesn't exist: `mkdir -p docs/memory`

## File format

```markdown
# <Topic> — <Short description>

**Data analisi**: YYYY-MM-DD
**Contesto**: <what triggered this analysis>

## Architettura / Stato attuale
<describe the current state of the code/feature>

## Problemi / Gap trovati
<what's wrong, what's missing, root cause>

## File coinvolti
| File | Ruolo | Modifica necessaria |
|------|-------|---------------------|

## Decisioni e richieste cliente
<what was decided, who asked for what>

## Fix / Piano di azione
<what needs to be done>
```

## Rules

1. **Always save in the repo** (`docs/memory/`), not only in `~/.claude/` — the repo version is the source of truth
2. **Also save in Claude memory** (`~/.claude/projects/.../memory/`) for cross-conversation context — but treat it as a cache, not the source
3. **Update, don't duplicate** — if a memory file for the same topic exists, update it rather than creating a new one
4. **Keep the README.md index** updated with one-line descriptions
5. **Include line numbers and file paths** — so future conversations can jump straight to the right place
6. **Include the "why"** — not just what was found, but why it matters and how it affects future work
7. **Date everything** — memory files become stale, dates help judge relevance
8. **Reference git commits** when relevant — e.g. "added in commit 947a354"

## After saving

- Inform the user: "Analisi salvata in `docs/memory/<file>.md` — committabile e disponibile per le prossime sessioni."
- If other memory files in the same area are now stale, update or remove them.
