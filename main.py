import os
import utilities as utils
import postman_cli as postman
import datetime
import line_notify as line

config = utils.read_config()
api_data = config.get('api_data', [])

environment_paths = {}
collections_dicts = {}


def initial_check():
    """Perform initial checks and setup.
    """
    print("Welcome to the Auto Postman CLI!")
    print("Starting Postman collections...")

    for api_info in api_data:
        api_name = api_info['api_name']
        is_api_enabled = utils.str_to_bool(api_info.get('use'))
        api_environment_name = api_info['environment_name']
        if is_api_enabled:
            env_path = f"./environments/{api_environment_name}.json"
            environment_paths.update({api_name: env_path})
            collections_dicts.update({api_name: f'./collections/{api_name}/'})
            collections_folder = collections_dicts.get(api_name)
            if collections_folder:
                utils.check_folders(api_data)
                utils.check_files(api_data)


def create_and_send_line_notify_message(collections_with_failures, api_with_failures):
    """Create a message to send via Line Notify.
    :param api_with_failures: api that has failures.
    :param list collections_with_failures: List of collections with failures.
    """
    if collections_with_failures:
        line_notify_message = "API Error \n" \
                              "----------------------------------\n"
        line_notify_message += f"Failures in Api Name : {api_with_failures}\n" \
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


def run_collections(api_name):
    """Run all collections for the specified API.
    :param str api_name: Name of the API.
    """

    collections_with_failures = []
    print(f"Running API {api_name} collections...")
    collections = [f for f in os.listdir(collections_dicts[api_name]) if f.endswith(".json")]
    # print(collections)
    today_folder = utils.create_log_folder(api_data)
    total_collections = len(collections)
    api_with_failures = ""
    for idx, collection_name in enumerate(collections, start=1):
        collection_name_without_extension, collection_output, _, line_count = postman.run_postman_collection(
            api_name,
            collection_name,
            collections_dicts[
                api_name],
            environment_paths[
                api_name],
            today_folder)
        if "Error" in collection_output or "failures" in collection_output:
            print(f"{idx}/{total_collections} collection(s) completed with errors: {collection_name_without_extension}")
            collections_with_failures.append(collection_name_without_extension)
            api_with_failures = api_name
        else:
            print(
                f"{idx}/{total_collections} collection(s) completed successfully: {collection_name_without_extension}")

    create_and_send_line_notify_message(collections_with_failures, api_with_failures)


def main():
    """Run all collections for all APIs.
    """
    line_notify_message = ""
    for api_info in api_data:
        api_name = api_info['api_name']
        is_api_enabled = utils.str_to_bool(api_info.get('use'))
        if is_api_enabled:
            run_collections(api_name)
    line.send_message(line_notify_message)


if __name__ == "__main__":
    initial_check()
    main()
