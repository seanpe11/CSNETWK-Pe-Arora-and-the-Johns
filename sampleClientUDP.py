import socket
import json


serverAddressPort   = ("127.0.0.1", 1234)

bufferSize          = 1024



# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



# Send to server using created UDP socket
register = json.dumps({"command":"register", "username":"user01"})
deregister = json.dumps({"command":"deregister", "username":"user01"})
msg = json.dumps({"command":"msg", "username":"user01", "message":"This is my message."})

UDPClientSocket.sendto(register.encode('utf-8'), serverAddressPort)
UDPClientSocket.sendto(msg.encode('utf-8'), serverAddressPort)
UDPClientSocket.sendto(deregister.encode('utf-8'), serverAddressPort)



msgFromServer = UDPClientSocket.recvfrom(bufferSize)



msg = "Message from Server {}".format(json.loads(msgFromServer[0])["code_no"])

print(msg)
