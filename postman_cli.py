import subprocess
import os
import utilities as utils
config = utils.read_config()
is_api_20 = utils.str_to_bool(utils.read_config().get('api_2.0'))
is_api_14 = utils.str_to_bool(utils.read_config().get('api_1.4'))


def run_postman_collection(collection_name, collections_folder, environment_path, today_folder):
    """Run a Postman collection and return the output.
    :param str collection_name: Name of the collection to run.
    :param str collections_folder: Path to the folder containing the collections.
    :param str environment_path: Path to the environment file to use.
    :param str today_folder: Path to today's folder.
    :return: Tuple containing the collection name, output, path to the log file, and the line count.
    :rtype: tuple
    """
    collection_name_without_extension = os.path.splitext(collection_name)[0]
    collection_results_file = None
    # Construct the command to run the Postman collection
    command = [
        "postman",
        "collection",
        "run",
        f"{collections_folder}/{collection_name}",
        "--environment",
        environment_path
    ]

    try:
        # Run the Postman collection command and capture the output
        completed_process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
        )
        collection_output = completed_process.stdout
        collection_output = utils.remove_ansi_escape_codes(collection_output)

        # Capture and log any errors
        error_output = completed_process.stderr
        error_output = utils.remove_ansi_escape_codes(error_output)
        # Handle errors if needed
        if completed_process.returncode != 0:
            print(f"Error running collection")
            collection_output += f"Error running collection: {error_output}"
    except Exception as e:
        print(f"Error running collection: {e}")
        collection_output = f"Error running collection: {e}"

    # Create a file to store today's results for this collection
    if is_api_14:
        collection_results_file = os.path.join(today_folder, "api 1.4", collection_name)
    elif is_api_20:
        collection_results_file = os.path.join(today_folder, "api 2.0", collection_name)
    # Check if collection_output is None and provide a default value
    if collection_output is None:
        collection_output = ""

    with open(collection_results_file, 'w', encoding='utf-8') as file:
        file.write(collection_output)

    line_count = len(collection_output.split('\n'))

    return collection_name_without_extension, collection_output, collection_results_file, line_count
