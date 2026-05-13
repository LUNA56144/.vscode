---
name: jira-ticket
description: "Create a standard Jira ticket in a natural human tone with deterministic structure. Use for: create jira ticket, write jira story/task/bug, jira format, ticket for this work."
---

# Jira Ticket Writer

Create a Jira-ready ticket from the conversation context (problem, change request, PR, or summary).

## When To Use

Use this skill when the user asks to:
- create a Jira ticket
- write a Jira story, task, or bug
- format work into Jira-ready text

Do not use this skill for implementation, code changes, or deployment steps.

## Workspace Defaults

- Default Primary Work Source: Azure
- Default Primary Work Source option ID: 10811
- Default Primary Work Source option ID: 10811
- Unless the user explicitly requests otherwise, always draft and create tickets in project DEVO and assign to the default assignee.
- Use default Primary Work Source {{Azure}} (option ID {{10811}}) by default unless the user explicitly requests otherwise.

1. Verify Target Exists
- Confirm the referenced repository/component/environment exists in available workspace/repo context.
- If ambiguous, list likely matches and ask the user to choose one.
- Do not continue until a single target is confirmed.

2. Source-Relevant Research
- Gather only sources relevant to the request (for example: target repo files, version/config declarations, related PR/issue context, and environment-specific constraints).
- Do not use generic assumptions when concrete source evidence exists.
- Summarize feasibility findings in 3-6 bullets before ticket creation.

3. Task-Type Internet Reference Check
- Run an external, authoritative reference check for best practices and upgrade guidance when it adds value to the ticket.
- Always ground the ticket in workspace evidence first, then refine with external sources.
- Use 1-3 high-quality references, selected by task type:
	- Infrastructure/Terraform: HashiCorp docs, Terraform provider docs, cloud vendor docs.
	- Azure/Microsoft stack: Microsoft Learn, Azure docs, official SDK docs.
	- Library/framework upgrade: official changelog, migration guide, release notes.
	- Security-sensitive changes: vendor advisories and CVE references.
- Avoid blog-only guidance unless no authoritative source exists.
- Capture source-backed refinements in requirements or acceptance criteria (not as generic prose).

4. Draft Preview Gate (No Jira Changes)
- Generate and return the Jira ticket draft using the deterministic output contract below.
- Present the draft to the user for review before any Jira create/update operation.
- Do not call Jira mutation tools in the same response as the first draft unless the user already gave explicit approval after seeing the draft.

5. Explicit User Confirmation (Post-Draft)
- Ask for explicit approval immediately after draft preview and immediately before Jira creation.
- Required confirmation payload: target repo/component, ticket intent, and assignee.
- Accept only clear consent (for example: "yes create it", "confirmed", "proceed").
- If confirmation is missing or unclear, stop and ask again.

6. Create Jira Ticket
- Only after step 5 succeeds, create the issue using the approved draft content.
- Use project key DEVO by default unless the user explicitly requests a different project.
- Use default assignee account ID {{712020:513de3f5-d046-4711-9c29-323c5005b3f1}} for Jira assignment by default.
- Use default Primary Work Source {{Azure}} (option ID {{10811}}) by default unless the user explicitly requests otherwise.
- If assignee cannot be resolved to an account ID, ask for account ID before creation.

7. Fallback: Clone-Then-Detach (When Create Is Blocked)
- Trigger this fallback only when Jira creation fails because required custom fields cannot be set via available mutation tools.
- Find one recent issue assigned to the target assignee in project DEVO (same issue type when possible) and use it as the clone source.
- Clone from that issue, then detach prior-context fields before finalizing:
	- Replace summary and description with the approved draft.
	- Clear or update stale links/references (old PR, old repo/component, old environment, old date).
	- Remove inherited labels/components/fix versions that do not apply.
	- Confirm assignee remains the approved assignee.
	- Keep required custom fields populated from the clone only when still valid for the new work; otherwise set correct values.
- If available tools cannot perform clone or required-field updates, stop and return a precise blocker plus a one-step UI workaround:
	- Clone source issue key
	- Required field values to set
	- Exact title/body to paste

7. Fallback: Clone-Then-Detach (When Create Is Blocked)
- Trigger this fallback only when Jira creation fails because required custom fields cannot be set via available mutation tools.
- Find one recent issue assigned to the target assignee in project DEVO (same issue type when possible) and use it as the clone source.
- Clone from that issue, then detach prior-context fields before finalizing:
	- Replace summary and description with the approved draft.
	- Clear or update stale links/references (old PR, old repo/component, old environment, old date).
	- Remove inherited labels/components/fix versions that do not apply.
	- Confirm assignee remains the approved assignee.
	- Keep required custom fields populated from the clone only when still valid for the new work; otherwise set correct values.
- If available tools cannot perform clone or required-field updates, stop and return a precise blocker plus a one-step UI workaround:
	- Clone source issue key
	- Required field values to set
	- Exact title/body to paste

## Continuous Learning Loop (Deterministic)

To improve accuracy and self-reliance as sessions progress, apply this loop on every ticket request:

1. Reuse Prior Learning
- Check existing session and repository memory notes for previous Jira ticket patterns, failures, and corrections.
- Reuse proven patterns first (title style, requirement wording, acceptance criteria phrasing, assignee handling).

2. Evidence-First Drafting
- Build ticket content only from verified inputs: user request, target repo context, source-relevant research, and task-type external references (when relevant).
- Do not infer missing technical details when the source can be queried.

3. Self-Score Accuracy
- Score confidence from 0.0 to 1.0 using these weighted checks:
	- target confirmed (0.30)
	- source-relevant research completed (0.30)
	- user confirmation captured (0.20)
	- assignee resolvable (0.20)
- If score is below 0.90, ask only the minimum missing question(s) before creating the ticket.

4. Record Outcome
- After drafting/creating, record concise lessons learned (what was missing, what improved accuracy, what to reuse next time).
- Favor updating existing memory notes over creating new files.

## Self-Reliance Rules

- Default to resolving ambiguities using available workspace/repo context before asking the user.
- Ask user questions only when a required field cannot be verified from relevant sources.
- Never skip preflight, confirmation, or quality checks for speed.

## Deterministic Output Contract

Always output exactly this order:

1. A single bold title line
2. A Jira wiki body with exactly three sections:
- `h2. Description`
- `h2. Requirements`
- `h2. Acceptance Criteria`

Use this exact template:

**Title:** <concise summary of the work>

```
h2. Description

<2-4 sentences in natural tone. First answer WHY this work is needed (problem, risk, or opportunity). Then answer WHAT will change (scope and expected impact). Write like a teammate, not a spec generator.>

h2. Requirements

* <specific requirement>
* <specific requirement>

h2. Acceptance Criteria

# <verifiable outcome/state>
# <criterion>
```

## Writing Rules (Must Follow)

- `h2.` for all section headings
- `*` bullet list for Requirements
- `#` numbered list for Acceptance Criteria
- Use `{{name}}` for inline code (resource names, envs, commands, modules)
- If a PR link exists, include it in Description as: `*PR:* [<title>|<url>]`
- No dividers, no sub-headings inside sections
- Keep the full ticket concise (target 15-30 lines)
- Prefer plain language over jargon
- Avoid placeholders in final output when concrete details are known
- Description must explicitly answer both: `Why now?` and `What is changing?`

## Quality Checks

Before returning the ticket, verify:
- Title is specific and action-oriented
- Description clearly answers both why this work matters and what is changing
- Requirements are concrete and implementation-relevant
- Acceptance criteria are testable outcomes, not tasks
- Target existence was validated against relevant source context
- Feasibility research is based on task-relevant sources and reflected in ticket requirements
- Task-type external references were checked when relevant and used to refine ticket quality
- Draft was shown to the user before any Jira create/update operation
- Explicit user confirmation to create Jira was obtained immediately before creation
- Accuracy self-score is >= 0.90 before Jira creation
- Missing fields were handled with minimal, targeted clarifications only
- Default board/project and default assignee behavior were applied unless explicitly overridden by the user
- If fallback clone path was used, inherited ticket metadata was detached and revalidated
- If fallback clone path was used, inherited ticket metadata was detached and revalidated

## Example

**Title:** Upgrade Terraform providers in client-implementations-infra with source-backed validation

```
h2. Description

The {{client-implementations-infra}} environments currently pin provider versions that should be reviewed and upgraded to reduce maintenance risk and keep deployments aligned with current supported behavior. This work updates provider constraints and validates each impacted environment to prevent drift and avoid upgrade surprises. Changes are refined using authoritative upgrade references from Terraform and provider documentation.

h2. Requirements

* Update provider constraints in impacted {{versions.tf}} files for {{qa}}, {{stage}}, and {{prod-secondary}}.
* Validate upgrade impact against [Terraform Provider Requirements|https://developer.hashicorp.com/terraform/language/providers/requirements] and [AzureRM Provider Version History|https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/version-history].
* Run {{terraform init -backend=false}}, {{terraform validate}}, and {{terraform fmt -check -recursive}} in each impacted environment.
* Ensure no hardcoded subscription IDs or secrets are introduced during provider updates.

h2. Acceptance Criteria

# Provider constraints are updated consistently across all impacted environments.
# Validation commands succeed in each impacted environment with no unexpected destructive plan changes.
# Ticket requirements and acceptance criteria reference authoritative upgrade guidance used during refinement.
```
