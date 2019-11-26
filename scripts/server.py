import socket
import select
import json

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

print(f'Listening for connections on {IP}:{PORT}...')
commandCode = []


def receive_message(client_socket):
    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:

        if notified_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            if user["command"] == "register":
                sockets_list.append(client_socket)
                if user in clients:  # user already exists in the server
                    commandCode.append({"command": "ret_code", "code_no": "502"})
                    client_socket.send(commandCode)
                else:
                    clients[client_socket] = user # command has been accepted and user is registered
                    commandCode.append({"command": "ret_code", "code_no": "401"})
                    client_socket.send(commandCode)
                    print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                                    user['username'].decode('utf-8')))
            elif user["command"] != "deregister" and user["command"] != "msg":
                commandCode.append({"command": "ret_code", "code_no": "301"}) #unknown command
                client_socket.send(commandCode)
                print("Unknown command received")
        else:

            message = receive_message(notified_socket)

            if message is False or message["command"] == "deregister": #receive deregister command
                print('Closed connection from: {}'.format(clients[notified_socket]['username'].decode('utf-8')))
                commandCode.append({"command": "ret_code", "code_no": "401"})
                notified_socket.send(commandCode)

                sockets_list.remove(notified_socket)

                del clients[notified_socket]

                continue

            elif message["command"] == "msg": #receive msg command
                user = clients[notified_socket]
                print(f'Received message from {message["username"].decode("utf-8")}: {message["message"].decode("utf-8")}')
                commandCode.append({"command": "ret_code", "code_no": "401"})
                notified_socket.send(commandCode)

            elif message["command"] != "register":
                commandCode.append({"command": "ret_code", "code_no": "301"})  # unknown command
                client_socket.send(commandCode)
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)

        del clients[notified_socket]
