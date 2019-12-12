import socket
import select
import json

bufferSize          = 1024
HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))



print(f'Listening for connections on {IP}:{PORT}...')
registeredUsers = []

# 201 incomplete 301 unknown 401 accepted 501 not registered 502 exists
def return_message(jsonDICT):
    ret_dict = {
        "command":"ret_code",
        "code_no":301,
    }
    if (jsonDICT["command"] == "register"):
        ret_dict["code_no"] = 201 #missing userparamater
        if (jsonDICT["username"] != "" and "username" in jsonDICT):
            ret_dict["code_no"] = 401 #user is registered with username
            if (jsonDICT["username"] in registeredUsers):
                ret_dict["code_no"] = 502

    if (jsonDICT["command"] == "deregister"):
        ret_dict["code_no"] = 201 #missing userparameter
        if (jsonDICT["username"] in registeredUsers):
            ret_dict["code_no"] = 401 # user is deregistered from server
        else:
            ret_dict["code_no"] = 501 #user was not found in server, can't deregister

    if (jsonDICT["command"] == "msg"):
        ret_dict["code_no"] = 201 #missing message and username parameter
        if ('message' in jsonDICT): # has message parameter
            if ('username' in jsonDICT): # has username parameter
                if (jsonDICT["username"] in registeredUsers): #user is registered in server
                    ret_dict["code_no"] = 401
                else: #user has to be registered first
                    ret_dict["code_no"] = 501

    return ret_dict

# Listen for incoming datagrams
while(True):

    bytesAddressPair = server_socket.recvfrom(bufferSize)

    data = json.loads(bytesAddressPair[0])
    address = bytesAddressPair[1]

    response = return_message(data)


    if response["code_no"] == 401: #check if data is valid

        if data["command"] == "register":
            bulletinBoard = "Registered user from {} with username {}".format(address, data["username"])
            registeredUsers.append(data["username"])

        if data["command"] == "deregister":
            bulletinBoard = "Deregistered user {} from server. If {} wants to post messages, please register them again.".format(address, data["username"])
            registeredUsers.remove(data["username"])

        if data["command"] == "msg":
            bulletinBoard = "Message from {}@{}: {}".format(data["username"], address, data["message"])

    elif response["code_no"] == 501:
        bulletinBoard = "User not registered. Did you register this user?"

    elif response["code_no"] == 201:
        bulletinBoard = "Missing parameters. Try again."

    else:
        bulletinBoard = "Unknown command. Try again."

    print(bulletinBoard)

    # Sending a reply to client
    server_socket.sendto(json.dumps(response).encode("utf-8"), address)
