#!/bin/bash

set -e  # Exit immediately if a command fails

# Global variables
SCRIPT_DIR="$(dirname "$0")"
VERSION="2.2.8"
PACKAGE_NAME="vcandy"
BIN_DIR="$SCRIPT_DIR/$PACKAGE_NAME/bin"
DEBIAN_DIR="$SCRIPT_DIR/$PACKAGE_NAME/DEBIAN"
VENV_DIR="$SCRIPT_DIR/venv"

# Log function
log() {
    echo "[INFO] $1"
}

# Check if dependencies are installed
check_dependencies() {
    log "Checking dependencies..."
    if ! dpkg -s python3-pip debhelper python3-venv &> /dev/null; then
        log "Installing dependencies..."
        sudo apt update
        sudo apt install python3-pip debhelper python3-venv -y
    else
        log "Dependencies already installed."
    fi
}

# Install required Python libraries in a virtual environment
install_python_dependencies() {
    log "Installing Python dependencies..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --no-cache-dir requests pyinstaller setuptools
    deactivate
}

# Clean previous build artifacts
log "Cleaning previous build artifacts..."
rm -rf "$SCRIPT_DIR/$PACKAGE_NAME"

# Ensure we're in the correct directory
cd "$SCRIPT_DIR" || exit

# Check and install dependencies
check_dependencies

# Remove the externally managed file for Python pip if it exists
if [ -f /usr/lib/python3.11/EXTERNALLY-MANAGED ]; then
    sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED
fi

# Install required Python libraries
if [ ! -d "$VENV_DIR" ]; then
    install_python_dependencies
fi

# Source the virtual environment
source "$VENV_DIR/bin/activate"

# Create necessary directories
mkdir -p "$BIN_DIR"

# Build the Python project
log "Building the Python project..."
~/.local/bin/pyinstaller --onefile ../../src/app.py --name=$PACKAGE_NAME

# Move the binary file to the build directory
mv dist/$PACKAGE_NAME "$BIN_DIR"

# Create the Debian control file location
mkdir -p "$DEBIAN_DIR"

# Create the control file
log "Creating the Debian control file..."
cat <<EOF > "$DEBIAN_DIR/control"
Package: $PACKAGE_NAME
Version: $VERSION
Architecture: all
Section: python
Priority: optional
Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Description: A Python CLI application that installs automatic container and virtualization tools for many Linux systems.
EOF

# Build the package
log "Building the package..."
dpkg-deb --root-owner-group --build "$SCRIPT_DIR/$PACKAGE_NAME"

# Install the package
log "Installing the package..."
sudo dpkg -i "$SCRIPT_DIR/$PACKAGE_NAME.deb"

# Clean up
log "Cleaning up..."
rm -rf "$SCRIPT_DIR/$PACKAGE_NAME" dist build "$SCRIPT_DIR/$PACKAGE_NAME.deb"

log "Installation completed successfully!"
