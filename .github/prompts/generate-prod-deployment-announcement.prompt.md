---
title: Generate Production Deployment Announcement for All Funding Repos
description: Generate Teams markdown production deployment announcements by comparing git tags across all funding repositories
tags: [deployment, notification, teams, production, announcement]
---

# Generate Production Deployment Announcement for All Funding Repos

Generates a professional Teams markdown announcement for production infrastructure deployments across all Funding repositories. Uses a Python script to scan all 11 funding repos, compare git tags to identify undeployed versions, extract PR titles, and create a unified announcement.

## Prerequisites

- GitHub CLI (`gh`) authenticated
- Python 3.6+ available
- Script location: `/home/saldave/projects/.vscode/.github/scripts/generate_prod_announcement.py`

## Workflow

### Step 1: Execute Python Script

Run the Python script with deployment date and time as arguments:

```bash
python3 /home/saldave/projects/.vscode/.github/scripts/generate_prod_deployment_announcement.py YYYY-MM-DD HH:MM
```

**Example:**
```bash
python3 /home/saldave/projects/.vscode/.github/scripts/generate_prod_deployment_announcement.py 2025-12-02 22:00
```

The script handles all validation and processing:

1. **Authenticate with GitHub**
   - Verifies `gh` CLI is authenticated
   - Exits with error if not authenticated

2. **Validate Input Parameters**
   - Date format: YYYY-MM-DD (must be in future)
   - Time format: HH:MM (24-hour format)
   - Exits with usage message if invalid

3. **Scan All 11 Funding Repositories**
   - Repositories scanned automatically:
     - **Configuration Domain:**
       - `im-funding/client-data-azure-infrastructure`
       - `im-funding/client-guides-infrastructure`
       - `im-funding/client-implementations-infra`
     - Configuration: `client-data-azure-infrastructure`, `client-guides-infrastructure`, `client-implementations-infra`
     - Calculation: `funding-calculation`
     - Exports: `funding-communication-infrastructure`, `funding-data-transfer-infrastructure`, `funding-reimbursement-infrastructure`, `log-file-analysis-infrastructure`
     - Facilitation: `funding-eligibility-infrastructure`, `funding-enrollment-support-infrastructure`, `funding-qualification-infrastructure`

4. **Determine Last Deployed Version in Production**
   - Uses GitHub API to fetch "Apply Terraform" workflow runs
   - Filters for successful prod deployments using flexible regex patterns:
     - `Apply prod terraform from v*` (most repos)
     - `Apply Terraform (prod) [v*]` (some repos)
     - Any workflow name containing "prod" with a version number
   - Excludes prod-secondary deployments
   - Extracts version number using regex: `v\d+\.\d+\.\d+`
   - Handles multiple repository workflow naming conventions automatically

5. **Determine Last Deployed Version in Stage**
   - Uses same workflow API logic but filters for stage deployments
   - Supports same flexible naming patterns for stage environment
   - Excludes stage-secondary deployments
   - Returns None if no stage deployment history found

6. **Identify Undeployed Versions**
   - Fetches all version tags (format: v*.*.*)
   - Compares tags to find versions after last prod deployment
   - Excludes environment tags (dev-release, stage-release, etc.)
   - Returns versions in newest-to-oldest order

7. **Validate Stage Deployment Status**
   - For each undeployed version, compares against last stage deployment
   - Uses semantic version comparison (major.minor.patch)
   - Categorizes versions into two groups:
     - **Ready for prod**: Versions <= last stage version (stage-validated)
     - **Blocked**: Versions > last stage version (not yet in stage)
   - If no stage history found, all versions are blocked

8. **Extract PR Titles**
   - Fetches commit message for each undeployed tag
   - Handles multiple commit message formats:
     - `Merge pull request #123` followed by title on next line
     - `Title (#123)` with PR number at the end
   - Extracts and cleans PR title (removes PR numbers)
   - Shows version only if no PR title found

9. **Exit Check for Blocked Deployments**
   - If ALL versions are blocked (zero ready for prod), script exits with error
   - Displays detailed error message listing all blocked repositories and versions
   - Exit code 1 indicates deployment cannot proceed
   - Requires action: Deploy blocked versions to stage first

10. **Generate Announcement**
   - Formats date as "Day, MM/DD/YY"
   - Formats time as "H:MM P.M./A.M. MT"
   - Creates Teams markdown with two sections:
     - Main section: Stage-validated versions ready for prod
     - Blocked section: Versions not yet deployed to stage
   - Lists versions newest to oldest per repository
   - Includes warnings for repos with issues

11. **Output Results**
   - Displays announcement in terminal
   - Shows summary with counts and schedule

### Step 2: Review Output

The script displays:

1. **Scanning Progress** - Shows each repository being checked
2. **Summary Statistics** - Repositories with changes and total versions
3. **Formatted Announcement** - Complete Teams markdown ready to copy

### Step 3: Copy Announcement

Manually copy the announcement text from the terminal output and paste it into Teams.

## Announcement Template Format

The script generates Teams markdown with **two distinct sections**:

### Main Deployment Message (Stage-Validated Versions Only)

```markdown
🚨 Infrastructure Production Deployment Announcement - [Day], [MM/DD/YY] 🚨

Hi team,

A production infrastructure deployment is scheduled for [Day], [MM/DD/YY], at [H:MM P.M./A.M.] MT. This release includes updates that have been validated across the Dev, QA, and Stage environments.

What's Included in This Deployment?

**[repository-name]**
v1.2.3 → PR title description
v1.2.2 → Another change description
v1.2.1

What You Need to Know:

✅ Deployment is scheduled outside of working hours

✅ No significant downtime is expected

❓ If you have any questions or concerns, feel free to reach out.

Thanks!
```

### Optional Warnings Section

```markdown
⚠️ **Note:** Unable to determine production deployment status for:
- [repo-with-warning]
```

**Format Rules:**
- **Main deployment section**: ONLY stage-validated versions that WILL be deployed
- Repositories listed alphabetically
- Versions listed newest to oldest per repository
- Version format: `v{version} → {PR title}` or just `v{version}` if no PR title
- Warnings section included if any repos have issues

## Error Handling

The script handles these scenarios:

- **All versions blocked**: Exits with error code 1, displays detailed list of blocked versions and requires stage deployment first
- **No undeployed versions**: Displays "No pending production deployments found" and exits successfully
- **GitHub auth failure**: Exits with message "Please run: gh auth login"
- **Invalid date format**: Exits with usage message and format requirements
- **Invalid time format**: Exits with usage message and format requirements
- **Date in past**: Exits with validation error
- **No PR title found**: Shows version without description arrow
- **Unable to determine prod version**: Shows warning in announcement
- **Unable to determine stage version**: All undeployed versions are blocked with warning
- **Version parsing failure**: Treats unparseable versions as blocked

### Common Causes for "Unable to Determine Prod Status"

A repository may show as "unable to determine prod deployment status" when:

1. **No Recent Prod Deployments**: The repository hasn't had a successful prod deployment within the last 200 workflow runs

2. **Workflow Name Changed**: The "Apply Terraform" workflow was renamed or doesn't exist

3. **Permissions Issue**: The script can't access workflow run data (rare)

**Note**: The script now automatically handles multiple workflow naming conventions through flexible pattern matching, including:
- `Apply prod terraform from v*`
- `Apply Terraform (prod) [v*]`
- Any format containing "prod" with a version number

If a repository still shows this warning, verify that it has successful prod deployments in its recent workflow history.

### Stage Deployment Validation

**Mandatory Requirement:** All versions MUST be deployed to stage before production deployment.

The script validates each undeployed version against stage deployment status:

1. **Stage-Validated Versions** (Ready for Prod):
   - Version number <= last stage deployment version
   - ✅ Shown in main "What's Included in This Deployment?" section
   - ✅ Will be deployed to production
   - ✅ Part of primary announcement message

2. **Blocked Versions** (Not in Stage):
   - Version number > last stage deployment version
   - OR no stage deployment history found for repository
   - ⚠️ Shown in separate "⚠️ Versions Blocked" section AFTER main message
   - ⚠️ **NOT included in deployment** - informational only
   - ❌ CANNOT be deployed to production
   - **Action required**: Deploy to stage first, then include in future production deployment

3. **Exit Behavior**:
   - If ALL versions across all repositories are blocked, script exits with error code 1
   - Error message lists all blocked repositories and versions
   - Indicates deployment should be postponed until versions are deployed to stage
   - No announcement generated if nothing is ready for deployment

**Version Comparison**: Uses semantic versioning comparison (major.minor.patch format). Versions are parsed as tuples and compared numerically.

## Usage

When invoked, this prompt will:
1. Ask for deployment date (YYYY-MM-DD) and time (HH:MM) if not provided
2. Execute the Python script: `/home/saldave/projects/.vscode/.github/scripts/generate_prod_announcement.py`
3. Parse the script output to extract the announcement content
4. Display a clean, formatted Teams markdown announcement in the chat ready to copy
5. Provide a summary of what's included

**Example interaction:**
```
User: #file:generate-prod-deployment-announcement.prompt.md
Assistant: [Asks for date and time]
User: 2025-12-02 at 22:00
Assistant: [Shows formatted announcement in chat with summary]
```

## Quick Start

If you already know the deployment schedule:
```
#file:generate-prod-deployment-announcement.prompt.md 2025-12-05 22:00
```

## Output Format

The assistant will display:
1. **Clean Teams Markdown Announcement** - Ready to copy and paste into Teams
2. **Deployment Summary** - Number of repos, versions, and any warnings
3. **Key Highlights** - Major changes worth noting

## Notes

- Script location: `/home/saldave/projects/.vscode/.github/scripts/generate_prod_announcement.py`
- Run before scheduled production deployments
- Post announcement to team channels and org-wide deployment notifications
- Format optimized for Microsoft Teams markdown
- Default deployment time: 22:00 (10:00 P.M. MT) is outside working hours
- Script automatically handles all GitHub API calls and validations
- Announcement is displayed directly in chat for easy copying
- See full documentation: `/home/saldave/projects/.vscode/.github/scripts/README.md`
