# Safety Dependency Scanner Configuration

This document describes the safety dependency vulnerability scanner configuration for the MCP Repository Cache project.

## 🔒 Overview

Safety is a dependency vulnerability scanner that checks Python packages for known security vulnerabilities. The MCP Repository Cache project has configured safety to exclude the `data/raw` directory, which contains cloned Git repositories and should not be scanned for vulnerabilities.

## 📁 Configuration Files

### 1. `.safety-policy.ini` (Primary Configuration)
The main safety configuration file that excludes specific directories and sets scanning policies.

### 2. `pyproject.toml` (Alternative Configuration)
Safety configuration embedded in the Poetry configuration file under `[tool.safety]`.

## 🚫 Excluded Directories

The following directories are excluded from safety scanning:

- **`data`** - Cloned Git repositories (primary exclusion)

## 🚀 Running Safety Scans

### Quick Commands

```bash
# Using Poetry scripts (recommended)
poetry run safety scan
poetry run safety generate policy-file # makes a new default policy file

# Using safety directly with YAML policy file
poetry run safety scan --policy-file .safety-policy.yml

# Full vulnerability report
poetry run safety scan --full-report --policy-file .safety-policy.yml

# JSON output format
poetry run safety scan --output json --policy-file .safety-policy.yml

# Scan specific requirements file
poetry run safety scan --file requirements.txt --policy-file .safety-policy.yml

# Continue scanning even if vulnerabilities found
poetry run safety scan --continue-on-error
```

## 📊 Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Safety Dependency Scan
  run: |
    poetry run safety scan --policy-file .safety-policy.yml
  continue-on-error: true  # Don't fail build on vulnerabilities
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: safety
        name: Safety dependency check
        entry: poetry run safety scan 
        language: system
        pass_filenames: false
```

## 📚 Additional Resources

- [Safety Documentation](https://docs.pyup.io/docs/safety-v3-cli/)
- [PyUp.io Security Database](https://pyup.io/)
- [Python Security Best Practices](https://python.org/dev/security/)
