import socket
import json

HOST = "0.0.0.0"
PORT = 3000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

complaint = {
    "type": "getcomplaints",
    "name": "sak",
    "issue": "Internet not working",
    "priority": "high",
    "status": "open"
}

payload = json.dumps(complaint).encode()

client.sendall(payload)

response = client.recv(1024)
print("Server response:", response.decode())

client.close()
