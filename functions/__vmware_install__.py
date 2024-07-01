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
    bundle_filename = f"VMware-Workstation-{pkgver}.{CARCH}.bundle.tar"
    download_file(bundle_url, bundle_filename)
    for url, filename in zip(component_urls, component_filenames):
        download_file(url, filename)
    
    # Step 2: Extract the bundle file
    print("Extracting the bundle file...")
    run_command(f"tar -xf {bundle_filename}")

    # Step 3: Make the installer executable
    print("Making the installer executable...")
    bundle_installer = f"VMware-Workstation-{pkgver}.{CARCH}.bundle"
    run_command(f"chmod +x {bundle_installer}")
    
    # Step 4: Run the installer with component installation
    print("Running the VMware Workstation installer with components...")
    install_command = f"sudo ./{bundle_installer} --console --required --eulas-agreed " + " ".join(
        [f'--install-component "{os.path.abspath(filename)}"' for filename in component_filenames]
    )
    run_command(install_command)

    # Step 5: Install necessary dependencies
    print("Installing dependencies...")
    dependencies = [
        "kernel-devel",
        "kernel-headers",
        "gcc",
        "make",
        "perl",
        "patch",
        "net-tools",
        "libx11",
        "libXtst",
        "libXinerama",
        "libXrandr",
        "libXrender",
        "libXext",
        "libXi",
        "libXt",
        "libcanberra-gtk2",
        "libcanberra-gtk3"
    ]
    run_command(f"sudo dnf install -y {' '.join(dependencies)}")
    
    # Step 6: Compile kernel modules
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
