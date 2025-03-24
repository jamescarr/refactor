"""Import replacement command."""
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from ..core.import_replacer import process_file, find_python_files
from .base import Command, register_command

console = Console()

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
                console.print(f"[red]Error: Path '{path}' does not exist[/]")
                raise typer.Exit(1)
            
            # Process a single file
            if path.is_file():
                if not str(path).endswith('.py'):
                    console.print(f"[red]Error: Path must be a Python file[/]")
                    raise typer.Exit(1)
                files = [path]
            
            # Process a directory
            else:
                files = find_python_files(path)
                if not files:
                    console.print(f"[yellow]Warning: No Python files found in {path}[/]")
                    return
            
            # Process each file
            modified_count = 0
            for file_path in files:
                if process_file(file_path, old_import, new_import, dry_run):
                    modified_count += 1
            
            # Show summary
            if dry_run:
                console.print("\n[yellow]Running in dry-run mode - no files were modified[/]")
            
            if modified_count > 0:
                console.print(f"\n[green]Modified imports in {modified_count} of {len(files)} files[/]")
            else:
                console.print("\n[yellow]No matching imports found[/]") 