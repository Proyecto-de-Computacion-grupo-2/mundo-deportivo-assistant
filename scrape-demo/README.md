# UA2C Library Installation Guide

This README outlines the steps necessary to install the UA2C library, a Python package designed to streamline your coding workflow. Follow these instructions to correctly install the library and start using its features.

### How to uninstall the library to reinstall a new version: 
```
python3 -m pip uninstall ua2c
```

## How to Install the Library

### Step 1: Unzip the Downloaded File

First, you need to unzip the downloaded file containing the UA2C library. Place the extracted folder in your desired location on your system.

### Step 2: Build and Install the Library

1. **Open a Terminal or Command Prompt**: Navigate to the folder where you extracted the library files.

2. **Navigate to the Setup Level**: Make sure you are in the directory that contains the `setup.py` file. This is crucial for the installation process.

3. **Build the Distribution Wheel**:
    - Run the following command:
      ```
      python3 setup.py bdist_wheel
      ```
      Note: Depending on your system's configuration, you may need to use `python3` instead of `python`.

4. **Install the Package**:
    - Once the wheel file is created, install the UA2C library using pip with the command below:
      ```
      python3 -m pip install dist/UA2C-0.2-py3-none-any.whl
      ```
      Ensure the wheel file name (`UA2C-0.2-py3-none-any.whl` in this case) matches the one generated in your `dist` folder.

### Step 3: Importing from the Library

After installation, you can start using the library in your projects. Instead of importing `Utils`, you should now be able to use the following syntax for imports:
```python
from UA2C import helper as helper, routes as route
