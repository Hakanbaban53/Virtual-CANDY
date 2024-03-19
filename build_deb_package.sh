#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf debian/vcandy

# Install dependencies
sudo apt install python3-pip debhelper -y

# Create the necessary directories
mkdir -p debian/vcandy/usr

# Make the rules file executable
chmod +x debian/rules

# Run rules file
debian/rules

# Build the package
dpkg-buildpackage -us -uc

# Clean up
rm -rf debian/vcandy
