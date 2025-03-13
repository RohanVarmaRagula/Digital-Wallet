import socket
import threading
import sys
import json

def start_client(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        option = input('Choose one option:\n1. Login\n2. Signup\n')
        if option not in ['1', '2']:
            print('Invalid option')
            return 
        
        username=input('Enter Username: ').strip()
        password=input('Enter Password: ').strip()
        
        if option == 1:
            request = {"type":"login",
                       "username":username,
                       "password":password}
        if option == 2:
            balance = float(input('Enter balance: '))
            request = {"type":"signup",
                       "username":username,
                       "password":password,
                       "balance":balance}
        
        client_socket.sendall(json.dumps(request).encode())
        response = json.loads(client_socket.recv(1024).decode())
        print('Server: ', response)
    
if __name__ == "__main__":
    start_client()
        