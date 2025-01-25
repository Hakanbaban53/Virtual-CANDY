### How to Add a Package Entry to `packages.json`

The `packages.json` file defines the package installation metadata for different Linux distributions. Each distribution (e.g., `arch`, `debian`, `fedora`) contains a list of packages and their installation details. This guide explains how to make a new package entry in the JSON file. After adding the package, you can test it using the VCANDY application.

---

#### 1. Understanding the File Structure

Each distribution has an array of objects. Each object represents a package group, with the following structure:

```json
{
  "name": "Package_Group_Name",
  "description": "Description of the package group",
  "values": [
    {
      "name": "Readable Package Name",
      "type": "package_type",
      "install_value": "package_name_for_package_manager",
      "check_value": "check_package_name_package_manager",
      "remove_value": "removal_name_for_package_manager",
      "install_script": ["optional_install_commands"],
      "check_script": ["optional_check_commands"],
      "remove_script": ["optional_remove_commands"]
    }
  ]
}
```

**Fields:**
- **`name`**: Display name of the package or group.
- **`description`**: Description of the package or group.
- **`type`**: Type of the package (`package`, `AUR-package`, `get-keys`, `service`, `group`, etc.).
- **`install_value`**: Command or identifier for installing the package.
- **`check_value`**: Command or identifier to check if the package is installed.
- **`remove_value`**: Command or identifier to remove the package.
- **`install_script`, `check_script`, `remove_script`** (Optional): Shell commands for special cases.

---

#### 2. Adding a New Package

**Steps:**

1. **Choose a Distribution**:
   Decide which distribution (`arch`, `debian`, `fedora`, `ubuntu`, etc.) the package applies to.

2. **Create a Package Entry**:
   Add a new package entry inside the relevant distribution's array.

3. **Fill Required Fields**:
   Include at least the `name`, `type`, `install_value`, `check_value`, and `remove_value`.

**Example:**

Here’s how to add a new package called `MyApp` for the `arch` distribution:

```json
{
  "name": "MyApp",
  "description": "MyApp is a CLI and GUI application.",
  "values": [
    {
      "name": "My App CLI",
      "type": "package",
      "install_value": "myapp",
      "check_value": "myapp",
      "remove_value": "myapp"
    },
    {
      "name": "My App GUI",
      "type": "AUR-package",
      "install_value": "myapp-gui",
      "check_value": "myapp-gui",
      "remove_value": "myapp-gui"
    },
  ]
}
```

**Command Run Example:**

Here’s how to add a **command-run** entry in the `packages.json`. Below is an example:

```json
{
  "name": "Command Run",
  "description": "Command Run is a special application.",
  "values": [
    {
      "name": "Special App",
      "type": "run_command",
      "install_script": [
        "wget -O- https://example.com/key.asc | sudo apt-key add -",
        "sudo add-apt-repository 'deb https://example.com/repo stable main'"
      ],
      "check_script": ["/etc/apt/sources.list.d/example.list"],
      "remove_script": [
        "sudo rm -rf /etc/apt/sources.list.d/example.list",
        "sudo apt-key del example_key_id"
      ]
    }
  ]
}
```

### Example: Adding a Special Package with `special_values`

Here’s how to add a **special-package** entry with a `special_values` field in the `packages.json`. Below is an example:

```json
{
  "name": "Special_Package_Example",
  "description": "Special Package Example",
  "values": [
    {
      "name": "Special App",
      "type": "special-package",
      "special_values": [
        {
          "app_name": "SpecialApp",
          "version": "1.2.3"
        }
      ],
      "install_script": [
        "wget https://example.com/specialapp-${version}.tar.gz -O $CACHE_PATH/${app_name}.tar.gz",
        "tar -xzf $CACHE_PATH/${app_name}.tar.gz -C $CACHE_PATH/${app_name}",
        "sudo $CACHE_PATH/${app_name}/install.sh"
      ],
      "check_script": [
        "/usr/local/bin/${app_name} --version"
      ],
      "remove_script": [
        "sudo rm -rf /usr/local/${app_name}",
        "sudo rm -rf $CACHE_PATH/${app_name}"
      ]
    }
  ]
}
```

---

### Explanation of the Fields:

1. **`special_values`**:
   - Used to define dynamic values such as the `app_name` and `version`.
   - These values are substituted in the `install_script`, `check_script`, and `remove_script`.
   - `CACHE_PATH` is default app variable. If you want to change it you can add a new value under this field (example `"CACHE_PATH": "~/user/some_path"`)
   - Default App Variables: `CACHE_PATH`

2. **`install_script`**:
   - Uses placeholders like `${version}` and `${app_name}` that will be replaced at runtime.
   - The script downloads the application, extracts it, and installs it.

3. **`check_script`**:
   - Checks whether the application is installed by verifying its binary or version.

4. **`remove_script`**:
   - Removes all installed files and directories associated with the application.


---

#### 3. Testing the Configuration

After adding the package entry:
1. **Validate JSON**:
   Use a JSON linter to ensure the syntax is correct.

2. **Run the Application**:
   Test the entry by running the application with the new package.

3. **Check Logging**:
   Enable verbose mode to confirm the package is detected and the commands execute correctly:
   ```bash
   python app.py --verbose --dry-run --json /your/json/file --all
   #Or
   vcandy --verbose --dry-run --json /your/json/file --all
   ```