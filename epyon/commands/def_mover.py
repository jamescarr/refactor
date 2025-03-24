"""Command for moving definitions between modules."""
from pathlib import Path
from typing import Optional
import typer

from ..core.def_mover import process_file_move, find_module_file, find_python_files
from ..display import display
from .base import Command, register_command

@register_command
class DefMoverCommand(Command):
    """Command to move class/function definitions between modules."""
    
    name = "move-def"
    help = "Move a class or function definition to a different module"
    
    def register(self, app: typer.Typer) -> None:
        """Register the command with the CLI app."""
        
        @app.command(name=self.name, help=self.help)
        def move_def(
            old_path: str = typer.Argument(..., help="The current import path (e.g., 'foo.bar.Baz')"),
            new_path: str = typer.Argument(..., help="The new import path (e.g., 'lorem.ipsum.Baz')"),
            path: Path = typer.Argument(..., help="Path to Python file or directory to update imports"),
            dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without modifying files"),
            verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
        ) -> None:
            """Move a class or function definition to a different module."""
            if not path.exists():
                display.error(f"Path '{path}' does not exist")
                raise typer.Exit(1)
            
            # Find all Python files to process
            files = [path] if path.is_file() else find_python_files(path)
            if not files:
                display.warning(f"No Python files found in {path}")
                return
            
            # Track changes and the extracted definition
            modified_count = 0
            extracted_def = None
            
            # First pass: find and extract the definition
            for file_path in files:
                changes_made, def_node = process_file_move(
                    file_path,
                    old_path,
                    new_path,
                    extracted_def=None,
                    dry_run=dry_run
                )
                if changes_made:
                    modified_count += 1
                if def_node is not None:
                    extracted_def = def_node
                    break
            
            if extracted_def is None:
                display.error(f"Could not find definition for {old_path}")
                raise typer.Exit(1)
            
            # Second pass: update imports and add definition to target
            for file_path in files:
                changes_made, _ = process_file_move(
                    file_path,
                    old_path,
                    new_path,
                    extracted_def=extracted_def,
                    dry_run=dry_run
                )
                if changes_made:
                    modified_count += 1
            
            # Show summary
            if dry_run:
                display.show_dry_run_notice()
            
            display.show_summary(modified_count, len(files)) 