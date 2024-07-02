import os
import subprocess
import shutil




class VMwareInstaller:
    def __init__(self):
        self.pkgver = "17.5.2"
        self.buildver = "23775571"
        self.tools_version = "12.4.0-23259341"
        self.CARCH = "x86_64"
        self.base_url = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{self.pkgver}/{self.buildver}/linux/packages"
        self.bundle_url = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{self.pkgver}/{self.buildver}/linux/core/VMware-Workstation-{self.pkgver}-{self.buildver}.{self.CARCH}.bundle.tar"
        self.bundle_filename = f"VMware-Workstation-{self.pkgver}-{self.buildver}.{self.CARCH}.bundle.tar"
        self.component_filenames = [
            f"vmware-tools-linux-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-linuxPreGlibc25-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-netware-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-solaris-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-windows-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-winPre2k-{self.tools_version}.{self.CARCH}.component.tar",
            f"vmware-tools-winPreVista-{self.tools_version}.{self.CARCH}.component.tar"
        ]
        self.component_urls = [f"{self.base_url}/{filename}" for filename in self.component_filenames]
        self.extracted_dir = os.path.join(os.getcwd(), "extracted_components")
        self.dependencies = [
            "kernel-devel",
            "kernel-headers",
            "gcc",
            "dkms",
            "make",
            "patch",
            "net-tools",
        ]

    def run_command(self, command):
        """Run a shell command and print its output."""
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            print(f"Command failed: {command}")
            print(result.stderr)
        else:
            print(result.stdout)



    def download_file(self, url, filename):
        """Download a file from a URL using wget."""
        print(f"Downloading {filename} from {url}...")
        self.run_command(f"wget -O {filename} {url}")
        print(f"Downloaded {filename}.")

    def extract_tar(self, filename):
        """Extract a tar file."""
        print(f"Extracting {filename} to {self.extracted_dir}...")
        self.run_command(f"tar -xf {filename} -C {self.extracted_dir}")
        self.run_command(f"find {self.extracted_dir} -name '*.xml' -type f -delete")

    def install_vmware_modules(self):
        print("Cloning vmware-host-modules repository...")
        self.run_command(f"git clone -b tmp/workstation-17.5.2-k6.9.1 https://github.com/nan0desu/vmware-host-modules.git ")
        
        os.chdir("vmware-host-modules")
        print("Making and copying vmmon.tar and vmnet.tar...")
        self.run_command("make tarballs")
        self.run_command("sudo cp -v vmmon.tar vmnet.tar /usr/lib/vmware/modules/source/")

        print("Extracting vmmon.tar and vmnet.tar...")
        os.chdir("/usr/lib/vmware/modules/source/")
        self.run_command("sudo tar -xvf vmmon.tar")
        self.run_command("sudo tar -xvf vmnet.tar")
        
        print("Creating directories for DKMS...")
        self.run_command("sudo mkdir -p /usr/src/vmware-host-modules-17.5.2")
        
        print("Moving source files to DKMS directory...")
        self.run_command("sudo cp -r vmmon-only /usr/src/vmware-host-modules-17.5.2/")
        self.run_command("sudo cp -r vmnet-only /usr/src/vmware-host-modules-17.5.2/")
        self.run_command("sudo cp -r /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/Makefile /usr/src/vmware-host-modules-17.5.2/")

        print("Creating DKMS configuration for vmware-host-modules...")
        dkms_conf_vmware_host_modules = """
PACKAGE_NAME="vmware-host-modules"
PACKAGE_VERSION="17.5.2"
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
        with open("/tmp/vmware-host-modules-17.5.2-dkms.conf", "w") as f:
            f.write(dkms_conf_vmware_host_modules)
        self.run_command("sudo mv /tmp/vmware-host-modules-17.5.2-dkms.conf /usr/src/vmware-host-modules-17.5.2/dkms.conf")
        
        print("Applying patches...")
        self.run_command("sudo patch -p2 -d /usr/src/vmware-host-modules-17.5.2/vmmon-only < /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/vmmon.patch")
        self.run_command("sudo patch -p2 -d /usr/src/vmware-host-modules-17.5.2/vmnet-only < /home/hakan/Belgeler/GitHub/Container-and-Virtualization-Installer/functions/vmnet.patch")

        print("Adding and building vmware-host-modules module with DKMS...")
        self.run_command("sudo dkms add -m vmware-host-modules -v 17.5.2")
        self.run_command("sudo dkms build -m vmware-host-modules -v 17.5.2")
        self.run_command("sudo dkms install -m vmware-host-modules -v 17.5.2")
        
        print("Running vmware-modconfig to install all modules...")
        self.run_command("sudo vmware-modconfig --console --install-all")
        
        os.chdir("..")  # Return to previous directory

    def create_service_files(self):
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
            print(f"Created {filename}.")
            self.run_command(f"sudo mv /tmp/{filename} /etc/systemd/system/{filename}")

    def install_dependencies(self):
        print("Installing dependencies...")
        self.run_command(f"sudo dnf install -y {' '.join(self.dependencies)}")

    def enable_services(self):
        print("Enabling and starting VMware services...")
        services = [
            "vmware-networks-configuration.service",
            "vmware-usbarbitrator.path",
            "vmware-usbarbitrator.service"
        ]
        for service in services:
            self.run_command(f"sudo systemctl enable --now {service}")

    def add_user_to_vmware_group(self):
        user = os.getlogin()
        print(f"Adding {user} to the vmware group...")
        self.run_command(f"sudo usermod -aG vmware {user}")

    def install_vmware_fedora(self):
        # print("Step 1: Downloading the VMware Workstation installer and components...")
        # self.download_file(self.bundle_url, self.bundle_filename)
        # for url, filename in zip(self.component_urls, self.component_filenames):
        #     self.download_file(url, filename)

        # print("Step 2: Extracting the bundle file...")
        # self.run_command(f"tar -xf {self.bundle_filename}")

        # os.makedirs(self.extracted_dir, exist_ok=True)
        # for filename in self.component_filenames:
        #     self.extract_tar(filename)

        # print("Step 3: Making the installer executable...")
        # bundle_installer = f"VMware-Workstation-{self.pkgver}-{self.buildver}.{self.CARCH}.bundle"
        # self.run_command(f"chmod +x {bundle_installer}")

        # print("Step 4: Running the VMware Workstation installer with extracted components...")
        # extracted_components = [os.path.join(self.extracted_dir, filename) for filename in os.listdir(self.extracted_dir)]
        # install_command = f"sudo ./{bundle_installer} --console --required --eulas-agreed " + " ".join(
        #     [f'--install-component "{os.path.abspath(filename)}"' for filename in extracted_components]
        # )
        # self.run_command(install_command)

        # print("Step 5: Installing necessary dependencies...")
        # self.install_dependencies()

        print("Step 6: Compiling kernel modules...")
        self.install_vmware_modules()

        # print("Step 7: Creating systemd service files...")
        # self.create_service_files()

        # print("Step 8: Enabling and starting VMware services...")
        # self.enable_services()

        # print("Step 9: Adding the user to the vmware group...")
        # self.add_user_to_vmware_group()

        # print("VMware installation and setup on Fedora is complete.")

    def uninstall_vmware_fedora(self):
        print("Uninstalling VMware Workstation...")
        
        # Step 1: Stop and disable VMware services
        print("Stopping and disabling VMware services...")
        services = [
            "vmware-networks-configuration.service",
            "vmware-usbarbitrator.path",
            "vmware-usbarbitrator.service"
        ]
        for service in services:
            self.run_command(f"sudo systemctl stop {service}")
            self.run_command(f"sudo systemctl disable {service}")

        # Step 2: Remove systemd service files
        print("Removing systemd service files...")
        for service in services:
            service_file = f"/etc/systemd/system/{service}"
            if os.path.exists(service_file):
                self.run_command(f"sudo rm {service_file}")

        # Step 3: Remove VMware modules
        print("Removing VMware modules...")
        self.run_command("sudo rm -rf /usr/lib/vmware")



        # Step 4: Uninstall VMware Workstation
        print("Running the uninstallation script...")
        uninstall_script = "/usr/bin/vmware-installer"
        if os.path.exists(uninstall_script):
            self.run_command(f'echo "yes" | sudo {uninstall_script} --uninstall-product vmware-workstation')

        # Step 5: Remove extracted components directory
        print("Removing extracted components directory...")
        if os.path.exists(self.extracted_dir):
            shutil.rmtree(self.extracted_dir)

        print("VMware uninstallation on Fedora is complete.")

if __name__ == "__main__":
    installer = VMwareInstaller()
    installer.install_vmware_fedora()  # Uncomment to install
    # installer.uninstall_vmware_fedora()  # Uncomment to uninstall