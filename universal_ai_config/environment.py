"""
XDG-compliant environment management for universal AI configuration.
"""

import os
import platform
from pathlib import Path
from typing import Optional


class AgentEnv:
    """Manages XDG-compliant directory structure for AI agent configuration."""
    
    def __init__(self, app_name: str = "ai"):
        self.app_name = app_name
        self.home = Path.home()
        self.system = platform.system()
    
    @property
    def config(self) -> Path:
        """User configurations, prompts, and credentials."""
        if self.system == "Windows":
            # Windows: %APPDATA%\ai\
            base = os.getenv("APPDATA", str(self.home / "AppData" / "Roaming"))
            return Path(base) / self.app_name
        else:
            # Linux/macOS: $XDG_CONFIG_HOME/ai/ or ~/.config/ai/
            base = os.getenv("XDG_CONFIG_HOME")
            path = Path(base) if base else self.home / ".config"
            return path / self.app_name
    
    @property
    def data(self) -> Path:
        """Persistent storage like long-term memory vector stores."""
        if self.system == "Windows":
            # Windows: %LOCALAPPDATA%\ai\
            base = os.getenv("LOCALAPPDATA", str(self.home / "AppData" / "Local"))
            return Path(base) / self.app_name
        else:
            # Linux/macOS: $XDG_DATA_HOME/ai/ or ~/.local/share/ai/
            base = os.getenv("XDG_DATA_HOME")
            path = Path(base) if base else self.home / ".local" / "share"
            return path / self.app_name
    
    @property
    def state(self) -> Path:
        """Dynamic runtime data like chat history and logs."""
        if self.system == "Windows":
            # Windows: %LOCALAPPDATA%\ai\state\
            base = os.getenv("LOCALAPPDATA", str(self.home / "AppData" / "Local"))
            return Path(base) / self.app_name / "state"
        else:
            # Linux/macOS: $XDG_STATE_HOME/ai/ or ~/.local/state/ai/
            base = os.getenv("XDG_STATE_HOME")
            path = Path(base) if base else self.home / ".local" / "state"
            return path / self.app_name
    
    @property
    def cache(self) -> Path:
        """Non-essential data like model caches and temporary embeddings."""
        if self.system == "Windows":
            # Windows: %TEMP%\ai\ or %LOCALAPPDATA%\ai\cache\
            temp = os.getenv("TEMP")
            if temp:
                return Path(temp) / self.app_name
            base = os.getenv("LOCALAPPDATA", str(self.home / "AppData" / "Local"))
            return Path(base) / self.app_name / "cache"
        else:
            # Linux/macOS: $XDG_CACHE_HOME/ai/ or ~/.cache/ai/
            base = os.getenv("XDG_CACHE_HOME")
            path = Path(base) if base else self.home / ".cache"
            return path / self.app_name
    
    @property
    def project_config(self, cwd: Optional[Path] = None) -> Optional[Path]:
        """Project-local .ai/ directory from current working directory."""
        start = Path(cwd) if cwd else Path.cwd()
        
        # Walk up from cwd looking for .ai/ directory
        current = start
        while current != current.parent:
            ai_dir = current / ".ai"
            if ai_dir.exists():
                return ai_dir
            current = current.parent
        
        return None
    
    def initialize_dirs(self) -> list[Path]:
        """Creates the directory structure safely."""
        dirs = [self.config, self.data, self.state, self.cache]
        created = []
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            created.append(d)
        
        # Create subdirectories
        (self.config / "skills").mkdir(exist_ok=True)
        (self.data / "memory").mkdir(exist_ok=True)
        (self.data / "plugins").mkdir(exist_ok=True)
        (self.state / "logs").mkdir(exist_ok=True)
        (self.state / "history").mkdir(exist_ok=True)
        (self.cache / "models").mkdir(exist_ok=True)
        (self.cache / "venv").mkdir(exist_ok=True)
        
        return created
    
    def get_config_precedence(self, cwd: Optional[Path] = None) -> list[Path]:
        """Returns config paths in precedence order (highest to lowest)."""
        precedence = []
        
        # 1. Project local overrides
        project_dir = self.project_config(cwd)
        if project_dir:
            precedence.append(project_dir / "config.local.json")
        
        # 2. Project shared config
        if project_dir:
            precedence.append(project_dir / "config.json")
        
        # 3. User config
        precedence.append(self.config / "config.json")
        
        return [p for p in precedence if p.exists()]


def find_project_root(cwd: Optional[Path] = None) -> Optional[Path]:
    """Find project root by looking for .git, .jj, or .ai/ directory."""
    start = Path(cwd) if cwd else Path.cwd()
    current = start
    
    while current != current.parent:
        # Check for version control or .ai/ directory
        if (current / ".git").exists() or \
           (current / ".jj").exists() or \
           (current / ".ai").exists():
            return current
        current = current.parent
    
    return None
