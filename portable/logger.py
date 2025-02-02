"""
Logging configuration for the dependency checker
"""
import logging
import os
from datetime import datetime
from pathlib import Path

class LogManager:
    def __init__(self, log_file: str = "dependency_checker.log"):
        self.log_file = log_file
        self._setup_logging()

    def _setup_logging(self):
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Generate log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"{timestamp}_{self.log_file}"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("DependencyChecker")
        self.logger.info(f"Logging initialized. Log file: {log_path}")

    def get_logger(self):
        return self.logger