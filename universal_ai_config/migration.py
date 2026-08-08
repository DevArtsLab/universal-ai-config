"""
Migration logic for existing AI provider configurations.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from .config import UnifiedConfig, deep_merge, load_json, save_json, ConfigError
from .environment import AgentEnv


class MigrationError(Exception):
    """Migration-related errors."""
    pass


class ProviderMigrator:
    """Handles migration from provider-specific configs to unified config."""
    
    # Legacy config paths for each provider
    LEGACY_PATHS = {
        "devin": {
            "user": "~/.config/devin/config.json",
            "user_mcp": "~/.config/devin/mcp_config.json",
            "project": ".devin/config.json",
            "project_mcp": ".devin/mcp_config.json",
            "project_local": ".devin/config.local.json",
            "project_local_mcp": ".devin/mcp_config.local.json",
            "skills": "~/.config/devin/skills/",
            "project_skills": ".devin/skills/",
            "rules": "~/.config/devin/AGENTS.md",
            "project_rules": "AGENTS.md"
        },
        "codium": {
            "user": "~/.codium/config.json",
            "project": ".codium/config.json"
        },
        "windsurf": {
            "user": "~/.windsurf/config.json",
            "project": ".windsurf/config.json"
        },
        "claude": {
            "user": "~/.config/claude/config.json",
            "project": ".claude/config.json"
        }
    }
    
    def __init__(self, env: Optional[AgentEnv] = None):
        self.env = env or AgentEnv()
        self.config = UnifiedConfig(env)
    
    def get_legacy_path(self, provider: str, key: str = "user") -> Optional[Path]:
        """Get legacy path for a provider."""
        if provider not in self.LEGACY_PATHS:
            return None
        
        path_str = self.LEGACY_PATHS[provider].get(key)
        if not path_str:
            return None
        
        path = Path(path_str).expanduser()
        return path if path.exists() else None
    
    def detect_providers(self) -> List[str]:
        """Detect which providers have legacy configs."""
        detected = []
        
        for provider in self.LEGACY_PATHS.keys():
            if self.get_legacy_path(provider, "user"):
                detected.append(provider)
        
        return detected
    
    def migrate_provider(self, provider: str) -> Dict[str, Any]:
        """Migrate a single provider to unified config."""
        if provider not in self.LEGACY_PATHS:
            raise MigrationError(f"Unknown provider: {provider}")
        
        legacy_path = self.get_legacy_path(provider, "user")
        if not legacy_path:
            raise MigrationError(f"No legacy config found for {provider}")
        
        print(f"Migrating {provider} from {legacy_path}")
        
        # Load legacy config
        try:
            legacy_config = load_json(legacy_path)
        except ConfigError as e:
            raise MigrationError(f"Failed to load {provider} config: {e}")
        
        # Transform to unified format
        provider_settings = self._transform_config(provider, legacy_config)
        
        # Update unified config
        self.config.update_provider(provider, provider_settings)
        
        # Migrate MCP servers if present
        if "mcpServers" in legacy_config:
            for name, mcp_config in legacy_config["mcpServers"].items():
                self.config.add_mcp_server(name, mcp_config)
                print(f"  Migrated MCP server: {name}")
        
        # Migrate skills directory
        self._migrate_skills(provider)
        
        # Migrate rules file
        self._migrate_rules(provider)
        
        # Backup legacy config
        backup_path = legacy_path.with_suffix('.json.backup')
        shutil.copy2(legacy_path, backup_path)
        print(f"  Backed up legacy config to: {backup_path}")
        
        return provider_settings
    
    def _transform_config(self, provider: str, legacy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Transform provider-specific config to unified format."""
        settings = {}
        
        # Common fields that might exist across providers
        if "agent" in legacy_config:
            settings["model"] = legacy_config["agent"].get("model")
        
        if "permissions" in legacy_config:
            settings["permissions"] = legacy_config["permissions"]
        
        if "theme_mode" in legacy_config:
            settings["theme_mode"] = legacy_config["theme_mode"]
        
        # Provider-specific transformations
        if provider == "devin":
            # Devin-specific fields
            if "show_history_on_continue" in legacy_config.get("agent", {}):
                settings["show_history_on_continue"] = legacy_config["agent"]["show_history_on_continue"]
        
        return settings
    
    def _migrate_skills(self, provider: str) -> None:
        """Migrate skills directory for a provider."""
        legacy_skills = self.get_legacy_path(provider, "skills")
        if not legacy_skills or not legacy_skills.exists():
            return
        
        unified_skills = self.env.config / "skills"
        
        # Copy skills to unified location
        for skill_file in legacy_skills.glob("*/SKILL.md"):
            skill_name = skill_file.parent.name
            target_dir = unified_skills / skill_name
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_file, target_dir / "SKILL.md")
            print(f"  Migrated skill: {skill_name}")
    
    def _migrate_rules(self, provider: str) -> None:
        """Migrate rules file for a provider."""
        legacy_rules = self.get_legacy_path(provider, "rules")
        if not legacy_rules or not legacy_rules.exists():
            return
        
        unified_rules = self.env.config / "AGENTS.md"
        
        if not unified_rules.exists():
            shutil.copy2(legacy_rules, unified_rules)
            print(f"  Migrated rules to: {unified_rules}")
    
    def migrate_all(self) -> Dict[str, Any]:
        """Migrate all detected providers."""
        detected = self.detect_providers()
        
        if not detected:
            print("No legacy configs found")
            return {}
        
        print(f"Detected providers: {', '.join(detected)}")
        
        results = {}
        for provider in detected:
            try:
                results[provider] = self.migrate_provider(provider)
            except MigrationError as e:
                print(f"Failed to migrate {provider}: {e}")
                results[provider] = None
        
        return results
    
    def migrate_project(self, project_root: Path) -> None:
        """Migrate project-specific configs."""
        ai_dir = project_root / ".ai"
        ai_dir.mkdir(exist_ok=True)
        
        for provider in self.LEGACY_PATHS.keys():
            # Migrate project config
            project_config = self.get_legacy_path(provider, "project")
            if project_config and project_config.exists():
                try:
                    legacy_config = load_json(project_config)
                    project_unified = ai_dir / "config.json"
                    
                    if project_unified.exists():
                        existing = load_json(project_unified)
                        merged = deep_merge(existing, legacy_config)
                    else:
                        merged = legacy_config
                    
                    save_json(project_unified, merged)
                    print(f"Migrated {provider} project config to {project_unified}")
                except ConfigError:
                    pass
            
            # Migrate project local config
            project_local = self.get_legacy_path(provider, "project_local")
            if project_local and project_local.exists():
                try:
                    legacy_config = load_json(project_local)
                    project_local_unified = ai_dir / "config.local.json"
                    
                    if project_local_unified.exists():
                        existing = load_json(project_local_unified)
                        merged = deep_merge(existing, legacy_config)
                    else:
                        merged = legacy_config
                    
                    save_json(project_local_unified, merged)
                    print(f"Migrated {provider} project local config to {project_local_unified}")
                except ConfigError:
                    pass
            
            # Migrate project skills
            project_skills = self.get_legacy_path(provider, "project_skills")
            if project_skills and project_skills.exists():
                unified_skills = ai_dir / "skills"
                unified_skills.mkdir(exist_ok=True)
                
                for skill_file in project_skills.glob("*/SKILL.md"):
                    skill_name = skill_file.parent.name
                    target_dir = unified_skills / skill_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(skill_file, target_dir / "SKILL.md")
                    print(f"Migrated {provider} project skill: {skill_name}")
        
        # Migrate project rules
        for provider in self.LEGACY_PATHS.keys():
            project_rules = self.get_legacy_path(provider, "project_rules")
            if project_rules and project_rules.exists():
                unified_rules = ai_dir / "AGENTS.md"
                if not unified_rules.exists():
                    shutil.copy2(project_rules, unified_rules)
                    print(f"Migrated {provider} project rules to {unified_rules}")
