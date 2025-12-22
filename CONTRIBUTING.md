# Contributing Guidelines

## ⚠️ This is a PUBLIC Repository

Before contributing, please understand that **this repository is PUBLIC**. All commits and changes are visible to everyone.

## 🔒 Security First

### Before EVERY Commit:

1. **Check for secrets:**
   ```bash
   # Search for common secret patterns
   git diff | grep -iE "(api[_-]?key|token|password|secret|shpat_|goldapi)"
   ```

2. **Review what you're committing:**
   ```bash
   git status
   git diff
   git diff --staged
   ```

3. **Verify no sensitive data:**
   - No API keys
   - No access tokens
   - No shop URLs (if private)
   - No theme IDs (if sensitive)
   - No credentials of any kind

## 📝 Contribution Process

### 1. Fork the Repository

Do NOT commit directly to main branch.

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Keep changes focused and atomic
- Follow existing code style
- Add tests if applicable
- Update documentation

### 4. Test Your Changes

```bash
# Run tests
cd tests
python test_price_calculator.py

# Test workflows with dry-run mode
# Do this via GitHub Actions UI
```

### 5. Commit Your Changes

```bash
# Add files
git add <files>

# BEFORE committing, check for secrets one more time!
git diff --staged | grep -iE "(api[_-]?key|token|password|secret|shpat_|goldapi)"

# Commit with descriptive message
git commit -m "feat: add feature description"
```

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

- Provide clear description of changes
- Link any related issues
- Ensure all checks pass
- Request review

## 🎯 Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use type hints where applicable
- Add docstrings to functions
- Keep functions focused and small
- Use meaningful variable names

### Example:

```python
def calculate_price(metal_weight: float, gold_rate: float) -> float:
    """
    Calculate metal price.

    Args:
        metal_weight: Weight in grams
        gold_rate: Rate per gram in rupees

    Returns:
        Calculated price in rupees
    """
    return metal_weight * gold_rate
```

### Documentation

- Update README.md if adding features
- Update CHANGELOG.md with your changes
- Add inline comments for complex logic
- Keep docs clear and concise

## ✅ Pull Request Checklist

Before submitting your PR:

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No secrets or credentials in code
- [ ] No `.env` or config files with real data
- [ ] Commit messages are clear
- [ ] PR description is detailed

## 🚫 What NOT to Commit

**NEVER commit:**

- [ ] API keys or tokens
- [ ] Shopify access tokens
- [ ] GoldAPI keys
- [ ] Any credentials
- [ ] `.env` files
- [ ] `secrets.json` files
- [ ] Configuration files with real shop URLs or IDs
- [ ] Log files with sensitive data
- [ ] Test outputs with real data

## 🔍 Code Review Process

1. Maintainer reviews PR
2. Automated checks run
3. Feedback provided if needed
4. Approve and merge when ready

## 📞 Getting Help

- Open an issue for bugs
- Open a discussion for questions
- Check existing issues/PRs first

## 🎓 Resources

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Security Best Practices](SECURITY.md)

## 📜 Commit Message Format

Use conventional commits:

```
feat: add new feature
fix: fix bug in price calculation
docs: update README
test: add tests for calculator
refactor: simplify price logic
chore: update dependencies
```

## 🙏 Thank You!

Thank you for contributing! Your help makes this project better for everyone.

Remember: **Security first, always check for secrets before committing!**

---

**Last Updated**: 2024-12-22
