# SRE Team VS Code Workspace Configuration

This repository contains comprehensive VS Code workspace configurations designed specifically for Site Reliability Engineering (SRE) teams managing Azure infrastructure across multiple projects and environments.

---

## 🤖 GitHub Copilot Instructions (✨ NEW - Best Practices Format!)

This workspace now uses the **official GitHub Copilot custom instructions format** following best practices from GitHub and VS Code documentation.

### What Changed?

**✅ New Structure:**
- `.github/copilot-instructions.md` - Auto-applies to all Copilot interactions
- `.github/instructions/*.instructions.md` - Path-specific rules (e.g., for Terraform files)
- `.github/prompts/*.prompt.md` - Reusable workflow prompts

### Instruction Reliability Migration (May 2026)

- `.github/copilot-instructions.md` now acts as a dispatcher only.
- Execution logic is split into `.github/01-generate.md` (max 5 rules).
- Formatting and response constraints are split into `.github/02-style.md` (max 5 rules).
- Per-rule verification is split into `.github/03-verify.md` (max 5 rules).
- Mirror copies are kept in `.copilot/` with the same filenames.
- Backup created before migration: `.github.backup-20260512-132745`.

**❌ Old Structure (Deprecated):**
- `copilot-instructions.json` - Custom JSON format (renamed to `.deprecated`)

### Available Prompts

Use these in Copilot Chat via 📎 Attach → Prompt:

| Prompt File | Purpose | Usage |
|-------------|---------|-------|
| `git-workflow` | Automate Git branch setup | Attach prompt → Follow guided workflow |
| `quick-commit-push` | Smart commit & push | Attach prompt → Auto-generates commit message |
| `terraform-safety` | Comprehensive safety review | Attach prompt → Reviews Terraform changes |
| `update-docs` | Auto-update documentation | Attach prompt → Updates READMEs, CHANGELOG, arch docs |

**Quick Example**:
```
You: [Click 📎 in Copilot Chat]
     [Select "Prompt..." → "git-workflow"]
→ Lists repositories, creates feature branch from latest main

You: [make changes to Terraform files]
     [Copilot automatically uses terraform.instructions.md]

You: [Attach "terraform-safety" prompt]
→ Comprehensive safety review with risk assessment

You: [Attach "update-docs" prompt]
→ Analyzes changes and updates documentation automatically

You: [Attach "quick-commit-push" prompt]
→ Commits with smart message and pushes
```

📖 **[Read Detailed Copilot Setup Guide](README.md#github-copilot-configuration---best-practices)** (Section added above for full details)

---

## 🏗️ Architecture Overview

```
/home/saldave/projects/
├── .vscode/                          # Global SRE Configuration
│   ├── copilot-instructions.json     # Copilot automation config
│   ├── git-workflow.instructions.md  # Git workflow automation
│   ├── quick-commit-push.instructions.md  # QCP automation
│   ├── terraform-safety.instructions.md   # Terraform safety checks
│   ├── templates/                    # Reusable configuration templates
│   ├── scripts/                      # Automation scripts
│   ├── snippets/                     # Code snippets for common tasks
│   └── workspaces/                   # Environment-specific workspaces
├── platform/                        # Platform infrastructure
├── funding/                          # Funding-related projects
└── sre-master-workspace.code-workspace
```

## 🚀 Quick Start

### For New Team Members

1. **Run the setup script:**
   ```bash
   cd /home/saldave/projects
   ./.vscode/scripts/setup-workspace.sh
   ```

2. **Open the master workspace:**
   ```bash
   code sre-master-workspace.code-workspace
   ```

3. **Configure Azure CLI:**
   ```bash
   az login
   ```

### For Existing Team Members

1. **Update all repositories:**
   ```bash
   ./.vscode/scripts/git-pull-all.sh
   ```

2. **Run health check:**
   ```bash
   ./.vscode/scripts/infrastructure-health-check.sh
   ```

## 📋 Available Workspaces

### Master Workspace
- **File:** `sre-master-workspace.code-workspace`
- **Purpose:** Complete overview of all infrastructure projects
- **Use case:** General development, code reviews, documentation

### Environment-Specific Workspaces
- **Development:** `.vscode/workspaces/development.code-workspace`
- **Staging:** `.vscode/workspaces/staging.code-workspace`
- **Production:** `.vscode/workspaces/production.code-workspace`
- **Incident Response:** `.vscode/workspaces/incident-response.code-workspace`

## 🛠️ Features

### Automated Tasks
- 🏗️ Terraform operations (init, plan, validate, format)
- ☁️ Azure CLI integration
- 🔍 Multi-environment validation
- 🧹 Workspace cleanup
- 📊 Infrastructure health checks

### Code Snippets
- **Terraform:** Azure resources with standard tags
- **Kubernetes:** Deployments, services, configmaps
- **Azure:** Resource groups, storage accounts, key vaults

### Security Features
- 🔒 Automated security scanning
- 🏷️ Tag compliance checking
- 🌐 Network rule validation
- 💾 Encryption verification

## 📚 Usage Guide

### Running Terraform Operations

#### Quick Plan (Current Directory)
```bash
# Use VS Code Task: Ctrl+Shift+P > Tasks: Run Task > "🏗️ Terraform: Init & Plan"
```

#### Multi-Environment Planning
```bash
./.vscode/scripts/plan-all-environments.sh
```

### Azure Operations

#### Login and Set Subscription
```bash
# Use VS Code Tasks for Azure operations
# Ctrl+Shift+P > Tasks: Run Task > "☁️ Azure: Login"
```

### Health Monitoring

#### Infrastructure Health Check
```bash
./.vscode/scripts/infrastructure-health-check.sh
```

#### Security Scan
```bash
./.vscode/scripts/security-scan.sh
```

## 🔧 Configuration Details

### Global Settings
- **Auto-save:** On focus change
- **Format on save:** Enabled for Terraform, YAML, JSON
- **Git integration:** Auto-fetch enabled
- **Search optimization:** Excludes build artifacts and temporary files

### Extensions
- **Required:** Terraform, Azure Account, GitHub PR, GitLens
- **Infrastructure:** Azure CLI, Docker, Kubernetes
- **Development:** PowerShell, Python, YAML
- **Productivity:** Material Icons, Copilot

### Environment Variables
- **Development:** Green status bar, relaxed git settings
- **Staging:** Yellow status bar, standard validation
- **Production:** Red status bar, strict confirmations
- **Incident:** Red theme, production access, auto-save disabled

## 📊 Monitoring and Analytics

### Task Execution Tracking
- All task executions are logged
- Usage analytics help optimize workflows
- Performance metrics guide configuration improvements

### Health Check Reports
- Terraform validation across all environments
- Configuration drift detection
- Security compliance monitoring

## 🚨 Incident Response

### Incident Response Workspace
Special workspace configuration for production incidents:
- Red visual theme for awareness
- Direct access to production environments
- Disabled auto-save to prevent accidental changes
- Quick access to runbooks and monitoring

### Emergency Procedures
1. Open incident response workspace
2. Verify Azure CLI authentication
3. Access relevant runbooks
4. Use dedicated incident scripts

## 🤖 GitHub Copilot Automation

### Overview

This workspace includes powerful GitHub Copilot instructions that automate common development workflows. These instructions work across all repositories in the workspace and provide smart automation for Git operations, commit management, and Terraform safety checks.

### 📁 Instruction Files

| File | Purpose | Trigger |
|------|---------|---------|
| `copilot-instructions.json` | Master configuration (registers all workflows) | N/A |
| `git-workflow.instructions.md` | Git branch setup automation | `git workflow`, `setup branch` |
| `quick-commit-push.instructions.md` | Smart commit and push | `qcp`, `quick commit push` |
| `terraform-plan-review.prompt.md` | Plan review & failure diagnosis | `/terraform-plan-review` |
| `terraform-safety.instructions.md` | Pre-deployment safety checks | `#tfsafety`, `terraform safety` |

### 🔄 Workflow 1: Git Workflow Automation

**When to use**: Starting new work on any repository

**Trigger**: `git workflow` or `setup branch`

**What it does**:
1. Lists all Git repositories in workspace
2. Lets you select which repository to work on
3. Switches to main branch and pulls latest changes
4. Handles uncommitted changes (stash/commit/discard)
5. Creates new feature branch with proper naming
6. Displays completion summary

**Example**:
```
You: git workflow

Copilot: 📚 Available Git Repositories:
  1. platform
  2. funding-reimbursement-infrastructure
  3. funding-calculation
  [... more repositories ...]

You: 2

Copilot: ✅ Switched to main branch
         📥 Pulled latest changes
         🌿 Enter new branch name:

You: feature/add-availability-tests

Copilot: ✅ Created branch: feature/add-availability-tests
         🎉 Ready for development!
```

### 💨 Workflow 2: Quick Commit and Push (QCP)

**When to use**: Ready to commit and push your changes

**Trigger**: `qcp` or `quick commit push`

**What it does**:
1. Shows git diff for review
2. Generates smart commit message (conventional commits format)
3. Creates feature branch if on main/master
4. Runs `terraform fmt -recursive` automatically
5. Stages all changes
6. Commits with generated message
7. Pushes to remote
8. Suggests creating PR

**Smart Commit Messages**:
- `feat:` for new features
- `fix:` for bug fixes
- `chore:` for maintenance
- `docs:` for documentation
- `refactor:` for code restructuring

**Example**:
```
You: qcp

Copilot: 📝 Changes detected:
         M  modules/monitoring/main.tf
         M  dev/main.tf
         
         Generated commit message:
         "feat: add availability tests for all app services
         
         - Created standard web tests for 11 services
         - Configured PagerDuty alerts
         - Set up metric alerts with failure thresholds"
         
         ✅ Committed: abc1234
         📤 Pushed to: feature/add-availability-tests
         💡 Create PR: https://github.com/.../pull/new/...
```

**Advanced Options**:
- `qcp skip format` - Skip Terraform formatting
- `qcp amend` - Amend last commit
- `qcp with message: <msg>` - Use custom message

### 🔍 Workflow 3: Terraform Plan Review

**When to use**: After PR creation or when terraform plan fails

**Trigger**: `/terraform-plan-review` or `terraform plan review`

**What it does**:
1. Auto-detects current scenario (active PR, merged PR, local changes, or failure)
2. Fetches terraform plan output from GitHub Actions workflow logs
3. **If plan succeeded**: Provides summary with risk analysis
4. **If plan failed**: Diagnoses the error and provides fix instructions
5. Categorizes error types (syntax, state lock, auth, resource conflicts, etc.)
6. Shows simple explanation in plain language + technical details
7. Provides step-by-step remediation instructions
8. Includes verification commands to confirm fix

**Success Example**:
```
You: /terraform-plan-review

Copilot: 
## Terraform Plan Summary - dev

**Repository:** funding-reimbursement-infrastructure
**Branch:** feature/add-monitoring
**PR:** #123 (open)
**Plan:** 15 to add, 2 to change, 0 to destroy
**Risk Level:** 🟡 MEDIUM
**Recommendation:** REVIEW REQUIRED

### Key Changes:
- Adding 5 availability tests for critical endpoints
- Scaling App Service Plan from 1 to 2 workers
- Updating application settings (non-breaking)

### Next Steps:
- Review plan output in PR comments
- Verify alert thresholds are appropriate
- Proceed with merge to deploy to dev
```

**Failure Example**:
```
You: /terraform-plan-review

Copilot:
## ❌ Terraform Plan Failed - dev

**Error Type:** STATE
**Severity:** FIXABLE

### 🔍 What Went Wrong
Terraform couldn't run your plan because someone else is 
currently making changes to the same infrastructure. This 
is like two people trying to edit the same document at 
once - Terraform locks the file to prevent conflicts.

### 🔧 How to Fix It
1. Check if another workflow is running:
   - Go to GitHub Actions tab
   - Look for running "auto-plan-the-tf" workflows
   
2. If no workflow is running, the lock is stale:
   ```bash
   cd dev
   terraform force-unlock cc54938e-a8be-2b63-70b5-a7f2827a66c9
   ```

3. Try your plan again:
   ```bash
   terraform plan
   ```

### ✅ Verify the Fix
Expected outcome: Plan should complete successfully
```

**Common Error Types Diagnosed**:
- 🔒 State lock conflicts
- 🔑 Authentication failures  
- ⚠️ Resource already exists
- 📝 Syntax errors
- 🔗 Dependency cycles
- 🚫 Missing required arguments
- 🔄 Provider version conflicts

### 🔒 Workflow 4: Terraform Safety Review

**When to use**: Before deploying Terraform changes (CRITICAL!)

**Trigger**: `#tfsafety` or `terraform safety`

**What it does**:
1. Scans all `.tf` file changes
2. Classifies risk (LOW/MEDIUM/HIGH/CRITICAL)
3. **BLOCKS** destructive operations:
   - Resource deletions
   - Forced replacements
   - Database changes
   - Network CIDR modifications
4. **WARNS** about risky changes:
   - In-place updates
   - Scaling changes
   - Module upgrades
5. Checks required tags and security compliance
6. Generates pre-deployment checklist
7. Provides APPROVE/REJECT recommendation
8. Includes detailed rollback plan

**Example**:
```
You: #tfsafety

Copilot: 
🔒 Terraform Safety Review Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Executive Summary
─────────────────
Repository: funding-reimbursement-infrastructure
Branch: feature/add-availability-tests
Risk Level: 🟢 LOW
Status: ✅ APPROVED

Changes
───────
📦 33 to add:
  - 11 availability tests
  - 11 PagerDuty action groups
  - 11 metric alerts

🔄 2 to modify:
  - App Service Plan worker count (1→2)
  - VM config (minor update)

🗑️ 0 to destroy

Risk Assessment
───────────────
✅ No critical issues
✅ No destructive operations
✅ All required tags present
✅ Security best practices followed

Deployment Recommendation
─────────────────────────
✅ APPROVED - Safe to deploy

[Pre-deployment checklist included]
[Rollback plan included]
```

### 🎯 Complete Workflow Example

Typical development cycle combining all four workflows:

```bash
# 1. Start new work
You: git workflow
→ Creates feature/add-monitoring branch from latest main

# 2. Make your changes
[Edit Terraform files]
[Update documentation]
[Add tests]

# 3. Commit and push
You: qcp
→ Generates: "feat: add comprehensive monitoring"
→ Formats Terraform files
→ Pushes to remote
→ Provides PR link

# 4. Review the plan
You: /terraform-plan-review
→ Fetches plan from GitHub Actions
→ Shows summary or diagnoses failures
→ Provides fix instructions if needed

# 5. Safety check before merge (for Terraform changes)
You: #tfsafety
→ Reviews safety of changes
→ Provides approval/rejection
→ Shows pre-deployment checklist

# 5. Create Pull Request
[Click PR link]
[Add reviewers]
[Wait for CI/CD]
```

### 📋 When to Use Each Workflow

| Scenario | Workflow | Why |
|----------|----------|-----|
| Starting new feature | `git workflow` | Ensures clean start from latest main |
| Made changes, ready to commit | `qcp` | Automates commit + push |
| **ANY Terraform change** | `#tfsafety` | **CRITICAL** - Prevents outages |
| Production deployment | `#tfsafety` | Extra safety validation |
| Quick doc fix | `qcp` | Fast commit and push |
| Emergency hotfix | All three | Full safe workflow |

### ⚠️ Critical Safety Rules

**ALWAYS run `#tfsafety` before deploying Terraform changes!**

The safety review will **BLOCK** these dangerous operations:
- ❌ Resource deletions
- ❌ Database instance changes
- ❌ Network CIDR modifications
- ❌ Storage account deletions
- ❌ Key Vault deletions
- ❌ Forced resource replacements

### 🎓 Best Practices

#### DO:
✅ Use `git workflow` to start all new work
✅ **ALWAYS** run `#tfsafety` before Terraform deployments
✅ Review generated commit messages before accepting
✅ Combine workflows (workflow → safety → qcp)
✅ Read the full instruction files for advanced features

#### DON'T:
❌ Skip safety checks for "quick fixes"
❌ Ignore warnings in safety reports
❌ Commit without reviewing diffs
❌ Work directly on main branch
❌ Push Terraform changes without safety review

### 📚 Detailed Documentation

Each workflow has comprehensive documentation in its instruction file:

- **`git-workflow.instructions.md`**: Complete workflow steps, error handling, repository patterns
- **`quick-commit-push.instructions.md`**: Commit message guidelines, branch naming, examples
- **`terraform-safety.instructions.md`**: Risk classification, compliance checks, rollback procedures

### 🔧 Customization

To modify or extend these workflows:

1. Edit the relevant `.instructions.md` file
2. Update `copilot-instructions.json` if triggers change
3. Test with Copilot to verify functionality
4. Document changes in this README

### 🤝 Team Usage

**All team members** with this workspace automatically get these workflows.

**To onboard new team members**:
1. Clone workspace repository
2. Open in VS Code with Copilot enabled
3. Share this README
4. Try each workflow once for familiarization

### � Troubleshooting

**Copilot doesn't recognize instructions**:
- Reload VS Code window (Cmd/Ctrl + Shift + P → "Reload Window")
- Verify `.instructions.md` file extensions
- Check `copilot-instructions.json` syntax

**Workflows not triggering**:
- Use exact trigger keywords
- Type in Copilot chat (not terminal)
- Ensure you're in a Git repository

**Safety check too strict**:
- Edit `terraform-safety.instructions.md`
- Adjust blocking/warning conditions
- Add repository-specific exceptions

---

## �🔒 Security Best Practices


### Implemented Security Measures
- No hardcoded secrets in configurations
- Regular security scanning
- Tag compliance monitoring
- Network rule validation
- Encryption verification

### Security Workflow
1. **Pre-commit:** Run security scan
2. **Code review:** Security checklist
3. **Deployment:** Automated validation
4. **Post-deployment:** Compliance monitoring

## 📈 Performance Optimization

### Workspace Performance
- Optimized file watching and exclusions
- Efficient search indexing
- Minimal extension set per workspace
- Background task optimization

### Monitoring
- Extension usage tracking
- Task execution analytics
- Performance bottleneck identification

## 🤝 Team Collaboration

### Shared Configuration
- Consistent settings across team members
- Standardized task definitions
- Shared code snippets
- Common keyboard shortcuts

### Onboarding Process
1. Run setup script
2. Install recommended extensions
3. Configure Azure CLI
4. Complete training checklist

## 🔄 Maintenance

### Regular Updates
- Monthly workspace configuration review
- Quarterly extension audit
- Annual security assessment

### Version Control
- Workspace configurations are version controlled
- Changes tracked in git
- Rollback capability for configurations

## 📞 Support and Troubleshooting

### Common Issues
- **Terraform not found:** Ensure Terraform is installed and in PATH
- **Azure CLI authentication:** Run `az login` and verify subscription
- **Extension conflicts:** Review and disable conflicting extensions

### Getting Help
- Check internal documentation
- Contact SRE team leads
- Submit issues to workspace configuration repository

## 🎯 Roadmap

### Planned Enhancements
- Integration with monitoring dashboards
- Automated compliance reporting
- Custom extension development
- Enhanced incident response tools

---

**Last Updated:** August 27, 2025  
**Maintained by:** SRE Team  
**Version:** 2.0.0
