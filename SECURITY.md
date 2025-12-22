# Security Policy

## ⚠️ IMPORTANT: This is a PUBLIC Repository

This repository is **PUBLIC** to take advantage of free GitHub Actions. Therefore, it is **CRITICAL** that you follow these security guidelines.

## 🔒 Critical Security Rules

### ❌ NEVER Commit These Files

**ABSOLUTELY NEVER commit or push:**
- API keys or tokens
- Shopify access tokens
- GoldAPI.io keys
- Shop URLs (if you want to keep them private)
- Theme IDs (if sensitive)
- Any `.env` files
- Any `secrets.json` files
- Any configuration files with actual credentials

### ✅ ALWAYS Use GitHub Secrets

**ALL sensitive data MUST be stored in GitHub Secrets:**

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret individually:
   - `GOLDAPI_KEY` - Your GoldAPI.io API key
   - `SHOPIFY_SHOP_URL` - Your Shopify store URL
   - `SHOPIFY_ACCESS_TOKEN` - Your Shopify Admin API access token
   - `SHOPIFY_THEME_ID` - Your theme ID

### 🔍 Before Every Commit

**ALWAYS check before committing:**

```bash
# Check what you're about to commit
git status
git diff

# Make sure no secrets are included
grep -r "shpat_" .
grep -r "goldapi-" .
grep -r "myshopify.com" .
```

## 🛡️ Security Best Practices

### 1. GitHub Secrets

- ✅ Secrets are encrypted at rest
- ✅ Secrets are only exposed to workflows
- ✅ Secrets are not printed in logs
- ✅ Secrets can be rotated easily

### 2. API Token Permissions

**Shopify Admin API Token:**
- ✅ Use the **minimum required scopes**:
  - `read_products`
  - `write_products`
  - `read_themes`
  - `write_themes`
- ❌ Do NOT grant unnecessary permissions
- 🔄 Rotate tokens regularly (every 3-6 months)

**GoldAPI.io Key:**
- ✅ Use a dedicated key for this automation
- 🔄 Rotate if compromised
- 📊 Monitor usage/quota

### 3. Repository Settings

**Recommended settings for public repo:**

1. **Settings** → **Actions** → **General**:
   - ✅ Require approval for first-time contributors
   - ✅ Prevent fork PRs from accessing secrets

2. **Settings** → **Branches**:
   - ✅ Protect your main branch
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

3. **Settings** → **Code security and analysis**:
   - ✅ Enable Dependabot alerts
   - ✅ Enable Dependabot security updates
   - ✅ Enable secret scanning (if available)

### 4. Workflow Security

The workflows are configured to:
- ✅ Only run on schedule or manual trigger
- ✅ Not run on pull requests from forks
- ✅ Not expose secrets in logs
- ✅ Validate all inputs

### 5. Code Review

Before merging any changes:
- 👀 Review all code changes carefully
- 🔍 Check for hardcoded credentials
- ✅ Verify no new files with secrets
- 🧪 Test in dry-run mode first

## 🚨 What to Do If Secrets Are Exposed

### If you accidentally commit a secret:

1. **Immediately revoke the secret:**
   - Shopify: Delete the custom app or regenerate token
   - GoldAPI: Regenerate API key

2. **Remove from git history:**
   ```bash
   # Use git filter-branch or BFG Repo-Cleaner
   # This is complex - consider creating a new repo instead
   ```

3. **Update GitHub Secrets** with new credentials

4. **Force push** (if you must clean history):
   ```bash
   git push --force
   ```

5. **Consider starting fresh** with a new repository if the exposure is severe

### If someone forks your repo:

- Forks **cannot** access your GitHub Secrets
- Forks **cannot** run workflows that use your secrets
- Your secrets remain safe

## 📋 Security Checklist

Before making repository public:

- [ ] All secrets removed from code
- [ ] `.env.example` removed or contains no real values
- [ ] `.gitignore` includes all sensitive file patterns
- [ ] GitHub Secrets configured correctly
- [ ] Workflows tested and verified
- [ ] No API keys in commit history
- [ ] Branch protection enabled
- [ ] Secret scanning enabled (if available)

## 🔐 Recommended .gitignore Patterns

Ensure your `.gitignore` includes:

```
# Secrets and credentials
.env
.env.*
!.env.example
secrets.json
secrets.yml
*.key
*.pem

# API keys
*api-key*
*apikey*
*access-token*

# Configuration with secrets
config.json
settings.json
credentials.json

# Logs (may contain sensitive data)
*.log
logs/
```

## 📞 Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. **DO NOT** commit a fix publicly
3. **Contact** the repository owner privately
4. **Wait** for response before disclosing

## 🎓 Educational Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Shopify API Security](https://shopify.dev/docs/api/usage/authentication)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

## ✅ Quick Security Check Commands

Before pushing:

```bash
# Check for common secret patterns
git diff | grep -E "(shpat_|goldapi-|password|secret|token|key)"

# Check staged files
git diff --staged | grep -E "(shpat_|goldapi-|password|secret|token|key)"

# List all files to be committed
git diff --staged --name-only

# Check specific file for secrets
git diff HEAD scripts/price_updater.py
```

## 🔄 Regular Security Maintenance

### Monthly:
- [ ] Review GitHub Secret Scanner alerts (if enabled)
- [ ] Check for unauthorized workflow runs
- [ ] Review access logs in Shopify
- [ ] Verify GoldAPI usage is expected

### Quarterly:
- [ ] Rotate API tokens
- [ ] Update dependencies
- [ ] Review and update scopes/permissions
- [ ] Audit workflow logs

### Annually:
- [ ] Full security audit
- [ ] Review all access controls
- [ ] Update security documentation
- [ ] Train team on security practices

---

## 🎯 Summary

**Remember:**
1. This is a PUBLIC repository
2. NEVER commit secrets
3. ALWAYS use GitHub Secrets
4. Check before EVERY commit
5. Rotate tokens regularly

**Stay safe! 🔒**

---

**Last Updated**: 2024-12-22
**Security Version**: 1.0
