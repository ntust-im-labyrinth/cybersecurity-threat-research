import os
import json
import pandas as pd
import yaml
import logging

logging.basicConfig(filename='build_threat.log', encoding='utf-8', level=logging.DEBUG)

def count_yaml_keys(file_path):
    """count"""
    if not file_path:
        logging.fatal("You need pass parameter in count_yaml_keys func.")
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        data = yaml.safe_load(yaml_file)
        if data is None:
            return 0
        return len(data.keys())

def save_yaml_content(file_path, content, testing=False):
    if not file_path or not content:
        logging.fatal("You need pass parameter in save_yaml_content func.")
    if testing:
        print(f"Testing {file_path}: {content}")
        return
    with open(file_path, "w+", encoding="utf-8") as yaml_file:
        yaml.safe_dump(content, yaml_file, encoding='utf-8', allow_unicode=True, default_flow_style=False, sort_keys=False)

def get_yaml_content(file_path):
    if not file_path:
        logging.fatal("You need pass parameter in get_yaml_content func.")
    with open(file_path,"r", encoding="utf-8") as yaml_file:
        raw = yaml.safe_load(yaml_file)
        normalized = {}
        for key in raw:
            normalized[key.lower()] = raw[key]
        if normalized != raw:
            save_yaml_content(file_path, normalized)
        return normalized

def find_yaml_files(root_dir):
    """process all yamls"""
    if not root_dir:
        logging.warn("You need pass parameter in find_yaml_files func.")
    yaml_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".yaml"):  # or file.endswith(".yml")
                yaml_files.append(os.path.join(root, file))
    return yaml_files

def main(threat_directory):
    """main"""
    actor_info = {}
    threat_yaml_files = find_yaml_files(threat_directory)

    logging.debug(threat_yaml_files)

    if not threat_yaml_files:
        logging.fatal("No YAML files found in the specified directory.")
        return

    with open('spec/threat.spec.json', 'r', encoding="utf-8") as stream:
        spec = json.load(stream)
        required = [requirement_field['name'] for requirement_field in spec['requirement']]

    for index, path in enumerate(threat_yaml_files):
        raw = get_yaml_content(path)
        required_contents = {k:raw[k] for k in required if k in raw}
        actor_info[index] = {
            "Index": index,
            **required_contents
        }

    logging.debug(actor_info)

    rows = []
    for key, value in actor_info.items():
        row = {"Index": key}
        row.update(value)
        rows.append(row)

    threat_actor_list = pd.DataFrame(rows)
    logging.debug(threat_actor_list)

    with open(f"{threat_directory}/README.md", "w+", encoding="utf-8") as markdownFile:
        logging.info("Start Generate Threat Actor Table...")
        markdownFile.write("### Threat Actors\n")
        markdownFile.writelines(threat_actor_list.to_markdown(index=False))

if __name__ == "__main__":
    logging.info("=== Threat Builder Start ===")
    main("./threat/actor")
    logging.info("=== Threat Builder Finished ===")
