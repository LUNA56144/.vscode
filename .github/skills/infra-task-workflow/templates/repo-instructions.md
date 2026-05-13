# Copilot Instructions — Infrastructure Repository

## Agent Skills

This repository is part of the **im-platform / im-funding** infrastructure estate.
The shared skills library lives at your VS Code workspace root under `.github/skills/`.

When working in this repository, the agent must:

1. **Use the `infra-task-workflow` skill** for any end-to-end change — it orchestrates
   setup, authoring, plan review, risk assessment, deployment, and cleanup automatically.

2. **Iterate until success** — never report a failure without first diagnosing and
   attempting to fix it. Apply the retry loops defined in the orchestrator skill.

3. **Reference planning files** — check `.terraform-planning-files/` at the repo root
   before making any changes. Treat them as the primary source of truth for requirements.

## Skill Reference

Skills are resolved from the workspace root `.github/skills/` folder:

| Skill | When to invoke |
|-------|---------------|
| `infra-task-workflow` | Any new task — invoke this first |
| `git-clean-setup` | Starting fresh on this repo |
| `git-sync-main` | Syncing to latest main |
| `jira-ticket` | Generating a Jira ticket |
| `tf-plan-risk-summary` | After CI plan completes on a PR |
| `pr-deprecated-comments` | Before merging — clean stale review threads |

## Terraform Standards

- AVM (Azure Verified Modules) where available
- Implicit dependencies; no unnecessary `depends_on`
- No hardcoded secrets or subscription IDs
- `terraform validate` + `terraform fmt` must pass before pushing
- Sequential environment promotion: dev → qa → stage → stage-secondary → prod-secondary → prod

## Repository-Specific Context

<!-- Customise this section per repo -->
<!-- Example:
**Environments:** dev, qa, stage, prod
**State backend:** Azure Storage — `<storage-account>/<container>`
**Workflow:** `.github/workflows/im-deploy-tf-manual-apply.yml`
**Key resources:** App Service, Key Vault, Storage Account, Event Hub
-->

---

> **CLI agents (gh copilot, claude, codex):** This file may not be auto-loaded.
> Place `AGENTS.md` and `CLAUDE.md` at the repo root with the same workflow rules.
> Copy from the workspace-level `AGENTS.md` at `/home/saldave/projects/.vscode/AGENTS.md`
> and add repo-specific context to the bottom.
