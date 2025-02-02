"""
Environment management for the portable dependency checker
"""
import os
import sys
import json
import venv
import logging
from pathlib import Path
from typing import Dict, Optional

class EnvironmentManager:
    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = settings_path
        self.settings = self.load_settings()
        self.logger = logging.getLogger(__name__)

    def load_settings(self) -> Dict:
        """Load settings from JSON file."""
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Settings file not found: {self.settings_path}")
            return {}

    def setup_virtual_environment(self) -> bool:
        """Set up a virtual environment."""
        try:
            if not self.settings.get("environment", {}).get("use_venv", False):
                return True

            venv_path = Path(self.settings["environment"]["venv_path"])
            if venv_path.exists():
                self.logger.info(f"Virtual environment already exists at {venv_path}")
                return True

            self.logger.info(f"Creating virtual environment at {venv_path}")
            venv.create(venv_path, with_pip=True)
            return True

        except Exception as e:
            self.logger.error(f"Failed to create virtual environment: {e}")
            return False

    def get_python_path(self) -> str:
        """Get the appropriate Python executable path."""
        if self.settings.get("environment", {}).get("use_venv", False):
            venv_path = Path(self.settings["environment"]["venv_path"])
            if sys.platform == "win32":
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                python_path = venv_path / "bin" / "python"
            return str(python_path) if python_path.exists() else sys.executable
        return self.settings.get("environment", {}).get("python_path", sys.executable)

    def is_venv_active(self) -> bool:
        """Check if running in a virtual environment."""
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

    def get_site_packages_path(self) -> Optional[str]:
        """Get the site-packages directory path."""
        try:
            import site
            if self.is_venv_active():
                return site.getsitepackages()[0]
            return site.getusersitepackages()
        except Exception as e:
            self.logger.error(f"Failed to get site-packages path: {e}")
            return None

    def set_environment_variable(self, key: str, value: str):
        """Set an environment variable."""
        os.environ[key] = value
        self.logger.info(f"Set environment variable: {key} = {value}")

    def get_environment_variable(self, key: str) -> Optional[str]:
        """Get an environment variable."""
        return os.environ.get(key)

    def activate_environment(self) -> bool:
        """Activate the virtual environment in the current process."""
        try:
            if not self.settings.get("environment", {}).get("use_venv", False):
                return True

            venv_path = Path(self.settings["environment"]["venv_path"])
            if not venv_path.exists():
                self.logger.error(f"Virtual environment not found at {venv_path}")
                return False

            # Activate virtual environment
            if sys.platform == "win32":
                activate_script = venv_path / "Scripts" / "activate_this.py"
            else:
                activate_script = venv_path / "bin" / "activate_this.py"

            if not activate_script.exists():
                self.logger.error(f"Activation script not found: {activate_script}")
                return False

            with open(activate_script) as f:
                exec(f.read(), {'__file__': str(activate_script)})

            self.logger.info(f"Virtual environment activated: {venv_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to activate environment: {e}")
            return False

    def get_environment_info(self) -> Dict:
        """Get information about the current environment."""
        import platform
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "is_venv": self.is_venv_active(),
            "venv_path": self.settings.get("environment", {}).get("venv_path"),
            "site_packages": self.get_site_packages_path(),
            "python_path": self.get_python_path(),
            "system_path": os.environ.get("PATH", "")
        }