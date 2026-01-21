"""
P2P Bootstrap Server (Optional)
This server facilitates peer discovery for Module 4.
Run this if you want peers to automatically discover each other.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)

# In-memory peer registry
# Format: {peer_id: {peer_id, address, timestamp}}
peers = {}

# Configuration
PEER_TIMEOUT = 120  # Remove peer if not seen for 2 minutes


def cleanup_stale_peers():
    """Remove peers that haven't checked in recently."""
    global peers
    while True:
        threading.Event().wait(30)  # Check every 30 seconds
        
        now = datetime.now()
        stale_peers = []
        
        for peer_id, peer_data in peers.items():
            try:
                timestamp = datetime.fromisoformat(peer_data['timestamp'])
                age_seconds = (now - timestamp).total_seconds()
                
                if age_seconds > PEER_TIMEOUT:
                    stale_peers.append(peer_id)
            except Exception as e:
                print(f"Error checking peer {peer_id}: {e}")
        
        for peer_id in stale_peers:
            del peers[peer_id]
            print(f"[Bootstrap] Removed stale peer: {peer_id}")


@app.route('/register', methods=['POST'])
def register_peer():
    """Register or update a peer."""
    try:
        peer_data = request.get_json()
        
        if not peer_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        peer_id = peer_data.get('peer_id')
        if not peer_id:
            return jsonify({
                "status": "error",
                "message": "peer_id is required"
            }), 400
        
        # Update or register peer
        peers[peer_id] = {
            "peer_id": peer_id,
            "address": peer_data.get('address'),
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[Bootstrap] Peer registered: {peer_id} @ {peer_data.get('address')}")
        
        return jsonify({
            "status": "success",
            "message": "Peer registered successfully",
            "peer_count": len(peers)
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/peers', methods=['GET'])
def get_peers():
    """Get list of all registered peers."""
    try:
        peer_list = list(peers.values())
        
        return jsonify({
            "status": "success",
            "peer_count": len(peer_list),
            "peers": peer_list
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/peer/<peer_id>', methods=['GET'])
def get_peer(peer_id):
    """Get information about a specific peer."""
    try:
        if peer_id not in peers:
            return jsonify({
                "status": "error",
                "message": "Peer not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "peer": peers[peer_id]
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/unregister/<peer_id>', methods=['DELETE'])
def unregister_peer(peer_id):
    """Unregister a peer."""
    try:
        if peer_id in peers:
            del peers[peer_id]
            print(f"[Bootstrap] Peer unregistered: {peer_id}")
            return jsonify({
                "status": "success",
                "message": "Peer unregistered successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Peer not found"
            }), 404
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Get bootstrap server status."""
    return jsonify({
        "status": "healthy",
        "service": "P2P Bootstrap Server",
        "active_peers": len(peers),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "P2P Bootstrap Server"
    }), 200


if __name__ == '__main__':
    print("\n" + "="*50)
    print("P2P BOOTSTRAP SERVER")
    print("="*50)
    print(f"Starting on http://0.0.0.0:9000")
    print(f"Peer timeout: {PEER_TIMEOUT} seconds")
    print("="*50 + "\n")
    
    # Start background cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_stale_peers, daemon=True)
    cleanup_thread.start()
    
    app.run(host='0.0.0.0', port=9000, debug=True)
