## Parallel sessions — per-ticket handoff and worktrees

Several sessions work in parallel on different tickets in the same repository.

- **No shared handoff file**: never use `.claude/HANDOFF.md`. The note to resume a ticket goes in
  `.claude/handoff/<ticket>.md` (e.g. `.claude/handoff/29885.md`), written by `/handoff` and read by `/riprendi`.
- **Read only the handoff of the ticket you are working on**; never open or edit the other tickets' files.
- **One worktree per branch**: every session on a different branch uses its own worktree (under the project's
  worktree root), never a branch checkout inside another session's worktree.
- Handoff notes stay out of git: every project must list `.claude/handoff/` (and `.claude/HANDOFF.md`) in its `.gitignore`.
