"""
Environment analyzer module for checking system and Python environment
"""

import sys
import os
import platform
import logging
import datetime
import json
from typing import Dict, List, Optional
try:
    import importlib.metadata as pkg_resources
except ImportError:
    import pkg_resources

logger = logging.getLogger(__name__)


class EnvironmentAnalyzer:
    def __init__(self):
        self._python_info = self._get_python_info()
        self._system_info = self._get_system_info()

    @property
    def python_info(self) -> Dict:
        """Get Python environment information."""
        return self._python_info

    @property
    def system_info(self) -> Dict:
        """Get system information."""
        return self._system_info

    def _get_python_info(self) -> Dict:
        """Collect Python environment information."""
        return {
            "version": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "path": sys.path,
            "pip_version": self._get_pip_version(),
        }

    def _get_system_info(self) -> Dict:
        """Collect system information."""
        return {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_compiler": platform.python_compiler(),
            "os_name": os.name,
            "env_vars": {
                k: v for k, v in os.environ.items() if "PATH" in k or "PYTHON" in k
            },
        }

    def _get_pip_version(self) -> Optional[str]:
        """Get pip version if available."""
        try:
            return pkg_resources.get_distribution("pip").version
        except pkg_resources.DistributionNotFound:
            return None

    def check_virtualenv(self) -> Dict:
        """Check virtual environment status."""
        is_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        return {
            "is_virtualenv": is_venv,
            "venv_path": sys.prefix if is_venv else None,
            "base_prefix": getattr(sys, "base_prefix", None),
            "real_prefix": getattr(sys, "real_prefix", None),
        }

    def check_development_tools(self) -> Dict:
        """Check for presence of common development tools."""
        tools = {
            "package_managers": {
                "pip": self._check_tool("pip"),
                "virtualenv": self._check_tool("virtualenv"),
            },
            "version_control": {
                "git": self._check_tool("git"),
            },
            "testing": {
                "pytest": self._check_tool("pytest"),
            },
            "linting": {
                "pylint": self._check_tool("pylint"),
            },
        }

        # Add editor detection
        if platform.system() == "Windows":
            tools["editors"] = {
                "pycharm": any(
                    os.path.exists(p)
                    for p in [
                        os.path.expandvars("%APPDATA%\\JetBrains\\PyCharm*"),
                        os.path.expandvars("%LOCALAPPDATA%\\JetBrains\\PyCharm*"),
                    ]
                ),
                "sublime": os.path.exists(
                    os.path.expandvars("%APPDATA%\\Sublime Text")
                ),
                "atom": os.path.exists(os.path.expandvars("%USERPROFILE%\\.atom")),
                "vscode": os.path.exists(os.path.expandvars("%APPDATA%\\Code")),
            }
        else:  # Unix-like systems
            tools["editors"] = {
                "vscode": os.path.exists(os.path.expanduser("~/.vscode")),
                "pycharm": os.path.exists(os.path.expanduser("~/.PyCharm")),
                "sublime": os.path.exists(os.path.expanduser("~/.config/sublime-text")),
                "atom": os.path.exists(os.path.expanduser("~/.atom")),
                "vim": self._check_tool("vim"),
                "emacs": self._check_tool("emacs"),
            }

        return tools

    def check_gpu_support(self) -> Dict:
        """Check for GPU support and related packages."""
        gpu_info = {"available": False, "details": {}}

        # Check PyTorch
        try:
            import torch

            gpu_info["details"]["pytorch"] = {
                "available": True,
                "version": torch.__version__,
                "cuda_available": (
                    torch.cuda.is_available() if hasattr(torch, "cuda") else False
                ),
                "gpu_count": torch.cuda.device_count() if hasattr(torch, "cuda") else 0,
            }
        except ImportError:
            gpu_info["details"]["pytorch"] = {"available": False}

        # Check TensorFlow
        try:
            import tensorflow as tf

            gpu_info["details"]["tensorflow"] = {
                "available": True,
                "version": tf.__version__,
                "gpu_devices": (
                    tf.config.list_physical_devices("GPU")
                    if hasattr(tf.config, "list_physical_devices")
                    else []
                ),
            }
        except ImportError:
            gpu_info["details"]["tensorflow"] = {"available": False}

        # Check CUDA installation
        if platform.system() == "Windows":
            cuda_path = os.getenv("CUDA_PATH")
            if cuda_path and os.path.exists(cuda_path):
                gpu_info["details"]["cuda"] = {
                    "available": True,
                    "path": cuda_path,
                    "version": os.path.basename(cuda_path).replace("v", ""),
                }
        else:
            cuda_paths = ["/usr/local/cuda", "/usr/cuda"]
            for path in cuda_paths:
                if os.path.exists(path):
                    version_file = os.path.join(path, "version.txt")
                    version = None
                    if os.path.exists(version_file):
                        with open(version_file) as f:
                            version = f.read().strip()
                    gpu_info["details"]["cuda"] = {
                        "available": True,
                        "path": path,
                        "version": version,
                    }
                    break

        gpu_info["available"] = any(
            info.get("available", False) for info in gpu_info["details"].values()
        )

        return gpu_info

    def check_security(self) -> Dict:
        """Check security-related aspects of the environment."""
        return {
            "ssl_version": self._get_ssl_version(),
            "python_warnings": self._get_python_warnings(),
            "environment_risks": self._check_environment_risks(),
        }

    def _check_tool(self, tool_name: str) -> bool:
        """Check if a Python package or system tool is available."""
        try:
            if tool_name in ["git", "vim", "emacs"]:  # System tools
                import shutil

                return shutil.which(tool_name) is not None
            else:  # Python packages
                __import__(tool_name)
                return True
        except (ImportError, ModuleNotFoundError):
            return False

    def _get_ssl_version(self) -> Optional[str]:
        """Get SSL version information."""
        try:
            import ssl

            return ssl.OPENSSL_VERSION
        except ImportError:
            return None

    def _get_python_warnings(self) -> List[str]:
        """Get active Python warnings."""
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Trigger some warnings
            import pkg_resources

            return [str(warning.message) for warning in w]

    def _check_environment_risks(self) -> List[str]:
        """Check for potential security risks in the environment."""
        risks = []

        # Check for PYTHONPATH modifications
        if "PYTHONPATH" in os.environ:
            risks.append("PYTHONPATH environment variable is set")

        # Check for world-writable directories in Python path
        for path in sys.path:
            if os.path.exists(path) and os.access(path, os.W_OK):
                try:
                    mode = os.stat(path).st_mode
                    if mode & 0o002:  # World-writable
                        risks.append(f"World-writable directory in Python path: {path}")
                except OSError:
                    pass

        return risks

    def generate_report(self) -> Dict:
        """Generate a comprehensive environment report."""
        return {
            "python_info": self.python_info,
            "system_info": self.system_info,
            "virtualenv_info": self.check_virtualenv(),
            "development_tools": self.check_development_tools(),
            "gpu_support": self.check_gpu_support(),
            "security": self.check_security(),
            "timestamp": datetime.datetime.now().isoformat(),
            "report_version": "1.0",
        }

    def save_report(self, filename: str = "environment_report.json"):
        """Save the environment report to a JSON file."""
        report = self.generate_report()
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return filename

    def check_compatibility(self, requirements_file: str) -> Dict[str, List[str]]:
        """Check compatibility of requirements with current environment."""
        issues = {
            "python_version": [],
            "platform": [],
            "architecture": [],
            "missing_dependencies": [],
        }

        try:
            with open(requirements_file) as f:
                requirements = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]

            for req in requirements:
                try:
                    req_obj = pkg_resources.Requirement.parse(req)

                    # Check if package is already installed
                    try:
                        pkg_resources.get_distribution(req_obj.name)
                    except pkg_resources.DistributionNotFound:
                        issues["missing_dependencies"].append(req_obj.name)

                    # Check markers if present
                    if req_obj.marker:
                        if not req_obj.marker.evaluate():
                            if "platform" in str(req_obj.marker):
                                issues["platform"].append(req_obj.name)
                            elif "python_version" in str(req_obj.marker):
                                issues["python_version"].append(req_obj.name)

                except Exception as e:
                    logger.warning(f"Error parsing requirement {req}: {e}")

        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")

        return issues
