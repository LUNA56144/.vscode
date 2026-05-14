# RG Policy Scan — Azure CLI and MCP Commands

All commands used by the `rg-policy-scan` skill.

## Authentication

```bash
# Check current login and active subscription
az account show --query "{subscription:name,id:id,tenantId:tenantId}" -o json

# List available subscriptions
az account list --query "[].{name:name,id:id,isDefault:isDefault}" -o table
```

## Policy State — Non-Compliant Only

### Full detail per RG
```bash
az policy state list \
  --resource-group "<rg_name>" \
  --filter "complianceState eq 'NonCompliant'" \
  --query "[].{
    policy:policyDefinitionName,
    effect:policyEffect,
    resourceId:resourceId,
    resourceType:resourceType,
    policySet:policySetDefinitionName,
    timestamp:timestamp
  }" \
  --top 200 \
  -o json
```

### Summary count per RG
```bash
az policy state summarize \
  --resource-group "<rg_name>" \
  --query "{
    nonCompliant:results.nonCompliantResources,
    compliant:results.compliantResources,
    total:results.resourceDetails[].count | sum(@)
  }" \
  -o json
```

### Filter by effect type (deny violations only)
```bash
az policy state list \
  --resource-group "<rg_name>" \
  --filter "complianceState eq 'NonCompliant' and policyEffect eq 'deny'" \
  --query "[].{policy:policyDefinitionName,resourceId:resourceId}" \
  -o json
```

## Policy Definition Lookup

### Get display name and description for a policy
```bash
az policy definition show \
  --name "<policyDefinitionName>" \
  --query "{
    displayName:displayName,
    description:description,
    category:metadata.category,
    effect:policyRule.then.effect
  }" \
  -o json 2>/dev/null
```

### List all policy assignments on a RG
```bash
az policy assignment list \
  --resource-group "<rg_name>" \
  --query "[].{name:name,displayName:displayName,policyDefinitionId:policyDefinitionId}" \
  -o json
```

## Remediation

> ⚠️ The rg-policy-scan skill is READ-ONLY. These commands are for reference in ticket descriptions only.

```bash
# Check if a policy supports remediation
az policy remediation list \
  --resource-group "<rg_name>" \
  -o table

# Start remediation (DO NOT run — include in ticket as CLI reference only)
# az policy remediation create \
#   --resource-group "<rg_name>" \
#   --policy-assignment "<assignment_name>" \
#   --name "remediate-<policy>"
```

## Azure MCP Alternative

When the `azure_mcp-policy` tool is available, use it instead of az CLI:

```
tool: azure_mcp-policy
command: policy get-assignments
parameters:
  resource-group: "<rg_name>"
  subscription: "<subscription_id>"
```

## Batch Script — Scan Multiple RGs

```bash
#!/bin/bash
RGS=("rg-im-funding-calc-dev" "rg-im-funding-calc-prod" "rg-im-funding-foundry-dev")

for RG in "${RGS[@]}"; do
  echo "=== Scanning: $RG ==="
  COUNT=$(az policy state list \
    --resource-group "$RG" \
    --filter "complianceState eq 'NonCompliant'" \
    --query "length(@)" \
    -o tsv 2>/dev/null)
  echo "Non-compliant findings: ${COUNT:-ERROR}"
done
```

## Effect Severity Reference

| policyEffect value | Severity | Ticket Priority |
|--------------------|----------|-----------------|
| `deny` | CRITICAL | High |
| `deployIfNotExists` | HIGH | High |
| `modify` | MEDIUM | Medium |
| `audit` | LOW | Low |
| `auditIfNotExists` | LOW | Low |
| `append` | LOW | Low |
| `disabled` | NONE | Skip |
