---
name: rg-jira-bulk
description: "Bulk-create Jira tickets from Azure resource group scan results. Use when: bulk jira tickets, create tickets from rg scan, batch ticket creation, rg audit tickets, funding repo jira bulk."
---

# RG Jira Bulk — Batch Ticket Creator

Takes structured YAML output from the `rg-scanner` skill and creates one Jira ticket
per repository in a single reviewed batch. Reuses the `jira-ticket` skill's output
contract and quality checks, but optimizes for bulk creation with a single user confirmation.

## When to Use

- After `rg-scanner` has produced findings for multiple repos
- When creating more than 2 Jira tickets from the same audit run
- Called automatically by the `rg-audit-jira` agent in Phase 3

## Input

Aggregated YAML from `rg-scanner`, e.g.:

```yaml
findings:
  - repo: funding-calculation
    environments:
      - name: dev
        resource_groups: [...]
  - repo: hra-foundry
    ...
```

## Procedure

### Step 1 — Pre-flight Validation

Before drafting tickets, verify:
- Input contains at least one repo with at least one RG name
- Assignee account ID is known: `712020:513de3f5-d046-4711-9c29-323c5005b3f1`
- Jira project is `DEVO`
- Primary Work Source custom field: `Azure` (option ID `10811`)

**Confidence gate**: If assignee cannot be resolved, stop and ask before continuing.

### Step 2 — Generate All Drafts (No Jira Calls)

For EACH repo in the findings, draft a ticket following the `jira-ticket` output contract:

**Title format**: `Document Azure resource groups in <repo-name>`

**Body template** (Jira wiki markup):

```
h2. Description

The {{<repo-name>}} repository references Azure resource groups that are not centrally
documented. This audit captures all resource group names used across all environments,
enabling governance, cost tracking, and naming compliance review. The data was extracted
via automated Terraform scan as part of the cross-repo RG audit initiative.

h2. Requirements

* Document all resource group names found per environment (see findings below).
* Verify each RG name follows the {{rg-im-<domain>-<service>-<env>}} naming convention.
* Flag and create follow-up tasks for any RG names that deviate from the standard.
* Validate RG names against Azure portal to confirm they exist and are active.

[Environment findings table — populated from scan output]

h2. Acceptance Criteria

# All resource group names for {{<repo-name>}} are documented per environment.
# Naming convention deviations are identified and linked to a follow-up ticket.
# Ticket is accepted by sandro.aldave@wtwco.com as accurate and complete.
```

**Findings table format** (append to Requirements section):

```
|| Environment || Resource Group Name || Source Type || Source File ||
| dev | rg-im-funding-calc-dev | direct | main.tf:12 |
| prod | rg-im-funding-calc-prod | variable → tfvars | terraform.tfvars:3 |
```

### Step 3 — Progressive Disclosure Review

Present ALL drafted tickets to the user in a single block:

```
=== BULK TICKET REVIEW ===
Total tickets: <n>
Repos covered: <list>

--- Ticket 1/<n> ---
<draft content>

--- Ticket 2/<n> ---
<draft content>
...
=== END REVIEW ===
```

**Self-score** (chain-of-thought) each draft:
- Title is action-oriented (0.25)
- Findings table is populated with concrete values (0.25)
- Acceptance criteria are verifiable (0.25)
- Assignee is confirmed (0.25)

Flag any draft with score < 0.90 for user attention before asking for confirmation.

### Step 4 — Single Confirmation Gate

Ask exactly once:

> "Ready to create <n> Jira tickets in DEVO, all assigned to sandro.aldave@wtwco.com.
> Confirm? (yes / no / edit <ticket_number>)"

If user says "edit <n>", update that draft and re-present the full block.
Accept only "yes", "confirmed", or "create them" as full approval.

### Step 5 — Sequential Ticket Creation

After confirmation, create tickets one at a time using the Atlassian MCP:

```
tool: createJiraIssue
cloudId: https://viabenefits.atlassian.net
projectKey: DEVO
issueTypeName: Task
summary: <title>
description: <body>
assignee_account_id: 712020:513de3f5-d046-4711-9c29-323c5005b3f1
additional_fields:
  customfield_10811: { id: "10811" }
```

After each ticket is created:
- Report: `✅ Created DEVO-XXXX: <title>`
- If creation fails, apply the Clone-Then-Detach fallback from the `jira-ticket` skill

### Step 6 — Final Summary

After all tickets are created, output:

```
=== BULK CREATION COMPLETE ===
Tickets created: <n>/<n>
│ DEVO-XXXX │ funding-calculation     │ ✅ Created │
│ DEVO-XXXX │ hra-foundry             │ ✅ Created │
│ ...       │ ...                     │ ...       │
```

## Constraints

- DO NOT call Jira create tools during draft generation (Step 2)
- DO NOT create tickets for repos with zero RG names — log as skipped
- DO NOT skip the confirmation gate even if user previously said "proceed"
- ALWAYS include the findings table in the ticket body
- ALWAYS use `contentFormat: markdown` for descriptions

## Fallback

If Jira ticket creation is blocked due to required custom fields, apply the
Clone-Then-Detach procedure from the `jira-ticket` skill:
1. Find a recent DEVO Task assigned to sandro as clone source
2. Update all fields with the new draft content
3. Clear inherited metadata that doesn't apply
