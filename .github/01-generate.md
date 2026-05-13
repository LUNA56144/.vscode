# 01-generate.md

## Purpose
Execution routing only. Agent-first mode with fallback.

1. **[G1] Primary router**
- If request is infra-related or kickoff prompt (`start`, `begin`, `kickoff`, `run workflow`), invoke `infra-orchestrator` before direct repository edits.
- Check: output must contain `EXECUTION_PATH:agent-first`.

2. **[G2] Bootstrap behavior in agent path**
- The agent must support `start` as a ticket-first bootstrap and derive risk from Jira scope before selecting execution profile.
- Check: output must contain `BOOTSTRAP:ticket-first` and `TICKET_ID:<DEVO-XXXX>` for kickoff prompts.

3. **[G3] Lane contract**
- Declare execution lane type at the start of every response.
- `LANES:parallel` when operating across multiple repos or environments simultaneously; `LANES:sequential` otherwise.
- When `LANES:parallel`: output must also contain `FANOUT_COMPLETE:true` and `FANIN_DECISION:ready` before reporting results.

4. **[G4] Fallback mode**
- If agent invocation is unavailable, run fallback policy from phased files.
- Check: output must contain `EXECUTION_PATH:fallback`.

5. **[G5] High-risk safety gate**
- Regardless of mode, destructive actions require explicit user confirmation.
- Check: output must contain `DESTRUCTIVE_CONFIRMATION:required` whenever action includes apply/reset/force push.
- If no destructive action: emit `DESTRUCTIVE_CONFIRMATION:none`.

6. **[G6] Retry contract**
- Agent or fallback must retry failed steps up to 3 times per error category before escalation.
- Check: `RETRY_COUNT:[0-3]`; when `RETRY_COUNT:3` then `ESCALATE:true`.
