---
name: jira-ticket
description: "Generate a Jira-formatted ticket ready to paste into Jira. Use when: create jira ticket, write jira story, jira task, jira format, ticket for this work."
---

# Jira Ticket Generator

Generate a Jira ticket from the work described in the conversation or any provided context (PR link, summary, feature description).

## Output Format

Output the title as a plain bold line, then the body using Jira wiki markup:

**Title:** <concise summary of the work>

```
h2. Description

<2–4 sentences. Context first — what's the problem or situation — then what's being done about it. Natural tone, no jargon.>

h2. Requirements

* <requirement>
* <use {{inline code}} for resource names, module names, env identifiers, CLI commands>

h2. Acceptance Criteria

# <verifiable outcome — not a task, but a state that can be checked>
# <criterion>
```

## Rules

- `h2.` for all section headings
- `*` bullet list for Requirements
- `#` numbered list for Acceptance Criteria  
- `{{name}}` for inline code (Jira wiki syntax — not backticks)
- If a PR link is available, add it in Description: `*PR:* [<title>|<url>]`
- No dividers, no sub-headings inside sections
- Keep the whole ticket under 25 lines
- Concise and human — avoid over-listing, write like a person not a robot
