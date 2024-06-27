import subprocess
import logging
import time
import sys
from functions._get_packages_data_ import PackagesJSONHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define dependencies
DEPENDENCIES = ['requests']

class DependencyManager:
    def __init__(self):
        self.packages_handler = PackagesJSONHandler()

    def check_dependencies(self, dependencies):

        """Check if required Python packages are installed."""

        missing_packages = []

        logger.info("Checking dependencies...")
        for package in dependencies:
            try:
                result = subprocess.run(["pip", "show", package], stdout=subprocess.PIPE, check=True, text=True)
                if "Version" not in result.stdout:
                    missing_packages.append(package)
                else:
                    logger.info(f"{package} is already installed (version {result.stdout.splitlines()[1].split(': ')[1]}).")
            except subprocess.CalledProcessError:
                missing_packages.append(package)

        return missing_packages

    def install_dependencies(self, dependencies):

        """Install missing Python packages using pip."""

        if dependencies:
            logger.info("Installing missing dependencies...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", *dependencies], check=True)
                logger.info("Dependencies installed successfully.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error occurred while installing dependencies: {e}")
                sys.exit(1)
        else:
            logger.info("No missing dependencies.")

    def get_packages_data(self):

        """Download and return the packages data."""

        try:
            return self.packages_handler.load_json_data()
        except Exception as e:
            logger.error(f"Failed to retrieve packages data: {e}")
            sys.exit(1)

    def handle_dependencies(self):
        logger.info("Starting dependency check and installation...\n")
        missing_packages = self.check_dependencies(DEPENDENCIES)

        if missing_packages:
            confirmation_key = input(f"{missing_packages} package(s) are missing. Do you want to install them? (Y/n): ")
            if confirmation_key.lower() in ['y', 'yes', '']:
                self.install_dependencies(missing_packages)
                print("\n" + "=" * 40)
                print("All dependencies installed successfully!")
                print("Please relaunch the application to continue.")
                print("=" * 40 + "\n")
                time.sleep(2)
                sys.exit(1)
            else:
                print("Operation aborted. Exiting...")
                time.sleep(3)
                sys.exit(1)
        else:
            logger.info("All dependencies are already installed.")
            time.sleep(1)

        try:
            self.get_packages_data()
            logger.info("Packages data successfully retrieved.")

        except Exception as e:
            logger.error(f"Failed to retrieve packages data: {e}")
            sys.exit(1)
