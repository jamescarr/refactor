#!/bin/bash
set -e

# Check if a version number was provided
if [ -z "$1" ]; then
    echo "Please provide a version number (e.g. 1.0.0)"
    exit 1
fi

VERSION=$1

# Update version in pyproject.toml
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update version in __init__.py
sed -i '' "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" refactor/__init__.py

# Create git tag
git add pyproject.toml refactor/__init__.py
git commit -m "Release v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

echo "Version $VERSION has been set and tagged."
echo "Now push the changes with:"
echo "  git push origin main v$VERSION" 