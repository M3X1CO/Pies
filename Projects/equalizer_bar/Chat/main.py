import socket
import select
import ssl
from databases import Database

class ChatServer:
    def __init__(self, port):
        self.port = port
        self.socket_list = []
        self.users = {}
        self.db = Database()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', port))
        self.server_socket.listen(5)
        self.socket_list.append(self.server_socket)

    def start(self):
        print(f"Server started on port {self.port}")
        while True:
            ready_to_read, _, _ = select.select(self.socket_list, [], [], 0)
            for sock in ready_to_read:
                if sock == self.server_socket:
                    connect, addr = self.server_socket.accept()
                    connect = ssl.wrap_socket(connect, server_side=True)
                    self.socket_list.append(connect)
                    print(f"New client connected from {addr}")
                    connect.send(f"You are connected from: {addr}\n".encode())

                    # Generate a username and prompt the user to create a password
                    username = self.generate_username()
                    connect.send(f"Your username is: {username}\n".encode())
                    password = self.prompt_password(connect)
                    self.db.add_user(username, password)
                    self.users[username] = connect

                else:
                    try:
                        data = sock.recv(2048).decode()
                        if not data:
                            self.socket_list.remove(sock)
                            continue
                        if data.startswith("@"):
                            recipient_username, message = data[1:].split(":", 1)
                            recipient_sock = self.users.get(recipient_username.lower())
                            if not recipient_sock:
                                sock.send(f"Recipient {recipient_username} is not available.\n".encode())
                            elif recipient_sock == sock:
                                sock.send("You can't send a message to yourself.\n".encode())
                            else:
                                recipient_sock.send(f"{username}: {message}".encode())
                    except Exception as e:
                        print(f"Error: {e}")
                        self.socket_list.remove(sock)
                        continue

        self.server_socket.close()

    def generate_username(self):
        # Generate a unique username based on the number of registered users
        num_users = len(self.users)
        username = f"user{num_users}"
        while username in self.users:
            num_users += 1
            username = f"user{num_users}"
        return username

    def prompt_password(self, sock):
        # Prompt the user to create a 5-digit password
        password = None
        while not password:
            sock.send("Please enter a 5-digit password: ".encode())
            data = sock.recv(2048).decode().strip()
            if len(data) == 5 and data.isnumeric():
                password = data
        return password
