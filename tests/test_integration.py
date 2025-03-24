"""Integration tests for Epyon CLI commands."""
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner
import pytest
from unittest.mock import patch, MagicMock

from epyon.cli import app
from epyon.core.import_replacer import replace_import
from epyon.core.def_mover import move_definition
from epyon.core.call_replacer import replace_call

runner = CliRunner()

@pytest.fixture
def setup_test_project():
    """Create a test project structure and return the paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a simple Python package structure
        (tmpdir_path / "myapp").mkdir()
        (tmpdir_path / "myapp" / "__init__.py").touch()
        (tmpdir_path / "myapp" / "core").mkdir(exist_ok=True)
        (tmpdir_path / "myapp" / "core" / "__init__.py").touch()
        (tmpdir_path / "tests").mkdir()
        
        # Create a module with a class definition
        with open(tmpdir_path / "myapp" / "models.py", "w") as f:
            f.write("""
class User:
    \"\"\"User model for the application.\"\"\"
    def __init__(self, username, email):
        self.username = username
        self.email = email
    
    def validate_token(self, token):
        # Validate the token
        return token == "valid"
""")
        
        # Create the target module to move to
        with open(tmpdir_path / "myapp" / "core" / "models.py", "w") as f:
            f.write("""
# This will receive the User class
""")
        
        # Create a module that imports the class
        with open(tmpdir_path / "myapp" / "auth.py", "w") as f:
            f.write("""
from myapp.models import User

def authenticate(username, password):
    user = User(username, "test@example.com")
    token = "valid"
    return user.validate_token(token)
""")
        
        # Create a test file that uses the class
        with open(tmpdir_path / "tests" / "test_auth.py", "w") as f:
            f.write("""
from myapp.models import User
import pytest

class TestAuth:
    def setup_method(self):
        self.user = User("testuser", "test@example.com")
    
    def test_validate_token(self):
        assert self.user.validate_token("valid")
        self.assert_token_valid("valid")
    
    def assert_token_valid(self, token):
        # Custom assertion
        assert token == "valid"
""")
        
        yield tmpdir_path

def test_cli_help():
    """Test the CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    
    # Test help for subcommands
    result = runner.invoke(app, ["replace-import", "--help"])
    assert result.exit_code == 0
    assert "Replace an import statement" in result.stdout
    
    result = runner.invoke(app, ["move-def", "--help"])
    assert result.exit_code == 0
    assert "Move a class or function definition" in result.stdout
    
    result = runner.invoke(app, ["replace-call", "--help"])
    assert result.exit_code == 0
    assert "Replace method/function calls" in result.stdout

# Create a separate test file for mocking core functions to avoid coverage issues
@pytest.mark.parametrize("command,args", [
    ("replace-import", ["myapp.models.User", "myapp.core.models.User"]),
    ("move-def", ["myapp.models.User", "myapp.core.models.User"]),
    ("replace-call", ["self.assert_token_valid", "self.assert_token_is_valid"]),
])
def test_commands_help(command, args):
    """Test that the commands display help correctly."""
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0
    assert command in result.stdout.lower() 