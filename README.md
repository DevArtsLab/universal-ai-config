# Universal AI Configuration

A unified configuration system for AI agents across multiple providers (Devin, Cursor, Windsurf, Claude, etc.). This tool provides a single source of truth for AI agent settings, skills, MCP servers, and rules.

## Features

- **Unified Configuration**: Single config file for all AI providers
- **XDG-Compliant**: Follows Linux/macOS/Windows directory standards
- **Migration Support**: Automatically migrates existing provider configs
- **Project-Local**: Per-project configuration with `.ai/` directory
- **Shared Resources**: MCP servers and skills shared across providers
- **Provider Overrides**: Provider-specific settings when needed

## Installation

### One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/install.sh | bash
```

This will:

- Download and install the package
- Set up the `ai-config` command
- Detect and migrate existing configurations
- Initialize the unified config structure

### Manual Install

```bash
# Clone the repository
git clone https://github.com/DevArtsLab/universal-ai-config.git
cd universal-ai-config

# Install via pip
pip install -e .
```

## Quick Start

### New Users

Initialize a fresh configuration:

```bash
ai-config init
```

Initialize for a project:

```bash
cd your-project
ai-config init-project
```

### Existing Users

Migrate from existing provider configurations:

```bash
ai-config migrate
```

Migrate project-specific configs:

```bash
cd your-project
ai-config migrate --project
```

## Directory Structure

### User-Global Configuration

```
~/.config/ai/              # $XDG_CONFIG_HOME/ai/
  ├── config.json         # Unified config (all providers read this)
  ├── skills/             # Shared skills
  │   └── example-skill/
  └── AGENTS.md           # Shared rules

~/.local/share/ai/         # $XDG_DATA_HOME/ai/
  ├── memory/             # Long-term memory vector DBs
  ├── datasets/           # Fine-tuning datasets
  └── plugins/            # Tool plugins

~/.local/state/ai/         # $XDG_STATE_HOME/ai/
  ├── logs/               # Execution logs
  ├── history/            # Chat history databases
  └── sessions/           # Active execution state

~/.cache/ai/               # $XDG_CACHE_HOME/ai/
  ├── models/             # Embedding model caches
  └── venv/               # Isolated tool environments
```

### Project-Local Configuration

```
.ai/                      # In repository root
  ├── config.json         # Shared team settings
  ├── config.local.json   # Personal overrides (gitignored)
  ├── skills/             # Project-specific skills
  ├── mcp_config.json     # Project MCP servers
  ├── mcp_config.local.json # Project MCP overrides (gitignored)
  └── AGENTS.md           # Project rules
```

## Configuration Format

### Unified Config (`~/.config/ai/config.json`)

```json
{
  "shared": {
    "permissions": {
      "allow": ["Read(**)", "Exec(git)"],
      "deny": ["Exec(sudo)"],
      "ask": ["Write(**/.env*)"]
    }
  },
  "providers": {
    "devin": {
      "permissions": {
        "allow": ["Read(**)", "Exec(git)", "Exec(npm)"]
      }
    }
  },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  },
  "skills": {
    "enabled": [],
    "paths": ["~/.config/ai/skills/", ".ai/skills/"]
  }
}
```

## Commands

### `ai-config init [--fresh]`

Initialize new configuration structure.

```bash
ai-config init           # Initialize new config
ai-config init --fresh   # Remove existing and start fresh
```

### `ai-config migrate [provider] [--project]`

Migrate existing provider configurations.

```bash
ai-config migrate              # Migrate all detected providers
ai-config migrate devin        # Migrate specific provider
ai-config migrate --project    # Migrate project configs
```

### `ai-config validate`

Validate configuration setup.

```bash
ai-config validate
```

### `ai-config status`

Show current configuration status.

```bash
ai-config status
```

### `ai-config init-project`

Initialize `.ai/` directory in current project.

```bash
ai-config init-project
```

### `ai-config get-config <provider>`

Get configuration for a specific provider.

```bash
ai-config get-config devin
```

### `ai-config set-config <provider> <key> <value>`

Set configuration value for a provider.

```bash
ai-config set-config devin model your-model-name
ai-config set-config devin theme_mode dark
```

## Provider Integration

Each AI provider should read from the unified configuration:

```python
from universal_ai_config import UnifiedConfig, AgentEnv

# Initialize
env = AgentEnv()
config = UnifiedConfig(env)

# Get provider-specific config
devin_config = config.get_provider_config("devin")
cursor_config = config.get_provider_config("cursor")

# Get merged config (user + project)
merged_config = config.get_merged_config(cwd=Path.cwd())
```

## Migration Details

The tool automatically detects and migrates from:

- **Devin CLI**: `~/.config/devin/config.json`, `.devin/config.json`
- **Cursor**: `~/.cursor/config.json`, `.cursor/config.json`
- **Windsurf**: `~/.windsurf/config.json`, `.windsurf/config.json`
- **Claude**: `~/.config/claude/config.json`, `.claude/config.json`

Legacy configs are backed up with `.backup` extension.

## Platform Support

- **Linux**: XDG Base Directory Specification
- **macOS**: XDG paths with `~/.config` fallback
- **Windows**: `%APPDATA%` and `%LOCALAPPDATA%` paths

## Best Practices

1. **Secrets Management**: Never store API keys in config files. Use system keyrings or environment variables.

2. **Project Config**: Use `.ai/config.json` for team settings and `.ai/config.local.json` for personal overrides.

3. **Shared Resources**: Put common MCP servers and skills in user config; project-specific ones in `.ai/`.

4. **Validation**: Always run `ai-config validate` after making changes.

## Development

### Setup Development Environment

```bash
git clone https://github.com/DevArtsLab/universal-ai-config.git
cd universal-ai-config
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Format Code

```bash
black universal_ai_config/
```

### Type Check

```bash
mypy universal_ai_config/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## Support

- GitHub Issues: https://github.com/DevArtsLab/universal-ai-config/issues
- Documentation: https://github.com/DevArtsLab/universal-ai-config/wiki
