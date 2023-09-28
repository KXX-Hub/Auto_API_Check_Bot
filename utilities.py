"""This python will handle some extra functions."""
import datetime
import os
import re
import sys
from os.path import exists
import postman_cli as postman
import yaml
from yaml import SafeLoader
import line_notify as line


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as f:
        f.write("""# ++--------------------------------++
# | API Auto Check Bot               |
# | Made by KXX (MIT License)        |
# ++--------------------------------++
# input your line_notify_tokens
line_notify_token: ""
# input your api 1.4 environment name
api_14_environment_name: ""
# input your api 2.0 environment name
api_20_environment_name: ""
# If you want to use the api_2.0, please fill "True"
api_2.0: "False"
# If you want to use the api_1.4, please fill "True"
api_1.4: "False"
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
                'api_14_environment_name': data['api_14_environment_name'],
                'api_20_environment_name': data['api_20_environment_name'],
                'api_2.0': data['api_2.0'],
                'api_1.4': data['api_1.4']
            }
            return config
    except (KeyError, TypeError):
        print(
            "An error occurred while reading config.yml, please check if the file is corrected filled.\n"
            "If the problem can't be solved, consider delete config.yml and restart the program.\n")
        sys.exit()


def check_files(check_14=False, check_20=False):
    """Check if the environments folder and collections folder is empty.
    :return: None
    """
    # Define the folder names
    api_14_collections_folder = "api_1.4_collections"
    api_20_collections_folder = "api_2.0_collections"
    empty_folder = "false"
    # Check if the created folders are empty
    if check_14 and not os.listdir(api_14_collections_folder):
        print(f"Error: The '{api_14_collections_folder}' folder is empty. Exiting.")
        empty_folder = "true"
    if check_20 and not os.listdir(api_20_collections_folder):
        print(f"Error: The '{api_20_collections_folder}' folder is empty. Exiting.")
        empty_folder = "true"
    if empty_folder == "true":
        sys.exit(1)


def str_to_bool(s):
    """Convert a string to a boolean, case-insensitive.
    :param s: The input string.
    :return: True if the string is "true" (case-insensitive), False otherwise.
    """
    return s.lower() == "true"


def check_folders(check_14=False, check_20=False):
    """Check if the required folders exist, and create them if they don't.
    :return: None
    """
    # Define the folder names
    environments_folder = "environments"
    api_14_collections_folder = "api_1.4_collections"
    api_20_collections_folder = "api_2.0_collections"
    log_folder = "log"  # New line to check the "log" folder

    # Check if the "environments" folder exists, and create it if it doesn't
    if not os.path.exists(environments_folder):
        os.makedirs(environments_folder)
        print(f"Created '{environments_folder}' folder.")

    # Check and create the 1.4 collections folder if needed
    if check_14 and not os.path.exists(api_14_collections_folder):
        os.makedirs(api_14_collections_folder)
        print(f"Created '{api_14_collections_folder}' folder.")

    # Check and create the 2.0 collections folder if needed
    if check_20 and not os.path.exists(api_20_collections_folder):
        os.makedirs(api_20_collections_folder)
        print(f"Created '{api_20_collections_folder}' folder.")

    # Check if the "log" folder exists, and create it if it doesn't
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Created '{log_folder}' folder.")

    # Check if any folder creation failed and exit the script
    if (
            not os.path.exists(environments_folder)
            or (check_14 and not os.path.exists(api_14_collections_folder))
            or (check_20 and not os.path.exists(api_20_collections_folder))
            or not os.path.exists(log_folder)
    ):
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

    # Check if "1.4" is in the configuration and create a subfolder if present
    if str_to_bool(read_config().get('api_1.4')):
        api_1_4_folder = os.path.join(today_folder, "api 1.4")
        os.makedirs(api_1_4_folder, exist_ok=True)

    # Check if "2.0" is in the configuration and create a subfolder if present
    if str_to_bool(read_config().get('api_2.0')):
        api_2_0_folder = os.path.join(today_folder, "api 2.0")
        os.makedirs(api_2_0_folder, exist_ok=True)

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
        for code_line in lines:
            current_split.append(code_line)
            if line_count == max_lines:
                with open(f"{collection_results_file}_split{split_count}", 'w') as split_file:
                    split_file.writelines(current_split)
                split_count += 1
                current_split = []
            line_count += 1
        if current_split:
            with open(f"{collection_results_file}_split{split_count}", 'w') as split_file:
                split_file.writelines(current_split)


def get_collections_with_failures(collections, collections_folder, environment_path, max_lines, today_folder):
    collections_with_failures = []
    for collection_name in collections:
        collection_name_without_extension, collection_output, _, line_count = postman.run_postman_collection(
            collection_name, collections_folder, environment_path, today_folder, max_lines)
        print()

        if "Error" in collection_output or "failures" in collection_output:
            collections_with_failures.append(collection_name_without_extension)

    return collections_with_failures


def create_and_send_line_notify_message(collections_with_failures):
    if collections_with_failures:
        line_notify_message = "API Error \n" \
                              "----------------------------------\n" \
                              "Failures in the following collections:\n\n"
        for collection in collections_with_failures:
            collection_name = collection.replace('.postman_collection', "")
            line_notify_message += f"{collection_name}\n"

    elif not collections_with_failures:
        formatted_date = datetime.datetime.now().strftime("%Y/%m/%d")
        line_notify_message = f"{formatted_date}\nAll collections completed"

    else:
        line_notify_message = "Something went wrong. Please check the log files."

    line.send_message(line_notify_message)
