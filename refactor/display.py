"""Display utilities for console output."""
from pathlib import Path
from typing import List
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class Display:
    """Handle console output and formatting."""

    @staticmethod
    def error(message: str) -> None:
        """Display an error message."""
        console.print(f"[red]Error: {message}[/]")

    @staticmethod
    def warning(message: str) -> None:
        """Display a warning message."""
        console.print(f"[yellow]Warning: {message}[/]")

    @staticmethod
    def success(message: str) -> None:
        """Display a success message."""
        console.print(f"[green]{message}[/]")

    @staticmethod
    def info(message: str) -> None:
        """Display an info message."""
        console.print(message)

    @staticmethod
    def show_code(content: str, file_path: Path) -> None:
        """Display formatted code with syntax highlighting."""
        console.print(f"[bold green]Changes in {file_path}:[/]")
        syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
        console.print(syntax)

    @staticmethod
    def show_dry_run_notice() -> None:
        """Display dry run mode notice."""
        console.print("\n[yellow]Running in dry-run mode - no files were modified[/]")

    @staticmethod
    def show_summary(modified_count: int, total_files: int) -> None:
        """Display operation summary."""
        if modified_count > 0:
            console.print(f"\n[green]Modified imports in {modified_count} of {total_files} files[/]")
        else:
            console.print("\n[yellow]No matching imports found[/]")

    @staticmethod
    def show_version(version: str) -> None:
        """Display version information."""
        console.print(f"refactor version: {version}")

display = Display() 