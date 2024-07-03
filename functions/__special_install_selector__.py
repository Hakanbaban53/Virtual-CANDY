from functions.__vmware_workstation__ import VMwareInstaller

class SelectSpecialInstaller():
    def __init__(self, hide, action, installer, linux_distro):
        self.hide = hide
        self.action = action
        self.installer = installer
        self.linux_distro = linux_distro

        self.special_installers = {
            "vmware-workstation": self.vmware_workstation()
        }

        if self.installer in self.special_installers:
            self.special_installers[self.installer]()
        else:
            print("Installer not found!")

    def vmware_workstation(self):
        VMwareInstaller(self.hide, self.action, self.linux_distro)