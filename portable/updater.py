"""
Updater for the portable dependency checker
"""
import subprocess
import sys

class Updater:
    def __init__(self, package_name: str):
        self.package_name = package_name

    def check_for_updates(self) -> bool:
        """Check for updates to the package."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", self.package_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("Package updated successfully.")
                return True
            else:
                print("Failed to update package:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False
