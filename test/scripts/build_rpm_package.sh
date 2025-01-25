#!/bin/bash

set -e  # Exit immediately if a command fails

# Global variables
VERSION="3.0"
PACKAGE_NAME="vcandy"
SOURCE_DIR="$PACKAGE_NAME-$VERSION"
RPMS_DIR=~/rpmbuild/RPMS
SOURCES_DIR=~/rpmbuild/SOURCES
SPECS_DIR=~/rpmbuild/SPECS
SPEC_FILE="$SPECS_DIR/$PACKAGE_NAME.spec"
TAR_FILE="$SOURCE_DIR.tar.gz"
PYTHONPATH=$(python3 -m site --user-site)

# Log function
log() {
    echo "[INFO] $1"
}

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
log "Cleaning previous build artifacts..."
rm -rf ~/rpmbuild "$SOURCE_DIR" dist build || true

# Check and install dependencies
log "Checking and installing dependencies..."
sudo dnf install -y python3-pip rpmdevtools rpmlint tar

# Set up the RPM development files home directory
rpmdev-setuptree

# Install required Python packages
log "Installing Python dependencies..."
pip3 install --user --no-cache-dir requests pyinstaller setuptools

# Build the Python project with PyInstaller
log "Building the Python project with PyInstaller..."
~/.local/bin/pyinstaller --onefile ../../src/app.py --name=$PACKAGE_NAME

# Create the binary folder
log "Creating the binary folder..."
mkdir "$SOURCE_DIR"

# Move the binary file to the binary folder
mv dist/$PACKAGE_NAME "$SOURCE_DIR"

# Package the binary into a tar.gz archive and move to the SOURCES directory
log "Packaging the binary into a tar.gz file..."
tar -czf "$TAR_FILE" "$SOURCE_DIR"
mv "$TAR_FILE" "$SOURCES_DIR"

# Create the spec file for RPM
log "Creating the spec file..."
cat <<EOF > "$SPEC_FILE"
%global debug_package %{nil}

Summary: A Python CLI application that installs automatic container and virtualization tools for Linux systems
Name: $PACKAGE_NAME
Version: $VERSION
Release: 1%{?dist}
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: %{name}-%{version}.tar.gz

%description
$PACKAGE_NAME is a command-line tool that simplifies the installation of container and virtualization tools on Linux systems.

%prep
%setup -q

%install
rm -rf \$RPM_BUILD_ROOT
mkdir -p \$RPM_BUILD_ROOT%{_bindir}
cp %{name} \$RPM_BUILD_ROOT%{_bindir}

%clean
rm -rf \$RPM_BUILD_ROOT

%files
%{_bindir}/%{name}

%changelog
* Tue Dec 19 2024 Hakan İSMAİL <hakanismail53@gmail.com> - $VERSION
- Initial release
EOF

# Build the RPM package
log "Building the RPM package..."
rpmbuild -bb "$SPEC_FILE"

# Install the RPM package
log "Installing the RPM package..."
sudo dnf install -y $RPMS_DIR/*/$PACKAGE_NAME-$VERSION*.rpm

# Clean up after the build process
log "Cleaning up temporary build files..."
rm -rf ~/rpmbuild "$SOURCE_DIR" dist build

log "Installation completed successfully!"
