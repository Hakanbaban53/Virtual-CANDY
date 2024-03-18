packages_data = {
    "arch": [
        {
            "name": "My_Apps",
            "values": [
                {
                    "name": "Visual Studio Code",
                    "type": "AUR-package",
                    "install_value": "visual-studio-code-bin",
                    "check_value": "visual-studio-code-bin",
                    "remove_value": "visual-studio-code-bin",
                },
                {
                    "name": "Github Desktop",
                    "type": "AUR-package",
                    "install_value": "github-desktop-bin",
                    "check_value": "github-desktop-bin",
                    "remove_value": "github-desktop-bin",
                },
                {
                    "name": "Steam",
                    "type": "package",
                    "install_value": "steam",
                    "check_value": "steam",
                    "remove_value": "steam",
                },
                {
                    "name": "Discord",
                    "type": "package",
                    "install_value": "discord",
                    "check_value": "discord",
                    "remove_value": "discord",
                },
                {
                    "name": "Vlc",
                    "type": "package",
                    "install_value": "vlc",
                    "check_value": "vlc",
                    "remove_value": "vlc",
                },
                {
                    "name": "Easyeffects",
                    "type": "package",
                    "install_value": "easyeffects",
                    "check_value": "easyeffects",
                    "remove_value": "easyeffects",
                },
                {
                    "name": "Calf",
                    "type": "package",
                    "install_value": "calf",
                    "check_value": "calf",
                    "remove_value": "calf",
                },
                {
                    "name": "Linux Studio Plugins",
                    "type": "package",
                    "install_value": "lsp-plugins",
                    "check_value": "lsp-plugins",
                    "remove_value": "lsp-plugins",
                },
                {
                    "name": "Wine",
                    "type": "package",
                    "install_value": "wine",
                    "check_value": "wine",
                    "remove_value": "wine",
                },
                {
                    "name": "Google Chrome Stable",
                    "type": "AUR-package",
                    "install_value": "google-chrome",
                    "check_value": "google-chrome",
                    "remove_value": "google-chrome",
                },
            ],
        },
        {
            "name": "VirtualBox-7.0",
            "values": [
                {
                    "name": "Virtual Box Extensions",
                    "type": "AUR-package",
                    "install_value": "virtualbox-ext-oracle",
                    "check_value": "virtualbox-ext-oracle",
                    "remove_value": "virtualbox-ext-oracle",
                },
                {
                    "name": "Virtual Box",
                    "type": "package",
                    "install_value": "virtualbox",
                    "check_value": "virtualbox",
                    "remove_value": "virtualbox",
                },
                {
                    "name": "Add User to vboxusers Group",
                    "type": "group",
                    "install_value": "vboxusers",
                },
            ],
        },
        {
            "name": "Qemu_and_VM_Manager",
            "values": [
                {
                    "name": "Qemu",
                    "type": "package",
                    "install_value": "qemu-full",
                    "check_value": "qemu-full",
                    "remove_value": "qemu-full",
                },
                {
                    "name": "Qemu-KVM GUI Manager",
                    "type": "package",
                    "install_value": "virt-manager",
                    "check_value": "virt-manager",
                    "remove_value": "virt-manager",
                },
                {
                    "name": "Start and Enable libvirtd.service",
                    "type": "service",
                    "install_value": "libvirtd.service",
                },
                {
                    "name": "Add User to libvirt Group.",
                    "type": "group",
                    "install_value": "libvirt",
                },
            ],
        },
        {
            "name": "Docker_CLI_and_Docker_Desktop",
            "values": [
                {
                    "name": "Docker Cli",
                    "type": "package",
                    "install_value": "docker",
                    "check_value": "docker",
                    "remove_value": "docker",
                },
                {
                    "name": "Wget",
                    "type": "package",
                    "install_value": "wget",
                    "check_value": "wget",
                    "remove_value": "",
                },
                {
                    "name": "Docker Desktop",
                    "type": "local-package",
                    "install_value": "https://desktop.docker.com/linux/main/amd64/139021/docker-desktop-4.28.0-x86_64.pkg.tar.zst",
                    "check_value": "docker-desktop",
                    "remove_value": "docker-desktop",
                },
                {
                    "name": "Start and Enable docker.service",
                    "type": "service",
                    "install_value": "docker.service",
                },
                {
                    "name": "Start and Enable docker.socket",
                    "type": "service",
                    "install_value": "docker.socket",
                },
            ],
        },
        {
            "name": "Podman_and_Podman_Desktop",
            "values": [
                {
                    "name": "Flatpak",
                    "type": "package",
                    "install_value": "flatpak",
                    "check_value": "flatpak",
                    "remove_value": "",
                },
                {
                    "name": "Flathub",
                    "type": "repo-flathub",
                    "install_value": "https://dl.flathub.org/repo/flathub.flatpakrepo",
                },
                {
                    "name": "Podman Cli",
                    "type": "package",
                    "install_value": "podman",
                    "check_value": "podman",
                    "remove_value": "podman",
                },
                {
                    "name": "Podman Desktop",
                    "type": "package-flatpak",
                    "install_value": "io.podman_desktop.PodmanDesktop",
                    "check_value": "io.podman_desktop.PodmanDesktop",
                    "remove_value": "io.podman_desktop.PodmanDesktop",
                },
            ],
        },
    ],
    "debian": [
        {
            "name": "My_Apps",
            "values": [
                {
                    "name": "Visual Studio Code Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt-get install wget gpg -y",
                        "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg",
                        "sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg",
                        "sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'",
                        "rm -f packages.microsoft.gpg",
                        "sudo apt-get update",
                    ],
                    "check_script": ["/etc/apt/sources.list.d/vscode.list"],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/vscode.list"
                    ],
                },
                {
                    "name": "Visual Studio Code",
                    "type": "package",
                    "install_value": "code",
                    "check_value": "code",
                    "remove_value": "code",
                },
                {
                    "name": "GitHub Desktop Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt install wget software-properties-common -y",
                        "wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/shiftkey-packages.gpg > /dev/null",
                        "sudo sh -c 'echo \"deb [arch=amd64 signed-by=/usr/share/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/ubuntu/ any main\" > /etc/apt/sources.list.d/shiftkey-packages-desktop.list'",
                        "sudo apt-get update",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/shiftkey-packages-desktop.list"
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/shiftkey-packages-desktop.list"
                    ],
                },
                {
                    "name": "Github Desktop",
                    "type": "package",
                    "install_value": "github-desktop",
                    "check_value": "github-desktop",
                    "remove_value": "github-desktop",
                },
            ],
        },
        {
            "name": "VirtualBox-7.0",
            "values": [
                {
                    "name": "VirtualBox Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt install wget gnupg2 lsb-release -y",
                        "curl -fsSL https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/vbox.gpg",
                        "curl -fsSL https://www.virtualbox.org/download/oracle_vbox.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                        'echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list',
                        "sudo apt update",
                        "sudo apt install linux-headers-$(uname -r) dkms -y",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/virtualbox.list",
                        "/etc/apt/trusted.gpg.d/vbox.gpg",
                        "/etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/virtualbox.list",
                        "sudo rm -rf /etc/apt/trusted.gpg.d/vbox.gpg",
                        "sudo rm -rf /etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                    ],
                },
                {
                    "name": "Virtual Box",
                    "type": "package",
                    "install_value": "virtualbox-7.0",
                    "check_value": "virtualbox-7.0",
                    "remove_value": "virtualbox-7.0",
                },
                {
                    "name": "Add User to vboxusers Group",
                    "type": "group",
                    "install_value": "vboxusers",
                },
            ],
        },
        {
            "name": "Qemu_and_VM_Manager",
            "values": [
                {
                    "name": "Qemu",
                    "type": "package",
                    "install_value": "qemu-system",
                    "check_value": "qemu-system",
                    "remove_value": "qemu-system",
                },
                {
                    "name": "Qemu-KVM GUI Manager",
                    "type": "package",
                    "install_value": "virt-manager",
                    "check_value": "virt-manager",
                    "remove_value": "virt-manager",
                },
                {
                    "name": "Start and Enable libvirtd.service",
                    "type": "service",
                    "install_value": "libvirtd.service",
                },
                {
                    "name": "Add User to libvirt Group.",
                    "type": "group",
                    "install_value": "libvirt",
                },
            ],
        },
        {
            "name": "Docker_CLI_and_Docker_Desktop",
            "values": [
                {
                    "name": "Docker Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt-get install ca-certificates curl -y",
                        "sudo install -d -m 0755 /etc/apt/keyrings",
                        "sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc",
                        "sudo chmod a+r /etc/apt/keyrings/docker.asc",
                        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                        "sudo apt-get update",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/docker.list",
                        "/etc/apt/keyrings/docker.asc",
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/docker.list",
                        "sudo rm -rf /etc/apt/keyrings/docker.asc",
                    ],
                },
                {
                    "name": "Remove Old Docker Cli",
                    "type": "remove-package",
                    "install_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                    "check_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                    "remove_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                },
                {
                    "name": "Install new Docker Cli",
                    "type": "package",
                    "install_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                    "check_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                    "remove_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                },
                {
                    "name": "Docker Desktop",
                    "type": "local-package",
                    "install_value": "https://desktop.docker.com/linux/main/amd64/139021/docker-desktop-4.28.0-amd64.deb",
                    "check_value": "docker-desktop",
                    "remove_value": "docker-desktop",
                },
                {
                    "name": "Start and Enable docker.service",
                    "type": "service",
                    "install_value": "docker.service",
                },
                {
                    "name": "Start and Enable docker.socket",
                    "type": "service",
                    "install_value": "docker.socket",
                },
            ],
        },
        {
            "name": "Podman_and_Podman_Desktop",
            "values": [
                {
                    "name": "Flatpak",
                    "type": "package",
                    "install_value": "flatpak",
                    "check_value": "flatpak",
                    "remove_value": "",
                },
                {
                    "name": "Flathub",
                    "type": "repo-flathub",
                    "install_value": "https://dl.flathub.org/repo/flathub.flatpakrepo",
                },
                {
                    "name": "Podman Cli",
                    "type": "package",
                    "install_value": "podman",
                    "check_value": "podman",
                    "remove_value": "podman",
                },
                {
                    "name": "Podman Desktop",
                    "type": "package-flatpak",
                    "install_value": "io.podman_desktop.PodmanDesktop",
                    "check_value": "io.podman_desktop.PodmanDesktop",
                    "remove_value": "io.podman_desktop.PodmanDesktop",
                },
            ],
        },
    ],
    "fedora": [
        {
            "name": "Rpm_Fusion",
            "values": [
                {
                    "name": "DNF repository manager",
                    "type": "package",
                    "install_value": "dnf-plugins-core",
                    "check_value": "dnf-plugins-core",
                    "remove_value": "dnf-plugins-core",
                },
                {
                    "name": "Enable RPM Fusion free",
                    "type": "url-package",
                    "install_value": "https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm",
                    "check_value": "rpmfusion-free-release",
                    "remove_value": "rpmfusion-free-release",
                },
                {
                    "name": "Enable RPM Fusion non-free",
                    "type": "url-package",
                    "install_value": "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm",
                    "check_value": "rpmfusion-nonfree-release",
                    "remove_value": "rpmfusion-nonfree-release",
                },
            ],
        },
        {
            "name": "My_Apps",
            "values": [
                {
                    "name": "Nvidia akmod",
                    "type": "package",
                    "install_value": "akmod-nvidia",
                    "check_value": "akmod-nvidia",
                    "remove_value": "akmod-nvidia",
                },
                {
                    "name": "Nvidia CUDA",
                    "type": "package",
                    "install_value": "xorg-x11-drv-nvidia-cuda",
                    "check_value": "xorg-x11-drv-nvidia-cuda",
                    "remove_value": "xorg-x11-drv-nvidia-cuda",
                },
                {
                    "name": "Discord",
                    "type": "package",
                    "install_value": "discord",
                    "check_value": "discord",
                    "remove_value": "discord",
                },
                {
                    "name": "Google Chrome Stable",
                    "type": "package",
                    "install_value": "google-chrome-stable",
                    "check_value": "google-chrome-stable",
                    "remove_value": "google-chrome-stable",
                },
                {
                    "name": "Steam",
                    "type": "package",
                    "install_value": "steam",
                    "check_value": "steam",
                    "remove_value": "steam",
                },
                {
                    "name": "Easyeffects",
                    "type": "package",
                    "install_value": "easyeffects",
                    "check_value": "easyeffects",
                    "remove_value": "easyeffects",
                },
                {
                    "name": "Visual Studio Code Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc",
                        "sudo sh -c 'echo -e \"[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc\" > /etc/yum.repos.d/vscode.repo'",
                    ],
                    "check_script": ["/etc/yum.repos.d/vscode.repo"],
                    "remove_script": ["sudo rm -rf /etc/yum.repos.d/vscode.repo"],
                },
                {
                    "name": "Visual Studio Code",
                    "type": "package",
                    "install_value": "code",
                    "check_value": "code",
                    "remove_value": "code",
                },
                {
                    "name": "GitHub Desktop Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo rpm --import https://rpm.packages.shiftkey.dev/gpg.key",
                        "sudo sh -c 'echo -e \"[shiftkey-packages]\\nname=GitHub Desktop\\nbaseurl=https://rpm.packages.shiftkey.dev/rpm/\\nenabled=1\\ngpgcheck=1\\nrepo_gpgcheck=1\\ngpgkey=https://rpm.packages.shiftkey.dev/gpg.key\" > /etc/yum.repos.d/shiftkey-packages.repo'",
                    ],
                    "check_script": ["/etc/yum.repos.d/shiftkey-packages.repo"],
                    "remove_script": [
                        "sudo rm -rf /etc/yum.repos.d/shiftkey-packages.repo"
                    ],
                },
                {
                    "name": "Github Desktop",
                    "type": "package",
                    "install_value": "github-desktop",
                    "check_value": "github-desktop",
                    "remove_value": "github-desktop",
                },
            ],
        },
        {
            "name": "VirtualBox-7.0",
            "values": [
                {
                    "name": "Virtual Box Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo dnf -y install @development-tools",
                        "sudo dnf -y install kernel-devel kernel-headers dkms qt5-qtx11extras elfutils-libelf-devel zlib-devel",
                        "sudo wget http://download.virtualbox.org/virtualbox/rpm/fedora/virtualbox.repo -P /etc/yum.repos.d/",
                        "sudo dnf makecache -y",
                    ],
                    "check_script": ["/etc/yum.repos.d/virtualbox.repo"],
                    "remove_script": ["sudo rm -rf /etc/yum.repos.d/virtualbox.repo"],
                },
                {
                    "name": "Virtual Box",
                    "type": "package",
                    "install_value": "VirtualBox-7.0",
                    "check_value": "VirtualBox-7.0",
                    "remove_value": "VirtualBox-7.0",
                },
                {
                    "name": "Start and Enable vboxdrv",
                    "type": "service",
                    "install_value": "vboxdrv",
                },
                {
                    "name": "Add User to vboxusers Group",
                    "type": "group",
                    "install_value": "vboxusers",
                },
                {
                    "name": "Virtual Box Extensions",
                    "type": "get-keys",
                    "install_script": [
                        "wget https://download.virtualbox.org/virtualbox/7.0.14/Oracle_VM_VirtualBox_Extension_Pack-7.0.14.vbox-extpack",
                        "echo 'y' | sudo vboxmanage extpack install Oracle_VM_VirtualBox_Extension_Pack-7.0.14.vbox-extpack",
                    ],
                    "check_script": [""],
                    "remove_script": [""],
                },
            ],
        },
        {
            "name": "Qemu_and_VM_Manager",
            "values": [
                {
                    "name": "Qemu package group",
                    "type": "package",
                    "install_value": "@virtualization",
                    "check_value": "virt-manager",
                    "remove_value": "@virtualization",
                },
                {
                    "name": "libvirtd.service for qemu",
                    "type": "service",
                    "install_value": "libvirtd.service",
                },
                {
                    "name": "Add User to libvirt Group.",
                    "type": "group",
                    "install_value": "libvirt",
                },
            ],
        },
        {
            "name": "Docker_CLI_and_Docker_Desktop",
            "values": [
                {
                    "name": "Docker Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo wget https://download.docker.com/linux/fedora/docker-ce.repo -P /etc/yum.repos.d/"
                    ],
                    "check_script": ["/etc/yum.repos.d/docker-ce.repo"],
                    "remove_script": ["sudo rm -rf /etc/yum.repos.d/docker-ce.repo"],
                },
                {
                    "name": "Remove Old Docker Cli",
                    "type": "remove-package",
                    "install_value": "",
                    "check_value": "",
                    "remove_value": "docker  docker-client  docker-client-latest  docker-common  docker-latest docker-selinux docker-latest-logrotate  docker-logrotate  docker-engine-selinux  docker-engine",
                },
                {
                    "name": "Install new Docker Cli",
                    "type": "package",
                    "install_value": "docker-ce  docker-ce-cli  containerd.io  docker-buildx-plugin  docker-compose-plugin",
                    "check_value": "docker-ce  docker-ce-cli  containerd.io  docker-buildx-plugin  docker-compose-plugin",
                    "remove_value": "docker-ce  docker-ce-cli  containerd.io  docker-buildx-plugin  docker-compose-plugin",
                },
                {
                    "name": "Docker Desktop",
                    "type": "local-package",
                    "install_value": "https://desktop.docker.com/linux/main/amd64/139021/docker-desktop-4.28.0-x86_64.rpm",
                    "check_value": "docker-desktop",
                    "remove_value": "docker-desktop",
                },
                {
                    "name": "Start and Enable docker.service",
                    "type": "service",
                    "install_value": "docker",
                },
            ],
        },
        {
            "name": "Podman_and_Podman_Desktop",
            "values": [
                {
                    "name": "Flatpak",
                    "type": "package",
                    "install_value": "flatpak",
                    "check_value": "flatpak",
                    "remove_value": "",
                },
                {
                    "name": "Flathub",
                    "type": "repo-flathub",
                    "install_value": "https://dl.flathub.org/repo/flathub.flatpakrepo",
                },
                {
                    "name": "Podman Cli",
                    "type": "package",
                    "install_value": "podman",
                    "check_value": "podman",
                    "remove_value": "podman",
                },
                {
                    "name": "Podman Desktop",
                    "type": "package-flatpak",
                    "install_value": "io.podman_desktop.PodmanDesktop",
                    "check_value": "io.podman_desktop.PodmanDesktop",
                    "remove_value": "io.podman_desktop.PodmanDesktop",
                },
            ],
        },
    ],
    "ubuntu": [
        {
            "name": "My_Apps",
            "values": [
                {
                    "name": "Visual Studio Code Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt-get install wget gpg -y",
                        "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg",
                        "sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg",
                        "sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'",
                        "rm -f packages.microsoft.gpg",
                        "sudo apt-get update",
                    ],
                    "check_script": ["/etc/apt/sources.list.d/vscode.list"],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/vscode.list"
                    ],
                },
                {
                    "name": "Visual Studio Code",
                    "type": "package",
                    "install_value": "code",
                    "check_value": "code",
                    "remove_value": "code",
                },
                {
                    "name": "GitHub Desktop Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt install wget software-properties-common -y",
                        "wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/shiftkey-packages.gpg > /dev/null",
                        "sudo sh -c 'echo \"deb [arch=amd64 signed-by=/usr/share/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/ubuntu/ any main\" > /etc/apt/sources.list.d/shiftkey-packages-desktop.list'",
                        "sudo apt-get update",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/shiftkey-packages-desktop.list"
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/shiftkey-packages-desktop.list"
                    ],
                },
                {
                    "name": "Github Desktop",
                    "type": "package",
                    "install_value": "github-desktop",
                    "check_value": "github-desktop",
                    "remove_value": "github-desktop",
                },
            ],
        },
        {
            "name": "VirtualBox-7.0",
            "values": [
                {
                    "name": "VirtualBox Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get update",
                        "sudo apt install wget gnupg2 lsb-release -y",
                        "curl -fsSL https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/vbox.gpg",
                        "curl -fsSL https://www.virtualbox.org/download/oracle_vbox.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                        'echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list',
                        "sudo apt update",
                        "sudo apt install linux-headers-$(uname -r) dkms -y",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/virtualbox.list",
                        "/etc/apt/trusted.gpg.d/vbox.gpg",
                        "/etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/virtualbox.list",
                        "sudo rm -rf /etc/apt/trusted.gpg.d/vbox.gpg",
                        "sudo rm -rf /etc/apt/trusted.gpg.d/oracle_vbox.gpg",
                    ],
                },
                {
                    "name": "Virtual Box",
                    "type": "package",
                    "install_value": "virtualbox-7.0",
                    "check_value": "virtualbox-7.0",
                    "remove_value": "virtualbox-7.0",
                },
                {
                    "name": "Add User to vboxusers Group",
                    "type": "group",
                    "install_value": "vboxusers",
                },
            ],
        },
        {
            "name": "Qemu_and_VM_Manager",
            "values": [
                {
                    "name": "Qemu",
                    "type": "package",
                    "install_value": "qemu-system",
                    "check_value": "qemu-system",
                    "remove_value": "qemu-system",
                },
                {
                    "name": "Qemu-KVM GUI Manager",
                    "type": "package",
                    "install_value": "virt-manager",
                    "check_value": "virt-manager",
                    "remove_value": "virt-manager",
                },
                {
                    "name": "Start and Enable libvirtd.service",
                    "type": "service",
                    "install_value": "libvirtd.service",
                },
                {
                    "name": "Add User to libvirt Group.",
                    "type": "group",
                    "install_value": "libvirt",
                },
            ],
        },
        {
            "name": "Docker_CLI_and_Docker_Desktop",
            "values": [
                {
                    "name": "Docker Repository",
                    "type": "get-keys",
                    "install_script": [
                        "sudo apt-get install ca-certificates curl -y",
                        "sudo install -d -m 0755 /etc/apt/keyrings",
                        "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
                        "sudo chmod a+r /etc/apt/keyrings/docker.asc",
                        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                        "sudo apt-get update",
                    ],
                    "check_script": [
                        "/etc/apt/sources.list.d/docker.list",
                        "/etc/apt/keyrings/docker.asc",
                    ],
                    "remove_script": [
                        "sudo rm -rf /etc/apt/sources.list.d/docker.list",
                        "sudo rm -rf /etc/apt/keyrings/docker.asc",
                    ],
                },
                {
                    "name": "Remove Old Docker Cli",
                    "type": "remove-package",
                    "install_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                    "check_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                    "remove_value": "docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc",
                },
                {
                    "name": "Install new Docker Cli",
                    "type": "package",
                    "install_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                    "check_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                    "remove_value": "docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                },
                {
                    "name": "Docker Desktop",
                    "type": "local-package",
                    "install_value": "https://desktop.docker.com/linux/main/amd64/139021/docker-desktop-4.28.0-amd64.deb",
                    "check_value": "docker-desktop",
                    "remove_value": "docker-desktop",
                },
                {
                    "name": "Start and Enable docker.service",
                    "type": "service",
                    "install_value": "docker.service",
                },
                {
                    "name": "Start and Enable docker.socket",
                    "type": "service",
                    "install_value": "docker.socket",
                },
            ],
        },
        {
            "name": "Podman_and_Podman_Desktop",
            "values": [
                {
                    "name": "Flatpak",
                    "type": "package",
                    "install_value": "flatpak",
                    "check_value": "flatpak",
                    "remove_value": "",
                },
                {
                    "name": "Flathub",
                    "type": "repo-flathub",
                    "install_value": "https://dl.flathub.org/repo/flathub.flatpakrepo",
                },
                {
                    "name": "Podman Cli",
                    "type": "package",
                    "install_value": "podman",
                    "check_value": "podman",
                    "remove_value": "podman",
                },
                {
                    "name": "Podman Desktop",
                    "type": "package-flatpak",
                    "install_value": "io.podman_desktop.PodmanDesktop",
                    "check_value": "io.podman_desktop.PodmanDesktop",
                    "remove_value": "io.podman_desktop.PodmanDesktop",
                },
            ],
        },
    ],
}
