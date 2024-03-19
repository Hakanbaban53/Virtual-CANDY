#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf debian/vcandy

# Build the Python project with PyInstaller
pyinstaller --onefile --distpath debian/vcandy/usr/bin --name vcandy app.py

# Create the necessary directories
mkdir -p debian/vcandy/usr

# Create the control file
cat <<EOF > debian/control
Source: vcandy
Section: python
Priority: optional
Maintainer: Your Name <your.email@example.com>
Build-Depends: debhelper (>= 9), python3-pip
Standards-Version: 4.5.0
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer

Package: vcandy
Architecture: any
Depends: \${misc:Depends}, python3-pip, \${python3:Depends}
Description: A python CLI application that installs automatic container and virtualization tools for many Linux systems
 vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.
EOF

# Create the rules file
cat <<EOF > debian/rules
#!/usr/bin/make -f

%:
	dh \$@

override_dh_auto_install:
	dh_auto_install
	python3 -m pip install --no-deps --prefix=\$(CURDIR)/debian/vcandy/usr requests pyinstaller
	rm \$(CURDIR)/debian/vcandy/usr/lib/python3.11/EXTERNALLY-MANAGED
EOF

# Make the rules file executable
chmod +x debian/rules

# Build the package
dpkg-buildpackage -us -uc

# Clean up
rm -rf debian/vcandy
