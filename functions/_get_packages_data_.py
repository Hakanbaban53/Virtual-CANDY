import datetime
import json
import os
import requests
from pathlib import Path
import time

class PackagesJSONHandler:
    def __init__(self):
        self.json_file_url = "https://raw.githubusercontent.com/Hakanbaban53/Container-and-Virtualization-Installer/Fetch-From-Github-Module/packages/packeges.json"
        self.json_file_path = self.get_cache_file_path()

    def get_cache_file_path(self):
        cache_dir = Path(os.path.expanduser("~")) / ".cache" / "vcany"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "packages.json"

    def download_json_file(self, url, file_path, max_retries=3, retry_delay=1):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
                with open(file_path, "w") as file:
                    json.dump(response.json(), file)
                return True
            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Failed to download JSON file (Attempt {retries}/{max_retries}): {e}")
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        return False

    def load_json_data(self, json_file_path=None):
        if json_file_path is None:
            json_file_path = self.json_file_path

        try:
            if os.path.exists(json_file_path):
                file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(json_file_path))
                if file_age > datetime.timedelta(days=1):
                    print(f"Updating JSON file from {self.json_file_url}...")
                    os.remove(json_file_path)
                    success = self.download_json_file(self.json_file_url, json_file_path)
                    if not success:
                        raise RuntimeError(f"Failed to update JSON file from {self.json_file_url}.")
            else:
                success = self.download_json_file(self.json_file_url, json_file_path)
                if not success:
                    raise RuntimeError(f"Failed to download JSON file from {self.json_file_url}.")

            with open(json_file_path, "r") as file:
                return json.load(file)

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON: {e}")

        except FileNotFoundError:
            raise RuntimeError(f"JSON file not found at {json_file_path}. Attempting to download from {self.json_file_url}.")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to retrieve JSON file from {self.json_file_url}: {e}")

        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")

