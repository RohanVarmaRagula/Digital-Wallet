import socket
import threading
import json
import queue
import utils
import auth
import homomorphic

clients_active = 0
clients_lock = threading.Lock()  
request_queue = queue.Queue()
phe = homomorphic.Paillier()

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
                data = conn.recv(1024 * 10)
                request = json.loads(data.decode())  
                print(request['request'])
                if not data or data.decode() == 'exit':
                    with clients_lock:
                        clients_active -= 1
                    print(f'Client {addr} disconnected. Active clients = {clients_active}')
                    break
                
                request = json.loads(data.decode())  
                request_queue.put((conn, request))  

            except json.JSONDecodeError:
                print("__________Received malformed JSON data___________")
                conn.sendall(json.dumps({"status": "error", "message": "Invalid request format"}).encode())

def process_request():
    """Processes requests from clients."""
    while True:
        conn, request = request_queue.get()
        response = {}

        if request["request"] == "signup" or request["request"] == "login":
            response = handle_authentication(request)
        elif request["request"] == "transfer":
            response = handle_transfer(request)
        elif request["request"] == "balance":
            response = handle_balance(request["username"])
        else:
            response = {"status": "error", "message": "Invalid request type"}

        conn.sendall(json.dumps(response).encode())
        request_queue.task_done()

def handle_transfer(request):
    """Handles secure transfer using homomorphic encryption."""
    sender = request["sender"]
    receiver = request["receiver"]
    
    users = utils.load_credentials()
    if sender not in users or receiver not in users:
        return {"status": "error", "message": "Invalid sender or receiver"}

    recv_enc_amount = request["receiver_encrypted_amount"]
    send_enc_amount = request["sender_encrypted_amount"]

    sender_enc_balance = int(users[sender]["balance"])
    receiver_enc_balance = int(users[receiver]["balance"])
    sender_public_key = tuple(map(int, users[sender]["public_key"]))
    receiver_public_key = tuple(map(int, users[receiver]["public_key"]))
    
    new_enc_sender_balance = phe.homomorphic_subtraction(sender_enc_balance, send_enc_amount, sender_public_key)
    new_enc_receiver_balance = phe.homomorphic_addition(receiver_enc_balance, recv_enc_amount, receiver_public_key)
    users[sender]["balance"] = int(new_enc_sender_balance)
    users[receiver]["balance"] = int(new_enc_receiver_balance)
    utils.save_credentials(users)
    print('saved creds')
    return {"status": "success", "message": "Transfer completed"}

def handle_balance(username):
    """Handles balance requests."""
    users = utils.load_credentials()
    
    if username not in users:
        return {"status": "error", "message": "User not found"}
    
    return {"status": "success", "balance": users[username]["balance"]}


def start_request_workers(num_threads=4):
    """Starts multiple worker threads to process client requests."""
    for _ in range(num_threads):
        threading.Thread(target=process_request, daemon=True).start()

def handle_authentication(request):
    """Handles login and signup requests."""
    users = utils.load_credentials()  
    username = request.get("username")
    password = request.get("password")

    if request["request"] == "signup":
        balance = request.get("balance", 0.0)
        public_key = request.get("public_key")

        if username in users:
            return {"status": "error", "message": "Username already exists"}
        
        auth.store_credentials(username, password, balance, public_key)
        return {"status": "success", "message": "Sign up successful"}

    elif request["request"] == "login":
        if username not in users:
            return {"status": "error", "message": "Username does not exist"}
        
        if auth.verify_credentials(username, password):
            return {"status": "success", "message": "Login successful"}
        else:
            return {"status": "error", "message": "Wrong password"}

    return {"status": "error", "message": "Invalid request type"}

def start_server(host="127.0.0.1", port=65432):
    """Starts the server."""
    utils.initialize_json(utils.FILE_PATH) 
    utils.initialize_json(utils.KEYS_FILE)
   
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
