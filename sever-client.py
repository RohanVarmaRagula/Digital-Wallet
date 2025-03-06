import socket
import threading
import sys

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

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sfd:
        sfd.bind((host, port))
        sfd.listen()
        print(f"Server listening on {host}:{port}")
        
        while True:
            conn, addr = sfd.accept()
            thread = threading.Thread(target=multi_client_handler, args=(conn, addr, ))
            thread.start()

def start_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        while True:
            message = input('Enter Message: ')
            client_socket.sendall(message.encode())
            data = client_socket.recv(1024)
            if message == 'exit':
                break
            print(f"Received from server: {data.decode()}")

if __name__ == "__main__":
    if sys.argv[1] == "server":
        start_server()
    elif sys.argv[1] == "client":
        start_client()
    else:
        print("Enter Proper Arguments\n")