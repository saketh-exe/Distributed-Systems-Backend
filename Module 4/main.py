"""
Module 4 - P2P Resource Sharing (Python)
A peer-to-peer file sharing system with peer discovery and file transfer.
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
import os
import uuid
import requests
from typing import List, Dict
import json
import threading
from io import BytesIO
import mimetypes

app = Flask(__name__)
CORS(app)

# Configuration
PEER_ID = str(uuid.uuid4())
PEER_PORT = 5004
BOOTSTRAP_SERVER = "http://localhost:9000"  # Bootstrap server for peer discovery
STORAGE_DIR = "peer_storage"

# Create storage directory if it doesn't exist
os.makedirs(STORAGE_DIR, exist_ok=True)

# In-memory peer registry
peers: Dict[str, Dict] = {}
local_files: List[Dict] = []

# Peer metadata
MY_PEER = {
    "peer_id": PEER_ID,
    "address": f"http://localhost:{PEER_PORT}",
    "timestamp": datetime.now().isoformat()
}


def register_with_bootstrap():
    """Register this peer with the bootstrap server."""
    try:
        response = requests.post(
            f"{BOOTSTRAP_SERVER}/register",
            json=MY_PEER,
            timeout=5
        )
        if response.status_code == 200:
            print(f"[P2P] Registered with bootstrap server: {response.json()}")
    except Exception as e:
        print(f"[P2P] Could not register with bootstrap server: {e}")


def discover_peers():
    """Discover other peers from the bootstrap server."""
    global peers
    try:
        response = requests.get(f"{BOOTSTRAP_SERVER}/peers", timeout=5)
        if response.status_code == 200:
            discovered = response.json().get("peers", [])
            for peer in discovered:
                if peer.get("peer_id") != PEER_ID:
                    peers[peer["peer_id"]] = peer
            print(f"[P2P] Discovered {len(peers)} peers")
    except Exception as e:
        print(f"[P2P] Could not discover peers: {e}")


@app.route('/api/peers', methods=['GET'])
def get_peers():
    """Get list of all discovered peers."""
    return jsonify({
        "status": "success",
        "peer_count": len(peers),
        "peers": list(peers.values()),
        "self": MY_PEER
    }), 200


@app.route('/api/p2p/upload', methods=['POST'])
def upload_file():
    """Upload a file and register it in peer network."""
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided"
            }), 400

        file = request.files['file']
        description = request.form.get('description', '')

        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400

        # Save file locally
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{file_ext}"
        filepath = os.path.join(STORAGE_DIR, saved_filename)

        file.save(filepath)
        file_size = os.path.getsize(filepath)

        # Register file metadata
        file_metadata = {
            "file_id": file_id,
            "original_name": file.filename,
            "saved_name": saved_filename,
            "size": file_size,
            "description": description,
            "peer_id": PEER_ID,
            "uploaded_at": datetime.now().isoformat(),
            "download_url": f"{MY_PEER['address']}/api/p2p/file/{file_id}"
        }

        local_files.append(file_metadata)

        # Notify other peers about the new file
        announce_file(file_metadata)

        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "file": file_metadata
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def announce_file(file_metadata):
    """Announce a new file to other peers."""
    for peer_id, peer in peers.items():
        try:
            requests.post(
                f"{peer['address']}/api/p2p/announce",
                json=file_metadata,
                timeout=5
            )
        except Exception as e:
            print(f"[P2P] Could not announce to peer {peer_id}: {e}")


@app.route('/api/p2p/announce', methods=['POST'])
def announce():
    """Receive announcement of files from other peers."""
    try:
        file_metadata = request.get_json()
        print(f"[P2P] File announced: {file_metadata.get('original_name')} from peer {file_metadata.get('peer_id')}")
        return jsonify({
            "status": "success",
            "message": "File announcement received"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/p2p/file/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a file from this peer."""
    try:
        # Find the file
        for file_meta in local_files:
            if file_meta['file_id'] == file_id:
                filepath = os.path.join(STORAGE_DIR, file_meta['saved_name'])
                if os.path.exists(filepath):
                    return send_file(
                        filepath,
                        as_attachment=True,
                        download_name=file_meta['original_name']
                    )
        
        return jsonify({
            "status": "error",
            "message": "File not found"
        }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/p2p/download/<peer_id>/<file_id>', methods=['GET'])
def proxy_download(peer_id, file_id):
    """Download a file from another peer (wrapper proxies the request)."""
    try:
        if peer_id not in peers:
            return jsonify({
                "status": "error",
                "message": "Peer not found"
            }), 404

        peer = peers[peer_id]
        download_url = f"{peer['address']}/api/p2p/file/{file_id}"

        # Proxy the download
        response = requests.get(download_url, timeout=30)
        if response.status_code == 200:
            return send_file(
                BytesIO(response.content),
                mimetype=response.headers.get('content-type', 'application/octet-stream'),
                as_attachment=True,
                download_name=response.headers.get('content-disposition', 'download')
            )
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to download from peer"
            }), response.status_code

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/p2p/files', methods=['GET'])
def list_local_files():
    """List all files available on this peer."""
    return jsonify({
        "status": "success",
        "peer_id": PEER_ID,
        "file_count": len(local_files),
        "files": local_files
    }), 200


@app.route('/api/p2p/status', methods=['GET'])
def status():
    """Get P2P system status."""
    return jsonify({
        "status": "success",
        "peer": MY_PEER,
        "peers_discovered": len(peers),
        "local_files": len(local_files),
        "storage_dir": STORAGE_DIR
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Module 4 - P2P Resource Sharing"}), 200


def start_background_discovery():
    """Periodically discover peers."""
    def discovery_loop():
        while True:
            discover_peers()
            threading.Event().wait(30)  # Wait 30 seconds before next discovery

    thread = threading.Thread(target=discovery_loop, daemon=True)
    thread.start()


if __name__ == '__main__':
    # Register and discover peers
    register_with_bootstrap()
    start_background_discovery()
    
    app.run(host='0.0.0.0', port=PEER_PORT, debug=True)
