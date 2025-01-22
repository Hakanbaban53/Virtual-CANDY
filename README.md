<h1 align="center"> Virtual CANDY "VCANDY" 🖥️<h1>

<h4 align="center">It's a package manager for Linux distributions. Handles the installation and removal of packages with a simple command-line interface or terminal UI. Also includes a JSON file for package information and a script for building packages for different distributions.</h4>

<div align="center">
  <img src="./assets/arguments.gif" style="width: 500px; height: auto;">
  <img src="./assets/terminal_ui.gif" style="width: 500px; height: auto;">
</div>

## 📦 Pre Builded Packages
This Packages building with github action. 
You can download it from [here](https://github.com/Hakanbaban53/Virtual-CANDY/releases) (Not yet available for Arch Linux. Please build from Github repository)

## 🏗️ Build From Github Repository and Testing

<details><summary>Arch</summary>

The initial installation of vcandy can be done by cloning the PKGBUILD and
building with makepkg:

```sh
pacman -S --needed git
git clone https://github.com/Hakanbaban53/Virtual-CANDY.git
cd Virtual-CANDY
makepkg -si
```

If you want to do all of this at once, we can chain the commands like so:

```sh
pacman -S --needed git && git clone https://github.com/Hakanbaban53/Virtual-CANDY.git && cd Virtual-CANDY && makepkg -si
```

</details>

<details><summary>Debian or Ubuntu</summary>

To install Candy on Debian or Ubuntu, it is sufficient to first clone this repository and make the build_deb_package.sh script executable and run it.
It will automatically create and install the debian package:

```sh
apt install git
git clone https://github.com/Hakanbaban53/Virtual-CANDY.git
cd Virtual-CANDY/test/scripts
chmod +x ./build_deb_package.sh
./build_deb_package.sh
```

If you want to do all of this at once, we can chain the commands like so:

```sh
apt install git && git clone https://github.com/Hakanbaban53/Virtual-CANDY.git && cd Virtual-CANDY/test/scripts && chmod +x ./build_deb_package.sh && ./build_deb_package.sh
```

</details>

<details><summary>Fedora</summary>

To install Candy on Fedora, it is sufficient to first clone this repository and make the build_rpm_package.sh script executable and run it.
It will automatically create and install the rpm package:

```sh
dnf install git
git clone https://github.com/Hakanbaban53/Virtual-CANDY.git
cd Virtual-CANDY/test/scripts
chmod +x ./build_rpm_package.sh
./build_rpm_package.sh
```

If you want to do all of this at once, we can chain the commands like so:

```sh
dnf install git && git clone https://github.com/Hakanbaban53/Virtual-CANDY.git && cd Virtual-CANDY/test/scripts && chmod +x ./build_rpm_package.sh && ./build_rpm_package.sh
```

</details>
- 🗑️ If you want to remove the package:

    # Arch
    pacman -Rsc vcandy
    
    # Debian or Ubuntu
    apt remove vcandy
    
    # Fedora
    dnf remove vcany

- Also you can check the [TEST.md](./docs/TEST.md) file for more information.

## ⚙️ Usage

<details><summary><strong><em>With Arguments</em></strong></summary>


#### Arguments

| Argument         | Description                                                                                                              | CLI  | TUI |
|------------------|--------------------------------------------------------------------------------------------------------------------------|------|-----|
| `-a`, `--action` | Specifies the action to perform. Choices are `'install'` or `'remove'`. Default is `'install'`.                         | ✅   | ❌  |
| `-j`, `--json`   | Specifies the JSON file to use for package information. Defaults to predefined.                                         | ✅   | ✅  |
| `-u`, `--url`    | Specifies the URL to use for package information. Overrides the JSON file. Its need the use with `-r` or `--refresh`.   | ✅   | ✅  |
| `-r`, `--refresh`| Refreshes the JSON data regardless of its file age. Useful to get the latest package information.                        | ✅   | ✅  |
| `-v`, `--verbose`| Enables verbose output for detailed information during execution. Helps with debugging or understanding process details. | ✅   | ✅  |
| `-d`, `--dry-run`| Performs a dry run of the command without making any changes. Useful for testing what would be done.                     | ✅   | ✅  |
| `-l`, `--list`   | Lists available packages for the specified distribution. Useful for checking what packages are available.               | ✅   | ❌  |
| `--distribution` | Specifies the Linux distribution to use. Defaults to auto-detecting the distribution.                                   | ✅   | ✅  |
| `--all`          | Installs or removes all available packages for the specified distribution.                                              | ✅   | ❌  |
| `packages`       | List of packages to install or remove.                                                                                   | ✅   | ❌  |


- **Install specific packages**:
  ```bash
  vcand -a install package1 package2
  ```

- **Remove specific packages**:
  ```bash
  vcand -a remove package1 package2
  ```

- **Refresh JSON data**:
  ```bash
  vcand -r
  ```

- **Enable verbose output**:
  ```bash
  vcand -v -a install package1
  ```

- **Perform a dry run**:
  ```bash
  vcand -d -a install package1
  ```

- **List available packages**:
  ```bash
  vcand -l --distribution ubuntu
  ```

- **Install or remove all available packages**:
  ```bash
  vcand --all -a install
  ```

- **Specify distribution**:
  ```bash
  vcand --distribution ubuntu -a install package1
  ```

And one more thing. Arguments are case-sensitive. You need to give the package names as specified below:
</details>

### 
<details><summary><strong><em>With Terminal UI</em></strong></summary>

<p align="left">If you install the in your pc you can use in the terminal vcandy or you can use "python app.py". Terminal UI start with default. Basic terminal UI for installer. </p>
<p align="left">Use Left/Right arrow key select "yes" or "no". Press "Enter" key for confirm..</p>
<p align="left">Use Up/Down arrow key move each other packager. Use "Tab" key Select/Unselect packages. Press Enter key the confirm packages.</p>

</details>

## 📦 Package Managing
- If you want to make own package `json` file for your purposes, you can check the [PACKAGES.md](./docs/PACKAGES.md) file for more information.

## ⁉️ IMPORTANT

- Reboot for the installed Apps to appear in the App menu and work properly!

## 📂 Folder structure

```css
🗃
├── 🗎 README.md
├── 🗎 LICENSE
├── 🖿 assets
│   └── 🖻 preview images
├── 🖿 docs
│   ├── 🗎 PACKAGES.md
│   └── 🗎 TEST.md
├── 🖿 packages
│   └── 🗎 packages.json
├── 🖿 src
│   ├── app.py
│   ├── 🖿 core
│   │   ├── 🗎 __check_repository_connection__.py
│   │   ├── 🗎 __command_handler__.py
│   │   ├── 🗎 __constants__.py
│   │   ├── 🗎 __get_os_package_manager__.py
│   │   ├── 🗎 __get_packages_data__.py
│   │   ├── 🗎 __linux_system__.py
│   │   ├── 🗎 __logging_manager__.py
│   │   ├── 🖿 package_handlers
│   │   │   ├── 🗎 __aur__.py
│   │   │   ├── 🗎 __flatpak__.py
│   │   │   ├── 🗎 __local__.py
│   │   │   ├── 🗎 __normal__.py
│   │   │   └── 🗎 __special__.py
│   │   └── 🗎 __pack_type_handler__.py
│   └── 🖿 utils
│       ├── 🖿 cli
│       │   └── 🗎 __arguments__.py
│       └── 🖿 TUI
│           ├── 🖿 core
│           │   ├── 🖿 components
│           │   │   ├── 🗎 __app_selector__.py
│           │   │   ├── 🗎 __footer__.py
│           │   │   ├── 🗎 __header__.py
│           │   │   ├── 🗎 __modal_win__.py
│           │   │   ├── 🗎 __print_apps__.py
│           │   │   └── 🗎 __selections__.py
│           │   ├── 🖿 static
│           │   │   ├── 🗎 __color_init__.py
│           │   │   └── 🗎 __data__.py
│           │   └── 🖿 utils
│           │       ├── 🗎 __check_connection__.py
│           │       ├── 🗎 __clean_line__.py
│           │       ├── 🗎 __clear_midde_section__.py
│           │       ├── 🗎 __errors_.py
│           │       ├── 🗎 __helper_keys__.py
│           │       ├── 🗎 __input__.py
│           │       └── 🗎 __resize_handler__.py
│           └── 🗎 __terminal_UI__.py
└── 🖿 test
    ├── 🖿 scripts
    │   ├── 🗎 build_deb_package.sh
    │   ├── 🗎 build_rpm_package.sh
    │   └── 🗎 PKGBUILD
    └── 🗎 test_app.py

```

<h2 align="center"> Hakan İSMAİL 💙 </h2>
