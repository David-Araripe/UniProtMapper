#!/bin/bash

# Get the current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Clean previous builds
rm -rf build
rm -rf deploy

# Build the docs
make html

# Create deployment directory
mkdir -p deploy

# Copy the built docs based on branch
if [ "$BRANCH" = "dev" ]; then
    echo "Preparing documentation for dev branch..."
    mkdir -p deploy/dev
    cp -r build/html/* deploy/dev/
    echo '<meta http-equiv="refresh" content="0; url=./dev/">' > deploy/index.html
else
    echo "Preparing documentation for stable branch..."
    mkdir -p deploy/stable
    cp -r build/html/* deploy/stable/
    echo '<meta http-equiv="refresh" content="0; url=./stable/">' > deploy/index.html
fi

# Copy the .nojekyll file to allow files starting with underscore
touch deploy/.nojekyll

echo "Documentation prepared in deploy directory."