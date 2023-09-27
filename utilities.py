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
# | Ethereum wallet Tracker          |
# | Made by KXX (MIT License)        |
# ++--------------------------------++
# input your line_notify_token
line_notify_token: ''
# input your environment name
environment_name: ''
#-------------------------------------
"""
                )
    sys.exit()


def read_config():
    """Read config file.
    Check if config file exists, if not, create one.
    if exists, read config file and return config with dict type.
    :rtype: dict
    """
    if not exists('./config.yml'):
        print("Config file not found, create one by default.\nPlease finish filling config.yml")
        with open('config.yml', 'w', encoding="utf8"):
            config_file_generator()

    try:
        with open('config.yml', 'r', encoding="utf8") as f:
            data = yaml.load(f, Loader=SafeLoader)
            config = {
                'line_notify_token': data['line_notify_token'],
                'environment_name': data['environment_name']
            }
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml, please check if the file is corrected filled.\n"
            "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()


def check_folders():
    """Check if the required folders exist, and create them if they don't.
    :return: None
    """
    # Define the folder names
    environments_folder = "environments"
    collections_folder = "collections"
    log_folder = "log"  # New line to check the "log" folder

    # Check if the "environments" folder exists, and create it if it doesn't
    if not os.path.exists(environments_folder):
        os.makedirs(environments_folder)
        print(f"Created '{environments_folder}' folder.")

    # Check if the "collections" folder exists, and create it if it doesn't
    if not os.path.exists(collections_folder):
        os.makedirs(collections_folder)
        print(f"Created '{collections_folder}' folder.")

    # Check if the "log" folder exists, and create it if it doesn't
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Created '{log_folder}' folder.")

    # Check if any folder creation failed and exit the script
    if not os.path.exists(environments_folder) or not os.path.exists(collections_folder) or not os.path.exists(
            log_folder):
        print("Error: Failed to create one or more folders. Exiting.")
        sys.exit(1)


def create_log_folder():
    """Create a folder for today's date and return the path.
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

    return today_folder


def remove_ansi_escape_codes(text):
    """Remove ANSI escape codes from text.
    :param str text: Text to remove ANSI escape codes from.
    :return: Text with ANSI escape codes removed.
    :rtype: str
    """
    return re.sub(r'\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]', '', text)


def split_and_remove_log_file(collection_results_file, line_count, max_lines):
    """Split the log file into multiple files if it exceeds the max lines.
    :param str collection_results_file: Path to the log file.
    :param collection_results_file:
    :param line_count:
    :param max_lines:
    :return:
    """
    split_count = 1
    with open(collection_results_file, 'r') as file:
        lines = file.readlines()
        current_split = []
        for line in lines:
            current_split.append(line)
            if line_count == max_lines:
                with open(f"{collection_results_file}_split{split_count}", 'w') as split_file:
                    split_file.writelines(current_split)
                split_count += 1
                current_split = []
            line_count += 1
        if current_split:
            with open(f"{collection_results_file}_split{split_count}", 'w') as split_file:
                split_file.writelines(current_split)
