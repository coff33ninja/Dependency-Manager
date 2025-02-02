"""
Command-line interface for the portable dependency checker
"""
import click
from dependency_checker import DependencyChecker

@click.command()
def main():
    """Main entry point for the portable dependency checker CLI."""
    checker = DependencyChecker()
    
    if not checker.settings_path.exists():
        click.echo("First-time setup required.")
        if not checker.setup_project():
            click.echo("Setup failed. Please check the errors and try again.")
            return
    
    if checker.settings["dependencies"]["check_on_startup"]:
        click.echo("Checking dependencies...")
        if not checker.check_all_dependencies():
            if checker.settings["dependencies"]["auto_install"]:
                click.echo("Attempting to fix dependencies...")
                if not checker.setup_project():
                    return
            else:
                click.echo("Dependency issues found. Please run setup to fix them.")
                return
    
    click.echo("Starting application...")
    checker.launch_application()

if __name__ == "__main__":
    main()
