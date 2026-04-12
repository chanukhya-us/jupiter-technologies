from __future__ import annotations

from datetime import UTC, datetime, timedelta

from flask import Blueprint, render_template
from flask_login import login_required

from ..constants import (
    CANDIDATE_STATUSES,
    JOB_STATUSES,
    SUBMISSION_STATUSES,
    TASK_STATUSES,
    TIMESHEET_STATUSES,
)
from ..extensions import db
from ..models import Candidate, Submission, Timesheet, Job, Employee, Task, ActivityLog
from ..utils import add_activity, build_donut_chart, csv_response

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/dashboard")
@login_required
def dashboard():
    today = datetime.now(tz=UTC).date()
    week_start = today - timedelta(days=today.weekday())
    metrics = {
        "total_candidates": Candidate.query.count(),
        "open_jobs": Job.query.filter_by(status="open").count(),
        "submissions_this_week": Submission.query.filter(
            db.func.date(Submission.submitted_at) >= week_start
        ).count(),
        "interviews_pending": Submission.query.filter_by(status="interview").count(),
        "active_employees": Employee.query.filter_by(status="active").count(),
        "pending_timesheets": Timesheet.query.filter_by(status="submitted").count(),
        "overdue_tasks": Task.query.filter(
            Task.due_date.isnot(None),
            Task.due_date < today,
            Task.status.in_(["open", "in_progress"]),
        ).count(),
    }
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    charts = {
        "candidate_status": build_donut_chart(
            [row[0] for row in db.session.query(Candidate.status).all()],
            preferred_order=CANDIDATE_STATUSES,
        ),
        "job_status": build_donut_chart(
            [row[0] for row in db.session.query(Job.status).all()],
            preferred_order=JOB_STATUSES,
        ),
        "submission_status": build_donut_chart(
            [row[0] for row in db.session.query(Submission.status).all()],
            preferred_order=SUBMISSION_STATUSES,
        ),
        "timesheet_status": build_donut_chart(
            [row[0] for row in db.session.query(Timesheet.status).all()],
            preferred_order=TIMESHEET_STATUSES,
        ),
        "task_status": build_donut_chart(
            [row[0] for row in db.session.query(Task.status).all()],
            preferred_order=TASK_STATUSES,
        ),
    }
    return render_template(
        "reports/dashboard.html",
        metrics=metrics,
        recent_logs=recent_logs,
        charts=charts,
    )


@reports_bp.get("/reports")
@login_required
def reports_home():
    return render_template("reports/index.html")


@reports_bp.get("/reports/candidates.csv")
@login_required
def candidates_csv():
    rows = [
        [
            str(c.id),
            c.full_name,
            c.email or "",
            c.phone or "",
            c.status,
            c.location or "",
            c.source or "",
            str(c.owner_user_id or ""),
        ]
        for c in Candidate.query.order_by(Candidate.created_at.desc()).all()
    ]
    add_activity("export", "report", None, "Exported candidates CSV")
    db.session.commit()
    return csv_response(
        "candidates.csv",
        ["id", "full_name", "email", "phone", "status", "location", "source", "owner_user_id"],
        rows,
    )


@reports_bp.get("/reports/submissions.csv")
@login_required
def submissions_csv():
    rows = [
        [
            str(s.id),
            str(s.candidate_id),
            str(s.job_id),
            s.status,
            s.submitted_at.isoformat() if s.submitted_at else "",
            str(s.recruiter_user_id),
        ]
        for s in Submission.query.order_by(Submission.created_at.desc()).all()
    ]
    add_activity("export", "report", None, "Exported submissions CSV")
    db.session.commit()
    return csv_response(
        "submissions.csv",
        ["id", "candidate_id", "job_id", "status", "submitted_at", "recruiter_user_id"],
        rows,
    )


@reports_bp.get("/reports/timesheets.csv")
@login_required
def timesheets_csv():
    rows = [
        [
            str(t.id),
            str(t.employee_id),
            t.week_start.isoformat(),
            t.week_end.isoformat(),
            str(t.total_hours),
            t.status,
        ]
        for t in Timesheet.query.order_by(Timesheet.created_at.desc()).all()
    ]
    add_activity("export", "report", None, "Exported timesheets CSV")
    db.session.commit()
    return csv_response(
        "timesheets.csv",
        ["id", "employee_id", "week_start", "week_end", "total_hours", "status"],
        rows,
    )
