#!/bin/bash

set -e  # Exit immediately if a command fails

# Directory of the script
SCRIPT_DIR="$(dirname "$0")"

# Log function
log() {
    echo "[INFO] $1"
}

# Check if dependencies are installed
check_dependencies() {
    log "Checking dependencies..."
    if ! dpkg -s python3-pip debhelper &> /dev/null; then
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
    python3 -m venv "$SCRIPT_DIR/venv"
    source "$SCRIPT_DIR/venv/bin/activate"
    pip install --no-cache-dir requests pyinstaller setuptools
    deactivate
}

# Clean previous build artifacts
log "Cleaning previous build artifacts..."
rm -rf "$SCRIPT_DIR/vcandy"

# Ensure we're in the correct directory
cd "$SCRIPT_DIR" || exit

# Check and install dependencies
check_dependencies

# Remove the externally managed file for Python pip
sudo rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED || true

# Install required Python libraries
install_python_dependencies

# Create necessary directories
mkdir -p "$SCRIPT_DIR/vcandy/bin"

# Build the Python project
log "Building the Python project..."
pyinstaller --onefile app.py --name=vcandy

# Move the binary file to the build directory
mv dist/vcandy "$SCRIPT_DIR/vcandy/bin"

# Create the Debian control file location
mkdir -p "$SCRIPT_DIR/vcandy/DEBIAN"

# Create the control file
log "Creating the Debian control file..."
cat <<EOF > "$SCRIPT_DIR/vcandy/DEBIAN/control"
Package: vcandy
Version: 0.2-1
Architecture: all
Section: python
Priority: optional
Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>
Homepage: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Description: A Python CLI application that installs automatic container and virtualization tools for many Linux systems.
EOF

# Build the package
log "Building the package..."
dpkg-deb --root-owner-group --build vcandy

# Install the package
log "Installing the package..."
sudo dpkg -i vcandy.deb

# Clean up
log "Cleaning up..."
rm -rf vcandy*

log "Installation completed successfully!"

