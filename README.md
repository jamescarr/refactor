# Epyon

A command-line tool for safely refactoring Python imports and moving definitions between modules. Named after the Gundam Epyon from Mobile Suit Gundam Wing, which represents perfect transformation and adaptation - much like how this tool helps you transform and adapt your Python code with precision and reliability.

## Features

- Safe, precise import replacement using Python's concrete syntax tree (CST)
- Move class and function definitions between modules while updating all imports
- Replace method and function calls throughout your codebase
- Preserves code formatting and comments
- Handles complex import cases (aliased imports, multi-line imports)
- Dry run mode to preview changes
- Verbose output option for detailed operation logging
- Works with single files or entire directories

## Installation

```bash
pip install epyon
```

## Usage

```bash
# Replace a single import
epyon replace-import "gundam.wing.zero.WingZero" "gundam.wing.custom.WingZeroCustom" path/to/files

# Replace with aliased imports
epyon replace-import "gundam.wing.epyon.BeamSaber" "gundam.wing.tallgeese.BeamSaber" path/to/files

# Replace from multi-line imports
epyon replace-import "gundam.wing.sandrock.HeatShortels" "gundam.wing.sandrock.custom.TwinHeatShortels" path/to/files

# Move a class definition to a different module
epyon move-def "gundam.wing.zero.WingZero" "gundam.wing.custom.WingZeroCustom" path/to/files

# Move a function with dry run
epyon move-def --dry-run "gundam.wing.utils.transform" "gundam.wing.core.transform" path/to/files

# Replace method calls across your codebase
epyon replace-call "self.assert_401_UNAUTHORIZED" "self.assert_403_FORBIDDEN" path/to/tests

# Replace method calls with arguments
epyon replace-call "self.assertEqual(404, response.status_code)" "self.assertEquals(response.status_code, 404)" 

# Parallel processing for large codebases
epyon replace-call "client.get_item" "client.get_resource" --workers 4

# Show version
epyon --version

# Show help
epyon --help
```

### Example Import Formats

```python
# Simple imports
from gundam.wing import WingZero
from gundam.epyon import BeamSaber as EpyonSaber

# Multi-line imports
from gundam.wing.pilots import (
    HeeroYuy,
    DuoMaxwell,
    TrowaBarton
)

# Multiple imports on one line
from gundam.wing.weapons import BeamSaber, BeamCannon, BusterRifle
```

### Example Definition Moves

```python
# Original file: gundam/wing/zero.py
class WingZero:
    """The Wing Zero Gundam."""
    def transform(self):
        pass

# After moving to: gundam/wing/custom.py
class WingZeroCustom:  # Name can be changed during move
    """The Wing Zero Gundam."""
    def transform(self):
        pass

# All imports are automatically updated
from gundam.wing.custom import WingZeroCustom  # Updated automatically
```

### Example Call Replacements

```python
# Before
def test_unauthorized_access(self):
    response = self.client.get('/protected')
    self.assert_401_UNAUTHORIZED(response)

# After running: epyon replace-call "self.assert_401_UNAUTHORIZED" "self.assert_403_FORBIDDEN"
def test_unauthorized_access(self):
    response = self.client.get('/protected')
    self.assert_403_FORBIDDEN(response)

# Works with nested attributes too
self.client.request.assert_success(response)  # Before
self.client.assert_request_success(response)  # After
```

## Development

```bash
# Clone the repository
git clone https://github.com/jamescarr/refactor.git
cd epyon

# Install development dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run linter
make lint
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- [libCST](https://github.com/Instagram/LibCST) - The core library powering the transformations
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting and syntax highlighting

## Troubleshooting

### Common Issues

1. **Installation Problems**
   ```bash
   # If you encounter permission issues
   pip install --user epyon
   ```

2. **Version Conflicts**
   ```bash
   # Install in an isolated environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install epyon
   ```

3. **Path Issues**
   - Ensure the target path exists
   - For files, ensure they have a `.py` extension
   - For directories, ensure they contain Python files

For more issues, please check the [GitHub Issues](https://github.com/jamescarr/epyon/issues) page.
