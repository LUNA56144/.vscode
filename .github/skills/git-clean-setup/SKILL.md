---
name: git-clean-setup
description: >-
  Reset a workspace repository to a clean state on the default branch with
  latest remote changes, then create a properly named feature branch. Use when
  user asks to start fresh, clean setup, reset repo, begin new work, switch
  repo, or mentions "clean setup", "fresh start", "start working on", or
  "new branch". Supports: (1) Multi-repo workspace discovery and selection,
  (2) Dirty state handling with stash/commit/discard options, (3) Full reset
  to origin default branch, (4) New branch creation with naming conventions.
license: MIT
compatibility: Requires git and bash. Designed for VS Code multi-root workspaces.
allowed-tools: Bash(git:*) Bash(find:*)
metadata:
  author: saldave
  version: "1.0"
---

# Git Clean Setup

Automate the standard workflow for starting fresh work on any repository in a
multi-root workspace. Ensures developers always begin from the latest default
branch with a clean working tree and a properly named feature branch.

## Workflow

Follow these steps in order. Use the bundled script at
[scripts/clean-setup.sh](scripts/clean-setup.sh) for non-interactive git
operations; handle all user decisions in the agent.

### 1. Repository Discovery

Scan the workspace for Git repositories:

```bash
find /home/saldave/projects -maxdepth 3 -name ".git" -type d \
  -exec dirname {} \; 2>/dev/null | sort
```

Present repositories grouped by organization:

| Group                    | Path prefix                              |
| ------------------------ | ---------------------------------------- |
| Platform Infrastructure  | `/home/saldave/projects/platform/`       |
| Funding – Configuration  | `/home/saldave/projects/funding/configuration/` |
| Funding – Calculation    | `/home/saldave/projects/funding/calculation/`   |
| Funding – Exports        | `/home/saldave/projects/funding/exports/`       |
| Funding – Facilitation   | `/home/saldave/projects/funding/facilitation/`  |
| Enrollment               | `/home/saldave/projects/enrollment/`            |

If the user is already inside a repository, detect it and offer to continue
there or choose a different one.

### 2. Check Working Tree Status

```bash
cd <selected-repo>
git status --short
```

**If uncommitted changes exist**, ask the user:

1. **Stash** (recommended) — `git stash push -m "WIP: auto-stashed by clean-setup"`
2. **Commit** — run a quick commit flow (consider the [git-commit](../git-commit/SKILL.md) skill if available)
3. **Discard** — `git checkout . && git clean -fd` (confirm before executing — destructive)
4. **Cancel** — abort the workflow

### 3. Reset to Default Branch

Run the bundled script:

```bash
bash scripts/clean-setup.sh <repo-path>
```

The script will:
- Detect the default branch (`main` or `master`)
- `git checkout <default>`
- `git fetch --all --prune`
- `git reset --hard origin/<default>`
- Report status

If the script exits non-zero, surface the error and offer:
1. Retry
2. Continue with local state
3. Cancel

### 4. Create Feature Branch

Prompt the user for a branch name. Suggest the format:

```
<type>/<description>

Types: feature | fix | hotfix | chore | docs | refactor | test
Examples:
  feature/add-monitoring-alerts
  fix/storage-account-permissions
  chore/DEVO-1234-update-dependencies
```

Validate:
- No special characters except `-` and `/`
- Does not already exist locally (`git branch --list <name>`)
- Does not already exist remotely (`git ls-remote --heads origin <name>`)

If the branch exists, offer:
1. Switch to existing branch and pull latest
2. Choose a different name
3. Delete and recreate (confirm — destructive)

Create the branch:

```bash
git checkout -b <branch-name>
```

### 5. Completion Summary

Display:

```
Repository:  <name>
Location:    <path>
Branch:      <branch-name>
Base:        origin/<default> (up to date)
Status:      clean working tree

Ready for development.
```

If changes were stashed in Step 2, remind the user:

```
Stashed changes available — run `git stash pop` to restore.
```

## Git Safety Protocol

- **NEVER** run destructive commands (`--force`, `reset --hard`, `clean -fd`)
  without explicit user confirmation
- **NEVER** force-push to the default branch
- **NEVER** skip pre-commit hooks (`--no-verify`) unless the user asks
- **NEVER** modify git config
- If a command fails due to hooks, fix the issue and create a new commit

## Best Practices

- Always fetch and reset before creating a new branch
- Use descriptive, kebab-case branch names
- Include Jira ticket IDs when available (e.g., `chore/DEVO-1234-description`)
- Stash over discard — prefer non-destructive options
- Verify the correct repository before making changes

## Edge Cases

| Scenario | Resolution |
| -------- | ---------- |
| No `.git` found | Inform user; re-scan or ask for path |
| Network unreachable | Offer offline mode (skip fetch/reset, use local HEAD) |
| Merge conflicts on reset | Should not happen with `reset --hard`; if it does, surface error |
| Default branch ambiguous | Fall back to `main`, then `master`, then ask user |
| Detached HEAD | Checkout default branch first, then proceed |
