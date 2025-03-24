# Epyon

A command-line tool for safely refactoring Python imports. Named after the Gundam Epyon from Mobile Suit Gundam Wing, which represents perfect transformation and adaptation - much like how this tool helps you transform and adapt your Python imports with precision and reliability.

## Features

- Safe, precise import replacement using Python's concrete syntax tree (CST)
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
epyon replace "gundam.wing.zero.WingZero" "gundam.wing.custom.WingZeroCustom" path/to/files

# Replace with aliased imports
epyon replace "gundam.wing.epyon.BeamSaber" "gundam.wing.tallgeese.BeamSaber" path/to/files

# Replace from multi-line imports
epyon replace "gundam.wing.sandrock.HeatShortels" "gundam.wing.sandrock.custom.TwinHeatShortels" path/to/files

# Show version
epyon --version

# Show help
epyon --help

# Dry run (show changes without applying them)
epyon replace --dry-run "gundam.heavyarms.GatlingGuns" "gundam.heavyarms.custom.DualGatlingGuns" path/to/files
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

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/epyon.git
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