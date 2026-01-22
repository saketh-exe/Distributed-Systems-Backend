# Distributed Systems Backend - Multi-Module Architecture

A distributed backend system implementing multiple communication paradigms including socket programming, RMI, HTTP, WebSocket, and REST APIs.

## 🏗️ System Architecture

This project consists of 5 modules working together to provide a comprehensive distributed system:

```
┌─────────────────────────────────────────────────────────────┐
│                    Wrapper (Port 3001)                      │
│                   Main API Gateway                          │
│              Flask + SocketIO + Gunicorn                    │
└───────────┬─────────────────────────────────────────────────┘
            │
            ├──► Module 1 (Port 3000) - Complaint Management
            │    Socket Server (TCP)
            │
            ├──► Module 2 (Ports 1099, 3002) - Hostel Room Mgmt
            │    RMI + HTTP Gateway
            │
            ├──► Module 3 (Integrated) - Notice Board
            │    REST API (part of Wrapper)
            │
            ├──► Module 4 (Port 8765) - WebRTC Signaling
            │    WebSocket Server
            │
            └──► Module 5 (Integrated) - Preference State
                 Shared Memory (part of Wrapper)
```

## 📦 Modules Overview

### **Module 1: Complaint Management System**
- **Protocol**: TCP Socket Server
- **Port**: `3000`
- **Technology**: Python (socket programming)
- **Functionality**: 
  - Handles complaint submissions from users
  - Stores complaints in `persistent.json`
  - Provides complaint retrieval functionality
  - Thread-safe file operations with locks
- **Endpoints**:
  - Send complaint (POST via socket)
  - Get all complaints (GET via socket)

### **Module 2: Hostel Room Management**
- **Protocols**: Java RMI + HTTP
- **Ports**: 
  - `1099` - RMI Registry
  - `3002` - HTTP Gateway
- **Technology**: Java (RMI, HttpServer)
- **Components**:
  1. **RMI Registry** (`port 1099`): Service discovery and binding
  2. **RMI Server**: Core business logic for hostel room operations
  3. **HTTP Gateway** (`port 3002`): HTTP-to-RMI bridge with CORS support
- **Functionality**:
  - Get room details by room number
  - Add residents to rooms
  - Get all residents in a room
  - HTTP API wrapping RMI calls
- **Sample Request**: 
  ```bash
  GET http://localhost:3002/room?no=101
  ```

### **Module 3: Notice Board (Integrated)**
- **Protocol**: REST API
- **Port**: `3001` (part of Wrapper)
- **Technology**: Python (Flask Blueprint)
- **Functionality**:
  - Create, read, and delete notices
  - Admin-only operations with Bearer token authentication
  - In-memory storage per process
- **Endpoints**:
  - `GET /api/notices` - Get all notices
  - `POST /api/notices` - Create notice (admin only)
  - `GET /api/notices/<id>` - Get specific notice
  - `DELETE /api/notices/<id>` - Delete notice (admin only)
  - `GET /health` - Health check

### **Module 4: WebRTC Signaling Server**
- **Protocol**: WebSocket
- **Port**: `8765`
- **Technology**: Python (websockets, asyncio)
- **Functionality**:
  - Peer-to-peer signaling for WebRTC connections
  - Peer registration and discovery
  - SDP offer/answer exchange
  - ICE candidate exchange
  - Real-time peer list broadcasting
- **Message Types**:
  - `register` - Register new peer
  - `signal` - Forward WebRTC signals
  - `peers_update` - Broadcast available peers
  - `ping/pong` - Keep-alive mechanism

### **Module 5: Preference State Manager (Integrated)**
- **Protocol**: Shared Memory IPC
- **Port**: `3001` (part of Wrapper)
- **Technology**: Python (multiprocessing.shared_memory)
- **Functionality**:
  - Manages global preference state (good/mid/bad counts)
  - Uses shared memory for inter-process communication
  - Real-time updates via SocketIO
- **Endpoints**:
  - `GET /prefs` - Get current preferences
  - `POST /prefs` - Update preferences

### **Wrapper: Main API Gateway**
- **Protocol**: HTTP + WebSocket (SocketIO)
- **Port**: `3001`
- **Technology**: Python (Flask, SocketIO, Gunicorn, Eventlet)
- **Functionality**:
  - Central entry point for all client requests
  - Routes requests to appropriate modules
  - Provides unified REST API
  - Real-time updates via WebSocket
  - CORS enabled for cross-origin requests
- **Key Endpoints**:
  - `POST /send-complaint` - Forward to Module 1
  - `GET /get-complaints` - Forward to Module 1
  - `GET /api/notices` - Module 3 endpoints
  - `POST /api/notices` - Module 3 endpoints
  - `GET /prefs` - Module 5 preferences
  - `POST /prefs` - Update preferences

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for Modules 1, 4, Wrapper)
- **Java JDK 8+** (for Module 2)
- **Linux/Unix** environment (for the start script)

### Installation

1. **Clone the repository** (if applicable)
   ```bash
   cd /path/to/projectBack
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the start script**
   ```bash
   ./start.sh
   ```

The script will automatically:
- Start Module 1 (Complaints Socket Server)
- Compile Java files for Module 2
- Start RMI Registry
- Start RMI Server
- Start HTTP Gateway
- Start Module 4 (WebRTC WebSocket Server)
- Start Wrapper (Main API with Gunicorn)

Each module runs in a separate terminal tab for easy monitoring.

### Manual Start (Alternative)

If you prefer to start modules manually:

**Terminal 1 - Module 1:**
```bash
cd "Module 1"
python3 main.py
```

**Terminal 2 - Module 2 (Compile):**
```bash
cd "Module 2"
javac *.java
```

**Terminal 3 - Module 2 (RMI Registry):**
```bash
cd "Module 2"
rmiregistry 1099
```

**Terminal 4 - Module 2 (RMI Server):**
```bash
cd "Module 2"
java RMIServer
```

**Terminal 5 - Module 2 (HTTP Gateway):**
```bash
cd "Module 2"
java HttpRmiGateway
```

**Terminal 6 - Module 4:**
```bash
cd "Module 4"
python3 main.py
```

**Terminal 7 - Wrapper:**
```bash
gunicorn -k eventlet -w 1 wrapper:app --bind 0.0.0.0:3001
```

## 🔌 Port Reference

| Module | Service | Port | Protocol |
|--------|---------|------|----------|
| Module 1 | Complaint Socket Server | 3000 | TCP Socket |
| Module 2 | RMI Registry | 1099 | Java RMI |
| Module 2 | HTTP Gateway | 3002 | HTTP |
| Module 3 | Notice Board API | 3001 | HTTP (Integrated) |
| Module 4 | WebRTC Signaling | 8765 | WebSocket |
| Module 5 | Preference State | 3001 | HTTP (Integrated) |
| **Wrapper** | **Main API Gateway** | **3001** | **HTTP + WebSocket** |

## 📝 API Examples

### Send a Complaint
```bash
curl -X POST http://localhost:3001/send-complaint \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "issue": "AC not working",
    "priority": "high",
    "category": "maintenance"
  }'
```

### Get Room Details
```bash
curl http://localhost:3002/room?no=101
```

### Get All Notices
```bash
curl http://localhost:3001/api/notices
```

### Create Notice (Admin)
```bash
curl -X POST http://localhost:3001/api/notices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin_secret_key_12345" \
  -d '{
    "title": "Maintenance Notice",
    "content": "Water supply will be off from 2-4 PM"
  }'
```

### Get Preferences
```bash
curl http://localhost:3001/prefs
```

### Update Preferences
```bash
curl -X POST http://localhost:3001/prefs \
  -H "Content-Type: application/json" \
  -d '{"good": 10, "mid": 5, "bad": 2}'
```

## 🛠️ Technology Stack

- **Python**: Flask, Flask-SocketIO, Gunicorn, Eventlet, WebSockets, AsyncIO
- **Java**: RMI, HttpServer, Sockets
- **Communication**: TCP Sockets, HTTP, WebSockets, RMI, Shared Memory
- **Data Format**: JSON
- **Server**: Gunicorn with Eventlet worker

## 📂 Project Structure

```
projectBack/
├── Module 1/
│   ├── main.py              # Complaint socket server
│   └── persistent.json      # Complaint storage
├── Module 2/
│   ├── HostelRoom.java      # Data class
│   ├── HostelService.java   # RMI interface
│   ├── HostelServiceImpl.java  # RMI implementation
│   ├── RMIServer.java       # RMI server
│   └── HttpRmiGateway.java  # HTTP to RMI bridge
├── Module 4/
│   └── main.py              # WebRTC signaling server
├── wrapper.py               # Main API gateway
├── module3_notice_board.py  # Notice board blueprint
├── module5.py               # Preference state manager
├── start.sh                 # Startup script
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🔒 Security Notes

- Module 3 uses a simple Bearer token for admin authentication
- Default admin token: `admin_secret_key_12345` (change in production)
- CORS is enabled on all HTTP services for development
- No encryption on socket connections (use SSL/TLS in production)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3000
# Kill process
kill -9 <PID>
```

### Java Compilation Errors
```bash
# Ensure Java is installed
java -version
javac -version
```

### Python Module Not Found
```bash
# Reinstall requirements
pip install -r requirements.txt
```

### RMI Server Not Binding
Ensure `rmiregistry` is started before `RMIServer`

## 📄 License

This is an educational project for a Distributed Systems course.

## 👥 Contributing

This project is part of coursework for Semester 6 Distributed Systems.
