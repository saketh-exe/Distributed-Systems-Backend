# Module 3 - Notice Board (Python REST)

## Overview
A REST microservice for managing hostel notices with CRUD operations and admin authentication.

## Features
- **Get All Notices**: Retrieve a list of all notices
- **Create Notice**: Add new notices (admin only)
- **Get Notice**: Retrieve a specific notice by ID
- **Delete Notice**: Remove a notice (admin only)
- **Health Check**: Service availability check

## Configuration
- **Host**: `0.0.0.0`
- **Port**: `5003`
- **Base URL**: `http://localhost:5003`
- **Admin Token**: `admin_secret_key_12345`

## API Endpoints

### 1. Get All Notices
```bash
curl -X GET http://localhost:5003/api/notices
```

**Response:**
```json
{
  "status": "success",
  "notices": [
    {
      "id": "uuid-string",
      "title": "Notice Title",
      "message": "Notice message content",
      "date": "2026-01-21T10:00:00",
      "created_at": "2026-01-21T10:00:00"
    }
  ]
}
```

### 2. Create Notice (Admin Only)
```bash
curl -X POST http://localhost:5003/api/notices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin_secret_key_12345" \
  -d '{
    "title": "Water Supply Notice",
    "message": "Water will be shut down for maintenance on Friday",
    "date": "2026-01-24T10:00:00"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Notice created successfully",
  "notice": {
    "id": "uuid-string",
    "title": "Water Supply Notice",
    "message": "Water will be shut down for maintenance on Friday",
    "date": "2026-01-24T10:00:00",
    "created_at": "2026-01-21T10:00:00"
  }
}
```

### 3. Get Specific Notice
```bash
curl -X GET http://localhost:5003/api/notices/uuid-string
```

**Response:**
```json
{
  "status": "success",
  "notice": {
    "id": "uuid-string",
    "title": "Water Supply Notice",
    "message": "Water will be shut down for maintenance on Friday",
    "date": "2026-01-24T10:00:00",
    "created_at": "2026-01-21T10:00:00"
  }
}
```

### 4. Delete Notice (Admin Only)
```bash
curl -X DELETE http://localhost:5003/api/notices/uuid-string \
  -H "Authorization: Bearer admin_secret_key_12345"
```

**Response:**
```json
{
  "status": "success",
  "message": "Notice deleted successfully"
}
```

### 5. Health Check
```bash
curl -X GET http://localhost:5003/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Module 3 - Notice Board"
}
```

## Running the Service

### Prerequisites
```bash
pip install flask flask-cors
```

### Start the Service
```bash
cd Module\ 3
python main.py
```

The service will start on `http://localhost:5003`

## Integration with Wrapper
The Flask API Gateway (`wrapper.py`) proxies requests to this service:
- `GET  /api/notices` → Module 3
- `POST /api/notices` → Module 3
- `GET  /api/notices/<id>` → Module 3
- `DELETE /api/notices/<id>` → Module 3

## Authentication
Admin operations require a bearer token in the `Authorization` header:
```
Authorization: Bearer admin_secret_key_12345
```

## Notes
- Notices are stored in-memory (not persisted)
- Each notice has a unique UUID
- Timestamps are in ISO 8601 format
- All responses include a status field indicating success or error
