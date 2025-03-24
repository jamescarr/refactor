"""Tests for the def_mover module."""
import pytest
from pathlib import Path
import libcst as cst
from epyon.core.def_mover import DefinitionExtractor, process_file_move, find_module_file

def test_extract_class_definition():
    """Test extracting a class definition."""
    source_code = """
class TargetClass:
    \"\"\"A test class.\"\"\"
    def __init__(self):
        self.x = 1

class OtherClass:
    pass
"""
    extractor = DefinitionExtractor("TargetClass")
    module = cst.parse_module(source_code)
    modified = module.visit(extractor)
    
    assert extractor.found
    assert isinstance(extractor.extracted_node, cst.ClassDef)
    assert extractor.extracted_node.name.value == "TargetClass"
    assert "class OtherClass" in modified.code
    assert "class TargetClass" not in modified.code

def test_extract_function_definition():
    """Test extracting a function definition."""
    source_code = """
def target_function(x: int) -> int:
    \"\"\"A test function.\"\"\"
    return x + 1

def other_function():
    pass
"""
    extractor = DefinitionExtractor("target_function")
    module = cst.parse_module(source_code)
    modified = module.visit(extractor)
    
    assert extractor.found
    assert isinstance(extractor.extracted_node, cst.FunctionDef)
    assert extractor.extracted_node.name.value == "target_function"
    assert "def other_function" in modified.code
    assert "def target_function" not in modified.code

def test_extract_nonexistent_definition():
    """Test attempting to extract a nonexistent definition."""
    source_code = """
def existing_function():
    pass
"""
    extractor = DefinitionExtractor("nonexistent_function")
    module = cst.parse_module(source_code)
    modified = module.visit(extractor)
    
    assert not extractor.found
    assert extractor.extracted_node is None
    assert modified.code == source_code

def test_process_file_move_source(tmp_path):
    """Test processing a file as the source of a definition."""
    source_file = tmp_path / "source.py"
    source_file.write_text("""
class TargetClass:
    \"\"\"A test class.\"\"\"
    def method(self):
        pass

class OtherClass:
    pass
""")
    
    changes_made, extracted_def = process_file_move(
        source_file,
        "source.TargetClass",
        "target.NewClass",
        dry_run=False
    )
    
    assert changes_made
    assert extracted_def is not None
    assert isinstance(extracted_def, cst.ClassDef)
    assert "class OtherClass" in source_file.read_text()
    assert "class TargetClass" not in source_file.read_text()

def test_process_file_move_target(tmp_path):
    """Test processing a file as the target for a definition."""
    target_file = tmp_path / "target.py"
    target_file.write_text("""
def existing_function():
    pass
""")
    
    # Create a sample class definition
    class_def = cst.parse_module("""
class NewClass:
    pass
""").body[0]  # Get the class definition directly
    
    changes_made, _ = process_file_move(
        target_file,
        "source.OldClass",
        "target.NewClass",
        extracted_def=class_def,
        dry_run=False
    )
    
    assert changes_made
    modified_content = target_file.read_text()
    assert "def existing_function" in modified_content
    assert "class NewClass" in modified_content

def test_process_file_move_update_imports(tmp_path):
    """Test updating imports in a file."""
    user_file = tmp_path / "user.py"
    user_file.write_text("""
from source import TargetClass

def use_class():
    return TargetClass()
""")
    
    # Create a sample class definition
    class_def = cst.parse_module("""
class TargetClass:
    pass
""").body[0]  # Get the class definition directly
    
    changes_made, _ = process_file_move(
        user_file,
        "source.TargetClass",
        "target.NewClass",
        extracted_def=class_def,
        dry_run=False
    )
    
    assert changes_made
    modified_content = user_file.read_text()
    assert "from target import NewClass" in modified_content
    assert "from source import TargetClass" not in modified_content

def test_process_file_move_dry_run(tmp_path):
    """Test dry run mode doesn't modify files."""
    source_file = tmp_path / "source.py"
    original_content = """
class TargetClass:
    pass

class OtherClass:
    pass
"""
    source_file.write_text(original_content)
    
    changes_made, extracted_def = process_file_move(
        source_file,
        "source.TargetClass",
        "target.NewClass",
        dry_run=True
    )
    
    assert changes_made
    assert extracted_def is not None
    assert source_file.read_text() == original_content

def test_find_module_file(tmp_path):
    """Test finding a module file from a module path."""
    # Create a nested directory structure
    (tmp_path / "foo" / "bar").mkdir(parents=True)
    module_file = tmp_path / "foo" / "bar" / "baz.py"
    module_file.touch()
    
    found = find_module_file("foo.bar.baz", tmp_path)
    assert found == module_file
    
    not_found = find_module_file("nonexistent.module", tmp_path)
    assert not_found is None

def test_process_file_move_invalid_file(tmp_path):
    """Test handling invalid Python files."""
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("this is not valid python @@@@")
    
    changes_made, extracted_def = process_file_move(
        invalid_file,
        "module.Class",
        "new.module.Class",
        dry_run=False
    )
    
    assert not changes_made
    assert extracted_def is None 