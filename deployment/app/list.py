import os
import json
import logging

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

def get_files(folder_name):
    """Get all files in a folder recursively."""
    files = []
    if not folder_name:
        logging.fatal("No folder.")
    for root, dirs, file_names in os.walk(folder_name):
        for file_name in file_names:
            if file_name.endswith('.yaml') or file_name.endswith('.yml'):
                files.append(file_name)
            else;
                logging.error("No yaml or yml file.")

    return files

def main(event, lambda_context):
    """Main function."""
    logging.info("Start")
    
    files = {}
    folders = ["threat/actor", "domain/study"]
    for folder in folders:
        for file in get_files(folder):
            if folder not in files:
                files[folder] = []
            files[folder].append(file)

    return {
        'statusCode': 200,
        'body': json.dumps({
            "data": files,
        })
    }
    logging.info("End")