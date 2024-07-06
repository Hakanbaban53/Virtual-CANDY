import os
from pathlib import Path
import subprocess
import shutil
import logging


class VMwareInstaller:
    PKGVER = "17.5.2"
    BUILDVER = "23775571"
    TOOLS_VERSION = "12.4.0-23259341"
    CARCH = "x86_64"
    BASE_URL = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{PKGVER}/{BUILDVER}/linux/packages"
    BUNDLE_URL = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{PKGVER}/{BUILDVER}/linux/core/VMware-Workstation-{PKGVER}-{BUILDVER}.{CARCH}.bundle.tar"
    BUNDLE_FILENAME = f"VMware-Workstation-{PKGVER}-{BUILDVER}.{CARCH}.bundle.tar"
    CACHE_DIR = Path(os.path.expanduser("~")) / ".cache" / "vcandy" / "VMware"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    COMPONENT_FILENAMES = [
        f"vmware-tools-linux-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-linuxPreGlibc25-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-netware-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-solaris-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-windows-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-winPre2k-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-winPreVista-{TOOLS_VERSION}.{CARCH}.component.tar",
    ]
    EXTRACTED_DIR = os.path.join(CACHE_DIR, "extracted_components")
    DEPENDENCIES = []
    PACKAGE_MANAGER = ""
    PACKAGE_NAME = "vmware-host-modules"
    PACKAGE_VERSION = PKGVER  # Do not make the PACKAGE_VERSION to PKGVER
    SERVICES = {
        "vmware-networks-configuration.service",
        "vmware-networks.service",
        "vmware-usbarbitrator.service",
        "vmware-networks.path",
        "vmware-usbarbitrator.path",
    }

    def __init__(self, hide, action, linux_distro):
        self.COMPONENT_URLS = [
            f"{self.BASE_URL}/{filename}" for filename in self.COMPONENT_FILENAMES
        ]
        self.setup_logging()
        self.hide = hide
        self.action = action
        self.linux_distro = linux_distro

        if self.linux_distro == "fedora":
            self.PACKAGE_MANAGER = "dnf"
            self.DEPENDENCIES = [
                "kernel-devel",
                "kernel-headers",
                "git",
                "wget",
                "gcc",
                "dkms",
                "make",
                "patch",
                "net-tools",
            ]
        elif self.linux_distro in {"debian", "ubuntu"}:
            self.PACKAGE_MANAGER = "apt"
            self.DEPENDENCIES = [
                "build-essential",
                "git",
                "wget",
                "gcc",
                "dkms",
                "make",
                "patch",
                "net-tools",
            ]
            kernel_version = subprocess.run(
                "uname -r", shell=True, text=True
            ).stdout.strip()
            self.DEPENDENCIES.append(f"linux-headers-{kernel_version}")

        if self.action == "install":
            self.install_vmware()
        elif self.action == "remove":
            self.uninstall_vmware()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(f"{self.CACHE_DIR}/vmware_installer.log"),
                logging.StreamHandler(),
            ],
        )

    def run_command(self, command):
        """Run a shell command and print its output."""
        result = subprocess.run(
            command, shell=True, text=True, stderr=self.hide, stdout=self.hide
        )
        if result.returncode != 0:
            print(f"Command failed: {command}\n{result.stderr}")
            return False
        return True

    def download_file(self, url, filename):
        """Download a file from a URL using wget."""
        print(f"Downloading {filename} from {url}...")
        self.run_command(f"wget -O {os.path.join(self.CACHE_DIR, filename)} {url}")
        print(f"Downloaded {filename}.\n")

    def extract_tar(self, filename):
        """Extract a tar file."""
        print(f"Extracting {filename} to {self.EXTRACTED_DIR}...")
        self.run_command(
            f"tar -xf {os.path.join(self.CACHE_DIR, filename)} -C {self.EXTRACTED_DIR}"
        )
        self.run_command(f"find {self.EXTRACTED_DIR} -name '*.xml' -type f -delete")

    def clone_repository(self, repo_url, branch, destination):
        """Clone a Git repository."""
        print(f"Cloning repository from {repo_url} to {destination}...")
        clone_command = f"git clone -b {branch} {repo_url} {destination}"
        self.run_command(clone_command)

    def sparse_checkout(self, repo_url, branch, folder_to_clone, clone_location):
        """Perform a sparse checkout from a Git repository."""
        self.clone_repository(repo_url, branch, clone_location)
        os.chdir(clone_location)

        commands = [
            "git sparse-checkout init --cone",
            f"git sparse-checkout set {folder_to_clone}",
            f"git checkout {branch}",  # Specify the branch explicitly here
        ]

        for command in commands:
            self.run_command(command)

        print(
            f"Folder {folder_to_clone} has been cloned to {clone_location}/{folder_to_clone}"
        )

    def install_vmware_modules(self):
        """Install VMware modules."""

        os.chdir(f"{self.CACHE_DIR}/vmware_host_modules")
        print("Making and copying vmmon.tar and vmnet.tar...")
        self.run_command("make tarballs")
        self.run_command(
            f"sudo cp -v vmmon.tar vmnet.tar /usr/lib/vmware/modules/source/"
        )

        print("Extracting vmmon.tar and vmnet.tar...")
        os.chdir("/usr/lib/vmware/modules/source/")
        self.run_command("sudo tar -xvf vmmon.tar")
        self.run_command("sudo tar -xvf vmnet.tar")

        print("Creating directories for DKMS...")
        self.run_command(
            f"sudo mkdir -p /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}"
        )

        print("Moving source files to DKMS directory...")
        self.run_command(
            f"sudo cp -r vmmon-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )
        self.run_command(
            f"sudo cp -r vmnet-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )

        print("Copying Makefile and dkms.conf to DKMS directory...")
        self.run_command(
            f"sudo cp -r {self.CACHE_DIR}/vmware_dkms_files/vmware_dkms_files/Makefile /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )

        print("Creating DKMS configuration for vmware-host-modules...")
        with open(
            f"{self.CACHE_DIR}/vmware_dkms_files/vmware_dkms_files/dkms.conf", "r"
        ) as template_file:
            dkms_conf_template = template_file.read()

        dkms_conf_vmware_host_modules = dkms_conf_template.format(
            PACKAGE_NAME=self.PACKAGE_NAME, PACKAGE_VERSION=self.PACKAGE_VERSION
        )

        temp_conf_path = f"/tmp/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}-dkms.conf"
        with open(temp_conf_path, "w") as conf_file:
            conf_file.write(dkms_conf_vmware_host_modules)

        self.run_command(
            f"sudo mv {temp_conf_path} /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/dkms.conf"
        )
        print(
            f"DKMS configuration file created at /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/dkms.conf"
        )

        print("Applying patches...")
        self.run_command(
            f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmmon-only < {self.CACHE_DIR}/vmware_dkms_files/vmware_dkms_files/vmmon.patch"
        )
        self.run_command(
            f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmnet-only < {self.CACHE_DIR}/vmware_dkms_files/vmware_dkms_files/vmnet.patch"
        )

        print("Adding and building vmware-host-modules module with DKMS...")
        self.run_command(
            f"sudo dkms add -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms build -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms install -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )

        print("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")

        os.chdir("..")  # Return to previous directory

    def copy_service_files(self):
        """Copy systemd service files for VMware."""
        for filename in self.SERVICES:
            self.run_command(f"sudo cp {self.CACHE_DIR}/vmware_dkms_files/vmware_dkms_files/{filename} /etc/systemd/system/{filename}")
            print(f"Copied {filename}.")

        # Reload systemd daemon to apply changes
        self.run_command("sudo systemctl daemon-reload")
        

    def install_dependencies(self):
        """Install necessary dependencies for VMware."""
        print("Installing dependencies...")
        self.run_command(
            f"sudo {self.PACKAGE_MANAGER} install -y {' '.join(self.DEPENDENCIES)}"
        )

    def install_vmware(self):
        """Perform the full VMware installation."""

        print("\nStep 1: Installing necessary dependencies...")
        self.install_dependencies()

        print("\nStep 2: Clone the required repositories...")
        print(f"Cloning {self.PACKAGE_NAME} repository...")
        self.clone_repository(
            f"https://github.com/nan0desu/{self.PACKAGE_NAME}.git",
            "tmp/workstation-17.5.2-k6.9.1",
            f"{self.CACHE_DIR}/vmware_host_modules"
        )

        print("Getting the DKMS modules")
        self.sparse_checkout(
            "https://github.com/Hakanbaban53/Container-and-Virtualization-Installer",
            "main",
            "vmware_dkms_files",
            f"{self.CACHE_DIR}/vmware_dkms_files",
        )

        print(
            "\nStep 3: Downloading the VMware Workstation installer and components..."
        )
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        self.download_file(self.BUNDLE_URL, self.BUNDLE_FILENAME)
        for url, filename in zip(self.COMPONENT_URLS, self.COMPONENT_FILENAMES):
            self.download_file(url, filename)

        print("\nStep 4: Extracting the bundle file...")
        self.run_command(
            f"tar -xf {os.path.join(self.CACHE_DIR, self.BUNDLE_FILENAME)} -C {self.CACHE_DIR}"
        )

        os.makedirs(self.EXTRACTED_DIR, exist_ok=True)
        for filename in self.COMPONENT_FILENAMES:
            self.extract_tar(filename)

        print("\nStep 5: Making the installer executable...")
        bundle_installer = (
            f"VMware-Workstation-{self.PKGVER}-{self.BUILDVER}.{self.CARCH}.bundle"
        )
        self.run_command(f"chmod +x {os.path.join(self.CACHE_DIR, bundle_installer)}")

        print(
            "\nStep 6: Running the VMware Workstation installer with extracted components..."
        )
        extracted_components = [
            os.path.join(self.EXTRACTED_DIR, filename)
            for filename in os.listdir(self.EXTRACTED_DIR)
        ]
        install_command = (
            f"sudo {os.path.join(self.CACHE_DIR, bundle_installer)} --console --required --eulas-agreed "
            + " ".join(
                [
                    f'--install-component "{os.path.abspath(filename)}"'
                    for filename in extracted_components
                ]
            )
        )
        self.run_command(install_command)

        print("\nStep 7: Compiling kernel modules...")
        self.install_vmware_modules()

        print("\nStep 8: Creating systemd service files...")
        self.copy_service_files()

        print(f"VMware installation and setup on {self.linux_distro} is complete.")

    def uninstall_vmware(self):
        """Uninstall VMware Workstation."""
        print("Uninstalling VMware Workstation...")

        print("\nStep 1: Stopping and disabling VMware services...")
        vmware_service = ["vmware.service"]
        for service in vmware_service:
            self.run_command(f"sudo systemctl stop {service}")
            self.run_command(f"sudo systemctl disable {service}")

        print("\nStep 2: Removing systemd service files...")
        services = [
            "vmware-networks-configuration.service",
            "vmware-usbarbitrator.path",
            "vmware-usbarbitrator.service",
        ]
        for service in services:
            service_file = f"/etc/systemd/system/{service}"
            if os.path.exists(service_file):
                self.run_command(f"sudo rm {service_file}")

        print("\nStep 3: Removing VMware modules from DKMS...")
        self.run_command(
            f"sudo dkms remove -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION} --all"
        )

        print("\nStep 4: Running the uninstallation script...")
        uninstall_script = "/usr/bin/vmware-installer"
        if os.path.exists(uninstall_script):
            self.run_command(
                f'echo "yes" | sudo {uninstall_script} --uninstall-product vmware-workstation'
            )

        print("\nStep 5: Removing extracted components directory...")
        if os.path.exists(self.EXTRACTED_DIR):
            shutil.rmtree(self.EXTRACTED_DIR)
