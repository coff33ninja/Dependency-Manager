"""
Documentation generator for Python environment setup
"""

import os
import json
from typing import Dict, List
from pathlib import Path
import markdown
from jinja2 import Template


class DocumentationGenerator:
    def __init__(self, env_report: Dict = None):
        self.env_report = env_report
        self.templates_dir = Path(__file__).parent / "templates"

    def generate_markdown(self) -> str:
        """Generate markdown documentation from environment report."""
        sections = []

        # Basic Information
        sections.append("# Python Environment Setup Guide\n")

        if self.env_report:
            # Python Information
            sections.append("## Python Installation\n")
            py_info = self.env_report["python_info"]
            sections.append(f"- Python Version: {py_info['version'].split()[0]}")
            sections.append(f"- Implementation: {py_info['implementation']}")
            sections.append(f"- Location: {py_info['executable']}\n")

            # Virtual Environment
            venv_info = self.env_report["virtualenv_info"]
            sections.append("## Virtual Environment\n")
            if venv_info["is_virtualenv"]:
                sections.append("✅ Running in a virtual environment")
                sections.append(f"- Location: {venv_info['virtualenv_path']}")
                sections.append(
                    f"- Python Binary: {venv_info.get('venv_python', 'N/A')}\n"
                )
            else:
                sections.append("⚠️ Not running in a virtual environment")
                sections.append("Consider creating one using:\n")
                sections.append("```bash")
                sections.append("python -m venv .venv")
                sections.append("# On Windows:")
                sections.append(".venv\\Scripts\\activate")
                sections.append("# On Unix:")
                sections.append("source .venv/bin/activate")
                sections.append("```\n")

            # Development Tools
            sections.append("## Development Tools\n")
            dev_tools = self.env_report["development_tools"]

            # Package Managers
            sections.append("### Package Managers")
            for name, info in dev_tools["package_managers"].items():
                if info["available"]:
                    sections.append(
                        f"✅ {name} ({info.get('version', 'version unknown')})"
                    )
                else:
                    sections.append(f"❌ {name} (not installed)")
            sections.append("")

            # Testing Tools
            sections.append("### Testing Tools")
            for name, info in dev_tools["testing"].items():
                if info.get("available"):
                    sections.append(f"✅ {name}")
                else:
                    sections.append(f"❌ {name}")
            sections.append("")

            # Linters and Formatters
            sections.append("### Code Quality Tools")
            for name, info in dev_tools["linters_formatters"].items():
                if info["available"]:
                    sections.append(
                        f"✅ {name} ({info.get('version', 'version unknown')})"
                    )
                else:
                    sections.append(f"❌ {name}")
            sections.append("")

        # General Setup Instructions
        sections.append("## Setup Instructions\n")
        sections.append("1. **Clone the Repository**")
        sections.append("   ```bash")
        sections.append("   git clone <repository-url>")
        sections.append("   cd <project-directory>")
        sections.append("   ```\n")

        sections.append("2. **Create Virtual Environment**")
        sections.append("   ```bash")
        sections.append("   python -m venv .venv")
        sections.append("   ```\n")

        sections.append("3. **Activate Virtual Environment**")
        sections.append("   ```bash")
        sections.append("   # On Windows:")
        sections.append("   .venv\\Scripts\\activate")
        sections.append("   # On Unix:")
        sections.append("   source .venv/bin/activate")
        sections.append("   ```\n")

        sections.append("4. **Install Dependencies**")
        sections.append("   ```bash")
        sections.append("   pip install -r requirements.txt")
        sections.append("   ```\n")

        sections.append("5. **Verify Installation**")
        sections.append("   ```bash")
        sections.append("   python run_app.py --check")
        sections.append("   ```\n")

        # Troubleshooting
        sections.append("## Troubleshooting\n")
        sections.append("### Common Issues\n")
        sections.append("1. **Package Installation Fails**")
        sections.append(
            "   - Ensure pip is up to date: `python -m pip install --upgrade pip`"
        )
        sections.append(
            "   - Try installing packages one by one to identify problematic dependencies"
        )
        sections.append(
            "   - Check for system-level dependencies required by some packages\n"
        )

        sections.append("2. **Python Version Mismatch**")
        sections.append("   - Ensure you're using the correct Python version")
        sections.append("   - Check `python --version` output")
        sections.append(
            "   - Use pyenv or similar tools to manage multiple Python versions\n"
        )

        sections.append("3. **Virtual Environment Issues**")
        sections.append("   - Delete the virtual environment and recreate it")
        sections.append(
            "   - Ensure virtualenv/venv is installed: `pip install virtualenv`"
        )
        sections.append("   - Check for system PATH issues\n")

        return "\n".join(sections)

    def generate_html(self) -> str:
        """Generate HTML documentation from markdown."""
        md_content = self.generate_markdown()
        html_content = markdown.markdown(
            md_content, extensions=["fenced_code", "tables"]
        )

        # Basic HTML template
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python Environment Setup Guide</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                }
                code {
                    background-color: #f6f8fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                }
                pre {
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 6px;
                    overflow-x: auto;
                }
                h1, h2, h3 {
                    color: #24292e;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                }
                h1 { font-size: 2em; }
                h2 { font-size: 1.5em; }
                h3 { font-size: 1.25em; }
                .emoji { font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; }
            </style>
        </head>
        <body>
            {{ content }}
        </body>
        </html>
        """

        template = Template(template)
        return template.render(content=html_content)

    def save_documentation(self, output_dir: str = "."):
        """Save both markdown and HTML documentation."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown
        md_path = output_dir / "setup_guide.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.generate_markdown())

        # Save HTML
        html_path = output_dir / "setup_guide.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.generate_html())

        return {"markdown": str(md_path), "html": str(html_path)}
