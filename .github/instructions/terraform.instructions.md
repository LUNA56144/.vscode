---
description: "Use when writing, editing, or reviewing Terraform files. Applies Azure Terraform standards: AVM modules, implicit dependencies, no hardcoded secrets, naming conventions, validation requirements."
applyTo: "**/*.tf"
---
## Terraform Standards

### Modules
- Use Azure Verified Modules (AVM) where available; verify input properties before use
- Pin module versions explicitly — no floating `latest`

### Dependencies
- Prefer implicit references over `depends_on`
- Flag any `depends_on` where the resource is already referenced implicitly in the same block

### Security
- No hardcoded secrets, passwords, subscription IDs, or environment-specific values
- Source subscription ID from `ARM_SUBSCRIPTION_ID` env var — never in provider block

### Code hygiene
- All `variable`, `locals`, and `output` blocks must be used — remove dead declarations
- No excessive comments — only where logic is non-obvious

### Validation (run before every push)
```bash
terraform init -backend=false
terraform validate
terraform fmt -check -recursive
```

### Resource naming
- Follow Azure naming conventions
- Include standard tags (environment, owner, managed-by)

### Planning files
- Always check `.terraform-planning-files/` before making changes
- Reference planning docs explicitly: "Per INFRA.goal.md, ..."
