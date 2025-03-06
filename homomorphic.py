import random
import gmpy2
import json

class Paillier:
    def __init__(self, key_size=512):
        self.key_size = key_size
        self.public_key, self.private_key = self.generate_keys()

    def generate_keys(self):
        p = gmpy2.next_prime(random.getrandbits(self.key_size))
        q = gmpy2.next_prime(random.getrandbits(self.key_size))
        n = p * q
        λ = (p - 1) * (q - 1) // gmpy2.gcd(p - 1, q - 1)
        g = n + 1
        μ = gmpy2.invert(λ, n)
        return (n, g), (λ, μ, n)

    def encrypt(self, m):
        n, g = self.public_key
        r = random.randint(1, n - 1)
        return (pow(g, m, n * n) * pow(r, n, n * n)) % (n * n)

    def decrypt(self, c):
        λ, μ, n = self.private_key
        x = pow(c, λ, n * n) - 1
        return int((x // n) * μ % n)

    def homomorphic_addition(self, c1, c2):
        return (c1 * c2) % (self.public_key[0] ** 2)

    def homomorphic_subtraction(self, c1, b):
        n, _ = self.public_key
        neg_b = n - b  # Compute -b mod n
        enc_neg_b = self.encrypt(neg_b)  # Encrypt -b
        return (c1 * enc_neg_b) % (n * n)  # Enc(a) * Enc(-b)

# Initialize Paillier encryption
phe = Paillier()

file_path = "credentials.json" #modify to file based on file generated at server

def update_DB(sender_userID, receiver_userID, enc_transfer_amount):
    try:
        with open(file_path, "r") as file:
            users = json.load(file)  # Load existing JSON data
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: File not found or invalid JSON format.")
        return False

    if sender_userID in users and receiver_userID in users:
        enc_old_balance_sender = users[sender_userID]["balance"]
        enc_new_balance_sender = phe.homomorphic_subtraction(enc_old_balance_sender, enc_transfer_amount)
        users[sender_userID]["balance"] = enc_new_balance_sender
        
        enc_old_balance_receiver = users[receiver_userID]["balance"]
        enc_new_balance_receiver = phe.homomorphic_addition(enc_old_balance_receiver, enc_transfer_amount)
        users[receiver_userID]["balance"] = enc_new_balance_receiver

        with open(file_path, "w") as file:
            json.dump(users, file, indent=4)

        print(f"Transaction successful! Updated balances for {sender_userID} and {receiver_userID}.")
        return True
    else:
        print("Sender/Receiver not found! Please verify username again.")
        return False
