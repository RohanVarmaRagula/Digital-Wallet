import json
import gmpy2 
import os

FILE_PATH = "credentials.json"
KEYS_FILE = "keys.json"
HISTORY_PATH = "history.json"

def load_credentials():
    """Loads user credentials from the JSON file."""
    try:
        with open(FILE_PATH, "r") as file:
            users = json.load(file)
            for user in users:
                users[user]["balance"] = users[user]["balance"]
            return users
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_credentials(users):
    """Saves updated user credentials to the JSON file."""
    with open(FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)

def update_user_history(username, transaction):
    """Appends a transaction to the user's history in history.json."""
    try:
        with open(HISTORY_PATH, "r") as history_file:
            history_data = json.load(history_file)
    except (FileNotFoundError, json.JSONDecodeError):
        history_data = {}

    if username not in history_data:
        history_data[username] = []
    history_data[username].append(transaction)

    with open(HISTORY_PATH, "w") as history_file:
        json.dump(history_data, history_file, indent=4)


def initialize_json(file):
    """Ensures credentials.json exists and is a valid JSON object."""

    if not os.path.exists(file): 
        with open(file, "w") as f:
            json.dump({}, f, indent=4)
    else:
        try:
            with open(file, "r") as f:
                data = f.read().strip()
                if not data:  
                    raise json.JSONDecodeError("Empty file", data, 0)
                json.loads(data)  
        except json.JSONDecodeError:
            with open(file, "w") as f:
                json.dump({}, f, indent=4)
            
def save_keys(username, private_key, public_key):
    """Stores private key securely in a local file."""
    keys = {}
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as f:
            keys = json.load(f)
            
    keys[username] = {} 
    keys[username]["private_key"] = private_key
    keys[username]["public_key"] = public_key
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def load_private_key(username):
    """Retrieves stored private key and converts it back to mpz format."""
    if not os.path.exists(KEYS_FILE):
        return None  
    
    with open(KEYS_FILE, "r") as f:
        keys = json.load(f)  
    
    private_key = keys.get(username, {}).get("private_key", [0, 0, 0])  
    return tuple(gmpy2.mpz(x) for x in private_key)


def load_public_key(username):
    """Retrieves stored public key and converts it back to mpz format."""
    if not os.path.exists(KEYS_FILE):
        return None  
    
    with open(KEYS_FILE, "r") as f:
        keys = json.load(f)  
    
    public_key = keys.get(username, {}).get("public_key", [0, 0])  
    return tuple(gmpy2.mpz(x) for x in public_key)
