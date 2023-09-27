import os
import datetime
import utilities as utils
import line_notify as line
import postman_cli as postman

config = utils.read_config()
environment_path = f"./environments/{config.get('environment_name')}.json"
collections_folder = "./collections"



def initial_check():
    print("Welcome to the Auto Postman CLI!")
    print("Starting Postman collections...")
    utils.check_folders()
    utils.check_files()



def main():
    line_notify_message = ""
    collections = [f for f in os.listdir(collections_folder) if f.endswith(".json")]
    today_folder = utils.create_log_folder()
    total_collections = len(collections)
    current_collection = 0
    max_lines = 10000
    collections_with_failures = []
    for collection_name in collections:
        current_collection += 1
        collection_name_without_extension, collection_output, collection_results_file, line_count = (
            postman.run_postman_collection
            (collection_name, collections_folder, environment_path, today_folder, max_lines))

        if "Error" in collection_output:
            collections_with_failures.append(collection_name_without_extension)

        elif "failures" in collection_output:
            collections_with_failures.append(collection_name_without_extension)

        elif line_count > max_lines:
            utils.split_and_remove_log_file(collection_results_file, line_count, max_lines)
            os.remove(collection_results_file)

        print(f"Progress: {current_collection} / {total_collections} collections completed", "")

    if collections_with_failures:
        line_notify_message = f"API Error \n" \
                              f"----------------------------------\n" \
                              f"Failures in the following collections:\n\n"
        for collection in collections_with_failures:
            collection_name = collection.replace('.postman_collection', "")
            line_notify_message += f"{collection_name}\n"

    elif not collections_with_failures:
        if current_collection == total_collections:
            formatted_date = datetime.datetime.now().strftime("%Y/%m/%d")
            line_notify_message = f"{formatted_date}\nAll collections completed"
    else:
        line_notify_message = "Something went wrong. Please check the log files."
    line.send_message(line_notify_message)


if __name__ == "__main__":
    initial_check()
    main()
