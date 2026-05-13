# Production Deployment Announcement Generator

Automates the creation of Teams markdown announcements for production infrastructure deployments across all 11 Funding repositories.

## Features

- ✅ **Scans all 11 funding repositories** automatically
- ✅ **Compares git tags** to identify undeployed versions
- ✅ **Validates stage deployment** - ensures versions were deployed to stage before prod
- ✅ **Extracts PR titles** from commit messages
- ✅ **Generates Teams markdown** ready to paste
- ✅ **Blocks deployments** if versions haven't been deployed to stage

## Prerequisites

- **GitHub CLI (`gh`)** - Must be authenticated
- **Python 3.6+**

### Install GitHub CLI

```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh

# Authenticate
gh auth login
```

## Usage

### Basic Usage

```bash
python3 /home/saldave/projects/.vscode/.github/scripts/generate_prod_deployment_announcement.py YYYY-MM-DD HH:MM
```

### Example

```bash
# Schedule deployment for December 2, 2025 at 10:00 PM MT
python3 /home/saldave/projects/.vscode/.github/scripts/generate_prod_deployment_announcement.py 2025-12-02 22:00
```

### Using the Copilot Prompt

The easiest way to use this script is through the Copilot prompt:

```
#file:generate-prod-deployment-announcement.prompt.md 2025-12-02 22:00
```

Or interactively:

```
#file:generate-prod-deployment-announcement.prompt.md
```

Then provide the date and time when prompted.

## How It Works

1. **Authenticates with GitHub** - Verifies `gh` CLI is authenticated
2. **Validates input** - Ensures date/time format and future date
3. **Scans 11 funding repositories**:
   - Configuration: `client-data-azure-infrastructure`, `client-guides-infrastructure`, `client-implementations-infra`
   - Calculation: `funding-calculation`
   - Exports: `funding-communication-infrastructure`, `funding-data-transfer-infrastructure`, `funding-reimbursement-infrastructure`, `log-file-analysis-infrastructure`
   - Facilitation: `funding-eligibility-infrastructure`, `funding-enrollment-support-infrastructure`, `funding-qualification-infrastructure`
4. **Determines last deployed version** in prod and stage using GitHub Actions API
5. **Identifies undeployed versions** by comparing git tags
6. **Validates stage deployment**:
   - ✅ **Ready for prod**: Versions <= last stage version
   - ⚠️ **Blocked**: Versions > last stage version (not yet in stage)
7. **Exits with error** if ALL versions are blocked (zero ready for prod)
8. **Extracts PR titles** from commit messages
9. **Generates announcement** with two sections:
   - Main: Stage-validated versions ready for prod
   - Blocked: Versions not yet deployed to stage
10. **Outputs to terminal** ready to copy

## Output Format

The script generates a Teams markdown announcement with **two distinct sections**:

### Main Deployment Message

Contains **ONLY** stage-validated versions ready for production deployment:

```markdown
🚨 Infrastructure Production Deployment Announcement - Tuesday, 12/02/25 🚨

Hi team,

A production infrastructure deployment is scheduled for Tuesday, 12/02/25, at 10:00 P.M. MT. This release includes updates that have been validated across the Dev, QA, and Stage environments.

What's Included in This Deployment?

**client-data-azure-infrastructure**
v1.3.11 → Revert network-information module and remove Sumo Logic integrations
v1.3.10 → Updates the actions/github-script GitHub Action to the latest major version

**client-guides-infrastructure**
v0.1.147 → Remove deprecated Sumo Logic integrations and error filters

What You Need to Know:

✅ Deployment is scheduled outside of working hours

✅ No significant downtime is expected

❓ If you have any questions or concerns, feel free to reach out.

Thanks!
```

## Stage Deployment Validation

**🚨 IMPORTANT: All versions MUST be deployed to stage before production deployment.**

The script validates each undeployed version against the last stage deployment:

### Stage-Validated Versions (Ready for Prod)
- Version number <= last stage deployment version
- ✅ Listed in main "What's Included in This Deployment?" section
- ✅ Will be deployed to production
- ✅ Part of the primary announcement message

### Blocked Versions (Not in Stage)
- Version number > last stage deployment version
- OR no stage deployment history found
- ⚠️ Listed in separate "⚠️ Versions Blocked" section AFTER main message
- ⚠️ **NOT included in the deployment** - shown for informational purposes only
- ❌ **CANNOT be deployed to production**
- **Action Required**: Deploy to stage first, then these can be included in a future production deployment

### Exit Behavior
- If **ALL** versions are blocked, script exits with **error code 1**
- Error message lists all blocked repositories and versions
- Indicates deployment should be **postponed**
- Deploy blocked versions to stage before retrying

## Error Handling

### All Versions Blocked
```
❌ ERROR: No versions ready for production deployment

All versions must be deployed to stage before production.

Blocked versions (not yet in stage):

  **funding-calculation**
    ⚠️ No stage deployment history found
    - v1.0.361
    - v1.0.360

Action required: Deploy these versions to stage first, then retry.
```

### No Undeployed Versions
```
📊 Summary:
  Repositories with stage-validated changes: 0
  Total versions ready for prod: 0

No pending production deployments found.
```

### GitHub Auth Failure
```
❌ GitHub CLI not authenticated. Please run: gh auth login
```

### Invalid Date/Time
```
❌ Invalid date format. Use YYYY-MM-DD
Usage: generate_prod_announcement.py YYYY-MM-DD HH:MM
```

### Unable to Determine Prod/Stage Status
Shows warning in announcement:
```
⚠️ **Note:** Unable to determine production deployment status for:
- repository-name
```

## Repositories Scanned

The script automatically checks these 11 repositories:

**Configuration Domain:**
- `im-funding/client-data-azure-infrastructure`
- `im-funding/client-guides-infrastructure`
- `im-funding/client-implementations-infra`

**Calculation Domain:**
- `im-funding/funding-calculation`

**Exports Domain:**
- `im-funding/funding-communication-infrastructure`
- `im-funding/funding-data-transfer-infrastructure`
- `im-funding/funding-reimbursement-infrastructure`
- `im-funding/log-file-analysis-infrastructure`

**Facilitation Domain:**
- `im-funding/funding-eligibility-infrastructure`
- `im-funding/funding-enrollment-support-infrastructure`
- `im-funding/funding-qualification-infrastructure`

## Workflow Detection

The script detects successful deployments using flexible pattern matching:

**Production deployments:**
- `Apply prod terraform from v*`
- `Apply Terraform (prod) [v*]`
- Any workflow containing "prod" with a version number

**Stage deployments:**
- `Apply stage terraform from v*`
- `Apply Terraform (stage) [v*]`
- Any workflow containing "stage" with a version number

**Excludes:**
- `prod-secondary` deployments
- `stage-secondary` deployments

## Troubleshooting

### Script can't find workflow deployments
- Verify repository has recent successful prod/stage deployments
- Check workflow name matches "Apply Terraform"
- Ensure version tags follow `v*.*.*` format (e.g., v1.2.3)

### GitHub API rate limiting
- Script uses authenticated requests (higher rate limit)
- Increase timeout if network is slow: modify `timeout=60` in script

### PR titles not extracted
- Script handles multiple commit message formats
- If no PR title found, shows version only
- Manually verify commit messages in GitHub

## Team Usage

### For SRE Team
1. Run script before scheduled production deployments
2. Review blocked versions - deploy to stage if needed
3. Copy announcement to Teams
4. Post to team channels and org-wide notifications

### For Deployment Coordinators
1. Use prompt: `#file:prod-deployment-announcement.prompt.md`
2. Provide deployment date and time
3. Review output for blocked versions
4. Coordinate stage deployments if necessary
5. Share announcement with stakeholders

## File Locations

- **Script**: `/home/saldave/projects/.vscode/.github/scripts/generate_prod_deployment_announcement.py`
- **Prompt**: `/home/saldave/projects/.vscode/.github/prompts/generate-prod-deployment-announcement.prompt.md`
- **This README**: `/home/saldave/projects/.vscode/.github/scripts/README.md`

## Maintenance

### Adding New Repositories
Edit the `REPOS` list in the script:

```python
REPOS = [
    "im-funding/client-data-azure-infrastructure",
    # Add new repo here
    "im-funding/new-repository",
]
```

### Changing Workflow Detection
Modify the `get_last_deployed_version()` function to match different workflow naming patterns.

## Support

For issues or questions:
1. Check this README
2. Review the prompt file for additional context
3. Contact SRE team
4. Open an issue in the workspace repository

## License

Internal use only - IM Platform SRE Team
