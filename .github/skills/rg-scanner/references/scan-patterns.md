# RG Scanner — Terraform Search Patterns

Grep commands to extract resource group name references from Terraform files.
Run from the environment directory root unless noted.

## Pattern 1 — Direct string assignment

```bash
grep -rn 'resource_group_name\s*=\s*"' \
  --include="*.tf" --include="*.tfvars" \
  --exclude-dir=".terraform" \
  <env_dir>
```

## Pattern 2 — Variable reference

```bash
grep -rn 'resource_group_name\s*=\s*var\.' \
  --include="*.tf" \
  --exclude-dir=".terraform" \
  <env_dir>
```

Then resolve: search `terraform.tfvars` and `variables.tf` for the variable name:

```bash
VAR_NAME=$(grep -oh 'var\.\w*' <<< "<matched_line>" | sed 's/var\.//')
grep -n "\"$VAR_NAME\"" <env_dir>/terraform.tfvars <env_dir>/variables.tf 2>/dev/null
```

## Pattern 3 — Local reference

```bash
grep -rn 'resource_group_name\s*=\s*local\.' \
  --include="*.tf" \
  --exclude-dir=".terraform" \
  <env_dir>
```

Then resolve in `locals.tf` or `main.tf`:

```bash
LOCAL_NAME=$(grep -oh 'local\.\w*' <<< "<matched_line>" | sed 's/local\.//')
grep -n "$LOCAL_NAME" <env_dir>/locals.tf <env_dir>/main.tf 2>/dev/null
```

## Pattern 4 — Data source block

```bash
grep -rn -A5 'data\s+"azurerm_resource_group"' \
  --include="*.tf" \
  --exclude-dir=".terraform" \
  <env_dir>
```

## Pattern 5 — Module call passing RG name

```bash
grep -rn 'resource_group_name\s*=' \
  --include="*.tf" \
  --exclude-dir=".terraform" \
  <repo_root>
```

## Pattern 6 — tfvars direct values

```bash
grep -rn 'resource_group\|rg_name' \
  --include="*.tfvars" --include="*.auto.tfvars" \
  <env_dir>
```

## Batch command — all patterns in one pass

Run this from the repo root for a full sweep:

```bash
grep -rn \
  -e 'resource_group_name\s*=' \
  -e 'data\s*"azurerm_resource_group"' \
  -e '"rg-im-' \
  --include="*.tf" --include="*.tfvars" \
  --exclude-dir=".terraform" \
  <repo_root> \
  | grep -v "^Binary"
```

## Output normalization

After collecting raw grep output, extract just the RG name values:

```bash
# Extract quoted string values after resource_group_name =
grep -oP '(?<=resource_group_name\s=\s")[^"]+' <<< "<grep_output>"
```

## Anomaly detection

Flag lines where RG name:
- Does not start with `rg-im-`
- Contains uppercase letters
- Ends without an environment suffix (`-dev`, `-qa`, `-stage`, `-prod`, `-secondary`)
- Is a pure variable reference with no default value

```bash
# Check for non-standard names
grep -rn 'resource_group_name\s*=\s*"' \
  --include="*.tf" \
  --exclude-dir=".terraform" \
  <repo_root> \
  | grep -v '"rg-im-'
```
