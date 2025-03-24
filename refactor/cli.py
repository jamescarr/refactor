#!/usr/bin/env python3
"""Command-line interface for the refactor tool."""
import typer
from rich.console import Console
from typing import Optional

from . import __version__
from .commands import CommandRegistry

app = typer.Typer(
    name="refactor",
    help="Python refactoring tool using libCST",
    add_completion=False,
)
console = Console()

def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"refactor version: {__version__}")
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

# Register all commands
for command_class in CommandRegistry.get_all_commands().values():
    command = command_class()
    command.register(app)

if __name__ == "__main__":
    app()