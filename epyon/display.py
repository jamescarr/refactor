"""Display utilities for Epyon."""
from rich.console import Console
from rich.syntax import Syntax
from rich.theme import Theme
from rich.panel import Panel
from rich import print as rprint
from difflib import unified_diff
from pathlib import Path
from typing import Optional

# Create a custom theme for Gundam-inspired colors
theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
    "path": "blue",
    "diff.plus": "green",
    "diff.minus": "red",
    "diff.at": "cyan",
})

console = Console(theme=theme)

def show_diff(old_content: str, new_content: str, file_path: Optional[Path] = None) -> None:
    """Display a unified diff of the changes."""
    if old_content == new_content:
        return

    # Generate unified diff
    diff_lines = list(unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='Original',
        tofile='Modified',
        lineterm=''
    ))

    # If we have a file path, show it in a header
    if file_path:
        console.print(f"\n[path]Transforming {file_path}[/path]")

    # Print the diff with syntax highlighting
    for line in diff_lines:
        if line.startswith('+'):
            console.print(f"[diff.plus]{line.rstrip()}[/diff.plus]")
        elif line.startswith('-'):
            console.print(f"[diff.minus]{line.rstrip()}[/diff.minus]")
        elif line.startswith('@'):
            console.print(f"[diff.at]{line.rstrip()}[/diff.at]")
        else:
            console.print(line.rstrip())

def show_code(content: str, file_path: Optional[Path] = None) -> None:
    """Display code with syntax highlighting."""
    syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
    if file_path:
        console.print(f"\n[path]{file_path}[/path]")
    console.print(syntax)

def error(message: str) -> None:
    """Display an error message."""
    console.print(f"[error]Error:[/error] {message}")

def warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[warning]Warning:[/warning] {message}")

def success(message: str) -> None:
    """Display a success message."""
    console.print(f"[success]Success:[/success] {message}")

def info(message: str) -> None:
    """Display an info message."""
    console.print(f"[info]Info:[/info] {message}")

def operation_summary(total: int, modified: int, errors: int = 0) -> None:
    """Display an operation summary."""
    rprint(Panel.fit(
        f"[bold]Operation Summary[/bold]\n"
        f"Total files processed: {total}\n"
        f"Files modified: [success]{modified}[/success]\n"
        f"Errors encountered: [error]{errors}[/error]"
    ))

def show_dry_run_notice() -> None:
    """Display dry run mode notice."""
    console.print("\n[yellow]Running in dry-run mode - no files were modified[/]")

def show_summary(modified_count: int, total_files: int) -> None:
    """Display operation summary."""
    if modified_count > 0:
        console.print(f"\n[green]Modified imports in {modified_count} of {total_files} files[/]")
    else:
        console.print("\n[yellow]No matching imports found[/]")

def show_version(version: str) -> None:
    """Display version information."""
    console.print(f"refactor version: {version}")

display = Display() 