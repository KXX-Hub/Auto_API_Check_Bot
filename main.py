import os
import utilities as utils
import postman_cli as postman

config = utils.read_config()
is_api_20 = utils.str_to_bool(config.get('api_2.0'))
is_api_14 = utils.str_to_bool(config.get('api_1.4'))
environment_paths = {}
collections_dicts = {}

if is_api_20:
    api_20_env_path = f"./environments/{config.get('api_20_environment_name')}.json"
    environment_paths.update({'api 2.0': api_20_env_path})
    collections_dicts.update({'api 2.0': './api_2.0_collections/'})
if is_api_14:
    api_14_env_path = f"./environments/{config.get('api_14_environment_name')}.json"
    environment_paths.update({'api 1.4': api_14_env_path})
    collections_dicts.update({'api 1.4': './api_1.4_collections/'})


def initial_check():
    print("Welcome to the Auto Postman CLI!")
    print("Starting Postman collections...")
    utils.check_folders(check_14=is_api_14, check_20=is_api_20)
    utils.check_files(check_14=is_api_14, check_20=is_api_20)


def run_collections(api_version):
    print(f"Running API {api_version} collections...")
    collections = [f for f in os.listdir(collections_dicts[f'api {api_version}']) if f.endswith(".json")]
    today_folder = utils.create_log_folder()
    total_collections = len(collections)
    max_lines = 10000

    for idx, collection_name in enumerate(collections, start=1):
        collection_name_without_extension, collection_output, _, line_count = postman.run_postman_collection(
            collection_name, collections_dicts[f'api {api_version}'], environment_paths[f"api {api_version}"],
            today_folder, max_lines)

        if "Error" in collection_output or "failures" in collection_output:
            print(f"{idx}/{total_collections} collection(s) completed with errors: {collection_name_without_extension}")
        else:
            print(
                f"{idx}/{total_collections} collection(s) completed successfully: {collection_name_without_extension}")

    collections_with_failures = utils.get_collections_with_failures(
        collections, collections_dicts[f'api {api_version}'], environment_paths[f"api {api_version}"], max_lines,
        today_folder)

    utils.create_and_send_line_notify_message(collections_with_failures)


def main():
    if is_api_14:
        run_collections("1.4")
    elif is_api_20:
        run_collections("2.0")


if __name__ == "__main__":
    initial_check()
    main()
