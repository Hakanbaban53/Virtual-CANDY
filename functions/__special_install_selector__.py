from functions.__vmware_workstation__ import VMwareInstaller

class SelectSpecialInstaller():
    def __init__(self, hide, action, installer, linux_distro, dry_run):
        self.hide = hide
        self.action = action
        self.installer = installer
        self.linux_distro = linux_distro
        self.dry_run = dry_run

        self.special_installers = [
            ("vmware-workstation", self.vmware_workstation()),
        ]

        self.run_installer()

    def run_installer(self):
        for name, method in self.special_installers:
            if name == self.installer:
                method


    def vmware_workstation(self):
        VMwareInstaller(self.hide, self.action, self.linux_distro, self.dry_run)