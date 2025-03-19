import json

FILE_PATH = "credentials.json"

def load_credentials():
    """Loads user credentials from the JSON file."""
    try:
        with open(FILE_PATH, "r") as file:
            users = json.load(file)
            for user in users:
                users[user]["balance"] = float(users[user]["balance"])
            return users
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_credentials(users):
    """Saves updated user credentials to the JSON file."""
    with open(FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)
