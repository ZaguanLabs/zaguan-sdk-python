# Release Checklist for Zaguan SDK

Use this checklist when preparing a new release.

## Pre-Release

### 1. Version Update
- [ ] Update version in `zaguan_sdk/__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Ensure versions match

### 2. Documentation
- [ ] Update `CHANGELOG.md` with new features/fixes
- [ ] Update `README.md` if needed
- [ ] Review all example files
- [ ] Check that all URLs are correct

### 3. Code Quality
- [ ] Run tests: `make test` or `pytest tests/ -v`
- [ ] All 56+ tests passing
- [ ] No lint errors
- [ ] Type hints complete

### 4. Build & Verify
- [ ] Clean old builds: `make clean`
- [ ] Build package: `make build`
- [ ] Check package: `make check`
- [ ] Verify dist/ contains .whl and .tar.gz

### 5. Test PyPI (Optional but Recommended)
- [ ] Publish to Test PyPI: `make publish-test`
- [ ] Test installation from Test PyPI
- [ ] Verify imports work
- [ ] Run basic example

## Release

### 6. Git Operations
- [ ] Commit all changes
- [ ] Create git tag: `git tag v0.2.0`
- [ ] Push commits: `git push origin main`
- [ ] Push tag: `git push origin v0.2.0`

### 7. PyPI Publishing

**Option A: Manual**
```bash
make publish
```

**Option B: GitHub Release (Automated)**
1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Choose tag: `v0.2.0`
4. Title: `v0.2.0 - Feature Complete`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"
7. GitHub Actions will automatically publish to PyPI

### 8. Verify Publication
- [ ] Check PyPI: https://pypi.org/project/zaguan-sdk/
- [ ] Test installation: `pip install zaguan-sdk`
- [ ] Verify version: `python -c "import zaguan_sdk; print(zaguan_sdk.__version__)"`
- [ ] Run basic example

## Post-Release

### 9. Announcements
- [ ] Update documentation website
- [ ] Blog post (if applicable)
- [ ] Social media announcement
- [ ] Email to stakeholders

### 10. Next Version
- [ ] Create milestone for next version
- [ ] Update project board
- [ ] Plan next features

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | 2024-11-18 | Initial release with core features |
| 0.2.0 | 2024-11-18 | Added all endpoints (embeddings, audio, images, moderations) |

## Quick Commands

```bash
# Check current version
make version

# Full release workflow
make clean
make build
make check
make test
make publish

# Or step by step
make clean          # Clean old builds
make build          # Build package
make check          # Verify package
make test           # Run tests
make publish-test   # Test on Test PyPI (optional)
make publish        # Publish to PyPI
```

## Rollback Procedure

If something goes wrong:

1. **Cannot rollback PyPI**: Once published, a version cannot be deleted
2. **Fix forward**: Publish a new patch version (e.g., 0.2.1)
3. **Yank version**: Can mark as "yanked" on PyPI (not recommended)

## GitHub Secrets Setup

For automated publishing via GitHub Actions:

1. Go to repository Settings
2. Secrets and variables → Actions
3. New repository secret
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI API token (starts with `pypi-`)

## Support

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Contact: support@zaguanai.com
