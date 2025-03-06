import os
import json
import base64
import hashlib

CREDENTIALS_FILE = "credentials.json"

# Hash password using SHA-256 with a salt.
def hash_password(password: str, salt: bytes) -> str:
    hashed_pw = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return base64.b64encode(salt + hashed_pw).decode() 

# Store user credentials securely
def store_credentials(userid: str, password: str):
    salt = os.urandom(16)
    hashed_password = hash_password(password, salt)

    # Load existing credentials or create new storage
    data = {}
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            data = json.load(f)

    if userid not in data:
        data[userid] = {"pwd": hashed_password, "balance" : 0,"status" : True}  
    else:
        print("❌ User ID already exists.")
        return

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Credentials stored securely!")

# Verifying if the provided user ID and password are correct
def verify_credentials(userid: str, password: str) -> bool:
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ No credentials stored.")
        return False

    with open(CREDENTIALS_FILE, "r") as f:
        data = json.load(f)

    if userid not in data:
        print("❌ User ID not found.")
        return False

    # Retrieve stored salt and hash
    stored_hash_bytes = base64.b64decode(data[userid]["pwd"])
    salt, stored_hashed_pw = stored_hash_bytes[:16], stored_hash_bytes[16:]

    # Re-hash input password with the stored salt
    new_hashed_pw = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

    if new_hashed_pw == stored_hashed_pw:
        print("✅ Authentication successful!")
        return True
    else:
        print("❌ Incorrect password.")
        return False

store_credentials('user123','password')
verify_credentials('user123','password')