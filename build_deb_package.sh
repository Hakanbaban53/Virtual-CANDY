#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf debian/vcandy

# Install dependencies
sudo apt install python3-pip debhelper -y

# Create the necessary directories
mkdir -p debian/vcandy/bin

pyinstaller --onefile app.py --name=vcandy

mv dist/vcandy debian/vcandy/bin

mkdir -p debian/vcandy/DEBIAN

# Create the control file
cat <<EOF > debian/vcandy/DEBIAN
Source: vcandy
Section: python
Priority: optional
Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>
Build-Depends: debhelper (>= 9), python3-pip, debhelper-compat (>=9)
Standards-Version: 4.5.0
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer

Package: vcandy
Architecture: any
Depends: ${misc:Depends}, python3-pip, ${python3:Depends}
Description: A python CLI application that installs automatic container and virtualization tools for many Linux systems.
EOF

# Build the package
dpkg-deb --root-owner-group --build debian/vcandy

