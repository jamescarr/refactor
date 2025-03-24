"""Tests for the call_replacer module."""
import tempfile
from pathlib import Path
import pytest
import libcst as cst

from epyon.core.call_replacer import CallReplacer, replace_call

def test_call_replacer_simple():
    """Test replacing a simple method call."""
    code = """
def test_function():
    self.assert_401_UNAUTHORIZED()
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.assert_401_UNAUTHORIZED", "self.assert_403_FORBIDDEN")
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "assert_403_FORBIDDEN" in modified.code
    assert "assert_401_UNAUTHORIZED" not in modified.code

def test_call_replacer_with_args():
    """Test replacing a method call with arguments."""
    code = """
def test_function():
    self.assertEqual(404, response.status_code)
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.assertEqual", "self.assertEquals")
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "assertEquals(404, response.status_code)" in modified.code
    assert "assertEqual(404, response.status_code)" not in modified.code

def test_call_replacer_with_different_args():
    """Test replacing a method call with different arguments."""
    code = """
def test_function():
    self.assertEqual(404, response.status_code)
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.assertEqual(404, response.status_code)", 
                               "self.assertEquals(response.status_code, 404)")
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "assertEquals(response.status_code, 404)" in modified.code
    assert "assertEqual(404, response.status_code)" not in modified.code

def test_call_replacer_nested_attributes():
    """Test replacing a call with nested attributes."""
    code = """
def test_function():
    self.client.request.assert_success(response)
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.client.request.assert_success", 
                               "self.client.assert_request_success")
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert "self.client.assert_request_success(response)" in modified.code
    assert "self.client.request.assert_success" not in modified.code

def test_call_replacer_multiple_occurrences():
    """Test replacing multiple occurrences of a method call."""
    code = """
def test_function():
    self.assert_401_UNAUTHORIZED()
    some_other_code()
    self.assert_401_UNAUTHORIZED()
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.assert_401_UNAUTHORIZED", "self.assert_403_FORBIDDEN")
    modified = module.visit(transformer)
    
    assert transformer.changes_made
    assert modified.code.count("assert_403_FORBIDDEN") == 2
    assert "assert_401_UNAUTHORIZED" not in modified.code

def test_call_replacer_no_match():
    """Test when no replacements are made."""
    code = """
def test_function():
    self.assert_404_NOT_FOUND()
    return True
"""
    module = cst.parse_module(code)
    transformer = CallReplacer("self.assert_401_UNAUTHORIZED", "self.assert_403_FORBIDDEN")
    modified = module.visit(transformer)
    
    assert not transformer.changes_made
    assert "assert_404_NOT_FOUND" in modified.code
    assert "assert_403_FORBIDDEN" not in modified.code

def test_replace_call_integration():
    """Test the replace_call function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test_file.py"
        with open(test_file, 'w') as f:
            f.write("""
def test_function():
    self.assert_401_UNAUTHORIZED()
    return True
""")
        
        # Run the replace_call function
        modified_count = replace_call(
            Path(tmpdir), 
            "self.assert_401_UNAUTHORIZED", 
            "self.assert_403_FORBIDDEN"
        )
        
        # Check that the file was modified
        assert modified_count == 1
        
        # Verify the content was updated
        with open(test_file, 'r') as f:
            content = f.read()
            assert "assert_403_FORBIDDEN" in content
            assert "assert_401_UNAUTHORIZED" not in content

def test_replace_call_dry_run():
    """Test the replace_call function with dry_run=True."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test_file.py"
        with open(test_file, 'w') as f:
            f.write("""
def test_function():
    self.assert_401_UNAUTHORIZED()
    return True
""")
        
        # Run the replace_call function with dry_run=True
        modified_count = replace_call(
            Path(tmpdir), 
            "self.assert_401_UNAUTHORIZED", 
            "self.assert_403_FORBIDDEN",
            dry_run=True
        )
        
        # Check that the file would have been modified
        assert modified_count == 1
        
        # Verify the content was NOT updated
        with open(test_file, 'r') as f:
            content = f.read()
            assert "assert_403_FORBIDDEN" not in content
            assert "assert_401_UNAUTHORIZED" in content 