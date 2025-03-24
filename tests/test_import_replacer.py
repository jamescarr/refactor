"""Tests for the import_replacer module."""
import pytest
from pathlib import Path
import libcst as cst
from epyon.core.import_replacer import ImportReplacer, process_file, find_python_files

def test_simple_import_replacement():
    """Test basic import replacement functionality."""
    source_code = """
from foo.bar import OldClass
from other.module import Something
"""
    transformer = ImportReplacer("foo.bar.OldClass", "new.module.NewClass")
    module = cst.parse_module(source_code)
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "from new.module import NewClass" in modified.code
    assert "from other.module import Something" in modified.code
    assert "from foo.bar import OldClass" not in modified.code

def test_multiple_imports_same_line():
    """Test handling multiple imports on the same line."""
    source_code = """
from foo.bar import OldClass, AnotherClass
"""
    transformer = ImportReplacer("foo.bar.OldClass", "new.module.NewClass")
    module = cst.parse_module(source_code)
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "from foo.bar import AnotherClass" in modified.code
    assert "from new.module import NewClass" in modified.code

def test_no_matching_import():
    """Test behavior when no matching import is found."""
    source_code = """
from other.module import Something
"""
    transformer = ImportReplacer("foo.bar.OldClass", "new.module.NewClass")
    module = cst.parse_module(source_code)
    modified = module.visit(transformer)
    
    assert not transformer.changes_made
    assert modified.code.strip() == source_code.strip()

def test_nested_module_import():
    """Test replacement in deeply nested module imports."""
    source_code = """
from foo.bar.baz.qux import OldClass
"""
    transformer = ImportReplacer("foo.bar.baz.qux.OldClass", "new.thing.NewClass")
    module = cst.parse_module(source_code)
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "from new.thing import NewClass" in modified.code

def test_process_file(tmp_path):
    """Test the process_file function."""
    # Create a temporary Python file
    test_file = tmp_path / "test.py"
    test_content = """
from old.module import OldClass
x = OldClass()
"""
    test_file.write_text(test_content)
    
    # Test dry run
    assert process_file(test_file, "old.module.OldClass", "new.module.NewClass", dry_run=True)
    assert test_file.read_text() == test_content  # File should not be modified
    
    # Test actual modification
    assert process_file(test_file, "old.module.OldClass", "new.module.NewClass", dry_run=False)
    modified_content = test_file.read_text()
    assert "from new.module import NewClass" in modified_content
    assert "from old.module import OldClass" not in modified_content

def test_find_python_files(tmp_path):
    """Test the find_python_files function."""
    # Create test directory structure
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    
    test_files = [
        tmp_path / "test1.py",
        tmp_path / "dir1" / "test2.py",
        tmp_path / "dir2" / "test3.py",
        tmp_path / "not_python.txt"
    ]
    
    for file in test_files:
        file.touch()
    
    python_files = find_python_files(tmp_path)
    
    assert len([f for f in python_files if f.suffix == '.py']) == 3
    assert tmp_path / "not_python.txt" not in python_files

def test_import_with_alias():
    """Test handling imports with aliases."""
    source_code = """
from foo.bar import OldClass as MyClass
"""
    transformer = ImportReplacer("foo.bar.OldClass", "new.module.NewClass")
    module = cst.parse_module(source_code)
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "from new.module import NewClass" in modified.code

def test_invalid_file_handling(tmp_path):
    """Test handling of invalid Python files."""
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("this is not valid python code @@@@")
    
    result = process_file(invalid_file, "old.module.OldClass", "new.module.NewClass", dry_run=False)
    assert not result  # Should return False for invalid files

def test_split_import():
    """Test the _split_import helper method."""
    transformer = ImportReplacer("foo.bar.OldClass", "new.module.NewClass")
    
    module, name = transformer._split_import("a.b.c.ClassName")
    assert module == "a.b.c"
    assert name == "ClassName"
    
    module, name = transformer._split_import("ClassName")
    assert module == ""
    assert name == "ClassName" 