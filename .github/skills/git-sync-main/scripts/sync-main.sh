#!/usr/bin/env bash
# git-sync-main/scripts/sync-main.sh
#
# Syncs a repository to the latest default branch.
# Always switches to the default branch and pulls latest.
# Caller (agent) is responsible for dirty-state checks before invoking.
#
# Usage: sync-main.sh <repo-path>
#
# Output: JSON line for machine parsing, plus human-readable status lines.
#
# Exit codes:
#   0  — success (up-to-date or fast-forwarded)
#   1  — invalid arguments / not a git repo
#   2  — default branch detection failed
#   3  — network / fetch error
#   5  — fast-forward failed (diverged)

set -euo pipefail

# ── Helpers ──────────────────────────────────────────────────────────────────

die() {
  local msg="$1"
  local code="${2:-1}"
  echo "ERROR: ${msg}" >&2
  echo "{\"repo\":\"${REPO_NAME:-unknown}\",\"status\":\"error\",\"message\":\"${msg}\"}"
  exit "${code}"
}

output_result() {
  echo "Repository:  ${REPO_NAME}"
  echo "Previous:    ${ORIGINAL_BRANCH}"
  echo "Branch:      ${CURRENT_BRANCH}"
  echo "Default:     ${DEFAULT_BRANCH}"
  echo "Latest:      ${LATEST_COMMIT}"
  echo "Status:      ${STATUS_ICON} ${STATUS}"
  echo ""
  echo "{\"repo\":\"${REPO_NAME}\",\"previous\":\"${ORIGINAL_BRANCH}\",\"branch\":\"${CURRENT_BRANCH}\",\"default\":\"${DEFAULT_BRANCH}\",\"latest\":\"${LATEST_COMMIT}\",\"status\":\"${STATUS}\"}"
}

# ── Arguments ────────────────────────────────────────────────────────────────

REPO_PATH="${1:?Usage: sync-main.sh <repo-path>}"

if [[ ! -d "${REPO_PATH}/.git" ]]; then
  REPO_NAME="$(basename "${REPO_PATH}")"
  die "'${REPO_PATH}' is not a git repository" 1
fi

cd "${REPO_PATH}"
REPO_NAME="$(basename "${PWD}")"

# ── Detect default branch ───────────────────────────────────────────────────

detect_default_branch() {
  local ref
  ref=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null || true)
  if [[ -n "${ref}" ]]; then
    echo "${ref#refs/remotes/origin/}"
    return
  fi

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

# ── Current branch ───────────────────────────────────────────────────────────

ORIGINAL_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [[ -z "${ORIGINAL_BRANCH}" ]]; then
  ORIGINAL_BRANCH="(detached HEAD)"
fi

# ── Switch to default branch ────────────────────────────────────────────────

if [[ "${ORIGINAL_BRANCH}" != "${DEFAULT_BRANCH}" ]]; then
  git checkout "${DEFAULT_BRANCH}" --quiet
fi
CURRENT_BRANCH="${DEFAULT_BRANCH}"

# ── Fetch ────────────────────────────────────────────────────────────────────

if ! git fetch origin "${DEFAULT_BRANCH}" --prune --quiet 2>/dev/null; then
  die "Fetch failed — check network connectivity and remote configuration" 3
fi

# ── Pull ─────────────────────────────────────────────────────────────────────

LATEST_COMMIT=$(git log --oneline -1 "origin/${DEFAULT_BRANCH}" 2>/dev/null)
HEAD_BEFORE=$(git rev-parse HEAD)

if git pull --ff-only --quiet 2>/dev/null; then
  HEAD_AFTER=$(git rev-parse HEAD)
  if [[ "${HEAD_BEFORE}" == "${HEAD_AFTER}" ]]; then
    STATUS="up-to-date"
    STATUS_ICON="✅"
  else
    STATUS="updated"
    STATUS_ICON="🔄"
  fi
else
  STATUS="diverged"
  STATUS_ICON="⚠️"
  output_result
  exit 5
fi

# ── Output ───────────────────────────────────────────────────────────────────

output_result
