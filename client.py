import socket
import json

BUFFER_SIZE = 1024

def start_client(host="127.0.0.1", port=65432):
    """Connects to the server and sends authentication requests."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            
            option = input("Choose one option:\n1. Login\n2. Signup\n").strip()
            if option not in ["1", "2"]:
                print("Invalid option")
                return

            username = input("Enter Username: ").strip()
            password = input("Enter Password: ").strip()

            if option == "1":
                request = {"type": "login", "username": username, "password": password}
            else:
                try:
                    balance = float(input("Enter balance: "))
                except ValueError:
                    print("Invalid balance amount")
                    return
                request = {"type": "signup", "username": username, "password": password, "balance": balance}

            client_socket.sendall(json.dumps(request).encode())
            response = json.loads(client_socket.recv(BUFFER_SIZE).decode())
            print("Server:", response)

    except ConnectionRefusedError:
        print("Failed to connect to server. Is it running?")


if __name__ == "__main__":
    start_client()
