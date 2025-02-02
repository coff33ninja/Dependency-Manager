"""
Installer and Updater module for managing application installation and updates
"""
import os
import sys
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class InstallerUpdater:
    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = settings_path
        self.root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.app_data = self.root_dir / "app_data"
        self.temp_dir = self.root_dir / "temp"
        self.backup_dir = self.root_dir / "backup"

    def ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.app_data, self.temp_dir, self.backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def backup_existing_installation(self) -> bool:
        """Backup the current installation before updates."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            
            # Create backup of app files
            shutil.copytree(self.root_dir, backup_path, ignore=shutil.ignore_patterns(
                'backup*', 'temp*', '*.pyc', '__pycache__', 'venv'
            ))
            
            logger.info(f"Created backup at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def install_system_dependencies(self) -> bool:
        """Install system-level dependencies."""
        try:
            if sys.platform == "win32":
                return self._install_windows_dependencies()
            elif sys.platform == "linux":
                return self._install_linux_dependencies()
            elif sys.platform == "darwin":
                return self._install_mac_dependencies()
            else:
                logger.error(f"Unsupported platform: {sys.platform}")
                return False
        except Exception as e:
            logger.error(f"Failed to install system dependencies: {e}")
            return False

    def _install_windows_dependencies(self) -> bool:
        """Install Windows-specific dependencies."""
        try:
            # Check for Visual C++ Build Tools
            if not self._check_visual_cpp_build_tools():
                print("Installing Visual C++ Build Tools...")
                # Download and install Visual C++ Build Tools
                # You might want to use winget or a direct download link
                subprocess.run(["winget", "install", "Microsoft.VisualStudio.BuildTools"], check=True)

            # Install PyAudio dependencies
            print("Installing PyAudio dependencies...")
            subprocess.run(["winget", "install", "PortAudio"], check=True)

            return True
        except Exception as e:
            logger.error(f"Failed to install Windows dependencies: {e}")
            return False

    def _install_linux_dependencies(self) -> bool:
        """Install Linux-specific dependencies."""
        try:
            # Update package list
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            
            # Install required packages
            packages = [
                "python3-dev",
                "portaudio19-dev",
                "python3-pyaudio",
                "build-essential",
                "libssl-dev",
                "libffi-dev",
            ]
            
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to install Linux dependencies: {e}")
            return False

    def _install_mac_dependencies(self) -> bool:
        """Install macOS-specific dependencies."""
        try:
            # Check if Homebrew is installed
            if not shutil.which("brew"):
                print("Installing Homebrew...")
                subprocess.run(["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"], check=True)

            # Install required packages
            packages = ["portaudio", "python"]
            subprocess.run(["brew", "install"] + packages, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to install macOS dependencies: {e}")
            return False

    def _check_visual_cpp_build_tools(self) -> bool:
        """Check if Visual C++ Build Tools are installed."""
        # Check common installation paths
        paths_to_check = [
            r"C:\Program Files (x86)\Microsoft Visual Studio",
            r"C:\Program Files\Microsoft Visual Studio",
        ]
        return any(os.path.exists(path) for path in paths_to_check)

    def check_for_updates(self) -> Tuple[bool, str]:
        """Check if updates are available."""
        # Implement your update check logic here
        # This could involve checking a remote server or repository
        return False, "No updates available"

    def apply_update(self, update_info: Dict) -> bool:
        """Apply an available update."""
        try:
            # Backup current installation
            if not self.backup_existing_installation():
                return False

            # Download and apply update
            # Implement your update logic here

            return True
        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            return False

    def rollback_update(self, backup_path: str) -> bool:
        """Rollback to a previous version if update fails."""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup path not found: {backup_path}")
                return False

            # Restore from backup
            shutil.rmtree(self.root_dir, ignore_errors=True)
            shutil.copytree(backup_path, self.root_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to rollback update: {e}")
            return False