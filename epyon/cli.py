#!/usr/bin/env python3
"""Command-line interface for the refactor tool."""
import typer
from pathlib import Path
from typing import Optional

from . import __version__
from .commands import CommandRegistry
from .display import display
from .core.import_replacer import replace_import
from .core.def_mover import move_definition
from .core.call_replacer import replace_call

app = typer.Typer(
    name="refactor",
    help="Python refactoring tool using libCST",
    add_completion=False,
)

def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        display.show_version(__version__)
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Python refactoring tool using libCST."""
    pass

@app.command("replace-import")
def replace_import_cmd(
    old_import: str,
    new_import: str,
    directory: Path = Path("."),
    dry_run: bool = False,
    verbose: bool = False
):
    """Replace an import statement across all Python files in a directory."""
    display.verbose = verbose
    modified_count = replace_import(directory, old_import, new_import, dry_run)
    display.info(f"Modified {modified_count} files")

@app.command("move-def")
def move_def_cmd(
    old_path: str,
    new_path: str,
    directory: Path = Path("."),
    dry_run: bool = False,
    verbose: bool = False,
    workers: Optional[int] = None
):
    """
    Move a class or function definition between modules.
    
    Example:
        epyon move-def foo.bar.Baz lorem.ipsum.Baz
    
    Args:
        old_path: Original import path (e.g., 'foo.bar.Baz')
        new_path: New import path (e.g., 'lorem.ipsum.Baz')
        directory: Root directory to process
        dry_run: If True, don't modify files
        verbose: If True, show detailed output
        workers: Number of parallel workers (default: CPU count)
    """
    display.verbose = verbose
    modified_count = move_definition(directory, old_path, new_path, dry_run, workers)
    display.info(f"Modified {modified_count} files")

@app.command("replace-call")
def replace_call_cmd(
    old_call: str,
    new_call: str,
    directory: Path = Path("."),
    dry_run: bool = False,
    verbose: bool = False,
    workers: Optional[int] = None
):
    """
    Replace method/function calls across Python files in a directory.
    
    Example:
        epyon replace-call "self.assert_401_UNAUTHORIZED" "self.assert_403_FORBIDDEN"
    
    Args:
        old_call: Original function call (e.g., 'self.assert_401_UNAUTHORIZED')
        new_call: New function call (e.g., 'self.assert_403_FORBIDDEN')
        directory: Root directory to process
        dry_run: If True, don't modify files
        verbose: If True, show detailed output
        workers: Number of parallel workers (default: CPU count)
    """
    display.verbose = verbose
    modified_count = replace_call(directory, old_call, new_call, dry_run, workers)
    display.info(f"Modified {modified_count} files")

# Register all commands
for command_class in CommandRegistry.get_all_commands().values():
    command = command_class()
    command.register(app)

if __name__ == "__main__":
    app()