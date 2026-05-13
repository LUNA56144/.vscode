---
name: tf-plan-risk-summary
description: >-
  Read the autoplan Terraform comment on the active PR and produce a brief,
  risk-focused summary to catch unexpected changes that could cause app
  unavailability. Use when reviewing a PR with a terraform plan comment and
  you want a concise risk report instead of reading the raw plan output.
---

# Terraform Plan Risk Summary

Read the existing autoplan PR comment and produce a concise availability-risk report.
Do not run terraform yourself. Do not modify any files.

## Availability-Critical Resource Types

Flag any change to these resource types at ⚠️ or 🔴 depending on the action:

| Resource type pattern | Why it matters |
|-----------------------|----------------|
| `azurerm_linux_function_app` / `azurerm_function_app` | App goes offline |
| `azurerm_service_plan` / `azurerm_app_service_plan` | All apps on the plan go offline |
| `azurerm_storage_account` | Data loss / app failure |
| `azurerm_eventhub_namespace` / `azurerm_eventhub` | Message pipeline breaks |
| `azurerm_key_vault` | All secret-dependent apps break |
| `azurerm_sql_server` / `azurerm_mssql_server` | Database unavailable |
| `azurerm_virtual_network` / `azurerm_subnet` | Network connectivity loss |
| `azurerm_role_assignment` | Permission changes may break access |
| `azurerm_management_lock` | Lock removed — deletion possible |
| `azuread_group_member` | AAD group membership change — access impact |

## Workflow

### 1. Find the autoplan comment

Read PR comments (general + review) and find the one posted by the GitHub Actions
bot that contains `### Format, Init and Plan Results`. There may be one per environment.
Collect all of them.

### 2. Extract the plan text

Each comment has a `<details>` block with the raw `terraform plan` output inside a
code fence. Extract the plan text from each environment comment.

> ⚠️ **Important**: Plans can be 70KB or larger. Always parse the plan text directly
> from the full API response body (e.g. by reading the comment's `body` field from
> the JSON). **Do not** pipe to temp files and grep — shell tools may silently truncate
> large outputs, causing destroys or replacements to be missed.

### 3. Classify each planned change

For each line matching the pattern:
```
  # <resource_address> will be <action>
```
or
```
  # <resource_address> must be replaced
```

Classify:
- 🔴 **destroy** or **replaced** on a critical resource type → availability risk
- ⚠️ **destroy** or **replaced** on any other resource → review needed
- 🔴 **update in-place** on a critical resource if the diff includes force-replace attributes
- ✅ **create** → generally safe
- ✅ **update in-place** on non-critical, no force-replace → safe
- ✅ **no changes** → safe

### 4. Delete any previous risk summary comments

Before posting, search the PR's existing comments for any that contain `## 🔍 Terraform Plan Risk Summary`. Delete **all** of them so the PR never shows more than one summary at a time.

### 5. Post a PR comment

Post a single PR comment using this format:

---
## 🔍 Terraform Plan Risk Summary

| Env | 🔴 Availability Risk | ⚠️ Review | ✅ Safe |
|-----|---------------------|-----------|--------|
| dev | N | N | N |

### 🔴 Availability Risks
_(only if any exist)_
- `<resource_address>` — **<action>** — `<resource_type>` _(reason: e.g. function app will be destroyed)_

### ⚠️ Needs Review
_(only if any exist)_
- `<resource_address>` — **<action>**

### ✅ Summary
One sentence: e.g. "No availability risks detected — 3 role assignments updated, 1 AAD group member added."

---

### 6. If no autoplan comment exists

Reply: "No autoplan comment found on this PR. The workflow may not have run yet, or no `infrastructure/**` files were changed."

## Tone & Format

- Be brief. The table is the headline.
- List only flagged resources by name — do not dump the raw plan.
- If there are zero risks, say so clearly in one line.
- Maximum 30 lines in the posted comment.
