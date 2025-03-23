import json
import socket
from homomorphic import Paillier
import utils

BUFFER_SIZE = 1024

def start_client(host="127.0.0.1", port=65432):
    """Handles client communication."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket, \
            socket.socket(socket.AF_INET, socket.SOCK_STREAM) as third_party_socket:
            client_socket.connect((host, port))
            third_party_socket.connect((host, port-1))
            
            option = input("Choose one option:\n1. Login\n2. Signup\n").strip()
            username = input("Enter Username: ").strip()
            password = input("Enter Password: ").strip()

            if option == "2":
                balance = int(input("Enter balance: "))
                p = Paillier()
                public_key, private_key = p.generate_keys()

                request = {
                    "type": "store_keys",
                    "username": username,
                    "private_key": [int(private_key[0]), int(private_key[1]), int(private_key[2])],
                    "public_key": [int(public_key[0]), int(public_key[1])]
                }
                third_party_socket.sendall(json.dumps(request).encode())
                response = json.loads(third_party_socket.recv(BUFFER_SIZE).decode())
                print("Third party:", response)
                
                request = {
                    "request": "signup",
                    "username": username,
                    "password": password,
                    "balance": int(p.encrypt(balance, public_key)),
                    "public_key": (int(public_key[0]), int(public_key[1]))
                }
                
            else:
                request = {
                    "type": "acquire_keys",
                    "username": username
                }
                third_party_socket.sendall(json.dumps(request).encode())
                response = json.loads(third_party_socket.recv(BUFFER_SIZE * 10).decode())
                public_key = response["public_key"]
                private_key = response["private_key"]
                request = {"request": "login", "username": username, "password": password}

            client_socket.sendall(json.dumps(request).encode())
            response = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            print("Server:", response)

            if response["status"] == "success":
                utils.save_keys(username, [int(private_key[0]), int(private_key[1]), int(private_key[2])], [int(public_key[0]), int(public_key[1])])
                while True:
                    option = input("Choose one option:\n1. Send Money\n2. Check balance\n").strip()

                    if option == "1":
                        receiver = input("Receiver: ").strip()
                        amount = int(input("Amount to transfer: "))
                        recv_pub_key = utils.load_public_key(receiver)
                        recv_enc_amount = Paillier().encrypt(amount, recv_pub_key)
                        send_enc_amount = Paillier().encrypt(amount, public_key)
                        request = {"request": "transfer", "sender": username, "receiver": receiver, "receiver_encrypted_amount": int(recv_enc_amount), "sender_encrypted_amount": int(send_enc_amount)}
                    else:
                        request = {"request": "balance", "username": username}

                    client_socket.sendall(json.dumps(request).encode())
                    response = json.loads(client_socket.recv(BUFFER_SIZE).decode())

                    if option == "2":  
                        private_key = utils.load_private_key(username)
                        decrypted_balance = Paillier().decrypt(response["balance"], private_key)
                        print("Your Balance:", decrypted_balance)
                    else:
                        print("Server:", response)

    except ConnectionRefusedError:
        print("Failed to connect to server. Is it running?")

if __name__ == "__main__":
    start_client()