#!/bin/bash

set -e  # Exit immediately if a command fails

# Global variables
VERSION="2.0"
PACKAGE_NAME="vcandy"
SOURCE_DIR="$PACKAGE_NAME-$VERSION"
RPMS_DIR=~/rpmbuild/RPMS
SOURCES_DIR=~/rpmbuild/SOURCES
SPECS_DIR=~/rpmbuild/SPECS
SPEC_FILE="$SPECS_DIR/$PACKAGE_NAME.spec"
TAR_FILE="$SOURCE_DIR.tar.gz"

# Log function
log() {
    echo "[INFO] $1"
}

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
log "Cleaning previous build artifacts..."
rm -rf ~/rpmbuild "$SOURCE_DIR" dist build

# Check and install dependencies
log "Checking and installing dependencies..."
sudo dnf install python3-pip rpmdevtools rpmlint -y

# Set up the RPM development files home directory
rpmdev-setuptree

# Install requests and PyInstaller using pip
log "Installing Python dependencies..."
pip3 install --no-cache-dir requests pyinstaller setuptools

# Build the Python project with PyInstaller
log "Building the Python project with PyInstaller..."
pyinstaller --onefile app.py --name=$PACKAGE_NAME

# Create the binary folder
mkdir "$SOURCE_DIR"

# Move the binary file to the binary folder we created
mv dist/$PACKAGE_NAME "$SOURCE_DIR"

# Add the .tar.gz folder to the RPM SOURCES directory
log "Moving the .tar.gz file to the RPM SOURCES directory..."
tar --create --file "$TAR_FILE" "$SOURCE_DIR"
mv "$TAR_FILE" "$SOURCES_DIR"

# Create the spec file
log "Creating the spec file..."
cat <<EOF > "$SPEC_FILE"
Summary: A python CLI application that installs automatic container and virtualization tools for many Linux systems
Name: $PACKAGE_NAME
Version: $VERSION
Release: 1%{?dist}
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: %{name}-%{version}.tar.gz

%description
$PACKAGE_NAME is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.

%prep
%setup -q

%install
rm -rf \$RPM_BUILD_ROOT
mkdir -p \$RPM_BUILD_ROOT/%{_bindir}
cp %{name} \$RPM_BUILD_ROOT/%{_bindir}

%clean
rm -rf \$RPM_BUILD_ROOT

%files
%{_bindir}/%{name}

%changelog
* Thu Mar 19 2024 Hakan İSMAİL <hakanismail53@gmail.com> - $VERSION
- Initial release
EOF

# Build the RPM package
log "Building the RPM package..."
rpmbuild -bb "$SPEC_FILE"

# Install the RPM package
log "Installing the RPM package..."
sudo dnf install $RPMS_DIR/*/$PACKAGE_NAME-$VERSION* -y

# Clean up
log "Cleaning up..."
rm -rf ~/rpmbuild "$SOURCE_DIR" dist build

log "Installation completed successfully!"
