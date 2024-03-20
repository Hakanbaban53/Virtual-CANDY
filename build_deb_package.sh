#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf vcandy

# Install dependencies
sudo apt install python3-pip debhelper -y

# Remove the externally managed file for python pip
sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

# Install the required python libraries
pip install --no-cache-dir requests pyinstaller setuptools

# Create the necessary directories
mkdir -p vcandy/bin

# Build the python project
pyinstaller --onefile app.py --name=vcandy

# Move the binary file the build directory
mv dist/vcandy vcandy/bin

# Create the debian control file location
mkdir -p vcandy/DEBIAN

# Create the control file
cat <<EOF > vcandy/DEBIAN/control
Package: vcandy
Version: 0.1-1
Architecture: all
Section: python
Priority: optional
Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Description: A python CLI application that installs automatic container and virtualization tools for many Linux systems.
EOF

# Build the package
dpkg-deb --root-owner-group --build vcandy

# Install the package
sudo dpkg -i vcandy.deb

# Clean up
rm -rf vcandy*
