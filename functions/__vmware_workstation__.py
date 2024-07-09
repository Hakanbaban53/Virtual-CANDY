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
    GITHUB_HOST_MODULES_REPO_URL = "https://github.com/mkubecek/vmware-host-modules.git"
    GITHUB_HOST_MODULES_BRANCH = "tmp/workstation-17.5.0-k6.8"
    GITHUB_REPO_URL = "https://github.com/Hakanbaban53/Container-and-Virtualization-Installer"
    GITHUB_BRANCH = "main"

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
        logging.basicConfig(level=logging.INFO,
                            format='%(levelname)s: %(message)s',
                            handlers=[logging.FileHandler(f"{self.CACHE_DIR}/vmware_installer.log"),
                                      logging.StreamHandler()])
        

    def run_command(self, command):
        """Run a shell command and logging. Error its output."""
        result = subprocess.run(
            command, shell=True, text=True, stderr=self.hide, stdout=self.hide
        )
        if result.returncode != 0:
            logging.error(f"Command failed: {command}")
            return False
        return True

    def download_file(self, url, filename):
        """Download a file from a URL using wget."""
        logging.info(f"Downloading {filename} from {url}...")
        self.run_command(f"wget -O {os.path.join(self.CACHE_DIR, filename)} {url}")
        logging.info(f"Downloaded {filename}.\n")

    def extract_tar(self, filename):
        """Extract a tar file."""
        logging.info(f"Extracting {filename} to {self.EXTRACTED_DIR}...")
        self.run_command(
            f"tar -xf {os.path.join(self.CACHE_DIR, filename)} -C {self.EXTRACTED_DIR}"
        )
        self.run_command(f"find {self.EXTRACTED_DIR} -name '*.xml' -type f -delete")

    def clone_repository(self, repo_url, branch, destination):
        """Clone a Git repository."""
        logging.info(f"Cloning repository from {repo_url} to {destination}...")
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

        logging.info(
            f"Folder {folder_to_clone} has been cloned to {clone_location}/{folder_to_clone}"
        )

    def install_vmware_modules(self):
        """Install VMware modules."""

        os.chdir(f"{self.CACHE_DIR}/vmware_host_modules")
        logging.info("Making and copying vmmon.tar and vmnet.tar...")
        self.run_command("make tarballs")
        self.run_command(
            f"sudo cp -v vmmon.tar vmnet.tar /usr/lib/vmware/modules/source/"
        )

        logging.info("Extracting vmmon.tar and vmnet.tar...")
        os.chdir("/usr/lib/vmware/modules/source/")
        self.run_command("sudo tar -xvf vmmon.tar")
        self.run_command("sudo tar -xvf vmnet.tar")

        logging.info("Creating directories for DKMS...")
        self.run_command(
            f"sudo mkdir -p /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}"
        )

        logging.info("Moving source files to DKMS directory...")
        self.run_command(
            f"sudo cp -r vmmon-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )
        self.run_command(
            f"sudo cp -r vmnet-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )

        logging.info("Copying Makefile and dkms.conf to DKMS directory...")
        self.run_command(
            f"sudo cp -r {self.CACHE_DIR}/vmware_files/vmware_files/DKMS_files/Makefile /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )

        logging.info("Creating DKMS configuration for vmware-host-modules...")
        with open(
            f"{self.CACHE_DIR}/vmware_files/vmware_files/DKMS_files/dkms.conf", "r"
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
        logging.info(
            f"DKMS configuration file created at /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/dkms.conf"
        )

        logging.info("Applying patches...")
        self.run_command(
            f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmmon-only < {self.CACHE_DIR}/vmware_files/vmware_files/DKMS_files/vmmon.patch"
        )
        self.run_command(
            f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmnet-only < {self.CACHE_DIR}/vmware_files/vmware_files/DKMS_files/vmnet.patch"
        )

        logging.info("Adding and building vmware-host-modules module with DKMS...")
        self.run_command(
            f"sudo dkms add -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms build -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms install -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )

        logging.info("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")

        os.chdir("..")  # Return to previous directory

    def copy_service_files(self):
        """Copy systemd service files for VMware."""
        for filename in self.SERVICES:
            self.run_command(f"sudo cp {self.CACHE_DIR}/vmware_files/vmware_files/services/{filename} /etc/systemd/system/{filename}")
            logging.info(f"Copied {filename}.")

        # Reload systemd daemon to apply changes
        self.run_command("sudo systemctl daemon-reload")
        

    def install_dependencies(self):
        """Install necessary dependencies for VMware."""
        logging.info("Installing dependencies...")
        self.run_command(
            f"sudo {self.PACKAGE_MANAGER} install -y {' '.join(self.DEPENDENCIES)}"
        )

    def install_vmware(self):
        """Perform the full VMware installation."""

        logging.info("\nStep 1: Installing necessary dependencies...")
        self.install_dependencies()

        logging.info("\nStep 2: Clone the required repositories...")
        logging.info(f"Cloning {self.PACKAGE_NAME} repository...")
        self.clone_repository(
            self.GITHUB_HOST_MODULES_REPO_URL,
            self.GITHUB_HOST_MODULES_BRANCH,
            f"{self.CACHE_DIR}/vmware_host_modules"
        )

        logging.info("Getting the DKMS modules")
        self.sparse_checkout(
            self.GITHUB_REPO_URL,
            self.GITHUB_BRANCH,
            "vmware_files",
            f"{self.CACHE_DIR}/vmware_files",
        )

        logging.info(
            "\nStep 3: Downloading the VMware Workstation installer and components..."
        )
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        self.download_file(self.BUNDLE_URL, self.BUNDLE_FILENAME)
        for url, filename in zip(self.COMPONENT_URLS, self.COMPONENT_FILENAMES):
            self.download_file(url, filename)

        logging.info("\nStep 4: Extracting the bundle file...")
        self.run_command(
            f"tar -xf {os.path.join(self.CACHE_DIR, self.BUNDLE_FILENAME)} -C {self.CACHE_DIR}"
        )

        os.makedirs(self.EXTRACTED_DIR, exist_ok=True)
        for filename in self.COMPONENT_FILENAMES:
            self.extract_tar(filename)

        logging.info("\nStep 5: Making the installer executable...")
        bundle_installer = (
            f"VMware-Workstation-{self.PKGVER}-{self.BUILDVER}.{self.CARCH}.bundle"
        )
        self.run_command(f"chmod +x {os.path.join(self.CACHE_DIR, bundle_installer)}")

        logging.info(
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

        logging.info("\nStep 7: Compiling kernel modules...")
        self.install_vmware_modules()

        logging.info("\nStep 8: Creating systemd service files...")
        self.copy_service_files()

        logging.info("\nStep 9: Set up the network adapters...")
        self.run_command("sudo chmod a+rw /dev/vmnet*")

        logging.info(f"VMware installation and setup on {self.linux_distro} is complete.")

    def uninstall_vmware(self):
        """Uninstall VMware Workstation."""
        logging.info("Uninstalling VMware Workstation...")

        logging.info("\nStep 1: Stopping and disabling VMware services...")
        vmware_service = ["vmware.service"]
        for service in vmware_service:
            self.run_command(f"sudo systemctl stop {service}")
            self.run_command(f"sudo systemctl disable {service}")

        logging.info("\nStep 2: Removing systemd service files...")

        for service in self.SERVICES:
            service_file = f"/etc/systemd/system/{service}"
            if os.path.exists(service_file):
                self.run_command(f"sudo rm {service_file}")

        logging.info("\nStep 3: Removing VMware modules from DKMS...")
        self.run_command(
            f"sudo dkms remove -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION} --all"
        )

        logging.info("\nStep 4: Running the uninstallation script...")
        uninstall_script = "/usr/bin/vmware-installer"
        if os.path.exists(uninstall_script):
            self.run_command(
                f'echo "yes" | sudo {uninstall_script} --uninstall-product vmware-workstation'
            )

        logging.info("\nStep 5: Removing extracted components directory...")
        if os.path.exists(self.EXTRACTED_DIR):
            shutil.rmtree(self.EXTRACTED_DIR)
