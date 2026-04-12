from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required

from ..decorators import roles_required
from ..models import ActivityLog

audit_bp = Blueprint("audit", __name__)


@audit_bp.get("/activity-logs")
@login_required
@roles_required("owner", "admin")
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(500).all()
    return render_template("audit/logs.html", logs=logs)
