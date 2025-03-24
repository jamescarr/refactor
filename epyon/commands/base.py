"""Base command infrastructure."""
from abc import ABC, abstractmethod
from typing import Dict, Type

class Command(ABC):
    """Base class for all commands."""
    
    name: str  # Command name used in CLI
    help: str  # Help text for the command
    
    @abstractmethod
    def register(self, app) -> None:
        """Register the command with the CLI app."""
        pass

class CommandRegistry:
    """Registry for command plugins."""
    
    _commands: Dict[str, Type[Command]] = {}
    
    @classmethod
    def register(cls, command_class: Type[Command]) -> None:
        """Register a command class."""
        if not hasattr(command_class, 'name'):
            raise ValueError(f"Command class {command_class.__name__} must have a 'name' attribute")
        cls._commands[command_class.name] = command_class
    
    @classmethod
    def get_command(cls, name: str) -> Type[Command]:
        """Get a command class by name."""
        return cls._commands.get(name)
    
    @classmethod
    def get_all_commands(cls) -> Dict[str, Type[Command]]:
        """Get all registered commands."""
        return cls._commands.copy()

def register_command(command_class: Type[Command]) -> Type[Command]:
    """Decorator to register a command."""
    CommandRegistry.register(command_class)
    return command_class 