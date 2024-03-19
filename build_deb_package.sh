#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf debian/vcandy

# Install dependencies
sudo apt install python3-pip debhelper -y

# Create the necessary directories
mkdir -p debian/vcandy/usr

# Install Python dependencies
python3 -m pip install --no-deps --prefix=/debian/vcandy/usr requests pyinstaller

# Remove EXTERNALLY-MANAGED file
rm /usr/lib/python3.11/EXTERNALLY-MANAGED

# Build the Python project with PyInstaller
pyinstaller --onefile ./app.py --distpath=/debian/vcandy/usr/bin --name=vcandy

# Create the control file
cat <<EOF > debian/control
Source: vcandy
Section: python
Priority: optional
Maintainer: Your Name <your.email@example.com>
Build-Depends: debhelper (>= 9), python3-pip, debhelper-compat (>=9)
Standards-Version: 4.5.0
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer

Package: vcandy
Architecture: any
Depends: \${misc:Depends}, python3-pip, \${python3:Depends}
Description: A python CLI application that installs automatic container and virtualization tools for many Linux systems
 vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.
EOF

# Create the changelog file
cat <<EOF > debian/changelog
vcandy (0.1-1) UNRELEASED; urgency=medium

  * Initial release.

 -- Hakan İSMAİL <hakanismail53@gmail.com>  Thu, 19 Mar 2024 00:00:00 +0000
EOF

# Build the package
dpkg-buildpackage -us -uc

# Clean up
rm -rf debian/vcandy
