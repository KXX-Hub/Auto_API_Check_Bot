"""This python will handle some extra functions."""
import datetime
import os
import re
import sys
from os.path import exists
import yaml
from yaml import SafeLoader


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as f:
        f.write("""# ++--------------------------------++
# | API Auto Check Bot               |
# | Made by KXX (MIT License)        |
# ++--------------------------------++
# input your line_notify_token
line_notify_token: 'line_notify_token'

# fill in the api_name and environment_name you want to check
# you can add more api to check
api_data:
      - api_name: 'api_name'
        environment_name: 'environment_name'
        use: "True"

      - api_name: 'api_name'
        environment_name: 'environment_name'
        use: "True"
#-------------------------------------


"""
                )
    sys.exit()


def read_config():
    """Read the config file.
    Check if the config file exists, if not, create one.
    If it exists, read the config file and return the configuration as a dictionary.
    :rtype: dict
    """
    if not exists('./config.yml'):
        print("Config file not found, creating one by default.\nPlease finish filling config.yml")
        config_file_generator()

    try:
        with open('config.yml', 'r', encoding="utf8") as f:
            data = yaml.load(f, Loader=SafeLoader)
            line_notify_token = data.get('line_notify_token')
            api_data = data.get('api_data', [])
            config = {
                'line_notify_token': line_notify_token,
                'api_data': api_data
            }
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml. Please check if the file is correctly filled.\n"
            "If the problem can't be solved, consider deleting config.yml and restarting the program.\n")
        sys.exit()


def check_files(api_data):
    """Check if the collections folders are empty based on the 'use' flag in api_data.

    :param api_data: List of dictionaries representing API data, each containing a 'use' flag.
    :return: None
    """
    for api_info in api_data:
        api_name = api_info['api_name']
        environment_name = api_info['environment_name']
        use = str_to_bool(api_info.get('use', False))
        collections_folder = f"./collections/{api_name}"

        if use and not os.listdir(collections_folder):
            print(
                f"Error: The '{collections_folder}' folder for API {api_name} and environment {environment_name} is empty.")
            sys.exit(1)


def str_to_bool(bool_str):
    """Convert a string to a boolean, case-insensitive.
    :param bool_str: The input string.
    :return: True if the string is "true" (case-insensitive), False otherwise.
    """
    return bool_str.lower() == "true"


def check_folders(api_data):
    """Check if the required folders exist and create them if they based on the 'use' flag in api_data.

    :param api_data: List of dictionaries representing API data, each containing a 'use' flag.
    :return: None
    """
    # Define the folder names
    collections_folder = "collections"
    environments_folder = "environments"
    log_folder = "log"

    # Create the "environments" folder if it doesn't exist
    if not os.path.exists(environments_folder):
        os.makedirs(environments_folder)
        print(f"Created '{environments_folder}' folder.")
    # Create the "collections" folder if it doesn't exist
    elif not os.path.exists(collections_folder):
        os.makedirs(collections_folder)
        print(f"Created '{collections_folder}' folder.")
    # Create the "log" folder if it doesn't exist
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Created '{log_folder}' folder.")

    # Check and create collections folders based on the 'use' flag in api_data
    for api_info in api_data:
        api_name = api_info['api_name']
        is_api_enable = str_to_bool(api_info.get('use', False))
        collections_api_folder = os.path.join(collections_folder, api_name)

        if is_api_enable and not os.path.exists(collections_api_folder):
            os.makedirs(collections_api_folder)
            print(f"Created '{collections_api_folder}' folder.")

        # Check if folder creation failed and exit the script
        if is_api_enable and not os.path.exists(collections_api_folder):
            environment_name = api_info['environment_name']
            print(
                f"Error: Failed to create '{collections_api_folder}' folder for API {api_name} and environment {environment_name}. Exiting.")
            sys.exit(1)


def create_log_folder(api_data):
    """Create a folder for today's date and return the path.
    :param api_data: List of dictionaries representing api data.
    :return: Path to today's folder
    """
    today_date = datetime.datetime.now().strftime("%Y%m%d")
    log_folder = "./log"

    # Check if the "log" folder exists, and create it if it doesn't
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    today_folder = os.path.join(log_folder, today_date)

    # Check if the folder for today's date exists, and create it if it doesn't
    if not os.path.exists(today_folder):
        os.makedirs(today_folder, exist_ok=True)

    for api_info in api_data:
        api_name = api_info['api_name']
        is_api_enabled = str_to_bool(api_info.get('use', False))
        if is_api_enabled:
            api_folder = os.path.join(today_folder, api_name)
            os.makedirs(api_folder, exist_ok=True)

    return today_folder


def remove_ansi_escape_codes(text):
    """Remove ANSI escape codes from text.
    :param str text: Text to remove ANSI escape codes from.
    :return: Text with ANSI escape codes removed.
    :rtype: str
    """
    return re.sub(r'\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]', '', text)

