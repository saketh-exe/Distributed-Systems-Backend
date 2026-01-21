from flask import Flask, jsonify, request, send_file
import socket
import json
from flask_cors import CORS
from flask_socketio import SocketIO , emit
from module5 import read_state, write_state
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")


# Configuration for the target socket server
TARGET_HOST = "0.0.0.0"
TARGET_PORT = 3000

# Configuration for Module 3 (Notice Board)
MODULE3_HOST = "localhost"
MODULE3_PORT = 5003
MODULE3_BASE_URL = f"http://{MODULE3_HOST}:{MODULE3_PORT}"

# Configuration for Module 4 (P2P Resource Sharing)
MODULE4_HOST = "localhost"
MODULE4_PORT = 5004
MODULE4_BASE_URL = f"http://{MODULE4_HOST}:{MODULE4_PORT}"

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


# ============================================================================
# MODULE 3 - NOTICE BOARD ENDPOINTS
# ============================================================================

@app.route('/api/notices', methods=['GET'])
def get_notices():
    """Retrieve all notices from Module 3."""
    try:
        response = requests.get(
            f"{MODULE3_BASE_URL}/api/notices",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve notices: {str(e)}"
        }), 503


@app.route('/api/notices', methods=['POST'])
def create_notice():
    """Create a new notice (forward to Module 3)."""
    try:
        data = request.get_json()
        auth_header = request.headers.get('Authorization')
        
        headers = {}
        if auth_header:
            headers['Authorization'] = auth_header
        
        response = requests.post(
            f"{MODULE3_BASE_URL}/api/notices",
            json=data,
            headers=headers,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create notice: {str(e)}"
        }), 503


@app.route('/api/notices/<notice_id>', methods=['GET'])
def get_notice(notice_id):
    """Retrieve a specific notice."""
    try:
        response = requests.get(
            f"{MODULE3_BASE_URL}/api/notices/{notice_id}",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve notice: {str(e)}"
        }), 503


@app.route('/api/notices/<notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    """Delete a notice."""
    try:
        auth_header = request.headers.get('Authorization')
        headers = {}
        if auth_header:
            headers['Authorization'] = auth_header
        
        response = requests.delete(
            f"{MODULE3_BASE_URL}/api/notices/{notice_id}",
            headers=headers,
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete notice: {str(e)}"
        }), 503


# ============================================================================
# MODULE 4 - P2P RESOURCE SHARING ENDPOINTS
# ============================================================================

@app.route('/api/peers', methods=['GET'])
def get_peers():
    """Get list of all discovered peers."""
    try:
        response = requests.get(
            f"{MODULE4_BASE_URL}/api/peers",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve peers: {str(e)}"
        }), 503


@app.route('/api/p2p/upload', methods=['POST'])
def upload_p2p_file():
    """Upload a file to P2P network."""
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided"
            }), 400

        files = {'file': request.files['file']}
        data = {'description': request.form.get('description', '')}

        response = requests.post(
            f"{MODULE4_BASE_URL}/api/p2p/upload",
            files=files,
            data=data,
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to upload file: {str(e)}"
        }), 503


@app.route('/api/p2p/download/<peer_id>/<file_id>', methods=['GET'])
def download_p2p_file(peer_id, file_id):
    """Download a file from a peer."""
    try:
        response = requests.get(
            f"{MODULE4_BASE_URL}/api/p2p/download/{peer_id}/{file_id}",
            timeout=30,
            stream=True
        )
        if response.status_code == 200:
            return send_file(
                response.raw,
                mimetype=response.headers.get('content-type', 'application/octet-stream'),
                as_attachment=True
            )
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to download file: {str(e)}"
        }), 503


@app.route('/api/p2p/files', methods=['GET'])
def list_p2p_files():
    """List all files available on a peer."""
    try:
        response = requests.get(
            f"{MODULE4_BASE_URL}/api/p2p/files",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve files: {str(e)}"
        }), 503


@app.route('/api/p2p/status', methods=['GET'])
def get_p2p_status():
    """Get P2P system status."""
    try:
        response = requests.get(
            f"{MODULE4_BASE_URL}/api/p2p/status",
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve P2P status: {str(e)}"
        }), 503
