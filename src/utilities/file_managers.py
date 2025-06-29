import json


def save_file(path, file):
    with open(path, "w") as backup_out:
        json.dump(file, backup_out, indent=4)

def load_file(path):
    try:
        with open(path, "r", encoding="utf-8") as json_in:
            return json.load(json_in)
    except FileNotFoundError:
        return {}
