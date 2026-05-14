---
name: rg-scanner
description: "Scan Azure Terraform repositories for resource group names. Use when: find resource groups, scan repos for rg names, audit resource groups in terraform, identify azure resource groups, list rg names, terraform rg extraction."
---

# RG Scanner — Azure Resource Group Name Extractor

Scans one or more Terraform repository directories and extracts every Azure resource
group name reference, resolving variables and locals to their concrete values where possible.

## When to Use

- Scanning a single repo for all RG names
- Parallel fan-out scan across multiple repos (used by `rg-audit-jira` agent)
- Validating naming convention compliance

## Input

A base path to a repo root, e.g.:
```
/home/saldave/projects/funding/calculation/funding-calculation
```

Or a group base path to scan all repos in a group:
```
/home/saldave/projects/funding/facilitation/
```

## Procedure

### Step 1 — Discover Environments

```bash
find <repo_root> -mindepth 1 -maxdepth 2 -type d \
  ! -path "*/.terraform/*" ! -path "*/node_modules/*" \
  | sort
```

Identify environment directories: `dev`, `qa`, `stage`, `stage-secondary`, `prod-secondary`, `prod`.
If no environment subdirs exist, treat the repo root as a single environment.

### Step 2 — Extract RG Name References

For each environment directory, run the patterns from [scan-patterns.md](./references/scan-patterns.md).

**Priority order (highest signal first):**

1. Direct assignments: `resource_group_name = "<value>"`
2. Variable references: `resource_group_name = var.<name>` → trace to `terraform.tfvars` or `variables.tf`
3. Local references: `resource_group_name = local.<name>` → trace to `locals.tf`
4. Data source blocks: `data "azurerm_resource_group" "..." { name = "<value>" }`
5. Module input variables named `resource_group_name` → trace to calling module

**ReAct Pattern per file:**
- **Reason**: "This file has N resource blocks — which ones likely reference RGs?"
- **Act**: Run the grep pattern
- **Reflect**: Do results follow `rg-im-<domain>-<service>-<env>` convention?

### Step 3 — Resolve Variables

When a reference is `var.resource_group_name` or `var.rg_name`:
1. Check `terraform.tfvars` in the same environment directory
2. Check `variables.tf` for default values
3. Check `*.auto.tfvars` files
4. If unresolvable, record as `VAR_UNRESOLVED:<var_name>`

When a reference is `local.resource_group_name` or `local.rg_name`:
1. Check `locals.tf` in same directory
2. Check `main.tf` locals blocks

### Step 4 — Structured Output

Return findings as YAML:

```yaml
repo: <repo_name>
base_path: <absolute_path>
environments:
  - name: <env>
    path: <absolute_path>
    resource_groups:
      - name: <rg_name_or_VAR_UNRESOLVED:var>
        source_type: direct|variable|local|data_source|module
        source_file: <relative_path>
        line: <line_number>
    anomalies:
      - <description_of_naming_deviation>
scan_gaps:
  - <description_if_no_rg_found>
```

### Step 5 — Validate

Before returning, verify:
- At least one RG name found per environment that contains `.tf` files with `resource` blocks
- All `VAR_UNRESOLVED` entries were traced as far as possible
- Anomalies are documented (names not matching `rg-im-*` pattern)

## Naming Convention

Expected pattern: `rg-im-<domain>-<service>-<environment>`

Examples:
- `rg-im-funding-calculation-dev`
- `rg-im-funding-eligibility-prod`
- `rg-im-funding-foundry-qa`

Flag as anomaly if: all-uppercase, missing env suffix, contains subscription ID, or uses a hardcoded non-standard name.

## Scan Patterns Reference

See [scan-patterns.md](./references/scan-patterns.md) for all grep commands.
