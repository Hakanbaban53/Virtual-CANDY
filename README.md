# Virtualization and container applications installer 🖥️

<h4 align="center">An application that installs certain virtualization applications (Docker/Docker Desktop, VirtManager/QEMU, VirtualBox and Podman/Podman Desktop) on Linux via argument or command line user interface.</h4>

<div align="center">
  <img src="./assets/arguments.gif" style="width: 500px; height: auto;">
  <img src="./assets/Command_gui.gif" style="width: 500px; height: auto;">
</div>

## 💡 Installation

<details><summary>Arch</summary>

The initial installation of vcandy can be done by cloning the PKGBUILD and
building with makepkg:

```sh
pacman -S --needed git
git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git
cd Container-and-Virtualization-Installer
makepkg -si
```

If you want to do all of this at once, we can chain the commands like so:

```sh
pacman -S --needed git && git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git && cd Container-and-Virtualization-Installer && makepkg -si
```

</details>

<details><summary>Debian or Ubuntu</summary>

To install Candy on Debian or Ubuntu, it is sufficient to first clone this repository and make the build_deb_package.sh script executable and run it.
It will automatically create and install the debian package:

```sh
apt install git
git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git
cd Container-and-Virtualization-Installer
chmod +x ./build_deb_package.sh
./build_deb_package.sh
```

If you want to do all of this at once, we can chain the commands like so:

```sh
apt install git && git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git && cd Container-and-Virtualization-Installer && chmod +x ./build_deb_package.sh && ./build_deb_package.sh
```

</details>

<details><summary>Fedora</summary>

To install Candy on Fedora, it is sufficient to first clone this repository and make the build_rpm_package.sh script executable and run it.
It will automatically create and install the rpm package:

```sh
dnf install git
git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git
cd Container-and-Virtualization-Installer
chmod +x ./build_rpm_package.sh
./build_rpm_package.sh
```

If you want to do all of this at once, we can chain the commands like so:

```sh
dnf install git && git clone https://github.com/Hakanbaban53/Container-and-Virtualization-Installer.git && cd Container-and-Virtualization-Installer && chmod +x ./build_rpm_package.sh && ./build_rpm_package.sh
```

</details>
- 🗑️ If you want to remove the package:

    # Arch
    pacman -Rsc vcandy
    
    # Debian or Ubuntu
    apt remove vcandy
    
    # Fedora
    dnf remove vcany

## ⚙️ Usage

<details><summary><strong><em>With Arguments</em></strong></summary>


#### Arguments

| Option         | Description                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| -a             | You select the action. 'install' or 'remove'. Default is 'install'.                                                                         |
| -o             | Hide or show terminal output. 'silent' hides the package manager and other outputs. 'noisy' shows the terminal output. Default is 'silent'. |
| --distribution | Specify the Linux distribution. Default detects your Linux distro. Use this if you want to specify another distro.                          |

```css
// If you install the app on your system;
vcandy -a remove -o noisy <package_name> # This is a remove example.

vcandy -a remove -o noisy VirtualBox-7.0 Qemu_and_VM_Manager # You can use more than one package. Like this.

// If you not install the app on your system;
python3 app.py -a remove -o noisy <package_name> # This is a remove example.

python3 app.py -a remove -o noisy VirtualBox-7.0 Qemu_and_VM_Manager # You can use more than one package. Like this.
```

And one more thing. Arguments are case-sensitive. You need to give the package names as specified below:
</details>

### 
<details><summary><strong><em>With Command UI</em></strong></summary>

<p align="left">If you install the in your pc you can use in the terminal vcandy or you can use "python app.py". Command UI start with default. Basic terminal UI for installer. </p>
<p align="left">Use Left/Right arrow key select "yes" or "no". Press "Enter" key for confirm..</p>
<p align="left">Use Up/Down arrow key move each other packager. Use "Tab" key Select/Unselect packages. Press Enter key the confirm packages.</p>

</details>

## 📦 Packages

<details><summary>Package Names</summary>

- Package names in the packages.py.

```css
🗃 .
├── 📦 My_Apps
│  ├── 🗋 Visual Studio Code
│  └── 🗋 Github Desktop
├── 📦 VirtualBox-7.0
│  ├── 🗋 VirtualBox 7.0
│  └── 🗋 Virtual Box Extensions
├── 📦 Qemu_and_VM_Manager
│  ├── 🗋 QEMU
│  └── 🗋 Virtual Machine Manager
├── 📦 Docker_CLI_and_Docker_Desktop
│  ├── 🗋 Docker CLI
│  └── 🗋 Docker Desktop
└── 📦 Podman_and_Podman_Desktop
   ├── 🗋 Podman CLI
   └── 🗋 Podman Desktop
```

</details>


## ⁉️ IMPORTANT

- Reboot for the installed Apps to appear in the App menu and work properly!

## 📂 Folder structure

```css
🗃 .
├── 🖿 assets
│  └── 🖻 preview images
├── 🖿 functions
│  ├── 🗎 __check_repository_connection__.py
│  ├── 🗎 __cli_dependencies_install__.py
│  └── 🗎 __get_os_package_manager__.py
├── 🖿 linux_distros
│  ├── 🗎 __arch__.py
│  ├── 🗎 __debian__.py
│  ├── 🗎 __fedora__.py
│  └── 🗎 __ubuntu__.py
├── 🖿 packages
│  └── 🗎 packages.py
├── 🖿 scripts
│  ├── 🗎 __arguments__.py
│  └── 🗎 __command_GUI__.py
├── 🗎 README.md
└── 🗎 app.py

```

## Hakan İSMAİL 💙
