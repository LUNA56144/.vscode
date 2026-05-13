---
name: git-sync-main
description: >-
  Fetch and fast-forward the default branch across one or all workspace
  repositories without resetting state. Use when user asks to "pull latest",
  "sync repos", "update main", "fetch all repos", "check latest commit",
  or "bring repos up to date". Non-destructive: uses pull --ff-only,
  never runs reset --hard. Always switches to default branch and pulls latest.
license: MIT
compatibility: Requires git and bash. Designed for VS Code multi-root workspaces.
allowed-tools: Bash(git:*) Bash(find:*) Bash(bash:*)
metadata:
  author: saldave
  version: "1.2"
---

# Git Sync Main

Quickly sync one or all workspace repositories to the latest remote default
branch. Unlike [git-clean-setup](../git-clean-setup/SKILL.md), this skill is
**non-destructive** — it never runs `reset --hard` and never creates new
branches.

## Workflow

### 1. Repository Discovery

Reuses the same discovery pattern as git-clean-setup:

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

**Single-repo mode**: If the user names a repo or is inside one, skip the
listing and proceed directly.

**All-repos mode**: Run the script against every discovered repository and
collect results for the summary table.

### 2. Check Working Tree Status

Before switching branches, check for uncommitted changes:

```bash
cd <selected-repo>
git status --short
```

**If uncommitted changes exist**, ask the user:

1. **Stash** (recommended) — `git stash push -m "WIP: auto-stashed by git-sync-main"`
2. **Discard** — `git checkout . && git clean -fd` (confirm before executing — destructive)
3. **Cancel** — abort the workflow

In **all-repos mode**, if a repo has uncommitted changes, skip it and report
a ⚠️ dirty status in the summary table instead of asking per repo.

### 3. Sync Repository

Run the bundled script:

```bash
bash scripts/sync-main.sh <repo-path>
```

The script will:
- Detect the default branch (`main` or `master`)
- `git checkout <default>` (if not already on it)
- `git fetch origin <default> --prune`
- `git pull --ff-only`
- Output result with JSON line

#### Script Exit Codes

| Code | Meaning |
| ---- | ------- |
| 0 | Success — up to date or fast-forwarded |
| 1 | Invalid arguments or not a git repo |
| 2 | Default branch detection failed |
| 3 | Network / fetch error |
| 5 | Fast-forward failed (local diverged from remote) |

### 4. Summary Output

**Single-repo mode** — display:

```
Repository:  <name>
Previous:    <previous-branch>
Branch:      <default-branch>
Latest:      <short-hash> <commit-message>
Status:      ✅ up-to-date | 🔄 updated | ⚠️ diverged
```

If changes were stashed in Step 2, remind the user:

```
Stashed changes available — run `git stash pop` to restore.
```

**All-repos mode** — display a summary table:

```markdown
| Repository | Previous | Default | Latest Commit | Status |
| ---------- | -------- | ------- | ------------- | ------ |
| ...        | ...      | ...     | ...           | ...    |
```

Status icons:
- ✅ up-to-date — already at latest remote commit
- 🔄 updated — fast-forwarded to latest
- ⚠️ diverged — local has commits not on remote; manual merge needed
- ⚠️ dirty — uncommitted changes; skipped (all-repos mode only)
- ❌ error — fetch failed (network, auth, etc.)

After the table, show a one-line tally:

```
Synced: X updated, Y up-to-date, Z diverged, W errors
```

## Safety

- **NEVER** run `reset --hard` or `push --force`
- **NEVER** discard or stash uncommitted changes without asking the user first
- Uses `pull --ff-only` to avoid merge commits; if it fails, report diverged
- Follow the same dirty-state handling pattern as
  [git-clean-setup](../git-clean-setup/SKILL.md)

## Edge Cases

| Scenario | Resolution |
| -------- | ---------- |
| No `.git` found | Skip with error status in table |
| Network unreachable | Report ❌ error per repo; continue with others |
| Default branch ambiguous | Fall back to `main`, then `master`, then skip |
| Detached HEAD | Checkout default branch |
| Dirty working tree (single) | Ask user to stash or discard |
| Dirty working tree (all) | Skip repo with ⚠️ dirty status |
| Shallow clone | `git fetch` works; `pull --ff-only` works if fast-forwardable |
