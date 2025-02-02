# Scripts Project

This project provides a portable solution for managing dependencies, environments, and installations for Python applications. It automates package management and ensures scripts are executed with the correct dependencies.

## Project Structure

```plaintext
root/
    ├── settings.json
    ├── run_app.py
    ├── requirements.txt
    ├── main.py
    ├── INSTRUCTIONS.txt
    └── portable/
        ├── __init__.py
        ├── updater.py
        ├── requirements_manager.py
        ├── requirements.py
        ├── package_metadata.py
        ├── logger.py
        ├── integration.py
        ├── installer_updater.py
        ├── installers.py
        ├── environment_manager.py
        ├── environment_analyzer.py
        ├── documentation_generator.py
        ├── dependency_checker.py
        ├── cli.py
        └── base_types.py
```

## Core Components

### Portable Package (`portable/`)
Contains the core functionality required for dependency management, environment handling, and installation automation.

- **`base_types.py`** - Defines base types and data structures.
- **`cli.py`** - Implements the command-line interface.
- **`dependency_checker.py`** - Verifies and manages dependencies.
- **`documentation_generator.py`** - Generates project documentation.
- **`environment_analyzer.py`** - Analyzes runtime environment details.
- **`environment_manager.py`** - Manages portable environments.
- **`installers.py`** - Handles installation procedures.
- **`installer_updater.py`** - Updates installed components.
- **`integration.py`** - Provides integration utilities.
- **`logger.py`** - Handles logging functionality.
- **`package_metadata.py`** - Manages package metadata.
- **`requirements.py`** - Defines requirement specifications.
- **`requirements_manager.py`** - Manages dependency requirements.
- **`updater.py`** - Handles update management.

### Root Files
- **`settings.json`** - Global configuration file.
- **`run_app.py`** - Main entry point for launching applications.
- **`requirements.txt`** - Lists required dependencies.
- **`main.py`** - Sample main application script.
- **`Readme.md`** - Documentation and usage guide.

## Getting Started

### 1. Prerequisites
- Python must be installed and available in `PATH`.
- Internet access is required for package installation.

### 2. Features
✔ Automates dependency management  
✔ Supports both virtual environments and global installations  
✔ Configurable through `settings.json`  
✔ Works with any Python project  
✔ Ensures correct package versions are installed  
✔ Acts as a unified launcher for scripts  

### 3. Usage
To integrate this into your project:

**a. Copy the following files into your project root:**
- The `portable/` folder
- `run_app.py`
- `settings.json` (optional)

**b. Modify `settings.json` as needed** (or leave it as default for automatic configuration).

**c. Run `run_app.py` to:**
- Verify and install dependencies.
- Set up a virtual environment (if enabled).
- Launch the main application script.

## Configuration (`settings.json`)
The `settings.json` file allows customization of the environment setup and dependency management.

### Available Settings:
- **`use_virtual_env`** *(Boolean)* – Whether to use a virtual environment.
- **`main_script`** *(String)* – Path to the main script to execute.
- **`install_packages`** *(Boolean)* – Whether to install missing dependencies automatically.
- **`custom_requirements`** *(String)* – Custom `requirements.txt` path (optional).

## Integration Steps
1. Copy the `portable/` folder and `run_app.py` into your project.
2. Modify `settings.json` to fit your project needs.
3. Run `run_app.py` to initiate setup and launch your application.
4. Follow any interactive prompts (if applicable).

## Troubleshooting

- **Missing dependencies?**  
  - Check the logs for detailed error messages and ensure `requirements.txt` is correctly formatted.
- **Python not found?**  
  - Ensure Python is installed and added to the system `PATH`.
- **Packages not installing?**  
  - Verify internet access and check if `pip` is working (`python -m pip --version`).
- **Permission issues?**  
  - Run the script with administrator/root privileges if necessary.

## Script Overview

### `run_app.py` - All-in-One Dependency Fixer & Launcher
This script ensures that all required dependencies are installed and up to date before executing the main Python script.

### Key Features:

#### Dependency Management
✅ Scans for a `requirements.txt` file in the project root.  
✅ Installs or updates missing dependencies automatically.  
✅ Generates a log report of installed/updated packages.  
✅ Handles its own dependencies without user intervention.  

#### Virtual Environment Support (Optional)
✅ Creates a virtual environment (`venv`) in the root directory.  
✅ Installs dependencies inside the `venv` when enabled.  

#### Portable Execution
✅ Works with any Python scripts placed in the same directory.  
✅ Supports customizable configurations via `settings.json`.  
✅ Can be packaged as a standalone, portable launcher.  

#### Application Launcher
✅ Functions as a unified launcher for Python applications.  
✅ Ensures the correct environment and dependencies before execution.  

## Final Notes
This script simplifies dependency management and application launching, making it a versatile tool for both development and deployment. Whether you're working in a virtual environment or globally, it ensures a seamless execution experience. Well I hope atleast :-)

