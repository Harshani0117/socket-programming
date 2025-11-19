import socket
import threading

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9999       # Choose any open port

clients = []

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"[{client_address}] {message}")
            broadcast(message, client_socket)
    except:
        print(f"[ERROR] Connection lost with {client_address}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"[DISCONNECTED] {client_address}")

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.remove(client)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[SERVER RUNNING] Listening on {HOST}:{PORT}")
    while True:
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    print("[STARTING SERVER...]")
    start_server()
