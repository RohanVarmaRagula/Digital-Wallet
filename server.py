import socket
import threading
import json
import queue
import utils
import os
import auth

clients_active = 0
clients_lock = threading.Lock()  
request_queue = queue.Queue()

def initialize_credentials():
    """Ensures credentials.json exists and is a valid JSON object."""
    FILE_PATH = "credentials.json"

    if not os.path.exists(FILE_PATH): 
        with open(FILE_PATH, "w") as f:
            json.dump({}, f, indent=4)
        print("Initialized credentials.json (file was missing).")
    else:
        try:
            with open(FILE_PATH, "r") as f:
                data = f.read().strip()
                if not data:  
                    raise json.JSONDecodeError("Empty file", data, 0)
                json.loads(data)  
        except json.JSONDecodeError:
            print("Warning: credentials.json was corrupted. Resetting it.")
            with open(FILE_PATH, "w") as f:
                json.dump({}, f, indent=4)

def client_handler(conn, addr):
    """Handles a new client connection."""
    global clients_active
    with clients_lock:
        clients_active += 1
    print(f'Number of active clients = {clients_active}')

    with conn:
        print(f"Connected by {addr}")
        while True:
            try:
                data = conn.recv(1024)
                if not data or data.decode() == 'exit':
                    with clients_lock:
                        clients_active -= 1
                    print(f'Client {addr} disconnected. Active clients = {clients_active}')
                    break
                
                request = json.loads(data.decode())  
                request_queue.put((conn, request))  

            except json.JSONDecodeError:
                print("Received malformed JSON data")
                conn.sendall(json.dumps({"status": "error", "message": "Invalid request format"}).encode())

def process_request():
    """Processes requests from clients continuously."""
    while True:
        conn, request = request_queue.get()
        response = handle_authentication(request)

        try:
            conn.sendall(json.dumps(response).encode())
        except (BrokenPipeError, ConnectionResetError):
            print("Client disconnected before receiving response")
        
        request_queue.task_done()

def start_request_workers(num_threads=4):
    """Starts multiple worker threads to process client requests."""
    for _ in range(num_threads):
        threading.Thread(target=process_request, daemon=True).start()

def handle_authentication(request):
    """Handles login and signup requests."""
    users = utils.load_credentials()  
    username = request.get("username")
    password = request.get("password")

    if request["type"] == "signup":
        balance = request.get("balance", 0.0)

        if username in users:
            return {"status": "error", "message": "Username already exists"}
        
        auth.store_credentials(username, password, balance)
        return {"status": "success", "message": "Sign up successful"}

    elif request["type"] == "login":
        if username not in users:
            return {"status": "error", "message": "Username does not exist"}
        
        if auth.verify_credentials(username, password):
            return {"status": "success", "message": "Login successful"}
        else:
            return {"status": "error", "message": "Wrong password"}

    return {"status": "error", "message": "Invalid request type"}

def start_server(host="127.0.0.1", port=65432):
    """Starts the server."""
    initialize_credentials()  # Ensure credentials.json is valid before starting
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sfd:
        sfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sfd.bind((host, port))
        sfd.listen()
        print(f"Server listening on {host}:{port}")

        start_request_workers()  

        while True:
            conn, addr = sfd.accept()
            threading.Thread(target=client_handler, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
