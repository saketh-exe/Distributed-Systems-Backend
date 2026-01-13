import socket
import threading
import json
import os
HOST = "0.0.0.0"
PORT = 3000


# Lock for file operations to prevent race conditions
file_lock = threading.Lock()

def Handel(conn,addr):
    print("Request from ", addr)
    try:
        data = conn.recv(1024)
        if data:
            complaint = dict(json.loads(data.decode()))
            if(complaint["type"] == "getcomplaints"):
                with file_lock:
                    try:
                        path = "persistent.json"
                        with open(path, "r") as f:
                            db = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        db = {"complaints": []}
                response = json.dumps(db).encode()
                conn.sendall(response)
                return

            id = hash(data.decode())
            with file_lock:
                try:
                    path = "persistent.json"
                    with open(path, "r") as f:
                        db = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    db = {"complaints": []}
                complaint["id"] = id
                print(complaint["type"])
                complaint.pop("type", None)
                db["complaints"].append(complaint)
                with open(path, "w") as f:
                    json.dump(db, f, indent=4)
                
                    
            conn.sendall(b"1")
    except Exception as e:
        conn.sendall(b"0")
        print(f"some error has occured: {e}")
    finally:
        conn.close()
        print("diconnected from ", addr)

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind((HOST,PORT))
server.listen()

print("Listening on port ", PORT)


while True:
    conn,addr = server.accept()
    threading.Thread(
        target=Handel,
        args= (conn,addr),
        daemon=True
    ).start()