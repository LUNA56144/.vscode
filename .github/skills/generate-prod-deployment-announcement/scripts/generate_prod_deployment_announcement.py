#!/usr/bin/env python3
"""
Production Deployment Announcement Generator

Generates Teams markdown announcements for production infrastructure deployments
across all Funding repositories by comparing git tags and workflow runs.
"""

import subprocess
import sys
import os
import signal
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# Debug/verbose flag (set via --verbose or --debug)
VERBOSE = False

def debug(msg):
    if VERBOSE:
        print(f"  [debug] {msg}")

# Define all 10 funding repositories
REPOS = [
    "im-funding/client-data-azure-infrastructure",
    "im-funding/client-guides-infrastructure",
    "im-funding/client-implementations-infra",
    "im-funding/funding-calculation",
    "im-funding/funding-communication-infrastructure",
    "im-funding/funding-data-transfer-infrastructure",
    "im-funding/funding-reimbursement-infrastructure",
    "im-funding/funding-eligibility-infrastructure",
    "im-funding/funding-enrollment-support-infrastructure",
    "im-funding/funding-qualification-infrastructure",
]

def run_gh_command(cmd, timeout=30, retries=3):
    """Run a GitHub CLI command and return output, with retry logic.

    Uses start_new_session=True so the spawned shell gets its own process group,
    allowing os.killpg to reliably terminate the entire process tree on timeout.
    """
    for attempt in range(1, retries + 1):
        proc = None
        try:
            debug(f"Running (attempt {attempt}/{retries}): {cmd[:120]}")
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, start_new_session=True,
            )
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                if proc.returncode == 0:
                    return stdout.strip()
                debug(f"Non-zero exit {proc.returncode}: {stderr.strip()[:120]}")
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
                debug(f"Timeout after {timeout}s on attempt {attempt}")
        except Exception as e:
            debug(f"Error: {e}")
            if proc is not None:
                try:
                    proc.kill()
                    proc.wait()
                except Exception:
                    pass
        if attempt < retries:
            time.sleep(1 * attempt)
    return None

def check_gh_auth():
    """Verify GitHub CLI is authenticated"""
    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
    return result.returncode == 0

def get_last_deployed_version(repo, environment='prod'):
    """Find the last successful deployment version for given environment using API"""
    # Get the Apply Terraform workflow ID
    cmd = f'gh api repos/{repo}/actions/workflows --jq \'.workflows[] | select(.name == "Apply Terraform") | .id\' 2>/dev/null | head -1'
    workflow_id = run_gh_command(cmd)

    if not workflow_id:
        debug(f"No 'Apply Terraform' workflow found for {repo}")
        return None

    # Validate workflow_id is a numeric string before shell interpolation
    if not re.fullmatch(r'\d+', workflow_id):
        debug(f"Unexpected workflow_id format for {repo}: {workflow_id!r}")
        return None

    debug(f"Workflow ID for {repo}: {workflow_id}")

    # Fetch last 30 successful runs only — no --paginate to avoid stalling
    cmd = (
        f'gh api "repos/{repo}/actions/workflows/{workflow_id}/runs'
        f'?status=success&per_page=30" '
        f'--jq \'.workflow_runs[] | {{name: .name, created: .created_at}}\' 2>/dev/null'
    )
    output = run_gh_command(cmd, timeout=30)

    if not output:
        debug(f"No workflow run output for {repo} env={environment}")
        return None

    # Parse JSON output and look for environment deployments
    import json
    for line in output.split('\n'):
        if not line.strip():
            continue
        try:
            run_data = json.loads(line)
            run_name = run_data.get('name', '')

            # Match various environment patterns:
            # - "Apply prod terraform from v1.2.3"
            # - "Apply Terraform (prod) [v1.2.3]"
            # - "Apply stage terraform from v1.2.3"
            # - "Apply Terraform (stage) [v1.2.3]"
            # Exclude prod-secondary and stage-secondary
            env_pattern = rf'\b{environment}\b'
            secondary_pattern = rf'\b{environment}-secondary\b'

            if re.search(env_pattern, run_name, re.IGNORECASE) and not re.search(secondary_pattern, run_name, re.IGNORECASE):
                match = re.search(r'v\d+\.\d+\.\d+', run_name)
                if match:
                    return match.group(0)
        except json.JSONDecodeError:
            continue

    return None

def get_all_version_tags(repo):
    """Fetch all version tags and their commit SHAs from repository.

    Returns (tags_list, sha_cache) where sha_cache maps tag name → commit SHA.
    The SHA cache eliminates a round-trip in get_commit_message.
    """
    import json
    cmd = (
        f'gh api "repos/{repo}/tags?per_page=100" --paginate '
        f'--jq \'.[] | select(.name | test("^v[0-9]+\\\\.[0-9]+\\\\.[0-9]+$")) '
        f'| {{name: .name, sha: .commit.sha}}\' 2>/dev/null'
    )
    output = run_gh_command(cmd, timeout=60)

    if not output:
        return [], {}

    tags = []
    sha_cache = {}
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            name = data.get('name', '')
            sha = data.get('sha', '')
            if name:
                tags.append(name)
                if sha:
                    sha_cache[name] = sha
        except json.JSONDecodeError:
            continue
    return tags, sha_cache

def get_commit_message(repo, tag, sha_cache=None):
    """Get commit message for a specific tag.

    Uses sha_cache (from get_all_version_tags) when available to skip the
    first API call that resolves the tag to a SHA.
    """
    sha = sha_cache.get(tag) if sha_cache else None

    if not sha:
        cmd = f'gh api repos/{repo}/git/refs/tags/{tag} --jq ".object.sha" 2>/dev/null'
        sha = run_gh_command(cmd)

    if not sha:
        cmd = f'gh api repos/{repo}/tags --jq \'.[] | select(.name=="{tag}") | .commit.sha\' 2>/dev/null'
        sha = run_gh_command(cmd)

    if sha:
        # Validate sha is a hex string before shell interpolation
        if not re.fullmatch(r'[0-9a-fA-F]{7,64}', sha):
            debug(f"Unexpected SHA format for {repo} {tag}: {sha!r}")
            return ""
        cmd = f'gh api repos/{repo}/commits/{sha} --jq ".commit.message" 2>/dev/null'
        message = run_gh_command(cmd)
        return message if message else ""
    return ""

def extract_pr_title(commit_message):
    """Extract PR title from commit message"""
    if not commit_message:
        return None

    lines = commit_message.split('\n')

    # Handle "Merge pull request #123" format
    if len(lines) > 1 and 'Merge pull request' in lines[0]:
        for i, line in enumerate(lines):
            if i > 0 and line.strip():
                return line.strip()

    # Handle direct PR title format: "Title (#123)"
    # Extract first line and remove PR number
    first_line = lines[0].strip()
    if first_line:
        # Remove PR number pattern like "(#123)" from the end
        title = re.sub(r'\s*\(#\d+\)\s*$', '', first_line)
        return title if title else None

    return None

def format_date(date_str):
    """Convert YYYY-MM-DD to 'Day, MM/DD/YY' format"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    day_name = date_obj.strftime('%A')
    formatted = date_obj.strftime('%m/%d/%y')
    return f"{day_name}, {formatted}"

def format_time(time_str):
    """Convert HH:MM (24-hour) to H:MM P.M./A.M. MT format"""
    time_obj = datetime.strptime(time_str, '%H:%M')
    hour = time_obj.hour
    minute = time_obj.minute

    if hour == 0:
        return f"12:{minute:02d} A.M. MT"
    elif hour < 12:
        return f"{hour}:{minute:02d} A.M. MT"
    elif hour == 12:
        return f"12:{minute:02d} P.M. MT"
    else:
        return f"{hour-12}:{minute:02d} P.M. MT"

def parse_version(version_str):
    """Parse semantic version string into tuple of integers for comparison"""
    try:
        # Remove 'v' prefix and split by '.'
        clean_version = version_str.lstrip('v')
        parts = clean_version.split('.')
        return tuple(int(part) for part in parts)
    except (ValueError, AttributeError):
        return None

def is_deployed_to_stage(version_str, last_stage_version):
    """Check if a version has been deployed to stage"""
    if last_stage_version is None:
        return False

    try:
        v_current = parse_version(version_str)
        v_stage = parse_version(last_stage_version)

        if v_current is None or v_stage is None:
            print(f"  ⚠️  Warning: Could not parse version {version_str}")
            return False

        # Compare tuples (major, minor, patch)
        return v_current <= v_stage
    except Exception as e:
        # If version parsing fails, treat as blocked
        print(f"  ⚠️  Warning: Could not parse version {version_str}: {e}")
        return False

def scan_repositories():
    """Scan all repositories for undeployed versions and validate stage deployment"""
    print("🔍 Scanning funding repositories for undeployed versions...\n")

    deployment_data = {}
    blocked_data = {}
    warnings = []
    stage_missing = []

    for repo in REPOS:
        repo_name = repo.split('/')[-1]
        print(f"📦 Checking {repo_name}...")

        last_prod = get_last_deployed_version(repo, 'prod')

        if not last_prod:
            print(f"  ⚠️  Unable to determine prod deployment status")
            warnings.append(repo_name)
            print()
            continue

        print(f"  ✓ Last prod deployment: {last_prod}")

        # Get last stage deployment
        last_stage = get_last_deployed_version(repo, 'stage')

        if not last_stage:
            print(f"  ⚠️  No stage deployment history found")
            stage_missing.append(repo_name)
        else:
            print(f"  ✓ Last stage deployment: {last_stage}")

        all_tags, sha_cache = get_all_version_tags(repo)

        if not all_tags:
            print("  No version tags found")
            print()
            continue

        # Get undeployed versions (newer than last prod)
        undeployed = []
        for tag in all_tags:
            if tag == last_prod:
                break
            undeployed.append(tag)

        if not undeployed:
            print("  ✓ No undeployed versions")
            print()
            continue

        # Split into ready (deployed to stage) and blocked (not in stage)
        ready_for_prod = []
        blocked_versions = []

        for ver in undeployed:
            if is_deployed_to_stage(ver, last_stage):
                ready_for_prod.append(ver)
            else:
                blocked_versions.append(ver)

        if ready_for_prod:
            print(f"  ✅ Found {len(ready_for_prod)} version(s) ready for prod (stage-validated)")
            deployment_data[repo] = {"versions": ready_for_prod, "sha_cache": sha_cache}

        if blocked_versions:
            print(f"  ⚠️  Found {len(blocked_versions)} version(s) blocked (not in stage)")
            blocked_data[repo] = blocked_versions

        print()

    return deployment_data, blocked_data, warnings, stage_missing

def fetch_pr_titles(deployment_data):
    """Fetch PR titles for all undeployed versions in parallel."""
    print("🔍 Fetching PR titles for undeployed versions...\n")

    version_details = {}

    def _fetch_one(repo, version, sha_cache):
        commit_msg = get_commit_message(repo, version, sha_cache)
        return extract_pr_title(commit_msg)

    for repo, data in deployment_data.items():
        repo_name = repo.split('/')[-1]
        versions = data["versions"][:10]
        sha_cache = data.get("sha_cache", {})
        print(f"  {repo_name}: {len(versions)} versions")
        version_details[repo_name] = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(_fetch_one, repo, ver, sha_cache): ver
                for ver in versions
            }
            for future in as_completed(futures):
                ver = futures[future]
                try:
                    version_details[repo_name][ver] = future.result()
                except Exception:
                    version_details[repo_name][ver] = None

        # Preserve original version order
        version_details[repo_name] = {
            ver: version_details[repo_name].get(ver)
            for ver in versions
        }

    print()
    return version_details

def generate_announcement(version_details, blocked_details, warnings, stage_missing, deployment_date, deployment_time):
    """Generate Teams markdown announcement"""
    formatted_date = format_date(deployment_date)
    formatted_time = format_time(deployment_time)

    sorted_repos = sorted(version_details.keys())

    announcement = f"""🚨 Infrastructure Production Deployment Announcement - {formatted_date} 🚨

Hi team,

A production infrastructure deployment is scheduled for {formatted_date}, at {formatted_time}. This release includes updates that have been validated across the Dev, QA, and Stage environments.

What's Included in This Deployment?

"""

    for repo_name in sorted_repos:
        versions = version_details[repo_name]
        announcement += f"**{repo_name}**\n"

        for version, pr_title in versions.items():
            if pr_title:
                announcement += f"{version} → {pr_title}\n"
            else:
                announcement += f"{version}\n"

        announcement += "\n"

    if warnings:
        announcement += "⚠️ **Note:** Unable to determine production deployment status for:\n"
        for warning in warnings:
            announcement += f"- {warning}\n"
        announcement += "\n"

    announcement += """What You Need to Know:

✅ Deployment is scheduled outside of working hours

✅ No significant downtime is expected

❓ If you have any questions or concerns, feel free to reach out.

Thanks!"""

    return announcement

def post_to_teams(announcement, webhook_url, version_details=None, deployment_date=None, deployment_time=None):
    """Post announcement to Teams channel via Power Automate webhook as a rich Adaptive Card"""
    try:
        import urllib.request
        import json

        body_elements = []

        # Header
        formatted_date = format_date(deployment_date) if deployment_date else ""
        formatted_time = format_time(deployment_time) if deployment_time else ""

        body_elements.append({
            "type": "TextBlock",
            "text": f"🚨 Infrastructure Production Deployment Announcement",
            "size": "Large",
            "weight": "Bolder",
            "wrap": True,
            "color": "Attention"
        })
        body_elements.append({
            "type": "TextBlock",
            "text": f"{formatted_date} at {formatted_time}",
            "size": "Medium",
            "isSubtle": True,
            "spacing": "None",
            "wrap": True
        })
        body_elements.append({
            "type": "TextBlock",
            "text": "Hi team,\n\nA production infrastructure deployment is scheduled for "
                    f"**{formatted_date}** at **{formatted_time}**. This release includes updates "
                    "that have been validated across the Dev, QA, and Stage environments.",
            "wrap": True,
            "spacing": "Medium"
        })
        body_elements.append({
            "type": "TextBlock",
            "text": "📦 What's Included in This Deployment?",
            "weight": "Bolder",
            "size": "Medium",
            "spacing": "Medium",
            "wrap": True
        })

        # Repo sections
        if version_details:
            for repo_name in sorted(version_details.keys()):
                versions = version_details[repo_name]
                version_lines = []
                for version, pr_title in versions.items():
                    if pr_title:
                        version_lines.append(f"- **{version}** → {pr_title}")
                    else:
                        version_lines.append(f"- **{version}**")

                body_elements.append({
                    "type": "Container",
                    "spacing": "Medium",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"🗂 {repo_name}",
                            "weight": "Bolder",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": "\n".join(version_lines),
                            "wrap": True,
                            "spacing": "Small"
                        }
                    ]
                })

        # Footer
        body_elements.append({
            "type": "TextBlock",
            "text": "📋 What You Need to Know:",
            "weight": "Bolder",
            "size": "Medium",
            "spacing": "Medium",
            "wrap": True
        })
        body_elements.append({
            "type": "TextBlock",
            "text": "✅ Deployment is scheduled outside of working hours\n\n"
                    "✅ No significant downtime is expected\n\n"
                    "❓ If you have any questions or concerns, feel free to reach out.\n\n"
                    "Thanks!",
            "wrap": True,
            "spacing": "Small"
        })

        adaptive_card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "msteams": {"width": "Full"},
            "body": body_elements
        }

        payload = json.dumps(adaptive_card).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status in (200, 202):
                print("✅ Announcement posted to Teams successfully!")
                return True
            else:
                print(f"⚠️  Unexpected response: HTTP {resp.status}")
                return False
    except Exception as e:
        print(f"❌ Failed to post to Teams: {e}")
        print("   Check that TEAMS_WEBHOOK_URL is set and the workflow is active.")
        return False


def main():
    """Main execution flow"""
    # Check GitHub authentication
    if not check_gh_auth():
        print("❌ GitHub CLI not authenticated. Please run: gh auth login")
        sys.exit(1)

    # Parse flags
    global VERBOSE
    post_to_channel = "--post" in sys.argv
    VERBOSE = "--verbose" in sys.argv or "--debug" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--post", "--verbose", "--debug")]

    # Check for command line arguments
    if len(args) == 2:
        deployment_date = args[0]
        deployment_time = args[1]

        # Validate date format
        try:
            date_obj = datetime.strptime(deployment_date, '%Y-%m-%d')
            today = datetime.now().date()
            if date_obj.date() <= today:
                print(f"❌ Date must be after {today}")
                sys.exit(1)
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

        # Validate time format
        try:
            datetime.strptime(deployment_time, '%H:%M')
        except ValueError:
            print("❌ Invalid time format. Use HH:MM (24-hour)")
            sys.exit(1)
    else:
        print("Usage: generate_prod_deployment_announcement.py YYYY-MM-DD HH:MM [--post] [--verbose]")
        print("Example: generate_prod_deployment_announcement.py 2025-12-02 22:00 --post")
        sys.exit(1)

    # Scan repositories
    deployment_data, blocked_data, warnings, stage_missing = scan_repositories()

    total_ready = len(deployment_data)
    total_ready_versions = sum(len(data["versions"]) for data in deployment_data.values())
    total_blocked = len(blocked_data)
    total_blocked_versions = sum(len(versions) for versions in blocked_data.values())

    print("=" * 50)
    print("📊 Summary:")
    print(f"  Repositories with stage-validated changes: {total_ready}")
    print(f"  Total versions ready for prod: {total_ready_versions}")
    if total_blocked > 0:
        print(f"  ⚠️  Repositories with blocked versions: {total_blocked}")
        print(f"  ⚠️  Total versions blocked (not in stage): {total_blocked_versions}")
    if warnings:
        print(f"  ⚠️  Warnings: {len(warnings)} repos with issues")
    print()

    # Exit with error if no versions are ready for production
    if total_ready_versions == 0:
        print("=" * 50)
        print("❌ ERROR: No versions ready for production deployment")
        print("=" * 50)
        print()
        print("All versions must be deployed to stage before production.")
        print()

        if total_blocked_versions > 0:
            print("Blocked versions (not yet in stage):\n")
            for repo, versions in sorted(blocked_data.items()):
                repo_name = repo.split('/')[-1]
                print(f"  **{repo_name}**")
                if repo_name in stage_missing:
                    print(f"    ⚠️ No stage deployment history found")
                for ver in versions:
                    print(f"    - {ver}")
                print()

        print("Action required: Deploy these versions to stage first, then retry.")
        sys.exit(1)

    # Fetch PR titles for ready versions only (blocked versions are not in the announcement)
    version_details = fetch_pr_titles(deployment_data)

    # Generate announcement
    announcement = generate_announcement(version_details, {}, warnings, stage_missing, deployment_date, deployment_time)

    print("=" * 50)
    print("📋 TEAMS ANNOUNCEMENT")
    print("=" * 50)
    print()
    print(announcement)
    print()
    print("=" * 50)
    print()
    print(f"📅 Summary:")
    print(f"   - {total_ready} repositories with stage-validated deployments")
    print(f"   - {total_ready_versions} versions ready to be deployed")
    if total_blocked_versions > 0:
        print(f"   - {total_blocked_versions} versions blocked (awaiting stage deployment)")
    print(f"   - Scheduled for: {format_date(deployment_date)} at {format_time(deployment_time)}")

    if post_to_channel:
        webhook_url = os.environ.get("TEAMS_WEBHOOK_URL")
        if not webhook_url:
            debug("TEAMS_WEBHOOK_URL not in env — fetching from GitHub repo variable")
            result = subprocess.run(
                ["gh", "api", "repos/LUNA56144/.vscode/actions/variables/TEAMS_WEBHOOK_URL", "--jq", ".value"],
                capture_output=True, text=True
            )
            webhook_url = result.stdout.strip() if result.returncode == 0 else None
        if not webhook_url:
            print("\n❌ Could not resolve TEAMS_WEBHOOK_URL.")
            print("   Either set it locally:  export TEAMS_WEBHOOK_URL=\"<url>\"")
            print("   Or ensure gh is authenticated with access to LUNA56144/.vscode")
            sys.exit(1)
        print()
        post_ok = post_to_teams(announcement, webhook_url, version_details, deployment_date, deployment_time)
        if not post_ok:
            sys.exit(1)
    else:
        print()
        print("💡 Tip: Run with --post to send directly to Teams.")

if __name__ == "__main__":
    main()
