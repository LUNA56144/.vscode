---
name: rg-jira-bulk
description: "Bulk-create Jira tickets from Azure resource group scan results. Use when: bulk jira tickets, create tickets from rg scan, batch ticket creation, rg audit tickets, funding repo jira bulk, policy non-compliance tickets, remediation tickets, azure policy violations tickets."
---

# RG Jira Bulk — Policy Remediation Ticket Creator

Takes structured YAML from the `rg-policy-scan` skill and creates one Jira remediation ticket
per non-compliant resource group. Uses a single-confirmation bulk-create flow optimized for
audit-driven workloads. Compliant RGs are skipped silently.

## When to Use

- After `rg-policy-scan` has returned compliance findings for multiple RGs
- Creating remediation work items for each non-compliant RG
- Called automatically by `rg-audit-jira` agent in Phase 3

## Input

Compliance YAML from `rg-policy-scan`:

```yaml
compliance_results:
  - rg: rg-im-funding-calculation-dev
    repo: funding-calculation
    environment: dev
    status: non_compliant
    max_severity: CRITICAL
    non_compliant_policies:
      - policy_name: <name>
        display_name: <human_readable>
        effect: deny
        severity: CRITICAL
        affected_resources:
          - resource_id: <id>
            resource_type: <type>
```

## Procedure

### Step 1 — Pre-flight Validation

- Filter input to `status: non_compliant` entries only
- Count tickets to create (1 per non-compliant RG)
- Confirm: Assignee `712020:513de3f5-d046-4711-9c29-323c5005b3f1`, project `DEVO`
- If zero non-compliant RGs → report "All RGs are compliant. No tickets needed." and stop.

### Step 2 — Map Severity to Jira Priority

| Max Severity | Jira Priority |
|-------------|---------------|
| CRITICAL | High |
| HIGH | High |
| MEDIUM | Medium |
| LOW | Low |

### Step 3 — Generate All Ticket Drafts (No Jira Calls)

For EACH non-compliant RG, draft a ticket using the format below.

**Title format**: `Remediate Azure Policy non-compliance in {{<rg_name>}} [<env>]`

**Body template** (Jira wiki markup):

```
h2. Description

The {{<rg_name>}} resource group (owned by {{<repo>}}, environment {{<environment>}}) has
<N> Azure Policy non-compliance finding(s). <max_severity>-severity policies are failing,
which may be blocking resource deployments or leaving required configurations absent.
This work remediates each failing policy to restore compliance and reduce governance risk.

h2. Requirements

* Review and remediate all non-compliant policies listed in the findings table below.
* For {{deny}}-effect policies: identify what is blocking deployment and update resource config or request a policy exception.
* For {{audit}}-effect policies: evaluate whether the finding warrants a config fix or a documented exception.
* For {{deployIfNotExists}} / {{modify}} policies: run the policy remediation task or apply the required configuration.
* Validate remediation by re-running {{az policy state list --resource-group <rg_name> --filter "complianceState eq 'NonCompliant'"}} after changes.
* Confirm zero non-compliant findings before closing this ticket.

[Findings Table]

h2. Acceptance Criteria

# All listed non-compliant policies show {{Compliant}} state in Azure after remediation.
# Any policy exceptions are documented and approved by the platform team.
# The owning Terraform repository ({{<repo>}}) reflects any config changes in a merged PR.
# No new non-compliant findings introduced during remediation.
```

**Findings table format** (Jira wiki table, appended to Requirements):

```
|| Policy Name || Display Name || Effect || Severity || Affected Resources ||
| <policy_name> | <display_name> | {{<effect>}} | 🔴 CRITICAL | <resource_id> (and N more) |
```

Truncate `resource_id` to the first 2 per policy; add "(and N more)" if > 2.

**Chain-of-thought self-score per draft** (0.0–1.0):
- Title includes RG name and env (0.25)
- Findings table is populated with at least one concrete policy name (0.25)
- Acceptance criteria reference the actual RG name (0.25)
- Priority correctly mapped from max_severity (0.25)

Flag any draft with score < 0.90 before the review gate.

### Step 4 — Progressive Disclosure Review

Present ALL drafted tickets to the user in one block:

```
=== BULK REMEDIATION TICKET REVIEW ===
Non-compliant RGs: <n>
Compliant RGs skipped: <n>
Total tickets to create: <n>

--- Ticket 1/<n> — [CRITICAL] rg-im-funding-calculation-dev ---
Repo: funding-calculation | Env: dev | Policies failed: 3

<draft body>

--- Ticket 2/<n> — [MEDIUM] rg-im-funding-foundry-qa ---
...
=== END REVIEW ===
```

Sort tickets by severity descending (CRITICAL first).

### Step 5 — Single Confirmation Gate

> "Ready to create <n> remediation tickets in DEVO assigned to sandro.aldave@wtwco.com.
> Confirm? (yes / no / edit <number>)"

If "edit <n>": update that draft and re-display the full block.
Accept only "yes", "confirmed", "create them", or "proceed".

### Step 6 — Sequential Ticket Creation

Create one ticket at a time via Atlassian MCP:

```
tool: createJiraIssue
cloudId: https://viabenefits.atlassian.net
projectKey: DEVO
issueTypeName: Task
summary: <title>
description: <body>
contentFormat: markdown
assignee_account_id: 712020:513de3f5-d046-4711-9c29-323c5005b3f1
additional_fields:
  priority: { name: "<High|Medium|Low>" }
  customfield_10811: { id: "10811" }
```

After each:
- `✅ Created DEVO-XXXX: <title>` on success
- Apply Clone-Then-Detach fallback from `jira-ticket` skill on failure

### Step 7 — Final Summary

```
=== REMEDIATION TICKETS CREATED ===
│ DEVO-XXXX │ rg-im-funding-calculation-dev  │ CRITICAL │ ✅ Created │
│ DEVO-XXXX │ rg-im-funding-foundry-qa       │ MEDIUM   │ ✅ Created │
│ —         │ rg-im-funding-eligibility-prod │ COMPLIANT│ ⏭ Skipped │
Tickets created: <n> | Skipped (compliant): <n>
```

## Constraints

- DO NOT create tickets for compliant RGs
- DO NOT call Jira create tools during Step 3 (draft generation)
- DO NOT skip the confirmation gate
- ALWAYS include the findings table in the ticket body
- ALWAYS set priority based on max_severity mapping
- ALWAYS reference the owning repo in the ticket body

## Fallback

If Jira creation is blocked by required custom fields, apply Clone-Then-Detach
from the `jira-ticket` skill: find a recent DEVO Task assigned to sandro, clone it,
replace all content with the approved draft, clear inherited metadata.
