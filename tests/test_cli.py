"""Tests for the CLI module."""
from pathlib import Path
import pytest
from typer.testing import CliRunner
from epyon.cli import app
from epyon import __version__

runner = CliRunner()

def test_version():
    """Test the version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"Epyon version {__version__}" in result.stdout

def test_replace_import_nonexistent_path():
    """Test replace_import with a nonexistent path."""
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        "nonexistent_path"
    ])
    assert result.exit_code == 1
    assert "Error: Path 'nonexistent_path' does not exist" in result.stdout

def test_replace_import_invalid_path(tmp_path):
    """Test replace_import with an invalid file (not a Python file)."""
    invalid_file = tmp_path / "test.txt"
    invalid_file.touch()
    
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        str(invalid_file)
    ])
    assert result.exit_code == 1
    assert "Error: Path" in result.stdout
    assert "must be a Python file" in result.stdout.replace("\n", " ")

def test_replace_import_empty_directory(tmp_path):
    """Test replace_import with an empty directory."""
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        str(tmp_path)
    ])
    assert result.exit_code == 0
    assert "Warning: No Python files found" in result.stdout

def test_replace_import_dry_run(tmp_path):
    """Test replace_import with dry run option."""
    # Create a test Python file
    test_file = tmp_path / "test.py"
    test_file.write_text("""from gundam.wing.zero import WingZero
x = WingZero()
""")
    
    result = runner.invoke(app, [
        "replace-import",
        "gundam.wing.zero.WingZero",
        "gundam.wing.custom.WingZeroCustom",
        str(test_file),
        "--dry-run"
    ])
    assert result.exit_code == 0
    assert "Running in dry-run mode" in result.stdout
    assert "-from gundam.wing.zero import WingZero" in result.stdout
    assert "+from gundam.wing.custom import WingZeroCustom" in result.stdout
    
    # Verify file wasn't modified
    assert "from gundam.wing.zero import WingZero" in test_file.read_text()

def test_replace_import_actual_change(tmp_path):
    """Test replace_import with actual file modification."""
    # Create a test Python file
    test_file = tmp_path / "test.py"
    test_file.write_text("""from gundam.wing.epyon import BeamSaber
x = BeamSaber()
""")
    
    result = runner.invoke(app, [
        "replace-import",
        "gundam.wing.epyon.BeamSaber",
        "gundam.wing.tallgeese.BeamSaber",
        str(test_file)
    ])
    assert result.exit_code == 0
    assert "Modified imports in 1 of 1 files" in result.stdout
    assert "-from gundam.wing.epyon import BeamSaber" in result.stdout
    assert "+from gundam.wing.tallgeese import BeamSaber" in result.stdout
    
    # Verify file was modified
    modified_content = test_file.read_text()
    assert "from gundam.wing.tallgeese import BeamSaber" in modified_content
    assert "from gundam.wing.epyon import BeamSaber" not in modified_content

def test_replace_import_multiple_files(tmp_path):
    """Test replace_import with multiple Python files."""
    # Create test files
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    
    files = [
        tmp_path / "test1.py",
        tmp_path / "dir1" / "test2.py",
        tmp_path / "dir2" / "test3.py"
    ]
    
    for file in files:
        file.write_text("""
from old.module import Class
x = Class()
""")
    
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        str(tmp_path)
    ])
    assert result.exit_code == 0
    assert "Modified imports in 3 of 3 files" in result.stdout
    
    # Verify all files were modified
    for file in files:
        content = file.read_text()
        assert "from new.module import Class" in content
        assert "from old.module import Class" not in content

def test_replace_import_no_matches(tmp_path):
    """Test replace_import when no matching imports are found."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
from different.module import Class
x = Class()
""")
    
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        str(test_file)
    ])
    assert result.exit_code == 0
    assert "No matching imports found" in result.stdout

def test_verbose_output(tmp_path):
    """Test verbose output option."""
    result = runner.invoke(app, [
        "replace-import",
        "old.module.Class",
        "new.module.Class",
        str(tmp_path),
        "--verbose"
    ])
    assert result.exit_code == 0
    assert "Warning: No Python files found" in result.stdout

def test_replace_import_parenthesized(tmp_path):
    """Test replacing an import from a parenthesized group."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""from gundam.wing.pilots import (
    HeeroYuy,
    DuoMaxwell,
    TrowaBarton
)

x = HeeroYuy()
y = DuoMaxwell()
z = TrowaBarton()
""")
    
    result = runner.invoke(app, [
        "replace-import",
        "gundam.wing.pilots.DuoMaxwell",
        "gundam.wing.pilots.QuatraWinner",
        str(test_file)
    ])
    assert result.exit_code == 0
    assert "Modified imports in 1 of 1 files" in result.stdout
    assert "-    DuoMaxwell," in result.stdout
    assert "     HeeroYuy," in result.stdout
    assert "     TrowaBarton" in result.stdout
    assert "+from gundam.wing.pilots import QuatraWinner" in result.stdout
    
    # Verify file was modified correctly
    modified_content = test_file.read_text()
    
    # The import statements should be at the start of the file
    import_section = modified_content.split('\n\n')[0]
    assert "from gundam.wing.pilots import QuatraWinner" in import_section
    assert "from gundam.wing.pilots import (" in import_section
    assert "HeeroYuy," in import_section
    assert "TrowaBarton" in import_section
    assert "DuoMaxwell" not in import_section 