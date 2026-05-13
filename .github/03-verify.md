# 03-verify.md

## Purpose
Checkpoint verification for agent-first workflow.

1. **Execution path verification**
- Verify chosen execution path is explicit: `agent-first` or `fallback`.
- Check: output must contain `EXECUTION_PATH:agent-first|fallback`.

2. **Bootstrap proof**
- For kickoff prompts, verify ticket-first bootstrap occurred before risk classification.
- Check: output must contain both `BOOTSTRAP:ticket-first` and `TICKET_ID:[A-Z]+-[0-9]+`.

3. **Lane contract verification**
- Verify lane type is declared on every response.
- Check: output must contain `LANES:parallel|sequential`.
- When `LANES:parallel`: output must also contain `FANOUT_COMPLETE:true` and `FANIN_DECISION:ready`.

4. **Safety gate verification**
- Verify destructive operations require explicit user confirmation.
- Check: output must contain `DESTRUCTIVE_CONFIRMATION:required|none`.
- If output includes apply/reset/force push: value must be `required`.

5. **Fallback audit rule**
- If `EXECUTION_PATH:fallback`, emit rule rows for G1..G6 and S1..S5.
- Check: exactly 11 rows with `RULE:<id> STATUS:<pass|fail> EVIDENCE:<artifact> REASON:<concise reasoning>`.

6. **Verdict policy**
- Any failed required checkpoint yields `VERDICT:FAIL`.
- Check: `VERDICT:PASS|FAIL|PASS_WITH_WARNINGS` is emitted only when `EXECUTION_PATH:fallback`.
