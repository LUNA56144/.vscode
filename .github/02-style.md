# 02-style.md

## Purpose
Response formatting for agent-first workflow.

1. **[S1] Compact default**
- Default response uses `RESULT`, `NEXT` sections only.
- Use full `CONTEXT`, `ACTION`, `RESULT`, `NEXT` only for high-risk operations.
- Check: section order must match selected verbosity mode.

2. **[S2] Command logging**
- Emit `CMD:` lines only when commands materially affect state.
- Check regex: `^CMD:\s.+` for each emitted command line.

3. **[S3] No vague quality terms**
- Ban these terms unless a measurable metric appears in the same sentence: `clean`, `efficient`, `robust`, `scalable`, `better`.
- Check: banned term must co-occur with one of `<=`, `>=`, `%`, `ms`, `count`, `regex`, `pass/fail`.

4. **[S4] Path policy**
- Every referenced workspace path must be absolute or workspace-relative and must exist before linking.
- Check: path starts with `/home/saldave/projects/` or approved workspace-relative root, plus existence check.

5. **[S5] Change summary format**
- If files were edited, emit one line per file: `FILE:<path> STATUS:<created|updated|deleted> CHECK:<pass|fail>`.
- If no files were edited, emit `CHANGES:none`.
- Check: either file-line regex or `^CHANGES:none$`.
