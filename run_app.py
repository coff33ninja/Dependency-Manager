#!/usr/bin/env python3
"""
Main launcher script for the project
"""
import os
import sys
import logging
import traceback
import argparse
from pathlib import Path

# Add parent directory to Python path to make portable package importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from portable.integration import Integration
from portable.logger import LogManager

def parse_arguments():
    parser = argparse.ArgumentParser(description="Dependency Checker and Application Launcher")
    parser.add_argument(
        "--app", "-a",
        help="Path to the main application to launch",
        default=None
    )
    parser.add_argument(
        "--requirements", "-r",
        help="Path to requirements.txt file",
        default="requirements.txt"
    )
    parser.add_argument(
        "--venv", "-v",
        help="Create/use virtual environment",
        action="store_true"
    )
    parser.add_argument(
        "--report",
        help="Generate dependency report",
        action="store_true"
    )
    return parser.parse_args()

def main():
    """Main application entry point"""
    try:
        # Initialize logging
        log_manager = LogManager()
        logger = log_manager.get_logger()
        logger.info("Starting dependency checker and launcher...")

        # Parse command line arguments
        args = parse_arguments()

        # Initialize integration
        integration = Integration()

        # Generate report if requested
        if args.report:
            report = integration.generate_report()
            print("\nEnvironment and Dependency Report:")
            print("-" * 40)
            print(f"Python: {report['environment']['python_version']}")
            print(f"Platform: {report['environment']['platform']}")
            print(f"Virtual Environment: {'Active' if report['environment']['is_venv'] else 'Inactive'}")
            if report['environment']['is_venv']:
                print(f"Virtual Environment Path: {report['environment']['venv_path']}")
            print("\nDependencies Status:", report['dependencies']['status'])
            for dep in report['dependencies']['results']:
                print(f"- {dep['name']}: {'✓' if dep['status'] == 'success' else '✗'} "
                      f"(required: {dep['required_version']}, found: {dep['version']})")
            return 0

        # Setup project
        logger.info("Setting up project environment...")
        if not integration.setup_project(args.requirements):
            logger.error("Failed to setup project")
            return 1

        # Launch application if specified
        if args.app:
            logger.info(f"Launching application: {args.app}")
            if not integration.launch_application(args.app):
                logger.error("Application launch failed")
                return 1
        else:
            print("\nProject setup completed successfully!")
            print("Use --app option to launch your application")

        return 0

    except Exception as e:
        error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Fatal error:\n{error_msg}")
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())