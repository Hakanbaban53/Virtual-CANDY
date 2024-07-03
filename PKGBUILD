# Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>

pkgname=vcandy
pkgver=1.5.0
pkgrel=1
pkgdesc="A python CLI application that installs automatic container and virtualization tools for many Linux systems"
url="https://github.com/Hakanbaban53/Container-and-Virtualization-Installer"
arch=('x86_64')
license=('MIT')
depends=('python' 'python-pip')
makedepends=('git' 'python-pyinstaller')
source=("git+$url.git")
b2sums=('SKIP')

prepare() {
  cd "$srcdir/Container-and-Virtualization-Installer"
  
  # Install Python dependencies
  python -m pip install --user requests pyinstaller setuptools --break-system-packages
}

build() {
  cd "$srcdir/Container-and-Virtualization-Installer"
  
  # Build the Python project with PyInstaller
  /home/$USER/.local/bin/pyinstaller --onefile app.py --name=vcandy
}

package() {
  cd "$srcdir/Container-and-Virtualization-Installer"

  # Install the binary
  install -Dm755 "dist/vcandy" "$pkgdir/usr/bin/vcandy"

  # Clean up build artifacts
  rm -rf "$srcdir/Container-and-Virtualization-Installer/build"
  rm -rf "$srcdir/Container-and-Virtualization-Installer/dist"
}
