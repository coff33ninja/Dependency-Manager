"""
Package metadata and compatibility checker
"""

import sys
import json
import requests
import platform
import pkg_resources
import logging
from typing import Dict, List, Optional, Tuple
from packaging import version
from pathlib import Path

logger = logging.getLogger(__name__)


class PackageMetadata:
    PYPI_API_URL = "https://pypi.org/pypi/{package}/json"
    WAREHOUSE_URL = "https://pypi.org/simple"

    def __init__(self):
        self._cache = {}
        self.session = requests.Session()

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Fetch package information from PyPI."""
        if package_name in self._cache:
            return self._cache[package_name]

        try:
            response = self.session.get(
                self.PYPI_API_URL.format(package=package_name), timeout=10
            )
            response.raise_for_status()
            self._cache[package_name] = response.json()
            return self._cache[package_name]
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch metadata for {package_name}: {e}")
            return None

    def check_python_compatibility(
        self, package_name: str, python_version: str = None
    ) -> Tuple[bool, str]:
        """Check if package is compatible with current Python version."""
        if not python_version:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        info = self.get_package_info(package_name)
        if not info:
            return False, "Could not fetch package information"

        try:
            latest_version = info["info"]["version"]
            classifiers = info["info"]["classifiers"]

            # Check Python version classifiers
            python_versions = [
                c.split("::")[-1].strip()
                for c in classifiers
                if c.startswith("Programming Language :: Python")
                and not c.endswith("Only")
                and not c.endswith("Implementation")
            ]

            if not python_versions:
                return True, "No Python version restrictions found"

            current = version.parse(python_version)
            compatible = False

            for ver in python_versions:
                try:
                    if ver.startswith(">="):
                        min_ver = version.parse(ver[2:])
                        if current >= min_ver:
                            compatible = True
                    elif ver.startswith("<="):
                        max_ver = version.parse(ver[2:])
                        if current <= max_ver:
                            compatible = True
                    else:
                        ver = ver.replace("Python ", "")
                        if ver == python_version:
                            compatible = True
                except version.InvalidVersion:
                    continue

            return compatible, f"Latest version: {latest_version}"

        except (KeyError, ValueError) as e:
            return False, f"Error parsing package metadata: {e}"

    def get_package_dependencies(self, package_name: str) -> List[str]:
        """Get list of package dependencies."""
        info = self.get_package_info(package_name)
        if not info:
            return []

        try:
            requires = info["info"].get("requires_dist", []) or []
            dependencies = []

            for req in requires:
                # Parse requirement string to get base package name
                if ";" in req:  # Remove environment markers
                    req = req.split(";")[0]
                if " " in req:  # Remove version specifiers
                    req = req.split(" ")[0]

                dependencies.append(req)

            return dependencies
        except Exception as e:
            logger.error(f"Error getting dependencies for {package_name}: {e}")
            return []

    def check_platform_compatibility(self, package_name: str) -> Tuple[bool, str]:
        """Check if package is compatible with current platform."""
        info = self.get_package_info(package_name)
        if not info:
            return False, "Could not fetch package information"

        current_platform = platform.system().lower()
        try:
            classifiers = info["info"]["classifiers"]
            platform_classifiers = [
                c.split("::")[-1].strip().lower()
                for c in classifiers
                if c.startswith("Operating System")
            ]

            if not platform_classifiers:
                return True, "No platform restrictions found"

            compatible = any(
                current_platform in platform.lower()
                for platform in platform_classifiers
            )

            return (
                compatible,
                f"Platform classifiers: {', '.join(platform_classifiers)}",
            )

        except Exception as e:
            return False, f"Error checking platform compatibility: {e}"

    def get_alternative_packages(self, package_name: str) -> List[str]:
        """Get list of alternative packages based on PyPI classifiers."""
        info = self.get_package_info(package_name)
        if not info:
            return []

        try:
            classifiers = info["info"]["classifiers"]
            topics = [
                c.split("::")[-1].strip() for c in classifiers if c.startswith("Topic")
            ]

            alternatives = []
            for topic in topics:
                # Search for packages with similar topics
                search_url = f"https://pypi.org/search/?q=&c={topic.replace(' ', '+')}"
                alternatives.append(f"Similar packages for '{topic}': {search_url}")

            return alternatives

        except Exception as e:
            logger.error(f"Error finding alternatives for {package_name}: {e}")
            return []

    def check_package_health(self, package_name: str) -> Dict[str, any]:
        """Check various health metrics of a package."""
        info = self.get_package_info(package_name)
        if not info:
            return {}

        try:
            latest_version = info["info"]["version"]
            release_info = info["releases"][latest_version]

            return {
                "name": package_name,
                "version": latest_version,
                "maintainers": len(info["info"].get("maintainers", [])),
                "github_url": info["info"].get("project_urls", {}).get("Source"),
                "download_stats": info["info"].get("downloads", {}).get("last_month"),
                "requires_python": info["info"].get("requires_python"),
                "release_date": (
                    release_info[0]["upload_time"] if release_info else None
                ),
                "has_wheel": any(
                    r["packagetype"] == "bdist_wheel" for r in release_info
                ),
                "license": info["info"].get("license"),
                "development_status": [
                    c
                    for c in info["info"]["classifiers"]
                    if c.startswith("Development Status")
                ],
                "documentation_url": info["info"]
                .get("project_urls", {})
                .get("Documentation"),
                "homepage": info["info"].get("home_page"),
                "author": info["info"].get("author"),
                "author_email": info["info"].get("author_email"),
                "package_size": sum(
                    r["size"]
                    for r in release_info
                    if r["packagetype"] in ("bdist_wheel", "sdist")
                ),
                "supported_implementations": [
                    c.split("::")[-1].strip()
                    for c in info["info"]["classifiers"]
                    if c.startswith("Programming Language :: Python :: Implementation")
                ],
            }
        except Exception as e:
            logger.error(f"Error checking package health for {package_name}: {e}")
            return {}

    def get_package_release_history(self, package_name: str) -> List[Dict]:
        """Get release history of a package."""
        info = self.get_package_info(package_name)
        if not info:
            return []

        try:
            releases = []
            for version_str, release_info in info["releases"].items():
                if release_info:  # Some versions might have no releases
                    releases.append(
                        {
                            "version": version_str,
                            "upload_time": release_info[0]["upload_time"],
                            "python_version": release_info[0].get("python_version"),
                            "url": release_info[0]["url"],
                            "size": release_info[0]["size"],
                            "has_wheel": any(
                                r["packagetype"] == "bdist_wheel" for r in release_info
                            ),
                        }
                    )
            return sorted(
                releases, key=lambda x: version.parse(x["version"]), reverse=True
            )
        except Exception as e:
            logger.error(f"Error getting release history for {package_name}: {e}")
            return []

    def get_package_size_impact(self, package_name: str) -> Dict[str, int]:
        """Calculate the total size impact of a package including its dependencies."""
        total_size = 0
        dependency_sizes = {}

        def calculate_size(pkg_name: str, visited: set):
            if pkg_name in visited:
                return 0
            visited.add(pkg_name)

            info = self.get_package_info(pkg_name)
            if not info:
                return 0

            try:
                latest_version = info["info"]["version"]
                release_info = info["releases"][latest_version]

                # Calculate package size
                pkg_size = sum(
                    r["size"]
                    for r in release_info
                    if r["packagetype"] in ("bdist_wheel", "sdist")
                )

                # Add dependency sizes
                dependencies = self.get_package_dependencies(pkg_name)
                dep_size = sum(calculate_size(dep, visited) for dep in dependencies)

                dependency_sizes[pkg_name] = pkg_size
                return pkg_size + dep_size

            except Exception as e:
                logger.error(f"Error calculating size for {pkg_name}: {e}")
                return 0

        total_size = calculate_size(package_name, set())

        return {
            "total_size": total_size,
            "package_size": dependency_sizes.get(package_name, 0),
            "dependencies_size": total_size - dependency_sizes.get(package_name, 0),
            "breakdown": dependency_sizes,
        }
