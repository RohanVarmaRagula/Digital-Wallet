import socket
import threading
import json
import utils

file_path = "key_vault.json"

def client_handler(conn, addr):
    """Handles a new client connection."""
    with conn:
        print(f"Connected by {addr}")
        while True:
            try:
                data = conn.recv(1024 * 10)
                if not data:
                    break  
                print('recieved')
                request = json.loads(data.decode())  
                response = {}

                if request["type"] == "store_keys":
                    print('storing keys')
                    private_key = request["private_key"]
                    public_key = request["public_key"]
                    username = request["username"]
                    print(type(public_key))
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    if username not in data:
                        data[username] = {
                            "private_key": private_key,
                            "public_key": public_key
                        }
                        with open(file_path, "w") as f:
                            json.dump(data, f, indent=4)
                        response = {"status": "success", "message": "Stored keys successfully."}
                    else:
                        response = {"status": "error", "message": "Username already exists."}

                elif request["type"] == "acquire_keys":
                    username = request["username"]

                    with open(file_path, "r") as f:
                        data = json.load(f)

                    if username in data:
                        response = {
                            "status": "success",
                            "private_key": data[username]["private_key"],
                            "public_key": data[username]["public_key"],
                            "message": "Fetched private key successfully."
                        }
                    else:
                        response = {"status": "error", "message": "Username not found."}

                else:
                    response = {"status": "error", "message": "Request type not supported."}

            except json.JSONDecodeError:
                response = {"status": "error", "message": "Invalid request format"}

            conn.sendall(json.dumps(response).encode())

def start_server(host="127.0.0.1", port=65431):
    """Starts the third-party server."""
    utils.initialize_json(file_path)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sfd:
        sfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sfd.bind((host, port))
        sfd.listen()
        print(f"Third-party server listening on {host}:{port}")

        while True:
            conn, addr = sfd.accept()
            threading.Thread(target=client_handler, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
