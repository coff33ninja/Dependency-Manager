"""
Integration utilities for the dependency checker
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict
import subprocess

from portable.dependency_checker import DependencyChecker
from portable.environment_manager import EnvironmentManager
from portable.requirements_manager import RequirementsManager
from portable.base_types import InstallationStatus  # Import InstallationStatus


class Integration:
    def __init__(self, settings_path: str = "settings.json"):
        self.logger = logging.getLogger(__name__)
        self.settings_path = settings_path
        self.dependency_checker = DependencyChecker(settings_path)
        self.env_manager = EnvironmentManager(settings_path)
        self.req_manager = RequirementsManager()

    def install_missing_dependencies(self) -> bool:
        """Install any missing dependencies required by the project."""
        try:
            self.logger.info("Checking for missing dependencies...")
            all_ok, results = self.dependency_checker.check_all_dependencies()
            if all_ok:
                self.logger.info("All dependencies are installed.")
                return True

            for result in results:
                if result.status == InstallationStatus.FAILED:
                    self.logger.info(f"Installing missing dependency: {result.name}")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", result.name],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    self.logger.info(f"Successfully installed: {result.name}")

            return True

        except Exception as e:
            self.logger.error(f"Error installing missing dependencies: {e}")
            return False

    def setup_project(self, requirements_path: Optional[str] = None) -> bool:
        """
        Complete project setup including environment and dependencies.
        """
        try:
            self.logger.info("Starting project setup...")

            # Setup virtual environment if needed
            if not self.env_manager.setup_virtual_environment():
                self.logger.error("Failed to setup virtual environment")
                return False

            # Update requirements if a new file is provided
            if requirements_path:
                self.req_manager.load_requirements_from_txt(requirements_path)

            # Install dependencies
            if not self.dependency_checker.setup_project():
                self.logger.error("Failed to install dependencies")
                return False

            # Install any missing dependencies
            if not self.install_missing_dependencies():
                self.logger.error("Failed to install missing dependencies")
                return False

            self.logger.info("Project setup completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error during project setup: {e}")
            return False

    def launch_application(self, app_path: str, args: Optional[list] = None) -> bool:
        """
        Launch the main application with proper environment setup.
        """
        try:
            # Verify environment and dependencies first
            ok, results = self.dependency_checker.check_all_dependencies()
            if not ok:
                self.logger.error("Dependency check failed before launch")
                return False

            # Launch the application
            return self.dependency_checker.launch_application(app_path)

        except Exception as e:
            self.logger.error(f"Application launch failed: {e}")
            return False

    def generate_report(self) -> Dict:
        """
        Generate a comprehensive report about the environment and dependencies.
        """
        try:
            env_info = self.env_manager.get_environment_info()
            ok, dep_results = self.dependency_checker.check_all_dependencies()

            return {
                "environment": env_info,
                "dependencies": {
                    "status": "ok" if ok else "failed",
                    "results": [vars(r) for r in dep_results],
                },
                "requirements": self.req_manager.get_all_requirements(),
            }

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return {"error": str(e)}
