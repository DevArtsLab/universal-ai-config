# Deployment Guide

This guide explains how to deploy the Universal AI Configuration Manager to GitHub for public distribution.

## Prerequisites

- GitHub account
- GitHub CLI (gh) or git command-line tools
- Repository created at: `https://github.com/DevArtsLab/universal-ai-config`

## Deployment Steps

### 1. Create GitHub Repository

```bash
# Create repository using GitHub CLI
gh repo create DevArtsLab/universal-ai-config --public --description "Unified configuration management for AI agents across multiple providers"

# Or create manually at https://github.com/new
```

### 2. Push to GitHub

```bash
cd /Users/ao/universal-ai-config

# Add remote (replace with your GitHub username if different)
git remote add origin https://github.com/DevArtsLab/universal-ai-config.git

# Push to main branch
git push -u origin main
```

### 3. Verify Installation Script

After pushing, test the installation script:

```bash
# Test on a clean system or in a fresh environment
curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/install.sh | bash
```

### 4. Create GitHub Release (Optional)

For versioned releases:

```bash
# Create a tag
git tag v0.1.0
git push origin v0.1.0

# Create release using GitHub CLI
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes "Initial release of Universal AI Configuration Manager"
```

### 5. Update Installation Documentation

Update the README.md with the correct repository URL:

```bash
# Already updated to: https://github.com/DevArtsLab/universal-ai-config
```

## User Installation

Once deployed, users can install with:

```bash
curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/install.sh | bash
```

## Uninstallation

Users can uninstall with:

```bash
curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/uninstall.sh | bash
```

## Verification Checklist

- [ ] Repository created at correct URL
- [ ] Code pushed to main branch
- [ ] install.sh is executable and in repository
- [ ] uninstall.sh is executable and in repository
- [ ] Installation script works on clean system
- [ ] Migration works for existing users
- [ ] Documentation URLs are correct
- [ ] README.md installation instructions work

## Post-Deployment

### Monitor Issues

Watch for:
- Installation issues on different platforms
- Migration problems with specific providers
- Feature requests from users

### Update Documentation

Keep these files updated:
- README.md - Main documentation
- INSTALL.md - Installation guide
- PROVIDER_INTEGRATION.md - Developer guide

### Release New Versions

When making updates:
1. Update version in `pyproject.toml`
2. Update `universal_ai_config/__init__.py`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release

## Alternative Distribution Methods

### PyPI Distribution

To publish to PyPI:

```bash
# Build package
python -m build

# Install twine if not already installed
pip install twine

# Upload to PyPI (requires PyPI account)
twine upload dist/*
```

Then users can install via:
```bash
pip install universal-ai-config
```

### Homebrew Formula (macOS)

Create a Homebrew formula for macOS users:

```ruby
# Formula/universal-ai-config.rb
class UniversalAiConfig < Formula
  desc "Unified configuration management for AI agents"
  homepage "https://github.com/DevArtsLab/universal-ai-config"
  url "https://github.com/DevArtsLab/universal-ai-config/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "your-sha256-here"
  license "MIT"

  def install
    libexec.install Dir["*"]
    bin.install_symlink "#{libexec}/install.sh" => "ai-config-install"
  end
end
```

## Security Considerations

- Installation script should be reviewed for security
- Use HTTPS for all downloads
- Validate GPG signatures if implementing (future enhancement)
- Keep dependencies minimal and audited

## Support

For deployment issues:
- GitHub Issues: https://github.com/DevArtsLab/universal-ai-config/issues
