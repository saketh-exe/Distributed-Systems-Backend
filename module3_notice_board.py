"""Notice Board (Module 3) - reusable Flask blueprint.

This file exists so both:
- Module 3 can run standalone (via Module 3/main.py), and
- wrapper.py can mount the same endpoints without proxying to a separate server.

Endpoints (mounted at root):
- GET    /api/notices
- POST   /api/notices               (admin only)
- GET    /api/notices/<notice_id>
- DELETE /api/notices/<notice_id>   (admin only)
- GET    /health
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from flask import Blueprint, jsonify, request


DEFAULT_ADMIN_TOKEN = "admin_secret_key_12345"


def create_notice_board_blueprint(
    *,
    admin_token: str = DEFAULT_ADMIN_TOKEN,
    initial_notices: Optional[List[Dict]] = None,
) -> Blueprint:
    """Create a Blueprint implementing the notice-board REST API.

    Notes:
    - Storage is in-memory per-process.
    - This function is safe to call once; each call creates its own isolated state.
    """

    bp = Blueprint("module3_notice_board", __name__)

    notices: List[Dict] = list(initial_notices or [])

    def _is_admin_request() -> bool:
        auth_header = request.headers.get("Authorization")
        return bool(auth_header) and auth_header == f"Bearer {admin_token}"

    @bp.get("/api/notices")
    def get_notices():
        return jsonify({"status": "success", "notices": notices}), 200

    @bp.post("/api/notices")
    def create_notice():
        if not _is_admin_request():
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized - invalid or missing admin token",
                    }
                ),
                401,
            )

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data provided"}), 400

        title = (data.get("title") or "").strip()
        message = (data.get("message") or "").strip()
        date = data.get("date")

        if not title or not message:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Title and message are required",
                    }
                ),
                400,
            )

        notice = {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "date": date or datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
        }

        notices.append(notice)

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Notice created successfully",
                    "notice": notice,
                }
            ),
            201,
        )

    @bp.get("/api/notices/<notice_id>")
    def get_notice(notice_id: str):
        for notice in notices:
            if notice.get("id") == notice_id:
                return jsonify({"status": "success", "notice": notice}), 200

        return jsonify({"status": "error", "message": "Notice not found"}), 404

    @bp.delete("/api/notices/<notice_id>")
    def delete_notice(notice_id: str):
        if not _is_admin_request():
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Unauthorized - invalid or missing admin token",
                    }
                ),
                401,
            )

        before = len(notices)
        notices[:] = [n for n in notices if n.get("id") != notice_id]
        after = len(notices)

        if after == before:
            return jsonify({"status": "error", "message": "Notice not found"}), 404

        return jsonify({"status": "success", "message": "Notice deleted successfully"}), 200

    @bp.get("/health")
    def health():
        return jsonify({"status": "healthy", "service": "Module 3 - Notice Board"}), 200

    return bp
