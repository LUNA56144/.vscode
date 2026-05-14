---
name: rg-policy-scan
description: "Query Azure Policy compliance state for a list of resource groups. Use when: check policy compliance, find non-compliant resources, azure policy violations, policy state per rg, audit policy findings, non-compliant azure resources, policy remediation data."
---

# RG Policy Scan — Azure Policy Compliance Checker

Queries Azure Policy compliance state for a list of resource group names and returns
structured non-compliance findings: which policies failed, which resources are affected,
and what effect type each policy enforces.

## When to Use

- After `rg-scanner` (or cache load) has produced a list of RG names
- Checking compliance status before creating remediation tickets
- Called automatically by `rg-audit-jira` agent in Phase 2

## Input

Read the RG list from the cache file — do NOT re-read from repos:

```bash
CACHE_PATH="/home/saldave/projects/.vscode/docs/plan/rg-cache.json"
```

## Procedure

### Step 1 — Verify Azure CLI Login and Identify Subscriptions

```bash
az account show --query "{subscription:name,id:id}" -o json
```

If this fails, stop and report: "Azure CLI not authenticated — run `az login` first."

The cache groups RGs by `env`. Route them to the correct subscription:

| Environments | Subscription |
|---|---|
| `dev`, `qa`, `stage` | current active subscription (DEV) |
| `prod` | switch to `WTW-BDAIM-PROD` before querying |

### Step 2 — Per-RG Sequential Query

For each RG in the cache, run `az policy state list`. Group by subscription to minimize
context switches: query all dev/qa/stage RGs first, then switch to prod and query prod RGs.

```bash
# For each RG (dev/qa/stage — no subscription switch needed)
az policy state list \
  --resource-group "<rg_name>" \
  --filter "complianceState eq 'NonCompliant'" \
  --query "[].{
    policy:policyDefinitionName,
    effect:policyDefinitionAction,
    resourceId:resourceId,
    resourceType:resourceType,
    policySet:policySetDefinitionName
  }" \
  -o json

# Before querying prod RGs — switch subscription
az account set --subscription "WTW-BDAIM-PROD"

# Then run the same command for each prod RG
```

Switch back to the DEV subscription after prod queries complete:
```bash
az account set --subscription "<dev-subscription-name>"
```

**ReAct per RG:**
- **Reason**: "How many non-compliant findings? Are any `deny` effect — meaning active resource deployment is being blocked?"
- **Act**: Collect and structure the raw output
- **Reflect**: Are the affected resources tied to resources managed by the owning repo?

### Step 3 — Classify by Severity

Map `effect` to severity:

| Effect | Severity | Meaning |
|--------|----------|---------|
| `deny` | 🔴 CRITICAL | Resource creation/update is actively blocked |
| `deployIfNotExists` | 🟠 HIGH | Required configuration not deployed |
| `modify` | 🟡 MEDIUM | Resource property needs correction |
| `audit` / `auditIfNotExists` | 🟢 LOW | Logged but not blocked |
| `append` | 🟢 LOW | Missing tag or property |

### Step 4 — Deduplicate and Group

For each RG:
1. Group findings by `policy` (policyDefinitionName)
2. Deduplicate `resourceId` entries under each policy
3. Identify the maximum severity in the RG (for ticket priority)
4. Look up `repo` and `env` for each RG from the cache entries

### Step 5 — Get Policy Display Details (Optional Enrichment)

For each **unique** policy definition found across all RGs (not per-RG — deduplicate first), retrieve display name once:

```bash
az policy definition show \
  --name "<policyDefinitionName>" \
  --query "{displayName:displayName,description:description,category:metadata.category}" \
  -o json 2>/dev/null || echo "builtin_or_custom"
```

### Step 6 — Structured Output

Build the compliance results structure:

```yaml
compliance_results:
  - rg: <rg_name>
    repo: <owning_repo>
    environment: <env>
    status: non_compliant | compliant
    max_severity: CRITICAL | HIGH | MEDIUM | LOW
    non_compliant_policies:
      - policy_name: <name>
        display_name: <human_readable>
        effect: <deny|audit|...>
        severity: CRITICAL | HIGH | MEDIUM | LOW
        affected_resources:
          - resource_id: <id>
            resource_type: <type>
        policy_set: <initiative_name_or_null>
    compliant: <true|false>
```

### Step 6b — Write State File

Serialize the full compliance results to a state file. Phase 3 reads from this file
— it does NOT receive the data through conversation context.

```bash
STATE_PATH="/home/saldave/projects/.vscode/docs/plan/policy-findings.json"
```

Write the following structure:

```json
{
  "meta": {
    "generated": "<ISO timestamp>",
    "rgs_checked": "<n>",
    "rgs_non_compliant": "<n>",
    "rgs_compliant": "<n>",
    "query_mode": "per-rg-sequential"
  },
  "compliance_results": []
}
```

Emit after writing:
```
STATE_FILE_WRITTEN:true
PATH:/home/saldave/projects/.vscode/docs/plan/policy-findings.json
RGS_NON_COMPLIANT:<n>
RGS_COMPLIANT:<n>
```

### Step 7 — Summary Table

Output the human-readable summary table (stays in context for the user to review):

```
=== POLICY COMPLIANCE SUMMARY ===
Subscription: <name>

| RG Name                                  | Env   | Status        | Max Sev | Policies Failed | Repo                          |
|------------------------------------------|-------|---------------|---------|-----------------|-------------------------------|
| BDAIM-D-NA26-FundingCalculation-RGRP     | dev   | NON-COMPLIANT | LOW     | 11              | funding-calculation           |
| BDAIM-P-NA26-FundingCalculation-RGRP     | prod  | NON-COMPLIANT | LOW     | 11              | funding-calculation           |
```

## Error Handling

| Error | Action |
|-------|--------|
| RG not found in Azure | Record as `status: not_found` — may be plan-only or inactive |
| az CLI timeout | Retry once; if fails again, record as `status: scan_error` |
| Subscription access denied | Record as `status: access_restricted`; do NOT stop the scan |
| Empty result (no policies) | Record as `status: no_policies_assigned` |

## Constraints

- DO NOT run `az policy remediation create` — this skill is read-only
- DO NOT skip RGs that return errors — record them as scan gaps
- ALWAYS check `az account show` before running queries
- ALWAYS write `policy-findings.json` before returning — Phase 3 depends on it
- ALWAYS restore the original subscription context after querying prod RGs

## Policy Reference

See [policy-commands.md](./references/policy-commands.md) for all az CLI commands.
