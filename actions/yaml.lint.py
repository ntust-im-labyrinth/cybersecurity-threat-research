"""Module to provide linting for threat models."""
import os
import json
import sys
import yaml

# Allow Optional Fields without Spec
ALLOW_OPTIONAL = True

def get_files(folder_name):
    """Get all files in a folder recursively."""
    files = []
    for root, dirs, file_names in os.walk(folder_name):
        for file_name in file_names:
            if file_name.endswith('.yaml') or file_name.endswith('.yml'):
                files.append(os.path.join(root, file_name))
    return files


def get_yaml(file_name):
    """Get yaml content from a file."""
    try:
        with open(file_name, 'r', encoding="utf-8") as stream:
            return yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        return None
    except FileNotFoundError:
        return None


def get_spec(spec_file):
    """Get spec from a file."""
    try:
        with open(spec_file, 'r', encoding="utf-8") as stream:
            return json.load(stream)
    except json.JSONDecodeError as exc:
        print(exc)
        return None
    except FileNotFoundError:
        return None


def check_spec(spec, content):
    """Check if the content is valid according to the spec."""
    # Check Requirement & Optional Fields in Spec
    if 'requirement' not in spec or 'optional' not in spec:
        return False, "Spec file format error"

    # Check Requirement Fields
    requirement_fields = spec['requirement']
    for requirement_field in requirement_fields:
        name = requirement_field['name']
        field_type = requirement_field['type']
        if name not in content:
            return False, f"Field '{name}' is not in contents"
        elif field_type == 'str' and isinstance(content[name], str) is False:
            return False, f"Field '{name}' is not str"
        elif field_type == 'list' and isinstance(content[name], list) is False:
            return False, f"Field '{name}' is not list"
        else:
            continue

    # Extract name from requirement_fields
    requirement_fields = [requirement_field['name'] for requirement_field in requirement_fields]
    # Extract name from optional_fields
    optional_fields = [optional_field['name'] for optional_field in spec['optional']]

    # Check Optional Fields
    if not ALLOW_OPTIONAL:
        for item in content:
            if item not in requirement_fields and item not in optional_fields:
                return False, f"Optional field '{item}' not allowed"
            else:
                continue
    return True, "Success"


def main():
    """Main function."""
    folders = [
        {
            'name': 'threat',
            'spec': 'spec/threat.spec.json',
        },
        {
            'name': 'domain',
            'spec': 'spec/domain.spec.json',
        },
    ]
    for folder in folders:
        spec = get_spec(folder['spec'])
        if spec is None:
            print("Error: {} Spec file not found.".format(folder['name']))
            sys.exit(-1)

        for file in get_files(folder['name']):
            content = get_yaml(file)
            if content is None:
                print("Error: {} file format is error.".format(file))
                sys.exit(-1)
            passed, msg = check_spec(spec, content)
            if not passed:
                print("Error in file: {}, {}.".format(file, msg))
                sys.exit(-1)


if __name__ == '__main__':
    main()
