"""
Module 3 - Notice Board (Python REST)
A REST microservice for managing hostel notices.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from typing import List, Dict
import uuid

app = Flask(__name__)
CORS(app)

# In-memory storage for notices
notices: List[Dict] = []

# Admin token for create operations (simple security)
ADMIN_TOKEN = "admin_secret_key_12345"


@app.route('/api/notices', methods=['GET'])
def get_notices():
    """Retrieve all notices."""
    return jsonify({
        "status": "success",
        "notices": notices
    }), 200


@app.route('/api/notices', methods=['POST'])
def create_notice():
    """Create a new notice (admin only)."""
    try:
        # Validate admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f"Bearer {ADMIN_TOKEN}":
            return jsonify({
                "status": "error",
                "message": "Unauthorized - invalid or missing admin token"
            }), 401

        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400

        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        date = data.get('date')

        if not title or not message:
            return jsonify({
                "status": "error",
                "message": "Title and message are required"
            }), 400

        # Create notice object
        notice = {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "date": date or datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }

        notices.append(notice)

        return jsonify({
            "status": "success",
            "message": "Notice created successfully",
            "notice": notice
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/notices/<notice_id>', methods=['GET'])
def get_notice(notice_id):
    """Retrieve a specific notice by ID."""
    for notice in notices:
        if notice['id'] == notice_id:
            return jsonify({
                "status": "success",
                "notice": notice
            }), 200
    
    return jsonify({
        "status": "error",
        "message": "Notice not found"
    }), 404


@app.route('/api/notices/<notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    """Delete a notice (admin only)."""
    try:
        # Validate admin token
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != f"Bearer {ADMIN_TOKEN}":
            return jsonify({
                "status": "error",
                "message": "Unauthorized - invalid or missing admin token"
            }), 401

        global notices
        notices = [n for n in notices if n['id'] != notice_id]
        
        return jsonify({
            "status": "success",
            "message": "Notice deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Module 3 - Notice Board"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
