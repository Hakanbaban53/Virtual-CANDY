import os
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
    COMPONENT_FILENAMES = [
        f"vmware-tools-linux-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-linuxPreGlibc25-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-netware-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-solaris-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-windows-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-winPre2k-{TOOLS_VERSION}.{CARCH}.component.tar",
        f"vmware-tools-winPreVista-{TOOLS_VERSION}.{CARCH}.component.tar"
    ]
    EXTRACTED_DIR = os.path.join(os.getcwd(), "extracted_components")
    DEPENDENCIES = [
        "kernel-devel",
        "kernel-headers",
        "gcc",
        "dkms",
        "make",
        "patch",
        "net-tools",
    ]
    PACKAGE_NAME = "vmware-host-modules"
    PACKAGE_VERSION = PKGVER

    def __init__(self):
        self.COMPONENT_URLS = [f"{self.BASE_URL}/{filename}" for filename in self.COMPONENT_FILENAMES]
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[logging.FileHandler("vmware_installer.log"),
                                      logging.StreamHandler()])

    def run_command(self, command):
        """Run a shell command and print its output."""
        logging.info(f"Running command: {command}")
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            logging.error(f"Command failed: {command}\n{result.stderr}")
            return False
        logging.info(result.stdout)
        return True

    def download_file(self, url, filename):
        """Download a file from a URL using wget."""
        logging.info(f"Downloading {filename} from {url}...")
        if self.run_command(f"wget -O {filename} {url}"):
            logging.info(f"Downloaded {filename}.")
        else:
            logging.error(f"Failed to download {filename}.")

    def extract_tar(self, filename):
        """Extract a tar file."""
        logging.info(f"Extracting {filename} to {self.EXTRACTED_DIR}...")
        self.run_command(f"tar -xf {filename} -C {self.EXTRACTED_DIR}")

        # Remove XML files to clean up the extracted directory
        self.run_command(f"find {self.EXTRACTED_DIR} -name '*.xml' -type f -delete")

    def install_vmware_modules(self):
        """Install VMware modules."""
        logging.info(f"Cloning {self.PACKAGE_NAME} repository...")
        self.run_command(f"git clone -b tmp/workstation-{self.PACKAGE_VERSION}-k6.9.1 https://github.com/nan0desu/{self.PACKAGE_NAME}.git")

        os.chdir(self.PACKAGE_NAME)
        logging.info("Making and copying vmmon.tar and vmnet.tar...")
        self.run_command("make tarballs")
        self.run_command(f"sudo cp -v vmmon.tar vmnet.tar /usr/lib/vmware/modules/source/")

        logging.info("Extracting vmmon.tar and vmnet.tar...")
        os.chdir("/usr/lib/vmware/modules/source/")
        self.run_command("sudo tar -xvf vmmon.tar")
        self.run_command("sudo tar -xvf vmnet.tar")

        logging.info("Creating directories for DKMS...")
        self.run_command(f"sudo mkdir -p /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}")

        logging.info("Moving source files to DKMS directory...")
        self.run_command(f"sudo cp -r vmmon-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/")
        self.run_command(f"sudo cp -r vmnet-only /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/")
        self.run_command(f"sudo cp -r /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/Makefile /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/")

        logging.info("Creating DKMS configuration for vmware-host-modules...")
        dkms_conf = f"""
PACKAGE_NAME="{self.PACKAGE_NAME}"
PACKAGE_VERSION="{self.PACKAGE_VERSION}"
MAKE="make KVERSION=$kernelver SRCDIR=/usr/src/$PACKAGE_NAME-$PACKAGE_VERSION"
CLEAN="make clean"
AUTOINSTALL="YES"

BUILT_MODULE_NAME[0]="vmmon"
BUILT_MODULE_LOCATION[0]='vmmon-only'
DEST_MODULE_LOCATION[0]="/kernel/drivers/misc"

BUILT_MODULE_NAME[1]="vmnet"
BUILT_MODULE_LOCATION[1]='vmnet-only'
DEST_MODULE_LOCATION[1]="/kernel/drivers/net"
        """
        with open(f"/tmp/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}-dkms.conf", "w") as f:
            f.write(dkms_conf)
        self.run_command(f"sudo mv /tmp/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}-dkms.conf /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/dkms.conf")

        logging.info("Applying patches...")
        self.run_command(f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmmon-only < /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/vmmon.patch")
        self.run_command(f"sudo patch -p2 -d /usr/src/{self.PACKAGE_NAME}-{self.PACKAGE_VERSION}/vmnet-only < /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/vmnet.patch")

        logging.info("Adding and building vmware-host-modules module with DKMS...")
        self.run_command(f"sudo dkms add -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}")
        self.run_command(f"sudo dkms build -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}")
        self.run_command(f"sudo dkms install -m {self.PACKAGE_NAME} -v {self.PACKAGE_VERSION}")

        logging.info("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")

        os.chdir("..")  # Return to previous directory

    def create_service_files(self):
        """Create systemd service files for VMware."""
        services = {
            'vmware-networks-configuration.service': """
[Unit]
Description=VMware Networks Configuration Generation
ConditionPathExists=!/etc/vmware/networking

[Service]
UMask=0077
ExecStart=/usr/bin/vmware-networks --postinstall vmware-player,0,1
Type=oneshot
RemainAfterExit=yes
""",
            'vmware-usbarbitrator.path': """
[Unit]
Description=Monitor to Load-On-Demand the VMware USB Arbitrator

[Path]
PathExistsGlob=/var/run/vmware/*/*

[Install]
WantedBy=paths.target
""",
            'vmware-usbarbitrator.service': """
[Unit]
Description=VMware USB Arbitrator

[Service]
ExecStart=/usr/lib/vmware/bin/vmware-usbarbitrator -f

[Install]
WantedBy=multi-user.target
"""
        }

        for filename, content in services.items():
            with open(f"/tmp/{filename}", 'w') as file:
                file.write(content)
            logging.info(f"Created {filename}.")
            self.run_command(f"sudo mv /tmp/{filename} /etc/systemd/system/{filename}")

    def install_dependencies(self):
        """Install necessary dependencies for VMware."""
        logging.info("Installing dependencies...")
        self.run_command(f"sudo dnf install -y {' '.join(self.DEPENDENCIES)}")

    def enable_services(self):
        """Enable and start VMware services."""
        logging.info("Enabling and starting VMware services...")
        services = [
            "vmware-networks-configuration.service",
            "vmware-usbarbitrator.path",
            "vmware-usbarbitrator.service"
        ]
        for service in services:
            self.run_command(f"sudo systemctl enable --now {service}")

    def add_user_to_vmware_group(self):
        """Add the current user to the vmware group."""
        user = os.getlogin()
        logging.info(f"Adding {user} to the vmware group...")
        self.run_command(f"sudo usermod -aG vmware {user}")

    def install_vmware_fedora(self):
        """Perform the full VMware installation on Fedora."""
        # logging.info("Step 1: Downloading the VMware Workstation installer and components...")
        # self.download_file(self.BUNDLE_URL, self.BUNDLE_FILENAME)
        # for url, filename in zip(self.COMPONENT_URLS, self.COMPONENT_FILENAMES):
        #     self.download_file(url, filename)

        logging.info("Step 2: Extracting the bundle file...")
        self.run_command(f"tar -xf {self.BUNDLE_FILENAME}")

        os.makedirs(self.EXTRACTED_DIR, exist_ok=True)
        for filename in self.COMPONENT_FILENAMES:
            self.extract_tar(filename)

        logging.info("Step 3: Making the installer executable...")
        bundle_installer = f"VMware-Workstation-{self.PKGVER}-{self.BUILDVER}.{self.CARCH}.bundle"
        self.run_command(f"chmod +x {bundle_installer}")

        logging.info("Step 4: Running the VMware Workstation installer with extracted components...")
        extracted_components = [os.path.join(self.EXTRACTED_DIR, filename) for filename in os.listdir(self.EXTRACTED_DIR)]
        install_command = f"sudo ./{bundle_installer} --console --required --eulas-agreed " + " ".join(
            [f'--install-component "{os.path.abspath(filename)}"' for filename in extracted_components]
        )
        self.run_command(install_command)

        logging.info("Step 5: Installing necessary dependencies...")
        self.install_dependencies()

        logging.info("Step 6: Compiling kernel modules...")
        self.install_vmware_modules()

        logging.info("Step 7: Creating systemd service files...")
        self.create_service_files()

        logging.info("Step 8: Enabling and starting VMware services...")
        self.enable_services()

        logging.info("Step 9: Adding the user to the vmware group...")
        self.add_user_to_vmware_group()

        logging.info("VMware installation and setup on Fedora is complete.")

    def uninstall_vmware_fedora(self):
        """Uninstall VMware Workstation from Fedora."""
        logging.info("Uninstalling VMware Workstation...")

        # Step 1: Stop and disable VMware services
        logging.info("Stopping and disabling VMware services...")
        services = [
            "vmware-networks-configuration.service",
            "vmware-usbarbitrator.path",
            "vmware-usbarbitrator.service"
        ]
        for service in services:
            self.run_command(f"sudo systemctl stop {service}")
            self.run_command(f"sudo systemctl disable {service}")

        # Step 2: Remove systemd service files
        logging.info("Removing systemd service files...")
        for service in services:
            service_file = f"/etc/systemd/system/{service}"
            if os.path.exists(service_file):
                self.run_command(f"sudo rm {service_file}")

        # Step 3: Remove VMware modules
        logging.info("Removing VMware modules...")
        self.run_command("sudo rm -rf /usr/lib/vmware")

        # Step 4: Uninstall VMware Workstation
        logging.info("Running the uninstallation script...")
        uninstall_script = "/usr/bin/vmware-installer"
        if os.path.exists(uninstall_script):
            self.run_command(f'echo "yes" | sudo {uninstall_script} --uninstall-product vmware-workstation')

        # Step 5: Remove extracted components directory
        logging.info("Removing extracted components directory...")
        if os.path.exists(self.EXTRACTED_DIR):
            shutil.rmtree(self.EXTRACTED_DIR)

        logging.info("VMware uninstallation on Fedora is complete.")


if __name__ == "__main__":
    VMwareInstaller().install_vmware_fedora()  # Uncomment to install
    # VMwareInstaller().uninstall_vmware_fedora()  # Uncomment to uninstall
