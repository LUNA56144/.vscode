---
name: infra-task-workflow
description: "End-to-end orchestrator for any infrastructure task. Use for: Terraform changes, security fixes, drift remediation, PR review, investigation, documentation. Chains git setup, task execution, CI plan review, risk assessment, deployment, and cleanup with retry loops. Triggers: 'start working on', 'new task', 'end to end', 'full workflow', any infra change."
argument-hint: "Leave blank to auto-load latest Jira ticket, or paste a ticket ID"
---

# Infra Task Workflow

Shell around any infrastructure task. Handles everything before (setup, planning) and
after (validation, PR, deployment, cleanup). The task itself runs in Phase 3.

Full phase procedures: [references/phases.md](./references/phases.md)

---

## Workflow

Two sessions — Phase 4 is a hard stop awaiting external PR approval.

**Session A** (run once per task):
```
Phase 1 → Repo setup      (sync + clean branch)                    always
Phase 2 → Planning        (fetch Jira ticket + spec + confirm)      NEVER skippable
Phase 3 → TASK            (the actual work — varies)                always
Phase 4 → Validation      (validate, all-env plan-only, risk)       TF tasks only
          ↓ SESSION ENDS — await PR approval
```

**Session B** (triggered by user after PR is merged):
```
Phase 5 → Deployment      (sequential apply, post-deploy validation, prod gate)
Phase 6 → Cleanup         (sync repos, close Jira)                  always
```

## Entry phase

| State | Start |
|-------|-------|
| Fresh task | Phase 1 |
| On feature branch, **no `.approved` sentinel** | Phase 2.2 — spec review first |
| On feature branch, **`.approved` sentinel exists** | Phase 3 |
| PR open | Phase 4 |
| PR merged — deploy requested | Phase 5 |
| Post-prod deploy | Phase 6 |

> ⛔ **"On feature branch" never means skip planning.** The sentinel file
> `.terraform-planning-files/INFRA.<task-name>.approved` must exist before Phase 3 can start.
> If it is missing, run Phase 2.2 (present spec, await explicit user confirmation, create sentinel)
> before proceeding — regardless of how much work is already on the branch.

## Task type → Phase 3 path

| Type | Path | Phases 4–5? |
|------|------|------------|
| `terraform-change` / `security-fix` | [3-TF](./references/phases.md#phase-3-tf--terraform-change) | Yes |
| `pr-review` | [3-PR](./references/phases.md#phase-3-pr--pr-review) | Only if .tf changed |
| `investigation` | [3-INV](./references/phases.md#phase-3-inv--investigation) | No |

## Skills used per phase

| Phase | Skill / Prompt |
|-------|---------------|
| 1 | `git-clean-setup` (target repo only) |
| 2 | Jira query (fetch latest open ticket for `sandro.aldave@wtwco.com`) + spec creation |
| 4 | `tf-plan-risk-summary` |
| 3-PR, 6 | `pr-deprecated-comments` |
| 6 | `git-sync-main` (all repos, after target is back on main) |

## Output contract

Follow the output contract defined in `copilot-instructions.md`. Per-phase guidance:

| Phase | LANES | DESTRUCTIVE_CONFIRMATION | CMD: lines |
|-------|-------|--------------------------|------------|
| 1 (git setup) | sequential | none | `git checkout`, `git fetch`, `git reset`, `git checkout -b` |
| 2 (planning) | sequential | none | none (file writes only — use `FILE:`) |
| 3-TF (Terraform) | sequential | none | `terraform init`, `terraform validate`, `terraform fmt` |
| 4 (validate, multi-env plan) | parallel | none | `terraform plan` per env |
| 5 (deploy, sequential envs) | sequential | **required** | `terraform apply` per env |
| 6 (cleanup, all-repo sync) | parallel | none | `git checkout`, `git pull` per repo |
