from io import BytesIO
from os import makedirs, path, chdir, listdir
from pathlib import Path
from subprocess import run
import logging
from zipfile import ZipFile
import requests

from functions.__get_packages_data__ import PackagesJSONHandler

class VMwareInstaller:
    DATA_URL = "https://raw.githubusercontent.com/Hakanbaban53/Virtual-CANDY/refs/heads/main/packages/vmware_data.json"
    def __init__(self, hide, action, linux_distro):
        self.load_config()

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

    def load_config(self):
        """Load configuration data from config.json."""
        packages_data = PackagesJSONHandler(self.DATA_URL, json_file_name="vmware_config.json").load_json_data(refresh=True)

        self.VERSION = packages_data['VERSION']
        self.PACKAGE_NAME = packages_data['PACKAGE_NAME']
        self.BUNDLE_URL = packages_data['BUNDLE_URL']
        self.BUNDLE_FILENAME = path.basename(self.BUNDLE_URL)
        self.BUNDLE_INSTALLER = packages_data['BUNDLE_INSTALLER']
        
        self.CACHE_DIR = Path(path.expanduser(packages_data['CACHE_DIR']))
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.MODULES_DIR = path.abspath(packages_data['MODULES_DIR'])
        self.DKMS_DIR = path.abspath(f"/usr/src/{self.PACKAGE_NAME}-{self.VERSION}")

        self.COMPONENT_URLS = packages_data['COMPONENT_URLS']
        self.EXTRACTED_DIR = path.join(self.CACHE_DIR, "extracted_components")
        self.SERVICES = set(packages_data['SERVICES'])
        self.GITHUB_REPO_URL = packages_data['GITHUB_REPO_URL']
        self.GITHUB_BRANCH = packages_data['GITHUB_BRANCH']


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
        folders = ["vmmon", "vmnet"]

        logging.info("Creating directories for DKMS...")
        self.run_command(
            f"sudo mkdir -p {self.DKMS_DIR}"
        )

        logging.INFO(f"Exract the modules files to dkms directories")
        for folder in folders:
            self.run_command(
                f"tar -xf {self.MODULES_DIR}/{folder}.tar -C {self.DKMS_DIR}"
            )

        logging.info("Copying Makefile and dkms.conf to DKMS directory...")
        self.run_command(
            f"sudo cp -r {self.CACHE_DIR}/vmware_files/DKMS_files/Makefile {self.DKMS_DIR}/"
        )

        logging.info("Creating DKMS configuration for vmware-host-modules...")
        with open(
            f"{self.CACHE_DIR}/vmware_files/DKMS_files/dkms.conf", "r"
        ) as template_file:
            dkms_conf_template = template_file.read()

        dkms_conf_vmware_host_modules = dkms_conf_template.format(
            PACKAGE_NAME=self.PACKAGE_NAME, PACKAGE_VERSION=self.VERSION
        )

        temp_conf_path = f"/tmp/{self.PACKAGE_NAME}-{self.VERSION}-dkms.conf"
        with open(temp_conf_path, "w") as conf_file:
            conf_file.write(dkms_conf_vmware_host_modules)

        self.run_command(
            f"sudo mv {temp_conf_path} {self.DKMS_DIR}/dkms.conf"
        )
        logging.info(
            f"DKMS configuration file created at {self.DKMS_DIR}/dkms.conf"
        )

        logging.info("Applying patches...")
        for folder in folders:
            self.run_command(
                f"sudo patch -N -p2 -d {self.DKMS_DIR}/{folder}-only < {self.CACHE_DIR}/vmware_files/DKMS_files/{folder}.patch"
            )

        logging.info("Adding and building vmware-host-modules module with DKMS...")
        self.run_command(
            f"sudo dkms add --force -m {self.PACKAGE_NAME} -v {self.VERSION}"
        )
        self.run_command(
            f"sudo dkms build --force -m {self.PACKAGE_NAME} -v {self.VERSION}"
        )
        self.run_command(
            f"sudo dkms install --force -m {self.PACKAGE_NAME} -v {self.VERSION}"
        )

        logging.info("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")

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

        logging.info("Step 2:Getting the DKMS build files")
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
        for url in self.COMPONENT_URLS:
            filename = path.basename(url)
            self.download_file(url, filename)

        logging.info("\nStep 4: Extracting the bundle file...")
        self.run_command(
            f"tar -xf {path.join(self.CACHE_DIR, self.BUNDLE_FILENAME)} -C {self.CACHE_DIR}"
        )

        makedirs(self.EXTRACTED_DIR, exist_ok=True)
        for url in self.COMPONENT_URLS:
            filename = path.basename(url)
            self.extract_tar(filename)

        logging.info("\nStep 5: Making the installer executable...")
        self.run_command(f"chmod +x {path.join(self.CACHE_DIR, self.BUNDLE_INSTALLER)}")

        logging.info(
            "\nStep 6: Running the VMware Workstation installer with extracted components..."
        )
        extracted_components = [
            path.join(self.EXTRACTED_DIR, filename)
            for filename in listdir(self.EXTRACTED_DIR)
        ]
        install_command = (
            f"sudo {path.join(self.CACHE_DIR, self.BUNDLE_INSTALLER)} --console --required --eulas-agreed "
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
            f"sudo dkms remove -m {self.PACKAGE_NAME} -v {self.VERSION} --all"
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
