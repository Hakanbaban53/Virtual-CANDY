# Testing VCANDY

This document provides instructions on how to test the VCANDY application.

## Prerequisites

Before running the tests, ensure you have the following installed:

- Python 3.x
- `pip` (Python package installer)
- `virtualenv` (optional but recommended)
- Required dependencies listed in `requirements.txt`

## Setting Up the Environment

1. **Clone the Repository:**

    ```sh
    git clone https://github.com/Hakanbaban53/Virtual-CANDY.git
    cd Virtual-CANDY
    ```

2. **Create a Virtual Environment (Optional but Recommended):**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Dependencies:**

    ```sh
    pip install -r test/requirements.txt
    ```

## Running Tests

### Unit Tests

To run the unit tests, use the following command:

```sh
python -m unittest discover -s test
```

### Integration Tests

To run the integration tests, use the following command:

```sh
# Ensure you have the necessary permissions and dependencies
# For debian based systems
sudo ./test/script/build_deb_package.sh
# For rpm based systems
sudo ./test/script/build_rpm_package.sh
# For arch based systems
sudo ./test/script/PKGBUILD
```

### Manual Testing

You can also manually test the application by running it and verifying its functionality:

1. **Run the Application:**

    ```sh
    python app.py
    # or if you have installed the package
    vcandy
    ```

2. **Use the Command-Line Interface:**

    ```sh
    python app.py -a install package1 package2
    # or if you have installed the package
    vcandy -a install package1 package2
    ```

3. **Use the Terminal UI:**

    ```sh
    python app.py
    # or if you have installed the package
    vcandy
    ```

## Cleaning Up

After testing, you can clean up the environment by deactivating the virtual environment and removing any temporary files:

```sh
deactivate
rm -rf venv
```

## Reporting Issues

If you encounter any issues during testing, please report them on the [GitHub Issues](https://github.com/Hakanbaban53/Virtual-CANDY/issues) page.

