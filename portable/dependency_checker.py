"""
Main dependency checker implementation
"""
import os
import sys
import logging
import traceback
import json
import importlib
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from portable.base_types import DependencyResult, InstallationStatus, EnvironmentInfo
from portable.requirements_manager import RequirementsManager
from portable.environment_manager import EnvironmentManager
from portable.logger import LogManager

class DependencyChecker:
    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = settings_path
        self.log_manager = LogManager()
        self.logger = self.log_manager.get_logger()
        self.settings = self.load_settings()
        self.root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.req_manager = RequirementsManager()
        self.env_manager = EnvironmentManager(settings_path)

    def load_settings(self) -> Dict:
        """Load settings from JSON file or create default settings."""
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error loading settings: {e}")
                return self.get_default_settings()
        else:
            settings = self.get_default_settings()
            self.save_settings(settings)
            return settings

    def save_settings(self, settings: Dict) -> None:
        """Save settings to JSON file."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")

    def get_default_settings(self) -> Dict:
        """Get default settings configuration."""
        return {
            "environment": {
                "use_venv": True,
                "venv_path": "venv",
                "python_path": sys.executable
            },
            "dependencies": {
                "check_on_startup": True,
                "auto_install": True,
                "requirements_file": "requirements.txt",
                "allow_prerelease": False,
                "trusted_hosts": [],
                "extra_index_urls": []
            },
            "installer": {
                "preferred_manager": "pip",
                "allow_user_install": True,
                "upgrade_dependencies": False,
                "timeout": 60,
                "retries": 3
            },
            "logging": {
                "level": "INFO",
                "file": "dependency_checker.log",
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            }
        }

    def get_environment_info(self) -> EnvironmentInfo:
        """Get current environment information."""
        import platform
        import sys
        import site
        
        # Check if running in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        # Get pip version
        try:
            pip_version = subprocess.check_output(
                [sys.executable, '-m', 'pip', '--version'],
                text=True
            ).split()[1]
        except:
            pip_version = None
            
        return EnvironmentInfo(
            python_version=platform.python_version(),
            platform=platform.platform(),
            is_venv=in_venv,
            venv_path=sys.prefix if in_venv else None,
            pip_version=pip_version
        )

    def check_module(self, module_name: str, required_version: Optional[str] = None) -> DependencyResult:
        """Check if a Python module is available and meets version requirements."""
        try:
            # Handle special cases and extras
            base_module = module_name.split('[')[0] if '[' in module_name else module_name
            
            # Try to import the module
            module = importlib.import_module(base_module)
            version = getattr(module, '__version__', None)
            
            # Version check if required
            version_ok = True
            if required_version and version:
                from packaging import version as pkg_version
                try:
                    if required_version.startswith('>='):
                        version_ok = pkg_version.parse(version) >= pkg_version.parse(required_version[2:])
                    elif required_version.startswith('=='):
                        version_ok = pkg_version.parse(version) == pkg_version.parse(required_version[2:])
                except:
                    self.logger.warning(f"Could not parse version for {module_name}")
                    version_ok = False
            
            return DependencyResult(
                name=module_name,
                version=version,
                is_installed=True,
                required_version=required_version,
                status=InstallationStatus.SUCCESS if version_ok else InstallationStatus.FAILED
            )
            
        except ImportError:
            return DependencyResult(
                name=module_name,
                version=None,
                is_installed=False,
                required_version=required_version,
                status=InstallationStatus.FAILED
            )

    def check_all_dependencies(self) -> Tuple[bool, List[DependencyResult]]:
        """Check all project dependencies."""
        try:
            results = []
            all_ok = True
            
            # Get requirements
            requirements = self.req_manager.get_all_requirements()
            
            for package, version in requirements.items():
                result = self.check_module(package, version)
                results.append(result)
                if result.status != InstallationStatus.SUCCESS:
                    all_ok = False
                    self.logger.warning(
                        f"Dependency issue: {package} "
                        f"(required: {version}, found: {result.version})"
                    )

            return all_ok, results

        except Exception as e:
            self.logger.error(f"Error checking dependencies: {e}")
            return False, []

    def setup_project(self) -> bool:
        """Set up the project environment."""
        try:
            self.logger.info("Starting project setup...")
            
            # Setup virtual environment if needed
            if self.settings["environment"]["use_venv"]:
                venv_path = Path(self.settings["environment"]["venv_path"])
                if not venv_path.exists():
                    self.logger.info(f"Creating virtual environment at {venv_path}")
                    try:
                        import venv
                        venv.create(venv_path, with_pip=True)
                    except Exception as e:
                        self.logger.error(f"Failed to create virtual environment: {e}")
                        return False

            # Get appropriate Python executable
            python_exe = self.get_python_executable()
            
            # Upgrade pip
            try:
                self.logger.info("Upgrading pip...")
                subprocess.run(
                    [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to upgrade pip: {e.stderr}")
                return False

            # Install dependencies
            try:
                cmd = [
                    python_exe, "-m", "pip", "install",
                    "-r", self.settings["dependencies"]["requirements_file"]
                ]
                
                # Add any extra options from settings
                if self.settings["dependencies"]["allow_prerelease"]:
                    cmd.append("--pre")
                
                for host in self.settings["dependencies"]["trusted_hosts"]:
                    cmd.extend(["--trusted-host", host])
                
                for url in self.settings["dependencies"]["extra_index_urls"]:
                    cmd.extend(["--extra-index-url", url])
                
                self.logger.info("Installing dependencies...")
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                self.logger.info("Dependencies installed successfully")
                return True
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install dependencies: {e.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error during project setup: {e}")
            return False

    def get_python_executable(self) -> str:
        """Get the appropriate Python executable based on environment settings."""
        if self.settings["environment"]["use_venv"]:
            venv_path = Path(self.settings["environment"]["venv_path"])
            if sys.platform == "win32":
                python_path = venv_path / "Scripts" / "python.exe"
            else:
                python_path = venv_path / "bin" / "python"
            return str(python_path) if python_path.exists() else sys.executable
        return self.settings["environment"]["python_path"] or sys.executable

    def launch_application(self, app_path: str) -> bool:
        """Launch the main application in the correct environment."""
        try:
            python_exe = self.get_python_executable()
            self.logger.info(f"Launching application: {app_path}")
            
            result = subprocess.run(
                [python_exe, app_path],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info("Application completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Application failed: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error launching application: {e}")
            return False