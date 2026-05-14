---
name: rg-policy-scan
description: "Query Azure Policy compliance state for a list of resource groups. Use when: check policy compliance, find non-compliant resources, azure policy violations, policy state per rg, audit policy findings, non-compliant azure resources, policy remediation data."
---

# RG Policy Scan — Azure Policy Compliance Checker

Queries Azure Policy compliance state for a list of resource group names and returns
structured non-compliance findings: which policies failed, which resources are affected,
and what effect type each policy enforces.

## When to Use

- After `rg-scanner` has produced a list of RG names
- Checking compliance status before creating remediation tickets
- Called automatically by `rg-audit-jira` agent in Phase 2

## Input

A list of RG entries with their owning repo and environment context:

```yaml
rgs:
  - name: rg-im-funding-calculation-dev
    repo: funding-calculation
    environment: dev
  - name: rg-im-funding-foundry-prod
    repo: hra-foundry
    environment: prod
```

## Procedure

### Step 1 — Verify Azure CLI Login

```bash
az account show --query "{subscription:name,id:id}" -o json
```

If this fails, stop and report: "Azure CLI not authenticated — run `az login` first."

### Step 2 — Query Non-Compliant State Per RG

For each RG, run the compliance state query. See [policy-commands.md](./references/policy-commands.md) for all commands.

Primary command:

```bash
az policy state list \
  --resource-group "<rg_name>" \
  --filter "complianceState eq 'NonCompliant'" \
  --query "[].{
    policy:policyDefinitionName,
    policyDisplayName:policyDefinitionAction,
    effect:policyEffect,
    resourceId:resourceId,
    resourceType:resourceType,
    policySet:policySetDefinitionName,
    timestamp:timestamp
  }" \
  -o json
```

**ReAct per RG:**
- **Reason**: "How many non-compliant findings? Are any `deny` effect — meaning active resource deployment is being blocked?"
- **Act**: Collect and structure the raw output
- **Reflect**: Are the affected resources tied to resources managed by the owning repo?

### Step 3 — Classify by Severity

Map `policyEffect` to severity:

| Effect | Severity | Meaning |
|--------|----------|---------|
| `deny` | 🔴 CRITICAL | Resource creation/update is actively blocked |
| `deployIfNotExists` | 🟠 HIGH | Required configuration not deployed |
| `modify` | 🟡 MEDIUM | Resource property needs correction |
| `audit` / `auditIfNotExists` | 🟢 LOW | Logged but not blocked |
| `append` | 🟢 LOW | Missing tag or property |

### Step 4 — Deduplicate and Group

For each RG:
1. Group findings by `policyDefinitionName`
2. Deduplicate `resourceId` entries under each policy
3. Identify the maximum severity in the RG (for ticket priority)

### Step 5 — Get Policy Display Details (Optional Enrichment)

For each unique policy definition found, retrieve a human-readable description:

```bash
az policy definition show \
  --name "<policyDefinitionName>" \
  --query "{displayName:displayName,description:description,category:metadata.category}" \
  -o json 2>/dev/null || echo "builtin_or_custom"
```

Use this to populate the "Policy Description" column in output.

### Step 6 — Structured Output

Return findings as YAML:

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

### Step 7 — Summary Table

Before returning, output a human-readable summary:

```
=== POLICY COMPLIANCE SUMMARY ===
Subscription: <name>

| RG Name                        | Env  | Status          | Max Severity | Policies Failed | Repo                    |
|--------------------------------|------|-----------------|-------------|-----------------|-------------------------|
| rg-im-funding-calculation-dev  | dev  | NON-COMPLIANT   | 🔴 CRITICAL  | 3               | funding-calculation     |
| rg-im-funding-foundry-prod     | prod | COMPLIANT       | —           | 0               | hra-foundry             |
```

## Error Handling

| Error | Action |
|-------|--------|
| RG not found in Azure | Record as `status: not_found` — may be a plan-only repo |
| az CLI timeout | Retry once with `--top 100`; if fails again, record as `status: scan_error` |
| Subscription access denied | Stop and report subscription context |
| Empty result (no policies) | Record as `status: no_policies_assigned` |

## Constraints

- DO NOT run `az policy remediation create` — this skill is read-only
- DO NOT skip RGs that return errors — record them as scan gaps
- ALWAYS check `az account show` before running queries
- If output exceeds 200 resources, truncate to top 20 by severity and note the count

## Policy Reference

See [policy-commands.md](./references/policy-commands.md) for all az CLI and
Azure MCP commands used in this skill.
