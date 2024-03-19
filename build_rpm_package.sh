#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")" || exit

# Clean previous build artifacts
rm -rf ~/rpmbuild

# Install Python pip
sudo dnf install python3-pip rpmdevtools rpmlint -y

rpmdev-setuptree

# Install requests and PyInstaller using pip
pip3 install --no-cache-dir requests pyinstaller setuptools

# Build the Python project with PyInstaller
pyinstaller --onefile app.py --name=vcandy

mkdir vcandy-0.1

# Move the binary file to the SOURCES directory
mv dist/vcandy vcandy-0.1

tar --create --file vcandy-0.1.tar.gz vcandy-0.1

# Create the source tarball and directory

mv vcandy-0.1.tar.gz ~/rpmbuild/SOURCES


# Create the spec file
cat <<EOF > ~/rpmbuild/SPECS/vcandy.spec
Summary: A python CLI application that installs automatic container and virtualization tools for many Linux systems
Name: vcandy
Version: 0.1
Release: 1%{?dist}
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: %{name}-%{version}.tar.gz

%description
vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.

%prep
%setup -q

%build
# No build step required for Python scripts

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/bin
cp %{SOURCE0} %{buildroot}/usr/bin

%files
/usr/bin/vcandy

%changelog
* Thu Mar 19 2024 Hakan İSMAİL <hakanismail53@gmail.com> - 0.1-1
- Initial release
EOF

# Build the RPM package
rpmbuild -bb ~/rpmbuild/SPECS/vcandy.spec

