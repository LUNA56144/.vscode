---
name: generate-prod-deployment-announcement
description: "Generate Teams markdown production deployment announcements for funding infrastructure repos. Use when: generating prod announcement, deployment notification, Teams message, announcing production release, prod deployment announcement, infrastructure release, funding repos deployment."
argument-hint: "YYYY-MM-DD HH:MM (e.g. 2025-12-05 22:00)"
---

# Generate Production Deployment Announcement

Scans all 11 `im-funding` infrastructure repositories, identifies stage-validated versions not yet deployed to production, extracts PR titles, and outputs a ready-to-paste Teams markdown announcement.

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- Python 3.6+
- `TEAMS_WEBHOOK_URL` env var set in `~/.zshrc` (required only for `--post`)

## Procedure

### 1. Collect Inputs

If not provided via argument, ask:
- **Deployment date** — format `YYYY-MM-DD`, must be a future date
- **Deployment time** — format `HH:MM` (24-hour, Mountain Time)

### 2. Run the Script

Locate the script relative to this skill file, then run it:

```bash
SCRIPT="$(dirname "$(realpath "$0")")/scripts/generate_prod_deployment_announcement.py"

# Preview only — show announcement in terminal
python3 "$SCRIPT" YYYY-MM-DD HH:MM

# Generate + post directly to Teams (Funding SRE channel)
python3 "$SCRIPT" YYYY-MM-DD HH:MM --post
```

When running from an agent context, resolve the script path by finding this skill's directory in the workspace:

```bash
# From the workspace root
python3 .github/skills/generate-prod-deployment-announcement/scripts/generate_prod_deployment_announcement.py YYYY-MM-DD HH:MM
```

The script:
- Verifies `gh` authentication
- Scans all 11 funding repos for undeployed version tags
- Compares each version against the last stage deployment (semantic version comparison)
- Categorizes versions as **ready** (stage-validated) or **blocked** (not yet in stage)
- Exits with error code 1 if zero versions are ready — action required: deploy blocked versions to stage first
- Fetches PR titles for each ready version
- Generates the formatted announcement

### 3. Present the Output

Display the full Teams announcement from the script output (between the `TEAMS ANNOUNCEMENT` markers), followed by the deployment summary.

### 4. Confirm Before Posting

After displaying the announcement, **always ask the user for explicit confirmation** before posting to Teams:

> "Would you like me to post this announcement to the Funding SRE Teams channel now?"

- If **confirmed** → proceed to Step 5
- If **declined** → inform the user the announcement is ready to copy/paste manually and stop

### 5. Post to Teams

Once confirmed, run the script with the `--post` flag:

```bash
python3 .github/skills/generate-prod-deployment-announcement/scripts/generate_prod_deployment_announcement.py YYYY-MM-DD HH:MM --post
```

Report success or failure from the script output. On failure (non-zero exit or error message), display the error and advise the user to check that `TEAMS_WEBHOOK_URL` is set in `~/.zshrc`.

## Repositories Scanned

| Domain | Repository |
|--------|-----------|
| Configuration | `client-data-azure-infrastructure`, `client-guides-infrastructure`, `client-implementations-infra` |
| Calculation | `funding-calculation` |
| Exports | `funding-communication-infrastructure`, `funding-data-transfer-infrastructure`, `funding-reimbursement-infrastructure`, `log-file-analysis-infrastructure` |
| Facilitation | `funding-eligibility-infrastructure`, `funding-enrollment-support-infrastructure`, `funding-qualification-infrastructure` |

## Announcement Format

```
🚨 Infrastructure Production Deployment Announcement - [Day], [MM/DD/YY] 🚨

Hi team,

A production infrastructure deployment is scheduled for [Day], [MM/DD/YY], at [H:MM P.M./A.M.] MT.
...

**[repository-name]**
v1.2.3 → PR title
v1.2.2 → Another change
```

## Error Scenarios

| Error | Cause | Action |
|-------|-------|--------|
| All versions blocked | No version has been deployed to stage | Deploy to stage first |
| Unable to determine prod status | No recent successful prod workflow runs | Check workflow history manually |
| `gh` not authenticated | CLI not logged in | Run `gh auth login` |

## Script

[generate_prod_deployment_announcement.py](./scripts/generate_prod_deployment_announcement.py)
