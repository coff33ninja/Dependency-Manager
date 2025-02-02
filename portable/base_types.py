"""
Base types and constants for the dependency checker
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class InstallationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    IN_PROGRESS = "in_progress"

@dataclass
class DependencyResult:
    name: str
    version: Optional[str]
    is_installed: bool
    required_version: Optional[str]
    status: InstallationStatus
    error_message: Optional[str] = None

@dataclass
class EnvironmentInfo:
    python_version: str
    platform: str
    is_venv: bool
    venv_path: Optional[str]
    pip_version: Optional[str]