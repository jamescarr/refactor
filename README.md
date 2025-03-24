# Refactor

A command-line tool for safely refactoring Python imports across your codebase. Built with libCST for reliable Python code transformations.

## Features

- Replace imports across multiple Python files
- Handles various import formats:
  - Simple imports (`from foo import bar`)
  - Multi-line imports
  - Parenthesized imports (`from foo import (bar, baz)`)
- Preserves code formatting and comments
- Dry-run mode to preview changes
- Verbose output option

## Installation

```bash
# Install from PyPI
pip install refactor

# Or install from source
git clone https://github.com/jamescarr/refactor.git
cd refactor
make install
```

## Usage

### Basic Usage

```bash
refactor replace-import OLD_IMPORT NEW_IMPORT PATH
```

Examples:
```bash
# Replace a single import in a file
refactor replace-import old.module.Class new.module.Class path/to/file.py

# Replace imports in all Python files in a directory
refactor replace-import old.module.Class new.module.Class path/to/directory

# Preview changes without modifying files (dry-run)
refactor replace-import old.module.Class new.module.Class path/to/file.py --dry-run

# Show verbose output
refactor replace-import old.module.Class new.module.Class path/to/file.py --verbose
```

### Supported Import Formats

The tool handles various import formats:

```python
# Simple imports
from foo.bar import baz
from foo.bar import baz as alias

# Multi-line imports
from foo.bar import (
    baz,
    qux,
    quux
)

# Multiple imports on one line
from foo.bar import baz, qux, quux
```

### Command-Line Options

```bash
Options:
  --version                   Show version information
  --verbose                   Enable verbose output
  --dry-run                  Preview changes without modifying files
  --help                     Show this help message and exit
```

## Development

### Prerequisites

- Python 3.6 or higher
- make (for development commands)

### Available Make Commands

- `make install`: Install the package
- `make dev`: Install development dependencies
- `make test`: Run the test suite
- `make lint`: Run the linter
- `make clean`: Clean build artifacts

### Running Tests

```bash
make test
```

The test suite includes comprehensive tests for:
- Version command
- Import replacement functionality
- File handling
- Dry run mode
- Multiple file processing
- Error cases
- Command-line interface
- Verbose output

### Code Style

This project uses `ruff` for linting. To check your code:

```bash
make lint
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Run the tests and linter
5. Submit a Pull Request

### Commit Messages

Please follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [libCST](https://github.com/Instagram/LibCST) - The core library powering the transformations
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting and syntax highlighting

## Troubleshooting

### Common Issues

1. **Installation Problems**
   ```bash
   # If you encounter permission issues
   pip install --user refactor
   ```

2. **Version Conflicts**
   ```bash
   # Install in an isolated environment
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install refactor
   ```

3. **Path Issues**
   - Ensure the target path exists
   - For files, ensure they have a `.py` extension
   - For directories, ensure they contain Python files

For more issues, please check the [GitHub Issues](https://github.com/jamescarr/refactor/issues) page.