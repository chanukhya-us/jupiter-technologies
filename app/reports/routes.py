from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta

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


def _recent_month_buckets(anchor: date, count: int) -> list[tuple[int, int, str]]:
    serial_month = anchor.year * 12 + anchor.month - 1
    buckets: list[tuple[int, int, str]] = []
    for offset in range(count - 1, -1, -1):
        serial_value = serial_month - offset
        year, month_index = divmod(serial_value, 12)
        month = month_index + 1
        label = datetime(year, month, 1, tzinfo=UTC).strftime("%b '%y")
        buckets.append((year, month, label))
    return buckets


def _recent_week_starts(anchor: date, count: int) -> list[date]:
    current_week_start = anchor - timedelta(days=anchor.weekday())
    return [current_week_start - timedelta(days=offset * 7) for offset in range(count - 1, -1, -1)]


def _month_serial(year: int, month: int) -> int:
    return year * 12 + month - 1


def _infer_month_bucket_count(anchor: date, datetimes: list[datetime | None]) -> int:
    serial_anchor = _month_serial(anchor.year, anchor.month)
    serial_values = []
    for raw_dt in datetimes:
        if not raw_dt:
            continue
        normalized = raw_dt.astimezone(UTC) if raw_dt.tzinfo else raw_dt
        serial_values.append(_month_serial(normalized.year, normalized.month))
    if not serial_values:
        return 6
    span = serial_anchor - min(serial_values) + 1
    return max(6, min(span, 18))


def _infer_week_bucket_count(anchor: date, week_starts: list[date | None]) -> int:
    current_week_start = anchor - timedelta(days=anchor.weekday())
    valid_starts = [week_start for week_start in week_starts if week_start is not None]
    if not valid_starts:
        return 8
    oldest = min(valid_starts)
    span = ((current_week_start - oldest).days // 7) + 1
    return max(8, min(span, 26))


def _count_datetimes_by_month(
    datetimes: list[datetime | None], month_buckets: list[tuple[int, int, str]]
) -> list[int]:
    counts: Counter[tuple[int, int]] = Counter()
    for raw_dt in datetimes:
        if not raw_dt:
            continue
        normalized = raw_dt.astimezone(UTC) if raw_dt.tzinfo else raw_dt
        counts[(normalized.year, normalized.month)] += 1
    return [counts[(year, month)] for year, month, _label in month_buckets]


def _series_total(*series: list[int] | list[float]) -> float:
    total = 0.0
    for bucket in series:
        total += sum(float(value or 0) for value in bucket)
    return total


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
    candidate_created_dates = [row[0] for row in db.session.query(Candidate.created_at).all()]
    submission_submitted_dates = [row[0] for row in db.session.query(Submission.submitted_at).all()]
    job_created_dates = [row[0] for row in db.session.query(Job.created_at).all()]

    month_bucket_count = _infer_month_bucket_count(
        today,
        candidate_created_dates + submission_submitted_dates + job_created_dates,
    )
    recent_month_buckets = _recent_month_buckets(today, count=month_bucket_count)
    month_labels = [label for _year, _month, label in recent_month_buckets]

    candidate_month_series = _count_datetimes_by_month(
        candidate_created_dates,
        recent_month_buckets,
    )
    submission_month_series = _count_datetimes_by_month(
        submission_submitted_dates,
        recent_month_buckets,
    )
    job_month_series = _count_datetimes_by_month(
        job_created_dates,
        recent_month_buckets,
    )

    raw_week_starts = [row[0] for row in db.session.query(Timesheet.week_start).all()]
    week_bucket_count = _infer_week_bucket_count(today, raw_week_starts)
    week_starts = _recent_week_starts(today, count=week_bucket_count)
    hours_by_week: defaultdict[date, float] = defaultdict(float)
    count_by_week: Counter[date] = Counter()
    for week_start, total_hours in db.session.query(Timesheet.week_start, Timesheet.total_hours).all():
        if not week_start:
            continue
        hours_by_week[week_start] += float(total_hours or 0)
        count_by_week[week_start] += 1

    week_labels = [week_start.strftime("%b %d") for week_start in week_starts]
    timesheet_hours_series = [round(hours_by_week.get(week_start, 0.0), 1) for week_start in week_starts]
    timesheet_count_series = [count_by_week.get(week_start, 0) for week_start in week_starts]

    graphs = {
        "hiring_activity": {
            "labels": month_labels,
            "datasets": [
                {
                    "type": "bar",
                    "label": "Candidates Added",
                    "data": candidate_month_series,
                    "backgroundColor": "rgba(15, 98, 254, 0.72)",
                    "borderColor": "#0f62fe",
                    "borderRadius": 10,
                    "borderWidth": 1,
                },
                {
                    "type": "bar",
                    "label": "Submissions Created",
                    "data": submission_month_series,
                    "backgroundColor": "rgba(255, 131, 43, 0.7)",
                    "borderColor": "#ff832b",
                    "borderRadius": 10,
                    "borderWidth": 1,
                },
                {
                    "type": "line",
                    "label": "Jobs Opened",
                    "data": job_month_series,
                    "backgroundColor": "rgba(2, 136, 209, 0.14)",
                    "borderColor": "#0288d1",
                    "pointBackgroundColor": "#0288d1",
                    "fill": False,
                    "tension": 0.34,
                    "pointRadius": 3,
                    "borderWidth": 2,
                },
            ],
            "totals": {
                "candidates": sum(candidate_month_series),
                "submissions": sum(submission_month_series),
                "jobs": sum(job_month_series),
            },
            "is_empty": _series_total(
                candidate_month_series,
                submission_month_series,
                job_month_series,
            )
            <= 0,
        },
        "timesheet_velocity": {
            "labels": week_labels,
            "datasets": [
                {
                    "type": "bar",
                    "label": "Hours Logged",
                    "data": timesheet_hours_series,
                    "backgroundColor": "rgba(15, 98, 254, 0.66)",
                    "borderColor": "#0f62fe",
                    "borderRadius": 10,
                    "borderWidth": 1,
                },
                {
                    "type": "line",
                    "label": "Timesheets",
                    "data": timesheet_count_series,
                    "backgroundColor": "rgba(36, 161, 72, 0.2)",
                    "borderColor": "#24a148",
                    "pointBackgroundColor": "#24a148",
                    "fill": False,
                    "yAxisID": "y1",
                    "tension": 0.34,
                    "pointRadius": 3,
                    "borderWidth": 2,
                },
            ],
            "totals": {
                "hours": round(sum(timesheet_hours_series), 1),
                "timesheets": sum(timesheet_count_series),
            },
            "is_empty": _series_total(timesheet_hours_series, timesheet_count_series) <= 0,
        },
        "submission_funnel": {
            "labels": charts["submission_status"]["labels"],
            "datasets": [
                {
                    "label": "Submission Stage Volume",
                    "data": charts["submission_status"]["values"],
                    "backgroundColor": charts["submission_status"]["colors"],
                    "borderColor": charts["submission_status"]["colors"],
                    "borderWidth": 1,
                    "borderRadius": 8,
                }
            ],
            "total": charts["submission_status"]["total"],
            "is_empty": charts["submission_status"]["total"] <= 0,
        },
    }
    return render_template(
        "reports/dashboard.html",
        metrics=metrics,
        recent_logs=recent_logs,
        charts=charts,
        graphs=graphs,
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



@reports_bp.get("/test-charts")
@login_required
def test_charts():
    """Test page to verify charts are working"""
    return render_template("test_charts_page.html")



@reports_bp.get("/chart-debug")
@login_required
def chart_debug():
    """Debug page to check chart data"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Get candidates data
    candidates = Candidate.query.all()
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=29)
    
    by_date = defaultdict(int)
    for candidate in candidates:
        if candidate.created_at.date() >= thirty_days_ago:
            by_date[candidate.created_at.date()] += 1
    
    trend_labels = []
    trend_data = []
    current_date = thirty_days_ago
    while current_date <= today:
        trend_labels.append(current_date.strftime("%m/%d"))
        trend_data.append(by_date.get(current_date, 0))
        current_date += timedelta(days=1)
    
    debug_info = {
        "total_candidates": len(candidates),
        "candidates_last_30_days": sum(trend_data),
        "trend_labels_count": len(trend_labels),
        "trend_data_count": len(trend_data),
        "trend_labels_sample": trend_labels[:5],
        "trend_data_sample": trend_data[:5],
        "is_empty": sum(trend_data) == 0,
    }
    
    return render_template("test_charts_page.html")
