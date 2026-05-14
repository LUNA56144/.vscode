# Infra Workspace — Agent Instructions

## What this workspace is

im-platform and im-funding infrastructure repositories (Terraform, Azure).
Repos live under `/home/saldave/projects/platform/`, `funding/`, and `enrollment/`.

## For every task — use the orchestrator

Invoke the `infra-task-workflow` skill first. It handles repo setup, task execution,
validation, plan review, deployment, and cleanup in a single retry-driven loop.

Skill location: `.github/skills/infra-task-workflow/SKILL.md`

## Core rules (apply to every interaction)

- **Iterate until success** — never report a failure without diagnosing and attempting recovery
- **Max 3 retries** per distinct error before escalating with full context
- **Never destroy without confirmation** — `terraform apply`, `reset --hard`, `push --force` to main require explicit user approval
- **Sequential environments** — dev → qa → stage → stage-secondary → prod-secondary → prod; never skip
- **No hardcoded secrets or subscription IDs** in any committed file

## Skills available

| Skill | Trigger |
|-------|---------|
| `infra-task-workflow` | Any end-to-end infra task |
| `git-clean-setup` | "clean setup", "fresh start", "new branch" |
| `git-sync-main` | "pull latest", "sync repos", "update main" |
| `tf-plan-risk-summary` | "risk summary", PR with autoplan comment |
| `pr-deprecated-comments` | "clean up PR comments", "stale comments" |
| `rg-scanner` | "scan resource groups", "find rg names", "audit terraform rg" |
| `rg-policy-scan` | "policy compliance", "non-compliant resources", "azure policy violations" |
| `rg-jira-bulk` | "bulk jira tickets", "create tickets from rg scan", "batch ticket creation" |

## Custom Agents available

| Agent | Trigger |
|-------|---------|
| `infra-orchestrator` | Any infra task end-to-end |
| `rg-audit-jira` | "rg audit", "resource group audit", "identify resource groups", "funding rg scan" |

## Prompts available

`readme-blueprint-generator` · `generate-prod-deployment-announcement`

## Atlassian Rovo MCP

When connected to atlassian-rovo-mcp:
- **MUST** use Jira project key = DEVO
- **MUST** use cloudId = "https://viabenefits.atlassian.net" (do NOT call getAccessibleAtlassianResources)
- **MUST** use `maxResults: 10` or `limit: 10` for ALL Jira JQL search operations
