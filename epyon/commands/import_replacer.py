"""Import replacement command."""
from pathlib import Path
from typing import Optional
import typer

from ..core.import_replacer import process_file, find_python_files
from ..display import display
from .base import Command, register_command

@register_command
class ImportReplacerCommand(Command):
    """Command to replace imports in Python files."""
    
    name = "replace-import"
    help = "Replace an import statement across Python files"
    
    def register(self, app: typer.Typer) -> None:
        """Register the command with the CLI app."""
        
        @app.command(name=self.name, help=self.help)
        def replace_import(
            old_import: str = typer.Argument(..., help="The import to replace (e.g., 'foo.bar.baz.Class')"),
            new_import: str = typer.Argument(..., help="The replacement import (e.g., 'new.module.Class')"),
            path: Path = typer.Argument(..., help="Path to Python file or directory"),
            dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without modifying files"),
            verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
        ) -> None:
            """Replace imports in Python files."""
            if not path.exists():
                display.error(f"Path '{path}' does not exist")
                raise typer.Exit(1)
            
            # Process a single file
            if path.is_file():
                if not str(path).endswith('.py'):
                    display.error("Path must be a Python file")
                    raise typer.Exit(1)
                files = [path]
            
            # Process a directory
            else:
                files = find_python_files(path)
                if not files:
                    display.warning(f"No Python files found in {path}")
                    return
            
            # Process each file
            modified_count = 0
            for file_path in files:
                if process_file(file_path, old_import, new_import, dry_run):
                    modified_count += 1
            
            # Show summary
            if dry_run:
                display.show_dry_run_notice()
            
            display.show_summary(modified_count, len(files)) 