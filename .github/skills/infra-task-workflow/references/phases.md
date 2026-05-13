# Phase Procedures

Full step-by-step procedures for each phase of the infra task workflow.

---

## Communication Pattern

After each major step completes, send 3 to 4 short messages in a conversational tone.
No markdown separators. No "—". Write like a colleague giving a quick heads-up.

Example after setup completes (fresh task — ticket fetched first, then git setup):
```
Pulled the latest ticket from Jira — DEVO-1806, looks like the fileshare access task.
Target repo resolved: im-platform/production at /home/saldave/projects/platform/production.
Synced main and cleaned up — we're starting fresh on that repo.
Branch created as chore/DEVO-1806-add-fdt-fileshare-access. Moving into spec.
```

Keep it brief. Confirm what happened. State what's next.

---

## Phase 1 — Repository Setup

> ⚠️ **Execution order for fresh tasks:** Phase 1 git operations cannot run until the target
> repository is known. For fresh tasks, always run Phase 2.1 (fetch Jira ticket) and Phase 2.1.1
> (resolve target repo) **first**, then return here to perform the git setup on the confirmed repo.
> Phase 1 executes immediately only when the repo is already known (resuming a task, user specified
> it upfront, or re-entering on an existing branch).

**Logical execution order for a fresh task:**
```
Phase 2.1   → Fetch Jira ticket (repo is unknown — can't git setup yet)
Phase 2.1.1 → Resolve target repo from ticket (NOW we know the repo)
Phase 1     → Git setup on the confirmed repo  ← runs HERE, not before
Phase 2.1   → Create branch (name derived from ticket)
Phase 2.2   → Scope confirmation
Phase 2.3   → Write spec
Phase 3     → Start work
```

**Success:** Clean working tree on `main`, synced to latest remote. Branch creation happens after Phase 2.1 once the ticket and branch name are known.

Reset the target repo to `main`:

```bash
cd <target-repo>
git checkout main
git fetch --all --prune
git pull --ff-only
```

Handle dirty working tree:
- Uncommitted changes → ask stash or discard before proceeding
- Do not create the feature branch yet — branch name is derived from the Jira ticket in Phase 2.1

**Branch creation** — run after Phase 2.1 confirms ticket and name:
```bash
git checkout -b <type>/DEVO-XXXX-<kebab-purpose>
```

**Retry:**
| Failure | Recovery |
|---------|----------|
| Network / fetch error | Retry 3× with 5 s delay; offer offline mode |
| Uncommitted changes | Ask stash or discard; retry after resolution |
| Branch already exists | Offer switch-to-existing or rename |

---

## Phase 2 — Planning

**Success:** Active Jira ticket loaded, spec written, user confirms both before any code is touched.

### 2.1 Fetch active Jira ticket

Query Jira for the next upcoming ticket assigned to `sandro.aldave@wtwco.com`:

```
JQL: project = DEVO
     AND assignee = "sandro.aldave@wtwco.com"
     AND statusCategory != Done
     AND due is not EMPTY
     ORDER BY due ASC
```

Use `maxResults: 10` and `cloudId: "https://viabenefits.atlassian.net"`. Present the ticket with the nearest upcoming due date (first in the list) as the default.

Present the ticket to the user:
```
Found ticket: DEVO-XXXX — <summary>
Status: <status>  |  Due: <due-date>

Description: <description excerpt>

Proceed with this ticket? [Yes] / No (provide different ticket ID)
```

If the user provides a specific ticket ID instead, fetch that ticket directly.
Store the ticket ID and derive the branch name and PR title as follows:

**Branch name convention:**
```
<type>/DEVO-XXXX-<kebab-case-ticket-purpose>

type is derived from task type:
  terraform-change  → chore
  security-fix      → fix
  investigation     → chore
  documentation     → docs
  pr-review         → chore

ticket-purpose: lowercase kebab-case summary of the ticket title (max 5 words, drop articles)

Examples:
  chore/DEVO-1806-add-fdt-fileshare-access
  fix/DEVO-1812-disable-ftp-local-auth
  docs/DEVO-1820-update-readme-funding-reimbursement
```

**PR title convention:**
```
[DEVO-XXXX] <ticket summary>

Examples:
  [DEVO-1806] Add FDT fileshare access
  [DEVO-1812] Disable FTP and local auth on function apps
```

### 2.1.1 Resolve target repository

Inspect the ticket for a repository reference. Look for:
- An explicit repo name in the description or custom fields (e.g. `funding-reimbursement-infrastructure`)
- A GitHub URL in the description
- A label or component that maps to a known repo

**If a repo is found in the ticket:**
```
Target repository detected from ticket: <org>/<repo>
Path: /home/saldave/projects/<group>/<repo>

Confirm? [Yes] / No (choose different repo)
```

**If no repo is found in the ticket:**
Scan workspace and present grouped options:

```
No repository specified in ticket. Which repo should this task target?

Platform Infrastructure:
  1. hub-vnet                        (/home/saldave/projects/platform/hub-vnet)
  2. hub-vnet-agw                    (/home/saldave/projects/platform/hub-vnet-agw)
  ...

Funding Infrastructure:
  N. funding-reimbursement-infrastructure
  ...

Choose a number or type the repo name:
```

Do not proceed to Phase 2.2 until the target repository is confirmed.

### 2.2 Scope confirmation

Present a one-paragraph summary: what changes, which resources, which environments, known risks.
Ask "Does this match your intent?" — do not advance until confirmed.

> ⛔ **HARD STOP — do not advance to 2.3 until the user types an explicit confirmation in this
> session.** Finding an existing spec file does NOT count as approval. Resuming an existing branch
> does NOT count as approval. The only valid approval is the user confirming in this session.

### 2.3 Spec creation and presentation (spec-driven development)

Create `.terraform-planning-files/INFRA.<task-name>.md` in the target repository.

This file is the **primary source of truth** for Phase 3. The agent authors all Terraform
changes against it — not against assumptions.

Minimum spec structure:

```markdown
# INFRA.<task-name>

## Jira
DEVO-XXXX — <ticket summary>

## Goal
<One sentence: what this change achieves>

## Resources
| Resource | Action | Notes |
|----------|--------|-------|
| <azurerm_type.name> | create / modify / destroy | <reason> |

## Requirements
- <specific requirement — from Jira ticket description>
- <security or compliance constraint>

## Acceptance Criteria
- [ ] `terraform validate` passes
- [ ] `terraform fmt -check` passes
- [ ] CI plan exit code 0 or 2
- [ ] No 🔴 availability risks (or documented and accepted)
- [ ] Deployed to dev successfully
- [ ] All smoke tests pass in every environment
- <task-specific criteria>

## Smoke Tests
<!-- One row per assertion. Agent runs these via `az cli` after each environment apply (Phase 5.5). -->
| Environment | Resource | `az` command | Expected value |
|-------------|----------|-------------|----------------|
| all | <resource-name> | `az <command> --query <field> -o tsv` | `<expected>` |

## Out of Scope
- <what is explicitly NOT changing>

## Approved
<!-- Agent fills this in only after user types explicit confirmation in this session. -->
- [ ] Confirmed by user in session on <YYYY-MM-DD>
```

After writing the file, **present the full spec inline** in the chat so the user can review it
without opening any file. Output the entire raw file content character-for-character — do NOT
summarize, truncate, or omit any section. The output must be identical to what was written to disk.
Then ask:

```
Spec written to .terraform-planning-files/INFRA.<task-name>.md.

--- SPEC PREVIEW ---
<output the complete verbatim file content here — every section, every line, nothing omitted>
--------------------

Two confirmations required before Phase 3:
  ✅ Scope confirmed (Phase 2.2)
  ⬜ Spec confirmed (this step)

Does this spec match your intent? [Yes / No / Edit]
```

> ⛔ **HARD STOP — this is the final gate before Phase 3. Do not create the `.approved` sentinel
> file or start Phase 3 until the user types an explicit "yes" confirming the presented spec.**
>
> There are **two required confirmations** — both must happen before Phase 3 starts:
> 1. Phase 2.2 scope confirmation
> 2. Phase 2.3 spec presentation confirmation ← this one
>
> Finding an existing spec file, existing sentinel, or existing branch does NOT satisfy this gate.
> The user must confirm the presented spec in this session.

Once confirmed, fill in the `## Approved` section with today's date and create the sentinel file:

```bash
sed -i "s/- \[ \] Confirmed by user in session on <YYYY-MM-DD>/- [x] Confirmed by user in session on $(date +%Y-%m-%d)/" \
  .terraform-planning-files/INFRA.<task-name>.md

touch .terraform-planning-files/INFRA.<task-name>.approved
```

If `.terraform-planning-files/` does not exist in the repo, create it first:
```bash
mkdir -p .terraform-planning-files
```

---

## Phase 3-TF — Terraform Change

> ⛔ **Spec approval gate — check before doing anything else:**
>
> 1. Check for `.terraform-planning-files/INFRA.<task-name>.approved`
> 2. If **missing** → go back to Phase 2.2: present the spec, await explicit user confirmation,
>    create the sentinel file, then return here.
> 3. If **present** → proceed. The sentinel file is proof approval happened in a prior session.
>
> **Do not read repo files, author changes, or run any commands until this check passes.**

**Success:** `terraform validate` exits 0, `terraform fmt -check` reports no diffs, and dev tfvars dry-run exits 0 or 2.

```bash
ls .terraform-planning-files/ 2>/dev/null   # read any found files
terraform init -backend=false
terraform validate
terraform fmt -check -recursive
```

**Environment tfvars validation (dry-run before Phase 4):**

Repos use different directory layouts for tfvars. Discover the dev tfvars dynamically:

```bash
DEV_TFVARS=$(find . -name "*.tfvars" -path "*/dev*" \
  -not -path "*/.terraform/*" \
  -not -path "*/.worktrees/*" \
  | head -1)

if [ -n "$DEV_TFVARS" ]; then
  echo "Found dev tfvars at: $DEV_TFVARS"
  terraform plan -backend=false -var-file="$DEV_TFVARS" -out=/dev/null
else
  echo "No dev tfvars found — skipping var-file dry-run (repo uses no per-env vars)"
fi
```

Common paths found in this workspace:
- `dev/terraform.tfvars` (funding-reimbursement-infrastructure, log-file-analysis-infrastructure)
- `infrastructure/dev/terraform.tfvars` (funding-data-transfer-infrastructure, funding-communication-infrastructure)
- `core/dev.tfvars` (front-door-viabenefits core)
- No tfvars (production, aad-group-members, storage-account-network-rules)

If the dry-run exits 1, treat it as a Phase 3 failure and enter the retry loop before continuing to Phase 4.

**Retry loop:**
```
WHILE validate or fmt or dry-run fails:
  1. Identify exact file + line from error
  2. Apply targeted fix
  3. Re-run validate && fmt -check && dry-run
  4. Same error 3× → escalate with full diagnosis
```

---

## Phase 3-PR — PR Review

**Success:** All actionable review comments addressed and committed.

```bash
gh pr view --comments
# Apply fixes per comment, then:
git push
```

Invoke [`pr-deprecated-comments`](../../pr-deprecated-comments/SKILL.md) for outdated threads.

---

## Phase 3-INV — Investigation

**Success:** Root cause identified; recommended action presented.

1. Read logs, state, and resource configs (read-only only)
2. Form hypothesis; test with read-only commands
3. Present: root cause, affected resources, recommended fix
4. If fix needed → re-classify as `terraform-change`; re-enter Phase 3-TF

---

## Phase 4 — Validation & Plan Review

**Success:** CI plan exits 0 or 2 on ALL environments; no unacknowledged 🔴 risks; PR marked ready for review.

> 🛑 **Session ends after Phase 4.** The agent cannot wait for an external reviewer.
> Resume at Phase 5 only when the user confirms the PR is approved and merged.

```bash
git push -u origin <branch>
```

**Build PR body from spec** — read `.terraform-planning-files/INFRA.<task-name>.md` and extract:
- The `## Goal` section
- The `## Acceptance Criteria` section

Compose the PR body as:

```markdown
## What
<Goal content from spec>

## Acceptance Criteria
<Acceptance Criteria checklist from spec>

Closes DEVO-XXXX
```

Create a draft PR:

```bash
# PR title must follow: [DEVO-XXXX] <ticket summary>
gh pr create \
  --title "[DEVO-XXXX] <ticket summary>" \
  --body "<composed body from spec above>" \
  --draft
```

After the PR is created, capture the PR URL and post a Jira comment:

```
Jira comment (post to DEVO-XXXX via addCommentToJiraIssue):
  "PR is up: <pr_url>
   Branch: <branch_name>
   Ready for review once CI plan passes."
```

Wait for CI, then read result:

```bash
gh run list --workflow=auto-plan-the-tf --limit 5
gh run view <run-id> --log
```

**Plan failure loop (exit code 1):**
```
WHILE plan fails:
  1. Extract full error — categorise: syntax | config | provider | state | conflict
  2. Apply targeted fix
  3. git commit --amend --no-edit && git push --force-with-lease
  4. Wait for CI re-run; re-read result
  5. Same error category 3× → pause with full diagnosis
```

**All-environment risk assessment (plan-only — NO APPLY):**

Simultaneously invoke [`tf-plan-risk-summary`](../../tf-plan-risk-summary/SKILL.md) across
**all environments**: dev, qa, stage, stage-secondary, prod-secondary, prod.

These are read-only plan evaluations. Under **no circumstance** should any apply be
triggered at this stage — the PR is not yet merged.

Flag any destroy/replace on:
`azurerm_linux_function_app`, `azurerm_service_plan`, `azurerm_storage_account`,
`azurerm_key_vault`, `azurerm_eventhub_namespace`, `azurerm_sql_server`,
`azurerm_virtual_network`, `azurerm_role_assignment`

If 🔴 risks: present to user → "Accept or revise?" → revise returns to Phase 3-TF.

**Resolve open review threads (required before `gh pr ready`):**

> ⚠️ GitHub blocks merging when ANY review thread is unresolved.

1. Invoke [`pr-deprecated-comments`](../../pr-deprecated-comments/SKILL.md) — auto-resolves deprecated/outdated threads
2. After the skill completes, check for remaining unresolved threads:

```bash
gh api graphql -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:50) {
          nodes { isResolved isOutdated path line }
        }
      }
    }
  }' -F owner=<org> -F repo=<repo> -F pr=<number> \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)'
```

3. If unresolved active threads remain, list them and **stop**:

```
⛔ Cannot mark PR ready — X unresolved review thread(s) remain:
  • <file>:<line> — <thread excerpt>
  ...

These are active threads and require manual resolution before the PR can be merged.
Resolve them in GitHub, then confirm here to continue.
```

Do not run `gh pr ready` until the user confirms all threads are resolved.

```bash
gh pr ready
```

**Session checkpoint — await PR approval:**
```
Phase 4 complete. Risk summary posted to PR for all environments.
All review threads resolved. PR is open and awaiting reviewer approval.

Session ends here. Re-invoke with "deploy" or "PR merged, proceed" once merged.
```

---

## Phase 5 — Deployment

> 🔒 **Entry gate:** Confirm PR is approved and merged before running any apply.
> Do not enter this phase if the PR is still open.

**Success:** All environments dev → qa → stage → stage-secondary → prod-secondary deployed and validated. Prod workflow is triggered and left pending its manual approval — completion is handled on a scheduled deployment window outside this session.

> ⚠️ **Prod rule:** The prod workflow run is triggered so it is queued and ready, but the
> manual approval step inside the workflow is **never actioned here**. The agent posts the
> run URL and stops. Prod completion always happens via the scheduled deployment process.

### 5.1 — Confirm merge

```bash
gh pr view --json state,mergedAt
```

If `state != "MERGED"` → refuse to proceed. Instruct user to merge first.

### 5.2 — Apply lower environments (manual gate per environment)

Each environment deployment has a **manual approval step** inside the GitHub Actions
workflow. The agent's role is to:
1. Trigger the workflow run
2. Provide the direct run URL for the user to action the manual approval
3. Watch for completion
4. **Wait for user confirmation** before triggering the next environment

Order: **dev → qa → stage → stage-secondary → prod-secondary**

Per environment, repeat this loop:

```bash
LATEST_TAG=$(git ls-remote --tags --sort=-v:refname origin \
  | head -1 | awk '{print $2}' | sed 's|refs/tags/||')

gh workflow run im-deploy-tf-manual-apply.yml \
  --ref main \
  -f branch-tag-sha="$LATEST_TAG" \
  -f root-module=<env> \
  -f enable_seasonal_resources=false

# Capture and present the run URL for manual approval
gh run list --workflow=im-deploy-tf-manual-apply.yml --limit 1
```

After triggering, present to user:
```
▶ <ENV> deployment triggered.
  Manual approval required: <run-url>

  Complete the approval step in GitHub Actions, then confirm here to proceed.
  Type "done" when <ENV> is deployed, or "failed" to enter the failure loop.
```

Agent waits for user response before advancing to the next environment.

After the user confirms "done", run Phase 5.5 smoke tests for that environment before
triggering the next one. A failing smoke test is treated as a deployment failure — halt,
diagnose, and do NOT promote until resolved.

**Apply failure loop (per environment):**
```
WHILE apply fails (user reports "failed"):
  - State lock      → wait 60 s, retry
  - Provider/auth   → verify credentials, retry once
  - Conflict        → fix in Phase 3-TF, re-run Phase 4, re-enter Phase 5
  - Timeout         → retry run directly
  - 3× same env     → halt with full diagnosis; do NOT advance to next env
```

> Promotion is strictly blocked at any failure. No environment is ever skipped.

### 5.5 — Smoke Tests (per environment, post-apply)

**Purpose:** Confirm Azure's actual state matches the intent in the spec's `## Smoke Tests`
table. Terraform exiting 0 is not sufficient — these tests query the Azure control plane directly.

**When to run:** After every environment apply (5.2), before promoting to the next environment.
Also run after prod completes (outside this session) as a final confirmation.

**How to execute:**

Read `## Smoke Tests` from the spec file (`.terraform-planning-files/INFRA.<task-name>.md`).
Each row in the table is one assertion. Run the `az` command and compare actual output to expected.

```bash
# General pattern — adapt to each assertion row:
ACTUAL=$(az <command> --query "<jmespath>" -o tsv 2>&1)
EXPECTED="<value from spec>"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "❌ FAIL: expected '$EXPECTED', got '$ACTUAL'"
  exit 1
fi
echo "✅ PASS"
```

**Task-type assertion library** — use the matching rows from this table as a starting point
when writing the spec's `## Smoke Tests` section:

| Task type | What to verify | `az` command |
|-----------|---------------|--------------|
| `security-fix` — FTP disabled | `ftpsState` = `Disabled` | `az webapp show -n <app> -g <rg> --query ftpsState -o tsv` |
| `security-fix` — HTTPS only | `httpsOnly` = `true` | `az webapp show -n <app> -g <rg> --query httpsOnly -o tsv` |
| `security-fix` — local auth disabled | `siteAuthEnabled` = `false` | `az webapp auth show -n <app> -g <rg> --query enabled -o tsv` |
| `terraform-change` — role assignment | role exists for principal | `az role assignment list --assignee <id> --scope <scope> --query "[].roleDefinitionName" -o tsv` |
| `terraform-change` — fileshare | share exists | `az storage share exists -n <share> --account-name <acct> --query exists -o tsv` |
| `terraform-change` — storage network rule | default action = `Deny` | `az storage account show -n <acct> --query networkRuleSet.defaultAction -o tsv` |
| `terraform-change` — subnet delegation | delegation name present | `az network vnet subnet show -n <sub> --vnet-name <vnet> -g <rg> --query "delegations[].serviceName" -o tsv` |
| `terraform-change` — eventhub namespace | namespace provisioned | `az eventhubs namespace show -n <ns> -g <rg> --query provisioningState -o tsv` |

**Failure behaviour:**
- Any assertion fails → halt promotion; present the exact actual vs. expected values
- Do not advance to the next environment until all assertions pass
- If the failure is an Azure propagation delay (< 60 s since apply) → wait 30 s and retry once
- Persistent failure → treat as deployment failure; re-enter Phase 3-TF to investigate

**Passing output format:**
```
Smoke tests — <ENV>
  ✅ ftpsState = Disabled      (funding-eligibility-api)
  ✅ httpsOnly = true           (funding-eligibility-api)
All smoke tests passed. Safe to promote to <NEXT_ENV>.
```

---

### 5.3 — Post-deploy validation (lower envs)

After prod-secondary completes, invoke [`tf-plan-risk-summary`](../../tf-plan-risk-summary/SKILL.md)
as a post-deploy verification across all lower environments to confirm state is clean
and matches intent.

If any drift or unexpected delta is detected → halt and present diagnosis.

### 5.4 — Trigger prod workflow (queue only — do NOT action approval)

```bash
gh workflow run im-deploy-tf-manual-apply.yml \
  --ref main \
  -f branch-tag-sha="$LATEST_TAG" \
  -f root-module=prod \
  -f enable_seasonal_resources=false

gh run list --workflow=im-deploy-tf-manual-apply.yml --limit 1
```

Present the run URL and stop:

```
Lower environments complete: dev ✅  qa ✅  stage ✅  stage-secondary ✅  prod-secondary ✅
Post-deploy validation passed.

▶ Prod workflow triggered and queued: <run-url>
  The manual approval step has NOT been actioned — prod will complete on its scheduled deployment window.

🏁 Session B complete. Proceed to Phase 6 — Cleanup.
```

> 🛑 The agent never actions the prod manual approval. Even if asked, refuse and explain
> that prod completes on a scheduled window only.

---

## Phase 6 — Cleanup

**Success:** All review threads resolved, PR merged, repos synced.

**Resolve any remaining open review threads before merge:**

1. Invoke [`pr-deprecated-comments`](../../pr-deprecated-comments/SKILL.md) to auto-resolve deprecated/outdated threads
2. Check for remaining unresolved active threads (same GraphQL query as Phase 4)
3. If any remain, list them for manual resolution — do not proceed until confirmed resolved

> ⚠️ GitHub blocks merging when ANY review thread is unresolved. Confirm all threads are closed before the PR can be merged.

```bash
git checkout main && git pull --ff-only
```

Use [`git-sync-main`](../../git-sync-main/SKILL.md) to sync all repos after the target repo is back on main.

---

## Self-Learning — Known Error Patterns

When a retry resolves a new error category not listed below, **add it here** so future
runs handle it automatically without user intervention.

| Error pattern | Root cause | Auto-fix |
|--------------|------------|----------|
| `Error acquiring state lock` | Concurrent run or crashed prior apply | `terraform force-unlock <lock-id>`, retry after 60 s |
| `AADSTS700016` / auth failure | SP token expired or wrong subscription | Re-init backend; verify `ARM_*` env vars |
| `A resource with the ID already exists` | Import drift — resource exists in Azure but not in state | `terraform import <resource> <azure-id>` |
| `terraform fmt -check` diff | Formatting not applied | `terraform fmt -recursive`, re-commit |
| `Error: Cycle` | Circular dependency in resources | Refactor to use `depends_on` or split resources |
