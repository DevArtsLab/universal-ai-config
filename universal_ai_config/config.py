"""
Unified configuration management for AI providers.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from .environment import AgentEnv


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")


def save_json(path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """Save JSON file with error handling."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent)


class UnifiedConfig:
    """Manages unified AI configuration across all providers."""
    
    def __init__(self, env: Optional[AgentEnv] = None):
        self.env = env or AgentEnv()
        self._unified_config = None
    
    @property
    def unified_config_path(self) -> Path:
        """Path to the unified config file."""
        return self.env.config / "config.json"
    
    def load_unified(self) -> Dict[str, Any]:
        """Load the unified configuration."""
        if self._unified_config is None:
            path = self.unified_config_path
            if not path.exists():
                return self._get_default_config()
            self._unified_config = load_json(path)
        return self._unified_config
    
    def save_unified(self, config: Dict[str, Any]) -> None:
        """Save the unified configuration."""
        save_json(self.unified_config_path, config)
        self._unified_config = config
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        unified = self.load_unified()
        
        # Start with shared settings
        config = unified.get("shared", {}).copy()
        
        # Apply provider-specific overrides
        provider_settings = unified.get("providers", {}).get(provider, {})
        config = deep_merge(config, provider_settings)
        
        # Add shared resources
        config["mcpServers"] = unified.get("mcpServers", {})
        config["skills"] = unified.get("skills", {})
        
        return config
    
    def get_merged_config(self, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Get merged configuration from all sources in precedence order."""
        env = AgentEnv()
        config_paths = env.get_config_precedence(cwd)
        
        # Start with unified user config
        merged = self.load_unified()
        
        # Merge project configs (lowest to highest priority)
        for path in reversed(config_paths):
            try:
                project_config = load_json(path)
                merged = deep_merge(merged, project_config)
            except ConfigError:
                continue
        
        return merged
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure."""
        return {
            "shared": {},
            "providers": {},
            "mcpServers": {},
            "skills": {
                "enabled": [],
                "paths": [
                    str(self.env.skills),
                    ".ai/skills"
                ]
            },
            "read_config_from": {
                "codium": False,
                "windsurf": False,
                "claude": False
            }
        }
    
    def update_provider(self, provider: str, settings: Dict[str, Any]) -> None:
        """Update settings for a specific provider."""
        unified = self.load_unified()
        
        if "providers" not in unified:
            unified["providers"] = {}
        
        unified["providers"][provider] = deep_merge(
            unified["providers"].get(provider, {}),
            settings
        )
        
        self.save_unified(unified)
    
    def update_shared(self, settings: Dict[str, Any]) -> None:
        """Update shared settings."""
        unified = self.load_unified()
        unified["shared"] = deep_merge(unified.get("shared", {}), settings)
        self.save_unified(unified)
    
    def add_mcp_server(self, name: str, config: Dict[str, Any]) -> None:
        """Add or update an MCP server."""
        unified = self.load_unified()
        
        if "mcpServers" not in unified:
            unified["mcpServers"] = {}
        
        unified["mcpServers"][name] = config
        self.save_unified(unified)
    
    def remove_mcp_server(self, name: str) -> None:
        """Remove an MCP server."""
        unified = self.load_unified()
        if "mcpServers" in unified and name in unified["mcpServers"]:
            del unified["mcpServers"][name]
            self.save_unified(unified)
