import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append("src")
from app import PackageManagerApp


class TestPackageManagerApp(unittest.TestCase):
    @patch("app.identify_distribution")
    @patch("app.get_linux_pretty_name")
    @patch("app.ArgumentHandler")
    @patch("app.LoggingManager")
    @patch("app.PackagesJSONHandler")
    def setUp(
        self,
        MockPackagesJSONHandler,
        MockLoggingManager,
        MockArgumentHandler,
        mock_get_linux_pretty_name,
        mock_identify_distribution,
    ):
        # Mock identify_distribution and get_linux_pretty_name
        mock_identify_distribution.return_value = "fedora"
        mock_get_linux_pretty_name.return_value = "Fedora Linux 41 (Workstation Edition)"

        # Mock ArgumentHandler
        mock_args = MagicMock()
        mock_args.verbose = False
        mock_args.dry_run = False
        mock_args.json = "packages.json"
        mock_args.url = None
        mock_args.refresh = False
        mock_args.packages = ["VMware_Workstation", "VirtualBox-7.0"]
        mock_args.list = False
        mock_args.all = False
        mock_args.distribution = "fedora"
        mock_args.action = "install"
        MockArgumentHandler.return_value.get_args.return_value = mock_args

        # Mock PackagesJSONHandler
        MockPackagesJSONHandler.return_value.load_json_data.return_value = {
            "fedora": [{"name": "VMware_Workstation"}, {"name": "VirtualBox-7.0"}]
        }

        self.mock_args = mock_args
        self.app = PackageManagerApp()

    def test_initialization(self):
        """Test if the app initializes with correct Linux distribution and pretty name."""
        self.assertEqual(self.app.linux_distro_id, "fedora")
        self.assertEqual(
            self.app.linux_pretty_name, "Fedora Linux 41 (Workstation Edition)"
        )

    def test_packages(self):
        """Test the packages method to retrieve relevant packages."""
        packages = self.app.packages("fedora")
        self.assertEqual(packages, ["VMware_Workstation", "VirtualBox-7.0"])

    @patch("app.get_linux_package_manager")
    @patch("app.check_linux_package_manager_connection")
    def test_run_with_valid_packages(
        self, mock_check_connection, mock_get_linux_package_manager
    ):
        """Test the run method with valid packages."""
        mock_check_connection.return_value = True
        self.mock_args.list = False
        self.mock_args.all = False

        # Run the app
        self.app.run()

        # Check connection was called
        mock_check_connection.assert_called_once_with("fedora")

        # Check package manager was called for each package
        mock_get_linux_package_manager.assert_any_call(
            linux_distribution="fedora",
            package_name="VMware_Workstation",
            output=False,
            action="install",
            dry_run=False,
        )
        mock_get_linux_package_manager.assert_any_call(
            linux_distribution="fedora",
            package_name="VirtualBox-7.0",
            output=False,
            action="install",
            dry_run=False,
        )
        self.assertEqual(mock_get_linux_package_manager.call_count, 2)

    @patch("app.start_terminal_ui")
    def test_run_terminal_ui(self, mock_start_terminal_ui):
        """Test the run method with no action arguments."""
        # Clear the action-related arguments
        self.mock_args.list = False
        self.mock_args.packages = None
        self.mock_args.all = False

        # Run the app
        self.app.run()

        # Ensure the terminal UI is started
        mock_start_terminal_ui.assert_called_once_with(
            "fedora",
            "Fedora Linux 41 (Workstation Edition)",
            self.app.packages_data,
            self.app.log_stream,
            False,
            False,
        )

    @patch("app.check_linux_package_manager_connection")
    def test_run_no_connection(self, mock_check_connection):
        """Test the run method when package manager connection fails."""
        mock_check_connection.return_value = False
        self.mock_args.list = False
        self.mock_args.all = False

        # Run the app
        self.app.run()

        # Ensure connection check was called and no further actions were taken
        mock_check_connection.assert_called_once_with("fedora")

    def test_packages_empty(self):
        """Test the packages method with a distribution that has no packages."""
        packages = self.app.packages("deaddistro")
        self.assertEqual(packages, [])


if __name__ == "__main__":
    unittest.main()
