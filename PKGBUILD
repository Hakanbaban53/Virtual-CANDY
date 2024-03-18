# Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>

pkgname=vcandy
pkgver=0.1
pkgrel=1
pkgdesc="A python CLI application that installs automatic container and virtualization tools for many Linux systems"
url="https://github.com/Hakanbaban53/Container-and-Virtualization-Installer"
arch=(x86_64)
license=(MIT)
depends=(
  python-pip
)
makedepends=()
checkdepends=()
groups=()
source=("git+https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git")
b2sums=('SKIP')

package() {
  cd "$srcdir/Container-and-Virtualization-Installer"

  # Remove EXTERNALLY-MANAGED file for pip
  rm -f "$pkgdir/usr/lib/python3.11/EXTERNALLY-MANAGED"

  # Install Python packages
  python -m pip install --no-deps --prefix="$pkgdir/usr" requests pyinstaller
  

  # Build the Python project with PyInstaller
  pyinstaller --onefile app.py --distpath="$pkgdir/usr/bin" --name=vcandy
  
  
  # Fix permissions if necessary
  chmod +x "$pkgdir/usr/bin/vcandy"
}
