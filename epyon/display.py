"""Display utilities for Epyon."""
from rich.console import Console
from rich.syntax import Syntax
from rich.theme import Theme
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich import print as rprint
from difflib import unified_diff
from pathlib import Path
from typing import Optional, List, Any

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

class Display:
    """Display utilities for Epyon."""
    
    def __init__(self):
        """Initialize the display with default settings."""
        self.verbose = False
    
    @staticmethod
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

    @staticmethod
    def show_code(content: str, file_path: Optional[Path] = None) -> None:
        """Display code with syntax highlighting."""
        syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
        if file_path:
            console.print(f"\n[path]{file_path}[/path]")
        console.print(syntax)

    def error(self, message: str) -> None:
        """Display an error message."""
        console.print(f"[error]Error:[/error] {message}")

    def warning(self, message: str) -> None:
        """Display a warning message."""
        console.print(f"[warning]Warning:[/warning] {message}")

    def success(self, message: str) -> None:
        """Display a success message."""
        console.print(f"[success]Success:[/success] {message}")

    def info(self, message: str) -> None:
        """Display an info message."""
        if self.verbose:
            console.print(f"[info]Info:[/info] {message}")
        else:
            # Only show important info messages in non-verbose mode
            if message.startswith("Found") or message.startswith("Modified") or message.startswith("Scanning"):
                console.print(f"[info]Info:[/info] {message}")

    @staticmethod
    def operation_summary(total: int, modified: int, errors: int = 0) -> None:
        """Display an operation summary."""
        rprint(Panel.fit(
            f"[bold]Operation Summary[/bold]\n"
            f"Total files processed: {total}\n"
            f"Files modified: [success]{modified}[/success]\n"
            f"Errors encountered: [error]{errors}[/error]"
        ))

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
        console.print(f"[bold cyan]Epyon[/bold cyan] version [bold]{version}[/bold]")
        
    def track_parallel_progress(self, items: List[Any], description: str = "Processing") -> None:
        """
        Track progress of parallel operations.
        Only shows progress if verbose mode is enabled.
        
        Args:
            items: List of items being processed
            description: Description of the operation
        """
        if not self.verbose:
            return
            
        total_items = len(items)
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(f"[cyan]{description}...", total=total_items)
            
            # This is just a placeholder - actual progress tracking would require modifications
            # to the parallel processing functions to update progress
            progress.update(task, completed=total_items)
            
# Create a singleton instance
display = Display() 