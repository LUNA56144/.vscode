---
name: pr-deprecated-comments
description: >-
  Reply to and resolve only deprecated or outdated PR review threads.
  Use when user asks to speedline/clean up stale Copilot comments without
  changing code. Skip active threads for manual review.
---

# PR Deprecated Comments Cleanup

Use this when the goal is simple: close review threads that are no longer valid.

## Scope

This skill handles only deprecated threads. It does not change any source files.

## Detection Rules

Mark a thread as deprecated when either condition is true:
- `is_outdated` is `true`
- The commented file path no longer exists on the current branch

If neither condition is true, skip the thread.

## Workflow

1. Load unresolved review threads for the active pull request.
   - Use `perPage: 100` and paginate through **all pages** until no more results are returned.
   - Do not stop after the first page — unresolved threads may appear on later pages.
2. Classify each thread using the two detection rules above.
3. For each deprecated thread:
   - Reply with a short note:
     - `Deprecated - this comment is no longer valid in the current branch.`
   - Resolve the thread.
4. Leave all non-deprecated threads unresolved for manual review.
5. Report totals: resolved deprecated threads, skipped active threads.

## Tone

Keep replies short, human, and direct. One sentence is enough.

## Safety

- Do not make code changes.
- Do not resolve active/non-deprecated threads.
- If thread status is unclear, skip it and report it for manual review.
