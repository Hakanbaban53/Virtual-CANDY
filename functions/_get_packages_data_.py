import datetime
import json
import os
import requests
from pathlib import Path

class PackagesJSONHandler:
    def __init__(self):
        self.json_file_url = "https://raw.githubusercontent.com/Hakanbaban53/Container-and-Virtualization-Installer/main/packages/packages.json"
        self.json_file_path = self.get_cache_file_path()

    def get_cache_file_path(self):
        cache_dir = Path(os.path.expanduser("~")) / ".cache" / "vcany"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir / "packages.json"

    def download_json_file(self, url, file_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "w") as file:
            json.dump(response.json(), file)
        return response.json()

    def load_json_data(self, json_file_path=None):
        if json_file_path is None:
            json_file_path = self.json_file_path

        if os.path.exists(json_file_path):
            file_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(json_file_path))
            if file_age > datetime.timedelta(days=1):
                os.remove(json_file_path)

        try:
            if os.path.exists(json_file_path):
                with open(json_file_path, "r") as file:
                    return json.load(file)
            else:
                return self.download_json_file(self.json_file_url, json_file_path)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except FileNotFoundError:
            return self.download_json_file(self.json_file_url, json_file_path)
        except Exception as e:
            print(f"An error occurred: {e}")
        return {}
