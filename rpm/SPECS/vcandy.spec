Name: vcandy
Version: 0.1
Release: 1%{?dist}
Summary: A python CLI application that installs automatic container and virtualization tools for many Linux systems
License: MIT
URL: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer
Source0: https://github.com/Hakanbaban53/Container-and-Virtualization-Installer/archive/%{version}.tar.gz

BuildRequires: python3-setuptools
Requires: python3-pip

%description
vcandy is a command-line tool that simplifies the installation process of container and virtualization tools on Linux systems.

%prep
%autosetup -p1

%build
# Nothing to do here

%install
mkdir -p %{buildroot}/%{_datadir}/%{name}
python3 -m pip install --no-deps --prefix=%{buildroot}/%{_datadir}/%{name} requests pyinstaller
pyinstaller --onefile %{_builddir}/%{name}-%{version}/app.py --distpath=%{buildroot}/%{_datadir}/%{name}/bin --name=vcandy

%files
%{_datadir}/%{name}/
