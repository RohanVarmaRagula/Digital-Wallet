import json

FILE_PATH = 'credentials.json'

def load_creadentials():
    with open(FILE_PATH, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}
        

def save_credentials(users):
    with open(FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)