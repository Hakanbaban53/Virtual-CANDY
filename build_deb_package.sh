#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf vcandy

# Install dependencies
sudo apt install python3-pip debhelper -y

sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

pip install --no-cache-dir requests pyinstaller setuptools

# Create the necessary directories
mkdir -p vcandy/bin

pyinstaller --onefile app.py --name=vcandy

mv dist/vcandy vcandy/bin

mkdir -p vcandy/DEBIAN

# Create the control file
cat <<EOF > vcandy/DEBIAN/control
Package: vcandy
Version: 0.1
Architecture: all
Section: python
Priority: optional
Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Description: A python CLI application that installs automatic container and virtualization tools for many Linux systems.
EOF

# Build the package
dpkg-deb --root-owner-group --build vcandy

sudo dpkg -i vcandy.deb

rm -rf vcandy*
