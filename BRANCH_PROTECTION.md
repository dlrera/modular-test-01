# Branch Protection Configuration

## Overview

This document outlines the branch protection rules for the `main` branch to ensure code quality and prevent direct pushes.

## 🔧 Configurable Protection (Environment Toggle)

Branch protection can be toggled via environment variable for different environments:

### Configuration

Set in `.env` file:
```bash
# Allow direct pushes to main branch
ALLOW_DIRECT_PUSH_TO_MAIN=true  # Development (default)
ALLOW_DIRECT_PUSH_TO_MAIN=false # Production (recommended)
```

### Setup Custom Hooks

```bash
# Windows
setup-hooks.bat

# Unix/Mac/Linux
./setup-hooks.sh

# Or manually
git config core.hooksPath .githooks
```

### Current Settings

- **Development Mode** (`ALLOW_DIRECT_PUSH_TO_MAIN=true`):
  - ⚠️ Direct pushes allowed with warning
  - Pre-commit hooks still run for code quality
  - Useful for solo development or prototyping

- **Protected Mode** (`ALLOW_DIRECT_PUSH_TO_MAIN=false`):
  - ❌ Direct pushes blocked
  - Must use feature branches and PRs
  - Recommended for teams and production

### Override for Single Push

```bash
# Temporarily allow a direct push (not recommended)
ALLOW_DIRECT_PUSH_TO_MAIN=true git push origin main

# Windows PowerShell
$env:ALLOW_DIRECT_PUSH_TO_MAIN='true'; git push origin main
```

## GitHub Branch Protection Settings

Navigate to: **Settings → Branches → Add rule**

### Branch name pattern: `main`

### ✅ Required Settings

#### 1. **Require a pull request before merging**

- [x] Require a pull request before merging
- [x] Require approvals: **1** (increase when team grows)
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require review from CODEOWNERS
- [ ] Require approval of the most recent reviewable push (optional)

#### 2. **Require status checks to pass before merging**

- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging

**Required status checks:**

- `backend` - Backend Tests & Linting
- `frontend` - Frontend Tests & Linting
- `security` - Security Checks
- `pre-commit` - Pre-commit Hooks
- `api-schema` - OpenAPI Schema Check
- `coverage-report` - Coverage Report (85% threshold)

#### 3. **Require conversation resolution before merging**

- [x] Require conversation resolution before merging

#### 4. **Require signed commits** (Optional but recommended)

- [ ] Require signed commits

#### 5. **Require linear history** (Optional)

- [ ] Require linear history

#### 6. **Include administrators**

- [x] Include administrators (enforce for everyone)

#### 7. **Restrict who can push to matching branches**

- [ ] Restrict who can push to matching branches (optional for now)

### ⛔ Protection Rules

#### **Do not allow:**

- [ ] Allow force pushes
- [ ] Allow deletions
- [ ] Allow bypass for specific users/teams

## Local Pre-commit Hooks

Pre-commit hooks are configured and will run automatically on every commit.

### Installation

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

### Hooks Configured

#### Python/Backend

- **black** - Code formatting
- **isort** - Import sorting
- **ruff** - Linting
- **djlint** - Django template linting
- **bandit** - Security checks

#### JavaScript/Frontend

- **eslint** - JavaScript/TypeScript linting
- **prettier** - Code formatting

#### General

- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **check-merge-conflict** - Check for merge conflict markers
- **detect-private-key** - Prevent committing private keys
- **check-added-large-files** - Prevent large files (>1MB)

## CI Pipeline Requirements

All pull requests must pass the following checks:

### 1. **Code Quality** ✅

- Black formatting (Python)
- isort imports (Python)
- Ruff linting (Python)
- ESLint (JavaScript/TypeScript)
- Prettier formatting (Frontend)

### 2. **Testing** ✅

- Backend: pytest with 85% coverage minimum
- Frontend: Vitest with 85% coverage target
- All tests must pass

### 3. **Security** ✅

- Bandit security scan
- Safety dependency check
- npm audit (high severity only)

### 4. **Build** ✅

- Backend: Django checks pass
- Frontend: Build completes successfully
- Migrations: No uncommitted migrations

## Workflow

### For Contributors

1. **Create feature branch**

   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and commit**

   ```bash
   # Pre-commit hooks run automatically
   git add .
   git commit -m "feat: your feature"
   ```

3. **Push to GitHub**

   ```bash
   git push origin feature/your-feature
   ```

4. **Create Pull Request**
   - Fill out PR template
   - Ensure all checks pass
   - Request review from CODEOWNERS

### For Reviewers

1. **Review code changes**
2. **Check test coverage**
3. **Verify CI checks pass**
4. **Approve if satisfactory**

## Enforcement

### ⚠️ What's Blocked

- ❌ Direct pushes to `main` (including admins)
- ❌ Merging without passing status checks
- ❌ Merging without required reviews
- ❌ Merging with failing coverage (<85%)
- ❌ Force pushes to `main`
- ❌ Deleting the `main` branch

### ✅ What's Allowed

- ✅ Creating pull requests
- ✅ Pushing to feature branches
- ✅ Merging PRs with all checks passing
- ✅ Reverting commits via PR

## Monitoring

### Coverage Tracking

- Backend coverage: Minimum 85%
- Frontend coverage: Target 85%
- Coverage reports uploaded to Codecov (if configured)

### Failed Checks

If CI checks fail:

1. Check the GitHub Actions tab for details
2. Fix issues locally
3. Run pre-commit hooks: `pre-commit run --all-files`
4. Push fixes to your branch

## Emergency Procedures

### If you need to bypass (NOT RECOMMENDED)

1. Must have admin access
2. Document reason in PR description
3. Create follow-up issue to fix
4. Should be extremely rare

### Rollback Procedure

1. Create a revert PR
2. Ensure revert PR passes all checks
3. Merge through normal process

## Support

### Common Issues

**Pre-commit hooks not running:**

```bash
pre-commit install --force
```

**Coverage falling below threshold:**

- Write more tests
- Check for untested code paths
- Use coverage report: `pytest --cov-report=html`

**Merge conflicts:**

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts
git push --force-with-lease
```

## Summary

This configuration ensures:

- ✅ No direct pushes to main
- ✅ All code is reviewed
- ✅ 85% test coverage maintained
- ✅ Code style consistency via pre-commit
- ✅ Security vulnerabilities caught early
- ✅ All CI checks pass before merge

---

*Last updated: 2025-08-31*
*Configured for: <https://github.com/dlrera/modular-test-01>*
