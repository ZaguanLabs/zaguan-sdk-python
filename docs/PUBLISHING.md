# Publishing Zaguan SDK to PyPI

This guide explains how to publish the Zaguan Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**
   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

2. **API Token**
   - Go to Account Settings → API tokens
   - Create token with scope "Entire account"
   - Save the token securely (starts with `pypi-`)

3. **Required Tools**
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version

Edit `zaguan_sdk/__init__.py`:
```python
__version__ = "0.2.0"  # Update version number
```

Also update in `pyproject.toml`:
```toml
version = "0.2.0"
```

### 2. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Build the Package

```bash
python -m build
```

This creates:
- `dist/zaguan_sdk-0.2.0-py3-none-any.whl` (wheel)
- `dist/zaguan-sdk-0.2.0.tar.gz` (source distribution)

### 4. Test on Test PyPI (Recommended First)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ zaguan-sdk
```

### 5. Publish to Production PyPI

```bash
python -m twine upload dist/*
```

Enter your credentials:
- Username: `__token__`
- Password: `pypi-YOUR_TOKEN_HERE`

### 6. Verify Installation

```bash
pip install zaguan-sdk
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

### Setting up GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI API token (starts with `pypi-`)

## Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 0.2.0)

- **PATCH** (0.2.1): Bug fixes, no new features
- **MINOR** (0.3.0): New features, backward compatible
- **MAJOR** (1.0.0): Breaking changes

## Pre-release Checklist

Before publishing:

- [ ] Update version in `__init__.py`
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run all tests: `pytest tests/`
- [ ] Build package: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Test on Test PyPI first
- [ ] Create Git tag: `git tag v0.2.0`
- [ ] Push tag: `git push origin v0.2.0`

## Post-release

After publishing:

1. **Verify on PyPI**: https://pypi.org/project/zaguan-sdk/
2. **Test installation**: `pip install zaguan-sdk`
3. **Update documentation**: Point users to PyPI
4. **Announce**: Blog post, social media, etc.

## Troubleshooting

### "File already exists"
- You cannot overwrite a version on PyPI
- Increment the version number and rebuild

### "Invalid credentials"
- Make sure username is `__token__` (not your PyPI username)
- Check that password is the full token including `pypi-` prefix

### "Package name already taken"
- The package name `zaguan-sdk` should be available
- If not, choose a different name in `pyproject.toml`

### Build errors
- Make sure `pyproject.toml` is valid
- Check that all dependencies are listed
- Ensure `__init__.py` has `__version__`

## Current Package Info

- **Package Name**: `zaguan-sdk`
- **Current Version**: `0.2.0`
- **Python Requires**: `>=3.8`
- **License**: Apache-2.0
- **Homepage**: https://zaguanai.com
- **Repository**: https://github.com/ZaguanLabs/zaguan-sdk-python
- **Documentation**: https://zaguanai.com/docs

## Quick Publish Commands

```bash
# Full workflow
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*

# Or use make (if you create a Makefile)
make clean
make build
make publish
```

## Support

For issues with publishing:
- PyPI Help: https://pypi.org/help/
- Twine Docs: https://twine.readthedocs.io/
- Contact: support@zaguanai.com
