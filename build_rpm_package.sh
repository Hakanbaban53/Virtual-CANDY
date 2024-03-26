#!/bin/bash

set -e  # Exit immediately if a command fails

# Log function
log() {
    echo "[INFO] $1"
}

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
log "Cleaning previous build artifacts..."
rm -rf ~/rpmbuild vcandy-0.1 dist build

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
pyinstaller --onefile app.py --name=vcandy

# Create the binary folder
mkdir vcandy-0.1

# Move the binary file to the binary folder we created
mv dist/vcandy vcandy-0.1

# Add the .tar.gz folder to the RPM SOURCES directory
log "Moving the .tar.gz file to the RPM SOURCES directory..."
tar --create --file vcandy-0.1.tar.gz vcandy-0.1
mv vcandy-0.1.tar.gz ~/rpmbuild/SOURCES

# Create the spec file
log "Creating the spec file..."
cat <<EOF > ~/rpmbuild/SPECS/vcandy.spec
Summary: A python CLI application that installs automatic container and virtualization tools for many Linux systems
Name: vcandy
Version: 0.2-1
Release: 1%{?dist}
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: %{name}-%{version}.tar.gz

%description
vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.

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
* Thu Mar 19 2024 Hakan İSMAİL <hakanismail53@gmail.com> - 0.1-1
- Initial release
EOF

# Build the RPM package
log "Building the RPM package..."
rpmbuild -bb ~/rpmbuild/SPECS/vcandy.spec

# Install the RPM package
log "Installing the RPM package..."
sudo dnf install ~/rpmbuild/RPMS/*/vcandy-0.1-1*

# Clean up
log "Cleaning up..."
rm -rf ~/rpmbuild vcandy-0.1 dist build

log "Installation completed successfully!"
