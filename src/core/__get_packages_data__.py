import datetime
import json
import logging
from pathlib import Path
import requests
import time

from core.__constants__ import CACHE_PATH, PACKAGES_JSON_URL

class PackagesJSONHandler:
    def __init__(self, json_file_url=None, json_file_name="packages.json", json_file_path=None):
        self.json_file_url = json_file_url or PACKAGES_JSON_URL
        
        if json_file_path is not None:
            # Use the custom path without downloading JSON
            self.json_file_path = Path(json_file_path)
            if not self.json_file_path.exists():
                raise FileNotFoundError(f"Custom JSON path provided but file does not exist: {self.json_file_path}")
        else:
            # Use cache directory for storing the JSON file
            self.json_file_path = self.get_cache_file_path(json_file_name)

    def get_cache_file_path(self, json_file_name):
        """Get the path to the cache directory for the JSON file."""
        CACHE_PATH.mkdir(parents=True, exist_ok=True)
        return CACHE_PATH / json_file_name

    def download_json_file(self, url, file_path, max_retries=3, retry_delay=1):
        """Download the JSON file from the specified URL."""
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(file_path, "w") as file:
                    json.dump(response.json(), file)
                logging.debug(f"JSON file downloaded successfully: {file_path}")
                return True
            except requests.exceptions.RequestException as e:
                retries += 1
                logging.debug(f"Failed to download JSON file from {url} (Attempt {retries}/{max_retries}): {e}")
                if retries < max_retries:
                    logging.debug(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        return False

    def load_json_data(self, refresh=False):
        """Load the JSON data, refreshing it if necessary."""
        try:
            if not self.json_file_path.exists():
                if self.json_file_url:
                    logging.debug(f"JSON file not found. Downloading from {self.json_file_url}...")
                    if not self.download_json_file(self.json_file_url, self.json_file_path):
                        raise RuntimeError(f"Failed to download JSON file from {self.json_file_url}.")
                else:
                    raise FileNotFoundError(f"JSON file path does not exist: {self.json_file_path}")

            # Check file age if refresh is needed
            file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(self.json_file_path.stat().st_mtime)
            if file_age > datetime.timedelta(days=1) or refresh:
                logging.debug(f"Refreshing JSON file from {self.json_file_url}...")
                if not self.download_json_file(self.json_file_url, self.json_file_path):
                    raise RuntimeError(f"Failed to refresh JSON file from {self.json_file_url}.")

            # Load and return JSON data
            with open(self.json_file_path, "r") as file:
                logging.debug(f"Loading JSON data from {self.json_file_path}...")
                return json.load(file)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON file: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")
