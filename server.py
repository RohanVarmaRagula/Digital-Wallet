import socket
import threading
import sys
import json
import utils
import auth

clients_active = 0

def multi_client_handler(conn, addr):
    global clients_active
    clients_active += 1
    print(f'Number of active clients = {clients_active}')
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data or data.decode() == 'exit':
                clients_active -= 1
                print(f'Number of active clients = {clients_active}')
                break
            print(f"Received: {data.decode()}")
            conn.sendall(b"Message received")

def process_request(request):
    """
    Addresses login and singup requests from client
    """
    
    users = utils.load_creadentials()
    
    if request['type'] == 'signup':
        username = request['username']
        password = request['password']
        balance = request['balance']
        
        if username in users:
            return {"status": "error", "message": "Username already exists"}
        else:
            auth.store_credentials(username, password, balance)
            return {"status": "success", "message": "Sign up Successful"}
    
    else:
        username = request['username']
        password = request['password']
        
        if username not in users:
            return {"status": "error", "message": "Username does not exist"}
        if auth.verify_credentials(username, password):
            return {"status": "success", "message": "Log in Successful"}
        else:
            return {"status": "error", "message": "Wrong password"}

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sfd:
        sfd.bind((host, port))
        sfd.listen()
        print(f"Server listening on {host}:{port}")
        
        while True:
            conn, addr = sfd.accept()
            thread = threading.Thread(target=multi_client_handler, args=(conn, addr, ))
            thread.start()

if __name__ == "__main__":
    start_server()