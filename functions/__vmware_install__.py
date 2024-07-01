import os
import subprocess

def run_command(command):
    """Run a shell command and print its output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Command failed: {command}")
        print(result.stderr)
    else:
        print(result.stdout)

def download_file(url, filename):
    """Download a file from a URL using wget."""
    print(f"Downloading {filename} from {url}...")
    run_command(f"wget -O {filename} {url}")
    print(f"Downloaded {filename}.")

def extract_tar(filename, exrated_dir):
    """Extract a tar file."""
    print(f"Extracting {filename} to {exrated_dir}...")
    run_command(f"tar -xf {filename} -C {exrated_dir}")

def install_vmware_fedora():
    # Set up URLs and filenames
    pkgver = "17.5.2"
    buildver = "23775571"
    tools_version = "12.4.0-23259341"
    CARCH = "x86_64"
    base_url = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{pkgver}/{buildver}/linux/packages"
    bundle_url = f"https://softwareupdate.vmware.com/cds/vmw-desktop/ws/{pkgver}/{buildver}/linux/core/VMware-Workstation-{pkgver}-{buildver}.{CARCH}.bundle.tar"

    component_filenames = [
        f"vmware-tools-linux-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-linuxPreGlibc25-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-netware-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-solaris-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-windows-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-winPre2k-{tools_version}.{CARCH}.component.tar",
        f"vmware-tools-winPreVista-{tools_version}.{CARCH}.component.tar"
    ]

    component_urls = [f"{base_url}/{filename}" for filename in component_filenames]

    # Step 1: Download the VMware Workstation installer and components
    bundle_filename = f"VMware-Workstation-{pkgver}-{buildver}.{CARCH}.bundle.tar"
    download_file(bundle_url, bundle_filename)
    for url, filename in zip(component_urls, component_filenames):
        download_file(url, filename)
    
    # # Step 2: Extract the bundle file
    print("Extracting the bundle file...")
    run_command(f"tar -xf {bundle_filename}")

    extracted_dir = os.path.join(os.getcwd(), "extracted_components")
    os.makedirs(extracted_dir, exist_ok=True)
    for filename in component_filenames:
        extract_tar(filename, extracted_dir)

    # Step 3: Make the installer executable
    print("Making the installer executable...")
    bundle_installer = f"VMware-Workstation-{pkgver}-{buildver}.{CARCH}.bundle"
    run_command(f"chmod +x {bundle_installer}")

    print("Installing dependencies...")
    dependencies = [
        "kernel-devel",
        "kernel-headers",
        "gcc",
        "make",
        "patch",
        "net-tools",
    ]
    run_command(f"sudo dnf install -y {' '.join(dependencies)}")
    
    # Step 4: Run the installer with component installation
    print("Running the VMware Workstation installer with components...")
    extracted_components = [os.path.join(extracted_dir, filename) for filename in os.listdir(extracted_dir)]
    install_command = f"sudo ./{bundle_installer} --console --required --eulas-agreed " + " ".join(
        [f'--install-component "{os.path.abspath(filename)}"' for filename in extracted_components]
    )
    run_command(install_command)


    print("Compiling kernel modules...")
    run_command("sudo vmware-modconfig --console --install-all")
    
    # Step 7: Enable and start VMware services
    print("Enabling and starting VMware services...")
    services = [
        "vmware-networks.service",
        "vmware-usbarbitrator.service",
        "vmware-hostd.service"
    ]
    for service in services:
        run_command(f"sudo systemctl enable --now {service}")
    
    # Step 8: Add the user to the vmware group
    user = os.getlogin()
    print(f"Adding {user} to the vmware group...")
    run_command(f"sudo usermod -aG vmware {user}")
    
    print("VMware installation and setup on Fedora is complete.")

if __name__ == "__main__":
    install_vmware_fedora()

#     I need the use this:
#     git clone -b tmp/workstation-17.5.2-k6.9.1 https://github.com/nan0desu/vmware-host-modules.git
# cd vmware-host-modules/
# sudo make tarballs && sudo cp -v vmmon.tar vmnet.tar /usr/lib/vmware/modules/source/
# sudo vmware-modconfig --console --install-all
