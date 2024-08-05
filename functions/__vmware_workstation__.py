from io import BytesIO
from os import makedirs, path, chdir, listdir
from pathlib import Path
from subprocess import run
import logging
from zipfile import ZipFile
import requests

class VMwareInstaller:
    PKGVER = "17.5.2"
    BUILDVER = "23775571"
    TOOLS_VERSION = "12.4.0-23259341"
    CARCH = "x86_64"
    BASE_URL = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{PKGVER}/{BUILDVER}/linux/packages"
    BUNDLE_URL = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{PKGVER}/{BUILDVER}/linux/core/VMware-Workstation-{PKGVER}-{BUILDVER}.{CARCH}.bundle.tar"
    BUNDLE_FILENAME = f"VMware-Workstation-{PKGVER}-{BUILDVER}.{CARCH}.bundle.tar"
    CACHE_DIR = Path(path.expanduser("~")) / ".cache" / "vcandy" / "VMware"
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
    EXTRACTED_DIR = path.join(CACHE_DIR, "extracted_components")
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
    GITHUB_HOST_MODULES_REPO_URL = "https://github.com/nan0desu/vmware-host-modules"
    GITHUB_HOST_MODULES_BRANCH = "workstation-17.5.2-k6.9%2B"
    GITHUB_REPO_URL = "https://github.com/Hakanbaban53/Virtual-CANDY"
    GITHUB_BRANCH = "main"

    def __init__(self, hide, action, linux_distro):
        self.COMPONENT_URLS = [
            f"{self.BASE_URL}/{filename}" for filename in self.COMPONENT_FILENAMES
        ]
        self.setup_logging()
        self.hide = hide
        self.action = action
        self.linux_distro = linux_distro
        self.PACKAGE_MANAGER, self.DEPENDENCIES = self._configure_distro()

        if self.action == "install":
            self.install_vmware()
        elif self.action == "remove":
            self.uninstall_vmware()
        else:
            logging.error("Invalid action specified. Use 'install' or 'remove'.")

    def _configure_distro(self):
        """Configure package manager and dependencies based on the Linux distribution."""
        if self.linux_distro == "fedora":
            return "dnf", [
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
            dependencies = [
                "build-essential",
                "git",
                "wget",
                "gcc",
                "dkms",
                "make",
                "patch",
                "net-tools",
            ]
            kernel_version = self._get_kernel_version()
            if kernel_version:
                dependencies.append(f"linux-headers-{kernel_version}")
            return "apt", dependencies
        else:
            logging.error(f"Unsupported Linux distribution: {self.linux_distro}")
            raise ValueError(f"Unsupported Linux distribution: {self.linux_distro}")

    def _get_kernel_version(self):
        """Retrieve the current kernel version."""
        try:
            result = run("uname -r", shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logging.error(f"Error retrieving kernel version: {result.stderr}")
                return None
        except Exception as e:
            logging.exception("Exception occurred while retrieving kernel version.")
            return None

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
            handlers=[
                logging.FileHandler(f"{self.CACHE_DIR}/vmware_installer.log"),
                logging.StreamHandler(),
            ],
        )

    def run_command(self, command):
        """Run a shell command and logging. Error its output."""
        result = run(
            command, shell=True, text=True, stderr=self.hide,
            stdout=self.hide
        )
        if result.returncode != 0:
            logging.error(f"Command failed: {command}")
            logging.error(f"Error output: {result.stderr}")
            return False, result.stderr
        return True, ""

    def download_file(self, url, filename):
        """Download a file from a URL using wget."""
        logging.info(f"Downloading {filename} from {url}...")
        self.run_command(f"wget -O {path.join(self.CACHE_DIR, filename)} {url}")
        logging.info(f"Downloaded {filename}.\n")

    def extract_tar(self, filename):
        """Extract a tar file."""
        logging.info(f"Extracting {filename} to {self.EXTRACTED_DIR}...")
        self.run_command(
            f"tar -xf {path.join(self.CACHE_DIR, filename)} -C {self.EXTRACTED_DIR}"
        )
        self.run_command(f"find {self.EXTRACTED_DIR} -name '*.xml' -type f -delete")

    def download_and_extract_zip(
        self, repo_url, branch, folder_path=None, extract_to=None
    ):
        """Download and extract a GitHub repository or a specific folder."""
        logging.info(f"Downloading repository from {repo_url}...")
        zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
        response = requests.get(zip_url)
        if response.status_code != 200:
            logging.error(
                f"Failed to download the repository. Status code: {response.status_code}"
            )
            return

        with ZipFile(BytesIO(response.content)) as zip_file:
            if folder_path:
                logging.info(f"Extracting the folder '{folder_path}'...")
                for member in zip_file.namelist():
                    if member.startswith(
                        f"{repo_url.split('/')[-1]}-{branch}/{folder_path}"
                    ):
                        relative_path = path.relpath(
                            member, f"{repo_url.split('/')[-1]}-{branch}"
                        )
                        target_path = path.join(extract_to, relative_path)
                        if not member.endswith("/"):
                            makedirs(path.dirname(target_path), exist_ok=True)
                            with open(target_path, "wb") as f:
                                f.write(zip_file.read(member))
                        else:
                            makedirs(target_path, exist_ok=True)
                logging.info(f"Extracted folder '{folder_path}' to {extract_to}.")
            else:
                logging.info(f"Extracting the entire repository to {extract_to}...")
                zip_file.extractall(extract_to)
                logging.info(f"Extracted repository to {extract_to}.")

    def install_vmware_modules(self):
        """Install VMware modules."""

        source_dir = f"{self.CACHE_DIR}/vmware-host-modules-workstation-17.5.2-k6.9-"
        dest_dir = "/usr/lib/vmware/modules/source/"
        folders_to_copy = ["vmmon-only", "vmnet-only"]

        chdir(source_dir)
        logging.info("Copying vmmon and vmnet folders...")

        for folder in folders_to_copy:
            src_folder = path.join(source_dir, folder)
            dest_folder = path.join(dest_dir, folder)

            if not path.exists(dest_folder):
                self.run_command(f"sudo mkdir -p {dest_folder}")

            logging.info(f"Copying {src_folder} to {dest_folder}...")
            self.run_command(f"sudo cp -r {src_folder} {dest_folder}")

        logging.info("Folders copied successfully.")

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
            f"sudo cp -r {self.CACHE_DIR}/vmware_files/DKMS_files/Makefile /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/"
        )

        logging.info("Creating DKMS configuration for vmware-host-modules...")
        with open(
            f"{self.CACHE_DIR}/vmware_files/DKMS_files/dkms.conf", "r"
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
            f"sudo patch -N -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmmon-only < {self.CACHE_DIR}/vmware_files/DKMS_files/vmmon.patch"
        )
        self.run_command(
            f"sudo patch -N -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmnet-only < {self.CACHE_DIR}/vmware_files/DKMS_files/vmnet.patch"
        )

        logging.info("Adding and building vmware-host-modules module with DKMS...")
        self.run_command(
            f"sudo dkms add --force -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms build --force -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )
        self.run_command(
            f"sudo dkms install --force -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}"
        )

        logging.info("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")

        chdir("..")  # Return to previous directory

    def copy_service_files(self):
        """Copy systemd service files for VMware."""
        for filename in self.SERVICES:
            self.run_command(
                f"sudo cp {self.CACHE_DIR}/vmware_files/services/{filename} /etc/systemd/system/{filename}"
            )
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
        self.download_and_extract_zip(
            repo_url=self.GITHUB_HOST_MODULES_REPO_URL,
            branch=self.GITHUB_HOST_MODULES_BRANCH,
            extract_to=self.CACHE_DIR,
        )

        logging.info("Getting the DKMS modules")
        self.download_and_extract_zip(
            repo_url=self.GITHUB_REPO_URL,
            branch=self.GITHUB_BRANCH,
            folder_path="vmware_files",
            extract_to=self.CACHE_DIR,
        )

        logging.info(
            "\nStep 3: Downloading the VMware Workstation installer and components..."
        )
        makedirs(self.CACHE_DIR, exist_ok=True)
        self.download_file(self.BUNDLE_URL, self.BUNDLE_FILENAME)
        for url, filename in zip(self.COMPONENT_URLS, self.COMPONENT_FILENAMES):
            self.download_file(url, filename)

        logging.info("\nStep 4: Extracting the bundle file...")
        self.run_command(
            f"tar -xf {path.join(self.CACHE_DIR, self.BUNDLE_FILENAME)} -C {self.CACHE_DIR}"
        )

        makedirs(self.EXTRACTED_DIR, exist_ok=True)
        for filename in self.COMPONENT_FILENAMES:
            self.extract_tar(filename)

        logging.info("\nStep 5: Making the installer executable...")
        bundle_installer = (
            f"VMware-Workstation-{self.PKGVER}-{self.BUILDVER}.{self.CARCH}.bundle"
        )
        self.run_command(f"chmod +x {path.join(self.CACHE_DIR, bundle_installer)}")

        logging.info(
            "\nStep 6: Running the VMware Workstation installer with extracted components..."
        )
        extracted_components = [
            path.join(self.EXTRACTED_DIR, filename)
            for filename in listdir(self.EXTRACTED_DIR)
        ]
        install_command = (
            f"sudo {path.join(self.CACHE_DIR, bundle_installer)} --console --required --eulas-agreed "
            + " ".join(
                [
                    f'--install-component "{path.abspath(filename)}"'
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

        logging.info(
            f"VMware installation and setup on {self.linux_distro} is complete."
        )

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
            if path.exists(service_file):
                self.run_command(f"sudo rm {service_file}")

        logging.info("\nStep 3: Removing VMware modules from DKMS...")
        self.run_command(
            f"sudo dkms remove -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION} --all"
        )

        logging.info("\nStep 4: Running the uninstallation script...")
        uninstall_script = "/usr/bin/vmware-installer"
        if path.exists(uninstall_script):
            self.run_command(
                f'echo "yes" | sudo {uninstall_script} --uninstall-product vmware-workstation'
            )

        logging.info("\nStep 5: Removing extracted components directory...")
        if path.exists(self.EXTRACTED_DIR):
            self.run_command(f"sudo rm -rf {self.EXTRACTED_DIR}")


if __name__ == "__main__":
    VMwareInstaller(hide=None, action="install", linux_distro="fedora")