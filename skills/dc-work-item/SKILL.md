---
name: dc-work-item
description: "Full DevOps Center NG work item cycle: start (create WI → In Progress → DC creates the branch → worktree on that branch), commit (MCP commit → push → PR → wait for DC registry), promote (pre-checks → promote → verify what really deployed). TRIGGER when: user says 'nuovo WI', 'stacca un WI', 'apri un work item', 'start work item', 'committa il WI', 'crea la PR', 'promuovi', 'promote', or any metadata feature is about to start in a DevOps Center project. DO NOT TRIGGER for docs/memory-only changes (they go straight to the integration branch, no WI)."
---

# DevOps Center NG — Work Item cycle

DevOps Center (DC) owns branches, pipeline stages and the deploy package. This skill never decides
those things itself: it drives DC through the MCP tools and checks the result.

## Relation to the official Salesforce skills (plugin `dx-devops@salesforce`)

This skill is the **orchestration + guardrails layer**; the single operations belong to the official skills:

| Need | Official skill / tool |
|---|---|
| create / list / update status of a WI, create the PR | `dx-devops-work-item-manage` (`sf devops work-item …`, `sf devops review create`) or the `*_devops_center_*` MCP tools |
| pipelines, stages | `dx-devops-pipeline-manage` |
| merge conflicts on the WI branch | `dx-devops-conflict-resolve` |
| stage test suites / failures | `dx-devops-test-suite-run`, `dx-devops-test-failures-analyze` |
| promote (validate → prepare → combine → promote → complete) | `dx-devops-promote` |
| polling of the async promote / deploy request | `dx-devops-request-status` |

Prerequisites (one-off per machine):
- CLI plugin `@salesforce/plugin-devops-center` **≥ 2.3.7** (`sf plugins install @salesforce/plugin-devops-center@latest`):
  older versions lack `sf devops promotion validate|complete`, `work-item prepare|combine`, `request status`.
- `dx-devops-promote` and `dx-devops-request-status` are **not** in the `dx-devops` Claude plugin (0.3.0) —
  they live in `forcedotcom/sf-skills/skills/`. Install:
  `npx skills add forcedotcom/sf-skills -g -a claude-code -s dx-devops-promote dx-devops-request-status -y`
  (update later with `npx skills update -g`).

Where they disagree, **this skill wins** for DC NG projects using it:
- official Phase "commit" = plain `git add/commit/push` → here commits go through
  `commit_devops_center_work_item` (the DC registry is what gets deployed);
- official skills do not wait for the DC-created branch, do not use worktrees, do not check the
  `WorkItemComponent` registry nor what the promote really deployed → phases A5–A7, B6, C below.

## 0. Parameters (read first)

Read the `## DevOps Center` section of the project `CLAUDE.md`:

| Key | Meaning |
|---|---|
| `dc_org` | alias of the org hosting DevOps Center (all `*_devops_center_*` MCP calls use it) |
| `dc_project` | DC project name + Id where new WIs are created |
| `worktree_root` | folder where WI worktrees live (`<worktree_root>/WI-00XXXX`) |
| `dev_org` | default org for retrieve/edit inside the worktree (per-WI override allowed) |
| `github_repo` | `owner/repo`, for `gh` checks |
| `promote_limit` | optional: furthest stage this kind of WI may be promoted to without explicit user go |

Missing section → ask the user for the values and propose adding the section. Never guess an alias.

## HARD RULES (all phases)

- **Never create, push or pick the WI branch yourself.** No `git worktree add -b`, no `git push -u`
  of a new branch, no choosing a base branch. DC creates `WI-00XXXX` from the right base when the WI
  goes **In Progress**. If you already created one by mistake: stop, tell the user, propose deleting it.
- **Never `git add/commit` manually** for WI content → `commit_devops_center_work_item` only.
- **Never merge the PR yourself** (`gh pr merge`) — DC merges it during promote. The hybrid path
  (manual merge + direct deploy) is a fallback only with explicit user agreement.
- **Never `sf project deploy start` / `deploy_metadata`** toward a pipeline stage org as a shortcut.
- **Never delete flow files in a WI** (DC generates destructive changes that cannot succeed).
- **Never promote past `promote_limit`** or to a stage the user did not name in this conversation.
- The user's commit/approval preferences in memory win over this skill (e.g. "the user runs commits").

---

## Phase A — START

1. **Subject**: ask the user (mandatory for the MCP tool). Propose one in English.
2. `create_devops_center_work_item(usernameOrAlias=dc_org, projectId=dc_project.Id, subject, description)`.
3. Get the name: `SELECT Name, Status FROM WorkItem WHERE Subject = '<subject>' ORDER BY CreatedDate DESC LIMIT 1` on `dc_org`.
4. `sf devops work-item update --work-item-name <WI> --status "In Progress" -o <dc_org> --json`
   (or MCP `update_devops_center_work_item_status`) → this is what makes DC create the branch
   and register it as the WI source branch (without it: PR fails with `422 head wasn't supplied`,
   promote fails with `PIPELINE_NOT_CONFIGURED`).
5. **Wait for DC's branch** — poll, don't assume:
   `until git ls-remote --exit-code origin refs/heads/<WI>; do sleep 15; done` (timeout ~5 min;
   observed: ~15 s, branch created at the head of the first pipeline stage branch).
   Cross-check `SELECT SourceCodeRepositoryBranch.Name FROM WorkItem WHERE Name='<WI>'` is set.
   Timeout → stop and report; do not create the branch.
6. **Worktree on DC's branch**:
   ```bash
   git fetch origin <WI>
   git worktree add <worktree_root>/<WI> -b <WI> --track origin/<WI>
   ```
   Then `checkout_devops_center_work_item(usernameOrAlias=dc_org, workItemName=<WI>, localPath=<worktree>)`.
7. **Verify** (all must hold, else stop):
   - `git -C <worktree> rev-parse --abbrev-ref @{u}` == `origin/<WI>` (never an integration branch)
   - `git -C <worktree> status` clean
8. `cd <worktree> && sf config set target-org <dev_org>` (local to the worktree).
9. Report: WI name, worktree path, upstream, target org. Save a project memory entry for the WI.

## Phase B — COMMIT

Preconditions: work done inside the worktree, files **uncommitted**, metadata retrieved from the org
(not hand-authored), no prettier on metadata XML.

1. Review the diff with the user (`git -C <worktree> status --short` + `git diff --stat`).
   Exclude from the change set: forceignored files, inactive flows, shared layouts/flexipages not
   belonging to the feature, per-org components handled by a separate procedure.
2. `commit_devops_center_work_item` (hasUpdates:false on modified files is a known DC NG trait — not an error).
3. `git -C <worktree> push origin HEAD` and verify it landed on `origin/<WI>`.
4. WI status must be **In Progress** → `create_devops_center_pull_request`.
5. `gh pr view <N> --repo <github_repo> --json mergeable,mergeStateStatus` (forces GitHub to compute
   mergeability; otherwise DC reports "source control is checking the pull request").
6. **Wait for the registry**: DC fills `WorkItemComponent` minutes after the PR. Poll on `dc_org`
   (`SELECT MemberName, MemberType, Operation FROM WorkItemComponent WHERE WorkItem.Name='<WI>'`, or
   `sf api request rest` if SOQL is blocked). Empty registry ≠ failure until it has had time.
   Compare with `git diff --name-only origin/<target-branch>...origin/<WI>`: missing files = they
   will NOT deploy.

## Phase C — PROMOTE

The mechanics belong to **`dx-devops-promote`** (validate → prepare → combine only if validate returns
`combineDetails` → promote → poll with **`dx-devops-request-status`** → `sf devops promotion complete`).
Invoke it; this phase only adds the project guardrails around it.

1. **Before** — confirm the target stage with the user (must be ≤ `promote_limit`) and resolve the IDs
   the official skill needs, on `dc_org`:
   - WI Id: `SELECT Id FROM WorkItem WHERE Name = '<WI>'`
   - target stage Id: `SELECT Id, Name, SourceCodeRepositoryBranch.Name FROM DevopsPipelineStage`
   `-o/--target-org` for every `sf devops` command is **`dc_org`**, never the worktree default org.
2. **Before** — project pre-checks the official validate does not do:
   - registry vs branch diff (step B6) — files missing from the registry will not deploy;
   - `git merge-tree` of the WI branch vs the target stage branch → `Duplicate picklist value` in record types;
   - dry-run deploy of the registry contents against the target org from an isolated copy → missing dependencies.
3. **Run `dx-devops-promote`.** Its `--skip-validation` rule stands (only when its own validate passed in
   this session). `--force`, `--deploy-all` and a non-default `--test-level` only with explicit user agreement.
4. **After** — verify what really deployed: latest `DeployRequest` on the target →
   `sf project deploy report --job-id <id> --json` → `details.componentSuccesses` vs expected files;
   PR merged (`gh pr view <N> --json state`); WI status advanced. A `*_SUCCESS` request status with
   non-null `errorDetails` is a failure (see `dx-devops-request-status`).

### Known promote errors
| Error | Real cause |
|---|---|
| `No components to deploy — resolved component set was empty` | registry empty (manual commit / WI never In Progress) |
| `named in package.xml, but was not found in zipped directory` | forceignored file in the PR diff |
| `Duplicate picklist value: <field> - <value>` | same value added by two branches in different positions |
| `Invalid version number: N` (flowDefinition) | flowDefinition committed without its flow |
| `insufficient access rights on cross-reference id` on flow | WI deletes a flow → unrecoverable, new WI without the delete |
| `source control is checking the pull request` | GitHub mergeability UNKNOWN → step B5 |
| `Global value set 'X__c' cannot be resolved` on RecordType | picklist field X__c missing on target |
