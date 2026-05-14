---
description: "Use when running Azure CLI commands, logging in to Azure, switching subscriptions, or accessing Azure resources. Covers login methods, Conditional Access constraints, account-to-subscription mapping, and storage file share access patterns."
applyTo: "**"
---
## Azure CLI — Login & Auth Patterns

### Preferred Login Method (VS Code Remote / SSH)
Always use `az login` (no flags) in VS Code remote environments.
VS Code auto-forwards the localhost OAuth redirect port to the local browser — sign-in completes there and the token is stored on the remote.

```bash
az login
# Select subscription when prompted, or press Enter for default
```

**Do NOT use `--use-device-code` for `_adm` accounts** — it is blocked by Conditional Access policy.
`--use-device-code` works fine for regular accounts (e.g. `Sandro.Aldave@towerswatson.com`).

---

### Account → Subscription Mapping

| Account | Default Subscription | Notes |
|---------|---------------------|-------|
| `Sandro.Aldave@towerswatson.com` | `WTW-BDAIM-DEV` | Access to 14 subscriptions; limited storage list RBAC in prod |
| `LUNA56144_ADM@towerswatson.com` | `WTW-BDAIM-PROD` | Required for prod storage account access; device code CA-blocked |

### Quick Subscription Switch
```bash
az account set --subscription f596c28e-9a50-47aa-bf5e-1a197041b603  # WTW-BDAIM-PROD
az account set --subscription 78dd0cb9-70cd-4cd5-8d3d-414581e421c9  # WTW-BDAIM-DEV
```

Verify active context:
```bash
az account show --query "{User:user.name, Sub:name}" --output table
```

---

### Azure Resource Graph — Finding Resources Across Subscriptions
When `az storage account list` returns empty (RBAC scope too narrow), use Resource Graph:
```bash
az graph query -q "Resources | where type == 'microsoft.storage/storageaccounts' and name == '<name>' | project name, resourceGroup, subscriptionId" --output json
```

---

### Azure Files — OAuth Access
`--auth-mode login` for Azure Files shares requires an extra flag:
```bash
az storage file list \
  --share-name <share> \
  --account-name <account> \
  --path "<path>" \
  --auth-mode login \
  --enable-file-backup-request-intent \
  --output table
```

#### Known Prod File Share
- **Storage account:** `bdaimpna26fdtfs`
- **Share:** `reporting`
- **Resource group:** `BDAIM-P-NA26-FundingDataTransfer-RGRP`
- **Subscription:** `WTW-BDAIM-PROD` (`f596c28e-9a50-47aa-bf5e-1a197041b603`)
- **Validated path:** `Clients/OPERS` (accessible by `LUNA56144_ADM`)
