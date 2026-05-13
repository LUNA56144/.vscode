#!/usr/bin/env bash
# git-clean-setup/scripts/clean-setup.sh
#
# Non-interactive script that resets a repository to the latest default branch.
# Intended to be called by the git-clean-setup skill.
#
# Usage: clean-setup.sh <repo-path>
#
# Exit codes:
#   0  — success
#   1  — invalid arguments / not a git repo
#   2  — default branch detection failed
#   3  — network / fetch error
#   4  — reset error

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

die() { echo "ERROR: $*" >&2; exit "${2:-1}"; }

# ── Arguments ────────────────────────────────────────────────────────────────

REPO_PATH="${1:?Usage: clean-setup.sh <repo-path>}"

if [[ ! -d "${REPO_PATH}/.git" ]]; then
  die "'${REPO_PATH}' is not a git repository" 1
fi

cd "${REPO_PATH}"
echo "Repository: $(basename "${PWD}")"
echo "Location:   ${PWD}"

# ── Detect default branch ───────────────────────────────────────────────────

detect_default_branch() {
  # 1. Try symbolic-ref (most reliable when remote HEAD is set)
  local ref
  ref=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -n "${ref}" ]]; then
    echo "${ref#refs/remotes/origin/}"
    return
  fi

  # 2. Fall back to common names
  for candidate in main master; do
    if git show-ref --verify --quiet "refs/remotes/origin/${candidate}" 2>/dev/null; then
      echo "${candidate}"
      return
    fi
  done

  return 1
}

DEFAULT_BRANCH=$(detect_default_branch) \
  || die "Cannot detect default branch. Set it with: git remote set-head origin --auto" 2

echo "Default:    ${DEFAULT_BRANCH}"

# ── Checkout default branch ─────────────────────────────────────────────────

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

if [[ "${CURRENT_BRANCH}" != "${DEFAULT_BRANCH}" ]]; then
  echo "Switching to ${DEFAULT_BRANCH}..."
  git checkout "${DEFAULT_BRANCH}" --quiet
fi

# ── Fetch all remotes and prune ──────────────────────────────────────────────

echo "Fetching all remotes..."
if ! git fetch --all --prune --quiet 2>/dev/null; then
  die "Fetch failed — check network connectivity and remote configuration" 3
fi

# ── Hard reset to origin default ─────────────────────────────────────────────

echo "Resetting to origin/${DEFAULT_BRANCH}..."
if ! git reset --hard "origin/${DEFAULT_BRANCH}" --quiet 2>/dev/null; then
  die "Reset failed" 4
fi

# ── Final status ─────────────────────────────────────────────────────────────

COMMIT=$(git log --oneline -1)
echo ""
echo "Status:     clean"
echo "HEAD:       ${COMMIT}"
echo "Tracking:   origin/${DEFAULT_BRANCH} (up to date)"
