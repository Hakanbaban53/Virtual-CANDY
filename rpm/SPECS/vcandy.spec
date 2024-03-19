Name: vcandy
Version: 0.1
Release: 1%{?dist}
Summary: A python CLI application that installs automatic container and virtualization tools for many Linux systems
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: %{name}-%{version}.tar.gz

BuildRequires: python3-setuptools
Requires: python3-pip

%description
vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.

%prep
%setup -q

%build
python3 -m pip install --no-deps --prefix=%{_builddir}/%{name}-%{version}/usr requests pyinstaller
rm -f %{_builddir}/%{name}-%{version}/usr/lib/python3.11/EXTERNALLY-MANAGED
pyinstaller app.py --distpath=%{_builddir}/%{name}-%{version}/usr/bin --name=vcandy

%install
mkdir -p %{buildroot}/%{_datadir}/%{name}
cp -r %{_builddir}/%{name}-%{version}/usr/* %{buildroot}/%{_datadir}/%{name}/

%files
%{_datadir}/%{name}/