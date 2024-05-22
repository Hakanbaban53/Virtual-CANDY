# Maintainer: Hakan İSMAİL <hakanismail53@gmail.com>

pkgname=vcandy
pkgver=0.2
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


  # Install Python packages
  python -m pip install requests pyinstaller --break-system-packages
  
  
  # Build the Python project with PyInstaller
  /home/$USER/.local/bin/pyinstaller --onefile app.py --distpath="$pkgdir/usr/bin" --name=vcandy
  
  # Fix permissions if necessary
  chmod +x "$pkgdir/usr/bin/vcandy"

  # Clean up build artifacts
  rm -rf "$srcdir/Container-and-Virtualization-Installer/build"
  rm -rf "$srcdir/Container-and-Virtualization-Installer/dist"
}
