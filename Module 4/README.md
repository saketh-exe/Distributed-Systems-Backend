# Module 4 - P2P Resource Sharing

## Overview
A peer-to-peer file sharing system with peer discovery, file upload/download, and distributed storage.

## Features
- **Peer Discovery**: Register and discover peers via bootstrap server
- **File Upload**: Upload files to the P2P network
- **File Download**: Download files from peers
- **File Announcements**: Notify other peers about new files
- **Peer Status**: View peer information and storage statistics

## Configuration
- **Peer Port**: `5004`
- **Peer ID**: Auto-generated UUID
- **Base URL**: `http://localhost:5004`
- **Bootstrap Server**: `http://localhost:9000` (default)
- **Storage Directory**: `peer_storage/`

## Architecture

### Peer Registration
1. Each peer registers with a bootstrap server
2. Peers periodically discover other peers (every 30 seconds)
3. File announcements are sent to discovered peers

### File Transfer
- Files are stored locally in `peer_storage/`
- Each file gets a unique ID
- Download requests can be proxied through other peers
- Support for streaming large files

## API Endpoints

### 1. Get All Peers
```bash
curl -X GET http://localhost:5004/api/peers
```

**Response:**
```json
{
  "status": "success",
  "peer_count": 2,
  "peers": [
    {
      "peer_id": "uuid-peer-1",
      "address": "http://localhost:5004",
      "timestamp": "2026-01-21T10:00:00"
    }
  ],
  "self": {
    "peer_id": "uuid-peer-current",
    "address": "http://localhost:5004",
    "timestamp": "2026-01-21T10:00:00"
  }
}
```

### 2. Upload File
```bash
curl -X POST http://localhost:5004/api/p2p/upload \
  -F "file=@/path/to/file.pdf" \
  -F "description=Important document"
```

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "file": {
    "file_id": "uuid-file",
    "original_name": "file.pdf",
    "saved_name": "uuid-file.pdf",
    "size": 1024000,
    "description": "Important document",
    "peer_id": "uuid-peer",
    "uploaded_at": "2026-01-21T10:00:00",
    "download_url": "http://localhost:5004/api/p2p/file/uuid-file"
  }
}
```

### 3. Download File from Peer
```bash
curl -X GET http://localhost:5004/api/p2p/download/peer-uuid/file-uuid \
  -o downloaded_file.pdf
```

### 4. Direct File Download
```bash
curl -X GET http://localhost:5004/api/p2p/file/file-uuid \
  -o downloaded_file.pdf
```

### 5. Announce File
```bash
curl -X POST http://localhost:5004/api/p2p/announce \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uuid-file",
    "original_name": "document.pdf",
    "size": 1024000,
    "peer_id": "uuid-peer",
    "uploaded_at": "2026-01-21T10:00:00"
  }'
```

### 6. List Local Files
```bash
curl -X GET http://localhost:5004/api/p2p/files
```

**Response:**
```json
{
  "status": "success",
  "peer_id": "uuid-peer",
  "file_count": 3,
  "files": [
    {
      "file_id": "uuid-file-1",
      "original_name": "document.pdf",
      "size": 1024000,
      "description": "Important doc",
      "uploaded_at": "2026-01-21T10:00:00",
      "download_url": "http://localhost:5004/api/p2p/file/uuid-file-1"
    }
  ]
}
```

### 7. P2P System Status
```bash
curl -X GET http://localhost:5004/api/p2p/status
```

**Response:**
```json
{
  "status": "success",
  "peer": {
    "peer_id": "uuid-peer",
    "address": "http://localhost:5004",
    "timestamp": "2026-01-21T10:00:00"
  },
  "peers_discovered": 2,
  "local_files": 3,
  "storage_dir": "peer_storage"
}
```

### 8. Health Check
```bash
curl -X GET http://localhost:5004/health
```

## Running a Peer

### Prerequisites
```bash
pip install flask flask-cors requests
```

### Start a Single Peer
```bash
cd Module\ 4
python main.py
```

The peer will start on `http://localhost:5004`

### Run Multiple Peers (Different Ports)
Edit `main.py` and change `PEER_PORT` before running:

**Peer 1:**
```bash
PEER_PORT=5004 python main.py
```

**Peer 2:**
```bash
PEER_PORT=5005 python main.py
```

## Bootstrap Server (Optional)

If you want to run a bootstrap server for peer discovery:

```python
# bootstrap_server.py
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

peers = {}

@app.route('/register', methods=['POST'])
def register():
    peer = request.get_json()
    peers[peer['peer_id']] = peer
    return jsonify({"status": "registered"}), 200

@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify({"peers": list(peers.values())}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
```

Run with: `python bootstrap_server.py`

## Integration with Wrapper
The Flask API Gateway (`wrapper.py`) proxies requests to this service:
- `GET  /api/peers` → Module 4
- `POST /api/p2p/upload` → Module 4
- `GET  /api/p2p/download/:peerId/:fileName` → Module 4
- `GET  /api/p2p/files` → Module 4
- `GET  /api/p2p/status` → Module 4

## Storage
- Files are stored in `peer_storage/` directory
- Each file is saved with its UUID as filename
- Original filename is preserved in metadata

## File Lifecycle
1. User uploads file → saved locally + metadata registered
2. File announcement sent → other peers notified
3. Other peers can download → via proxy or direct

## Notes
- Peers auto-discover every 30 seconds
- Files are stored in-memory metadata (not persisted)
- Storage directory is created automatically
- Support for any file type
- Concurrent uploads and downloads supported
