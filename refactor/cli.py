#!/usr/bin/env python3
"""
A command-line tool for refactoring Python imports using libCST.

Usage:
    refactor replace_import old_import new_import path [--dry-run]

Example:
    refactor replace_import foo.bar.baz.PermissionDenied rest_framework.exc.PermissionDenied ./my_project
"""
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.syntax import Syntax
from refactor.core.import_replacer import process_file, find_python_files
from typing import Optional
from rich import print
from refactor import __version__

app = typer.Typer(
    name="refactor",
    help="Python refactoring tool using libCST",
    add_completion=False,
)
console = Console()

def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        print(f"refactor version: {__version__}")
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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """
    Python refactoring tool using libCST.
    """
    pass

@app.command()
def replace_import(
    old_import: str = typer.Argument(..., help="The import to replace (e.g., 'foo.bar.baz.PermissionDenied')"),
    new_import: str = typer.Argument(..., help="The replacement import (e.g., 'rest_framework.exc.PermissionDenied')"),
    path: str = typer.Argument(..., help="Path to the Python project or file to refactor"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show changes without modifying files"),
):
    """
    Replace an import throughout a Python project or file.

    Examples:
        Replace a single class import:
        $ refactor replace_import foo.bar.baz.PermissionDenied rest_framework.exc.PermissionDenied ./my_project

        Dry run to preview changes:
        $ refactor replace_import foo.bar.baz.PermissionDenied rest_framework.exc.PermissionDenied ./my_project --dry-run
    """
    target_path = Path(path)

    if not target_path.exists():
        console.print(f"[bold red]Error: Path '{path}' does not exist.[/]")
        raise typer.Exit(code=1)

    files_to_process = []
    if target_path.is_file() and target_path.suffix == '.py':
        files_to_process = [target_path]
    elif target_path.is_dir():
        files_to_process = find_python_files(target_path)
    else:
        console.print(f"[bold red]Error: Path '{path}' must be a Python file or directory.[/]")
        raise typer.Exit(code=1)

    if not files_to_process:
        console.print(f"[bold yellow]Warning: No Python files found in '{path}'.[/]")
        raise typer.Exit(code=0)

    if dry_run:
        console.print("[bold yellow]Running in dry-run mode. No files will be changed.[/]")

    # Process all files
    total_files = len(files_to_process)
    changed_files = 0

    with console.status(f"Processing {total_files} Python files...") as status:
        for file_path in files_to_process:
            status.update(f"Processing {file_path}...")
            if process_file(file_path, old_import, new_import, dry_run):
                changed_files += 1

    # Print summary
    if changed_files > 0:
        console.print(f"[bold green]Completed: Modified imports in {changed_files} of {total_files} files.[/]")
    else:
        console.print(f"[bold yellow]Completed: No matching imports found in {total_files} files.[/]")

    raise typer.Exit(code=0)

if __name__ == "__main__":
    app()