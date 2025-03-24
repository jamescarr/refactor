"""Tests for the display module."""
from pathlib import Path
from epyon.display import Display, console

def test_show_diff_with_changes(capsys):
    """Test showing diff when there are changes."""
    old_content = """from gundam.wing.zero import WingZero
from gundam.wing.weapons import BeamSaber
"""
    new_content = """from gundam.wing.custom import WingZeroCustom
from gundam.wing.weapons import BeamSaber
"""
    
    # Temporarily disable color for testing
    console.no_color = True
    Display.show_diff(old_content, new_content, Path("test.py"))
    captured = capsys.readouterr()
    
    # Verify diff output
    assert "Transforming test.py" in captured.out
    assert "-from gundam.wing.zero import WingZero" in captured.out
    assert "+from gundam.wing.custom import WingZeroCustom" in captured.out
    assert "from gundam.wing.weapons import BeamSaber" in captured.out

def test_show_diff_no_changes(capsys):
    """Test showing diff when there are no changes."""
    content = """from gundam.wing.zero import WingZero"""
    
    console.no_color = True
    Display.show_diff(content, content, Path("test.py"))
    captured = capsys.readouterr()
    
    # Should not output anything when there are no changes
    assert captured.out == ""

def test_show_diff_multiline_changes(capsys):
    """Test showing diff with multi-line import changes."""
    old_content = """from gundam.wing.pilots import (
    HeeroYuy,
    DuoMaxwell,
    TrowaBarton
)"""
    new_content = """from gundam.wing.pilots import (
    HeeroYuy,
    TrowaBarton
)"""
    
    console.no_color = True
    Display.show_diff(old_content, new_content, Path("test.py"))
    captured = capsys.readouterr()
    
    # Verify diff shows the correct changes
    assert "Transforming test.py" in captured.out
    assert "-    DuoMaxwell," in captured.out
    assert "     HeeroYuy," in captured.out
    assert "     TrowaBarton" in captured.out 