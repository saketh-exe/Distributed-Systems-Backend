from flask import Flask, jsonify, request
import socket
import json
from flask_cors import CORS
from flask_socketio import SocketIO , emit
from module5 import read_state, write_state

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")


# Configuration for the target socket server
TARGET_HOST = "0.0.0.0"
TARGET_PORT = 3000

@app.route('/send-complaint', methods=['POST'])
def send_complaint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        # 1. Create a socket connection to the other server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((TARGET_HOST, TARGET_PORT))

        # 2. Prepare the data
        complaint = {
            "type": "sendcomplaint",
            "name": data.get("name", "Unknown"),
            "issue": data.get("issue", "No issue provided"),
            "priority": data.get("priority", "low"),
            "category": data.get("category", "general"),
            "status": "open"
        }
        
        payload = json.dumps(complaint).encode()

        # 3. Send data
        client.sendall(payload)

        # 4. Receive response
        response = client.recv(1024)
        decoded_response = response.decode()
        
        # 5. Close connection
        client.close()
        # 6. Return the response to the HTTP client (browser/Postman)
        return jsonify({
            "status": "success",
            "server_response": decoded_response
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/get-complaints', methods=['GET'])
def get_complaints():
    try:
        # 1. Create a socket connection to the other server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((TARGET_HOST, TARGET_PORT))

        # 2. Prepare the data
        request_data = {
            "type": "getcomplaints"
        }
        
        payload = json.dumps(request_data).encode()

        # 3. Send data
        client.sendall(payload)

        # 4. Receive response
        response = client.recv(4096)  # Increased buffer size for larger data
        decoded_response = response.decode()
        
        # 5. Close connection
        client.close()

        # 6. Parse the JSON response from the socket server
        complaints_data = json.loads(decoded_response)

        # 7. Return the complaints data to the HTTP client (browser/Postman)
        return jsonify({
            "status": "success",
            "complaints": complaints_data.get("complaints", [])
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/prefs',methods= ['GET'])
def get_prefs():
    return jsonify(read_state())

@app.route('/prefs',methods= ['POST'])
def set_prefs():
    data = request.get_json()
    good = data.get('good',0)
    mid = data.get('mid',0)
    bad = data.get('bad',0)
    write_state(good,mid,bad)
    state = read_state()
    socketio.emit('prefs_update',state)
    return jsonify(state)
    
@socketio.on('connect')
def handle_connect():
    state = read_state()
    emit('prefs_update',state)





