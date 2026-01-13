
# Hostel Assist – Distributed Systems Lab

## Purpose
Single React frontend + multiple module implementations demonstrating different distributed communication models.  
React communicates **only with the Flask API Gateway** for Modules 1, 3, 4, 5. Module 2 (Java RMI) is wrapped by a **separate Java HTTP server**; React calls that Java HTTP server directly.

This README explains architecture, APIs, precise responsibilities, and explicit tasks for teammates.

---

## Quick architecture
```
React Frontend
      |
      |  HTTP (REST)          <-- React
      v
Flask API Gateway (wrapper.py)   <-- Hosts endpoints for Modules 1,3,4,5
      |
      +--> Module 1 (Python sockets)   - complaint 
      +--> Module 3 (Python REST)      - notices 
      +--> Module 4 (Python P2P agent) - peer 
      +--> Module 5 (Python shared mem) - mess 

React Frontend
      |
      |  HTTP (REST)
      v
Java HTTP wrapper -> Java RMI Module (Module 2)
```

---

## Folder structure (current)
```
.
├── .venv/
├── Module 1/
├── Module 2/
│   └── Rmi.java (plus a Java HTTP wrapper service to be added here)
├── Module 3/
│   └── main.py
├── Module 4/
│   └── main.py
├── Module 5/
│   └── main.py
├── wrapper.py
└── .gitignore
```
---

## API Endpoints (wrapper-exposed)
These are the endpoints React calls on the **Flask wrapper**.

### Complaints (Module 1 - socket server)
- `POST /api/complaints`
  - Body: `{ "room": "110", "category": "Water", "description": "No supply" }`
  - Wrapper: send JSON to socket server, return `{ "ack": true, "id": "<ticketId>" }`

### Rooms (Module 2 - Java HTTP wrapper)
- `GET /api/rooms/:roomNo`
  - Wrapper: **Java HTTP server** receives request and internally calls Java RMI, returns JSON `{ roomNo, occupants:[], warden:{name,contact} }`

### Notices (Module 3 - REST)
- `GET  /api/notices` → list of notices
- `POST /api/notices` → body `{ title, message, date }` to create notice

### P2P Resource Sharing (Module 4 - P2P agent)
- `GET  /api/peers`  
- `POST /api/p2p/upload` (multipart/form-data)  
- `GET  /api/p2p/download/:peerId/:fileName` → wrapper returns peer address or proxied stream

### Mess Feedback (Module 5 - Shared Memory)
- `POST /api/mess/:type`  where `type ∈ {good,avg,poor}`
- `GET  /api/mess` → `{ good: N, avg: M, poor: K }`

---

## What to implement — explicit tasks (per-module)


### Module 1 — Complaint (Python socket)
- Implement a TCP server `Module1/main.py`:
  - Accept multiple clients (threading or asyncio).
  - Request/response format: JSON lines (`\n` delimited).
  - Maintain `complaints = []` in memory; append `{id, room, category, desc, timestamp}`.
  - Return acknowledgement: `{ ack: true, id }`.
- Provide `Module1/test.py` to simulate client requests.
- Flask wrapper tasks:
  - Add endpoint `POST /api/complaints` that:
    - Validates payload.
    - Opens socket, sends JSON, reads ack, returns JSON to React.
- To-do checklist:
  - [ ] Define socket host/port in config.
  - [ ] Unit test for concurrency (≥ 5 clients).
  - [ ] Add optional `persistent.json` writer for checkpointing.

---

### Module 2 — Room Info (Java RMI + Java HTTP wrapper)
- Java RMI tasks:
  - Implement RMI interface with at least 2 remote methods (e.g., `getRoomDetails(roomNo)`, `listRooms()`).
  - In-memory `Map<Integer, RoomDetails>` populated with sample data.
- Java HTTP wrapper:
  - Create a small HTTP server (Jetty/Spark/embedded Tomcat) exposing `GET /api/rooms/:roomNo`.
  - On request, call RMI method and return JSON.
- To-do checklist:
  - [ ] RMI server + registry script.
  - [ ] Build/run instructions (`javac` & `java` or Maven/Gradle).
  - [ ] Integration test: HTTP wrapper → RMI returns sample result.

---

### Module 3 — Notice Board (Python REST)
- Implement a REST microservice (`Module3/main.py`) or keep logic callable by wrapper.
- In-memory `notices = []` with CRUD minimal (`GET`, `POST`).
- Wrapper behavior:
  - Either proxy React requests to Module3, or wrapper calls Module3 internal functions and returns results.
- Tasks:
  - [ ] Add validation for admin create route (simple flag).
  - [ ] Provide sample UI payloads and curl commands.

---

### Module 4 — P2P Resource Sharing (Python)
- Peer agent:
  - Each peer runs an HTTP server + transfer endpoint.
  - Maintain `peers` list (addresses + metadata).
- Wrapper responsibilities:
  - `GET /api/peers` returns peers discovered by wrapper or bootstrap node.
  - `POST /api/p2p/upload` registers file metadata and places file in local peer storage.
  - `GET /api/p2p/download/:peerId/:fileName` returns URL or proxies the file stream.
- Tasks:
  - [ ] Implement peer discovery (simple bootstrap server or multicast).
  - [ ] Support file chunking or streaming.
  - [ ] Add upload/download test scripts.

---

### Module 5 — Mess Feedback (Shared Memory)
- Use `multiprocessing` shared memory or OS shared segment.
- Protect counters with lock/semaphore.
- API:
  - `POST /api/mess/:type` increments counter atomically.
  - `GET /api/mess` reads totals.
- Tasks:
  - [ ] Implement safe concurrent access tests.
  - [ ] Add demo script that spawns multiple processes incrementing counters.

---

## Run order (recommended for demo)
1. Start Java RMI server (Module 2) and Java HTTP wrapper.
2. Start Module 1 socket server.
3. Start Module 3 REST service (if separate).
4. Start Module 4 peer agent(s) (at least 2 peers for demo).
5. Start Module 5 shared memory service (if separate).
6. Start Flask API Gateway (`wrapper.py`).
7. Start React frontend (development server or build served).

---

## Sample curl requests
```bash
# Submit complaint (wrapper forwards to socket server)
curl -X POST http://localhost:5000/api/complaints -H "Content-Type: application/json" \
  -d '{"room":"110","category":"Water","description":"No supply"}'

# Get room info (Java HTTP wrapper)
curl http://localhost:8080/api/rooms/110

# Get notices (via wrapper)
curl http://localhost:5000/api/notices

# Mess vote
curl -X POST http://localhost:5000/api/mess/good
```



