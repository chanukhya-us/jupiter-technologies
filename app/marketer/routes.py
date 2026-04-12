from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import MARKETER_JOB_TYPES, MARKETER_LOG_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import MarketerDailyLog, MarketerNotification, MarketerProfile, Role, User
from ..utils import add_activity, build_donut_chart, csv_response, parse_date
from .service import (
    can_marketer_edit_date,
    can_marketer_edit_log,
    ensure_marketer_profile,
    ensure_profiles_for_all_marketers,
    format_workdays_mask,
    local_now_for_profile,
    parse_local_time,
    parse_reminder_times,
    parse_workdays_mask,
    serialize_reminder_times,
    submit_status_for_log,
)

marketer_activity_bp = Blueprint("marketer_activity", __name__)


@marketer_activity_bp.get("/marketer-activity")
@login_required
@roles_required("owner", "admin", "marketer")
def home():
    return redirect(url_for("marketer_activity.list_logs"))


@marketer_activity_bp.get("/marketer-activity/logs")
@login_required
@roles_required("owner", "admin", "marketer")
def list_logs():
    is_admin = _is_admin_user()
    marketers = _marketer_users()

    if not marketers:
        return render_template(
            "marketer_activity/list.html",
            logs=[],
            charts={
                "status": build_donut_chart([], preferred_order=MARKETER_LOG_STATUSES),
                "job_type": build_donut_chart([], preferred_order=MARKETER_JOB_TYPES),
            },
            metrics={
                "total_logs": 0,
                "submitted_logs": 0,
                "missed_logs": 0,
                "completion_rate": 0.0,
                "avg_activities_per_log": 0.0,
            },
            filters={
                "from_date": "",
                "to_date": "",
                "status": "",
                "marketer_user_id": "",
            },
            marketers=[],
            today_log=None,
            can_log_today=False,
            can_log_yesterday=False,
            selected_profile=None,
        )

    target_marketer_id = _resolve_marketer_filter_id(is_admin=is_admin)
    if target_marketer_id is None:
        target_marketer_id = marketers[0].id

    if not is_admin:
        target_marketer_id = current_user.id

    target_profile = ensure_marketer_profile(target_marketer_id)
    local_today = local_now_for_profile(target_profile).date()

    default_from = local_today - timedelta(days=29)
    from_date = parse_date(request.args.get("from_date")) or default_from
    to_date = parse_date(request.args.get("to_date")) or local_today
    if from_date > to_date:
        from_date, to_date = to_date, from_date

    status_filter = (request.args.get("status") or "").strip()

    query = MarketerDailyLog.query.filter(
        MarketerDailyLog.log_date >= from_date,
        MarketerDailyLog.log_date <= to_date,
    )

    if status_filter in MARKETER_LOG_STATUSES:
        query = query.filter(MarketerDailyLog.status == status_filter)

    if target_marketer_id:
        query = query.filter(MarketerDailyLog.marketer_user_id == target_marketer_id)

    logs = query.order_by(MarketerDailyLog.log_date.desc(), MarketerDailyLog.created_at.desc()).all()

    submitted_logs = [log for log in logs if log.status in {"submitted", "late", "waived"}]
    missed_logs = [log for log in logs if log.status == "missed"]
    total_activities = sum(_activity_total(log) for log in logs)
    metrics = {
        "total_logs": len(logs),
        "submitted_logs": len(submitted_logs),
        "missed_logs": len(missed_logs),
        "completion_rate": round((len(submitted_logs) / len(logs)) * 100, 1) if logs else 0.0,
        "avg_activities_per_log": round(total_activities / len(logs), 1) if logs else 0.0,
    }

    charts = {
        "status": build_donut_chart([log.status for log in logs], preferred_order=MARKETER_LOG_STATUSES),
        "job_type": build_donut_chart([log.job_type for log in logs], preferred_order=MARKETER_JOB_TYPES),
    }

    today_log = MarketerDailyLog.query.filter_by(
        marketer_user_id=target_marketer_id,
        log_date=local_today,
    ).first()

    can_log_today = False
    can_log_yesterday = False
    if not is_admin and target_marketer_id == current_user.id:
        can_log_today = can_marketer_edit_date(target_profile, local_today)
        can_log_yesterday = can_marketer_edit_date(target_profile, local_today - timedelta(days=1))

    return render_template(
        "marketer_activity/list.html",
        logs=logs,
        charts=charts,
        metrics=metrics,
        filters={
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "status": status_filter,
            "marketer_user_id": str(target_marketer_id or ""),
        },
        marketers=marketers,
        today_log=today_log,
        can_log_today=can_log_today,
        can_log_yesterday=can_log_yesterday,
        selected_profile=target_profile,
    )


@marketer_activity_bp.get("/marketer-activity/logs/new")
@login_required
@roles_required("owner", "admin", "marketer")
def new_log():
    is_admin = _is_admin_user()
    marketers = _marketer_users()
    if not marketers:
        flash("No marketer users found. Create a marketer user first.", "warning")
        return redirect(url_for("marketer_activity.list_logs"))

    if is_admin:
        marketer_user_id = _resolve_marketer_filter_id(is_admin=True) or marketers[0].id
    else:
        marketer_user_id = current_user.id

    profile = ensure_marketer_profile(marketer_user_id)
    local_today = local_now_for_profile(profile).date()
    log_date = parse_date(request.args.get("log_date")) or local_today

    if not is_admin and not can_marketer_edit_date(profile, log_date):
        flash("You can only create logs for today or yesterday before cutoff.", "warning")
        return redirect(url_for("marketer_activity.list_logs"))

    existing = MarketerDailyLog.query.filter_by(
        marketer_user_id=marketer_user_id,
        log_date=log_date,
    ).first()
    if existing is not None:
        flash("A log already exists for this marketer and date.", "warning")
        return redirect(url_for("marketer_activity.log_detail", log_id=existing.id))

    form_data = {
        "marketer_user_id": marketer_user_id,
        "log_date": log_date.isoformat(),
        "jobs_applied": 0,
        "follow_ups": 0,
        "interviews_scheduled": 0,
        "pay_discussions": 0,
        "job_type": "unknown",
        "hourly_rate_min": "",
        "hourly_rate_max": "",
        "project_duration_weeks": "",
        "notes": "",
    }

    return render_template(
        "marketer_activity/new.html",
        marketers=marketers,
        profile=profile,
        form_data=form_data,
        is_admin=is_admin,
        marketer_job_types=MARKETER_JOB_TYPES,
    )


@marketer_activity_bp.post("/marketer-activity/logs")
@login_required
@roles_required("owner", "admin", "marketer")
def create_log():
    is_admin = _is_admin_user()

    marketer_user_id = _resolve_marketer_id_for_form(is_admin=is_admin)
    if marketer_user_id is None:
        flash("A marketer is required.", "danger")
        return redirect(url_for("marketer_activity.new_log"))

    profile = ensure_marketer_profile(marketer_user_id)

    log_date = parse_date(request.form.get("log_date"))
    if not log_date:
        flash("Log date is required.", "danger")
        return redirect(url_for("marketer_activity.new_log", marketer_user_id=marketer_user_id))

    if not is_admin and not can_marketer_edit_date(profile, log_date):
        flash("You can only create logs for today or yesterday before cutoff.", "warning")
        return redirect(url_for("marketer_activity.list_logs"))

    duplicate = MarketerDailyLog.query.filter_by(marketer_user_id=marketer_user_id, log_date=log_date).first()
    if duplicate is not None:
        flash("A log already exists for this marketer and date.", "warning")
        return redirect(url_for("marketer_activity.log_detail", log_id=duplicate.id))

    payload, errors = _parse_log_form_payload()
    if errors:
        for message in errors:
            flash(message, "danger")
        return redirect(
            url_for(
                "marketer_activity.new_log",
                marketer_user_id=marketer_user_id,
                log_date=log_date.isoformat(),
            )
        )

    log = MarketerDailyLog(
        marketer_user_id=marketer_user_id,
        log_date=log_date,
        status="draft",
        jobs_applied=payload["jobs_applied"],
        follow_ups=payload["follow_ups"],
        interviews_scheduled=payload["interviews_scheduled"],
        pay_discussions=payload["pay_discussions"],
        job_type=payload["job_type"],
        hourly_rate_min=payload["hourly_rate_min"],
        hourly_rate_max=payload["hourly_rate_max"],
        project_duration_weeks=payload["project_duration_weeks"],
        notes=payload["notes"],
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(log)
    db.session.flush()

    if request.form.get("submit_now") == "1":
        log.status = submit_status_for_log(profile, log.log_date)
        log.submitted_at = datetime.now(tz=UTC)
        log.submitted_by_user_id = current_user.id

    add_activity(
        "create",
        "marketer_daily_log",
        log.id,
        f"Created marketer log for user {log.marketer_user_id} on {log.log_date.isoformat()}",
    )
    db.session.commit()
    flash("Marketer activity log created.", "success")
    return redirect(url_for("marketer_activity.log_detail", log_id=log.id))


@marketer_activity_bp.get("/marketer-activity/logs/<int:log_id>")
@login_required
@roles_required("owner", "admin", "marketer")
def log_detail(log_id: int):
    log = MarketerDailyLog.query.get_or_404(log_id)
    _assert_log_access(log)

    is_admin = _is_admin_user()
    profile = ensure_marketer_profile(log.marketer_user_id)
    notifications = (
        MarketerNotification.query.filter_by(
            marketer_user_id=log.marketer_user_id,
            target_date=log.log_date,
        )
        .order_by(MarketerNotification.created_at.desc())
        .all()
    )

    editable = can_marketer_edit_log(log, profile, is_admin=is_admin)

    form_data = {
        "marketer_user_id": log.marketer_user_id,
        "log_date": log.log_date.isoformat(),
        "jobs_applied": log.jobs_applied,
        "follow_ups": log.follow_ups,
        "interviews_scheduled": log.interviews_scheduled,
        "pay_discussions": log.pay_discussions,
        "job_type": log.job_type,
        "hourly_rate_min": "" if log.hourly_rate_min is None else log.hourly_rate_min,
        "hourly_rate_max": "" if log.hourly_rate_max is None else log.hourly_rate_max,
        "project_duration_weeks": "" if log.project_duration_weeks is None else log.project_duration_weeks,
        "notes": log.notes or "",
        "status": log.status,
    }

    return render_template(
        "marketer_activity/detail.html",
        log=log,
        form_data=form_data,
        marketers=_marketer_users(),
        is_admin=is_admin,
        editable=editable,
        notifications=notifications,
    )


@marketer_activity_bp.post("/marketer-activity/logs/<int:log_id>")
@login_required
@roles_required("owner", "admin", "marketer")
def update_log(log_id: int):
    log = MarketerDailyLog.query.get_or_404(log_id)
    _assert_log_access(log)

    is_admin = _is_admin_user()
    profile = ensure_marketer_profile(log.marketer_user_id)
    if not can_marketer_edit_log(log, profile, is_admin=is_admin):
        flash("This log is locked and cannot be edited.", "warning")
        return redirect(url_for("marketer_activity.log_detail", log_id=log.id))

    payload, errors = _parse_log_form_payload()
    if errors:
        for message in errors:
            flash(message, "danger")
        return redirect(url_for("marketer_activity.log_detail", log_id=log.id))

    log.jobs_applied = payload["jobs_applied"]
    log.follow_ups = payload["follow_ups"]
    log.interviews_scheduled = payload["interviews_scheduled"]
    log.pay_discussions = payload["pay_discussions"]
    log.job_type = payload["job_type"]
    log.hourly_rate_min = payload["hourly_rate_min"]
    log.hourly_rate_max = payload["hourly_rate_max"]
    log.project_duration_weeks = payload["project_duration_weeks"]
    log.notes = payload["notes"]

    if is_admin:
        status = (request.form.get("status") or "").strip()
        if status in MARKETER_LOG_STATUSES:
            log.status = status

    log.updated_by = current_user.id
    add_activity("update", "marketer_daily_log", log.id, f"Updated marketer log {log.id}")
    db.session.commit()
    flash("Marketer activity log updated.", "success")
    return redirect(url_for("marketer_activity.log_detail", log_id=log.id))


@marketer_activity_bp.post("/marketer-activity/logs/<int:log_id>/submit")
@login_required
@roles_required("owner", "admin", "marketer")
def submit_log(log_id: int):
    log = MarketerDailyLog.query.get_or_404(log_id)
    _assert_log_access(log)

    is_admin = _is_admin_user()
    profile = ensure_marketer_profile(log.marketer_user_id)
    if not can_marketer_edit_log(log, profile, is_admin=is_admin):
        flash("This log cannot be submitted because it is locked.", "warning")
        return redirect(url_for("marketer_activity.log_detail", log_id=log.id))

    log.status = submit_status_for_log(profile, log.log_date)
    log.submitted_at = datetime.now(tz=UTC)
    log.submitted_by_user_id = current_user.id
    log.updated_by = current_user.id

    add_activity(
        "status_change",
        "marketer_daily_log",
        log.id,
        f"Submitted marketer log {log.id} with status {log.status}",
    )
    db.session.commit()
    flash("Marketer activity log submitted.", "success")
    return redirect(url_for("marketer_activity.log_detail", log_id=log.id))


@marketer_activity_bp.get("/marketer-activity/reports")
@login_required
@roles_required("owner", "admin", "marketer")
def reports():
    is_admin = _is_admin_user()
    marketers = _marketer_users()
    if not marketers:
        flash("No marketer users available for reporting.", "warning")
        return redirect(url_for("marketer_activity.list_logs"))

    selected_marketer_id = _resolve_marketer_filter_id(is_admin=is_admin)
    if not is_admin:
        selected_marketer_id = current_user.id

    today = date.today()
    from_date = parse_date(request.args.get("from_date")) or (today - timedelta(days=29))
    to_date = parse_date(request.args.get("to_date")) or today
    if from_date > to_date:
        from_date, to_date = to_date, from_date

    query = MarketerDailyLog.query.filter(
        MarketerDailyLog.log_date >= from_date,
        MarketerDailyLog.log_date <= to_date,
    )
    if selected_marketer_id:
        query = query.filter(MarketerDailyLog.marketer_user_id == selected_marketer_id)

    logs = query.order_by(MarketerDailyLog.log_date.asc(), MarketerDailyLog.id.asc()).all()

    status_counts = build_donut_chart([log.status for log in logs], preferred_order=MARKETER_LOG_STATUSES)
    job_type_counts = build_donut_chart([log.job_type for log in logs], preferred_order=MARKETER_JOB_TYPES)

    total_jobs_applied = sum(log.jobs_applied for log in logs)
    total_follow_ups = sum(log.follow_ups for log in logs)
    total_interviews = sum(log.interviews_scheduled for log in logs)
    total_pay_discussions = sum(log.pay_discussions for log in logs)
    total_activities = total_jobs_applied + total_follow_ups + total_interviews + total_pay_discussions

    expected_workdays = _expected_workdays(from_date, to_date, selected_marketer_id, marketers)
    completed_logs = [log for log in logs if log.status in {"submitted", "late", "waived"}]
    missed_logs = [log for log in logs if log.status == "missed"]

    report_metrics = {
        "jobs_applied": total_jobs_applied,
        "follow_ups": total_follow_ups,
        "interviews_scheduled": total_interviews,
        "pay_discussions": total_pay_discussions,
        "avg_activities_per_day": round(total_activities / len(logs), 1) if logs else 0.0,
        "completion_rate": round((len(completed_logs) / expected_workdays) * 100, 1)
        if expected_workdays
        else 0.0,
        "missed_rate": round((len(missed_logs) / expected_workdays) * 100, 1) if expected_workdays else 0.0,
    }

    by_date: dict[date, dict[str, float]] = defaultdict(lambda: {
        "jobs_applied": 0,
        "follow_ups": 0,
        "interviews_scheduled": 0,
        "pay_discussions": 0,
        "completed": 0,
        "missed": 0,
    })
    by_marketer: dict[int, dict[str, float]] = defaultdict(lambda: {
        "marketer_name": "",
        "total_logs": 0,
        "completed": 0,
        "missed": 0,
        "activities": 0,
    })

    marketer_lookup = {user.id: user.full_name for user in marketers}

    for log in logs:
        bucket = by_date[log.log_date]
        bucket["jobs_applied"] += log.jobs_applied
        bucket["follow_ups"] += log.follow_ups
        bucket["interviews_scheduled"] += log.interviews_scheduled
        bucket["pay_discussions"] += log.pay_discussions
        if log.status in {"submitted", "late", "waived"}:
            bucket["completed"] += 1
        if log.status == "missed":
            bucket["missed"] += 1

        marketer_bucket = by_marketer[log.marketer_user_id]
        marketer_bucket["marketer_name"] = marketer_lookup.get(log.marketer_user_id, f"User {log.marketer_user_id}")
        marketer_bucket["total_logs"] += 1
        if log.status in {"submitted", "late", "waived"}:
            marketer_bucket["completed"] += 1
        if log.status == "missed":
            marketer_bucket["missed"] += 1
        marketer_bucket["activities"] += _activity_total(log)

    ordered_dates = sorted(by_date.keys())
    trend_labels = [day.isoformat() for day in ordered_dates]
    jobs_series = [by_date[day]["jobs_applied"] for day in ordered_dates]
    followups_series = [by_date[day]["follow_ups"] for day in ordered_dates]
    interviews_series = [by_date[day]["interviews_scheduled"] for day in ordered_dates]
    pay_series = [by_date[day]["pay_discussions"] for day in ordered_dates]
    completed_series = [by_date[day]["completed"] for day in ordered_dates]
    missed_series = [by_date[day]["missed"] for day in ordered_dates]

    trend_graph = {
        "labels": trend_labels,
        "datasets": [
            {
                "type": "bar",
                "label": "Jobs Applied",
                "data": jobs_series,
                "backgroundColor": "rgba(15, 98, 254, 0.66)",
                "borderColor": "#0f62fe",
                "borderRadius": 8,
            },
            {
                "type": "line",
                "label": "Follow-ups",
                "data": followups_series,
                "borderColor": "#24a148",
                "backgroundColor": "rgba(36, 161, 72, 0.2)",
                "pointBackgroundColor": "#24a148",
                "fill": False,
            },
            {
                "type": "line",
                "label": "Interviews",
                "data": interviews_series,
                "borderColor": "#ff832b",
                "backgroundColor": "rgba(255, 131, 43, 0.2)",
                "pointBackgroundColor": "#ff832b",
                "fill": False,
            },
            {
                "type": "line",
                "label": "Pay Discussions",
                "data": pay_series,
                "borderColor": "#8b5cf6",
                "backgroundColor": "rgba(139, 92, 246, 0.2)",
                "pointBackgroundColor": "#8b5cf6",
                "fill": False,
            },
        ],
        "is_empty": sum(jobs_series) + sum(followups_series) + sum(interviews_series) + sum(pay_series) <= 0,
    }

    completion_graph = {
        "labels": trend_labels,
        "datasets": [
            {
                "type": "bar",
                "label": "Completed",
                "data": completed_series,
                "backgroundColor": "rgba(36, 161, 72, 0.68)",
                "borderColor": "#24a148",
                "borderRadius": 8,
            },
            {
                "type": "bar",
                "label": "Missed",
                "data": missed_series,
                "backgroundColor": "rgba(218, 30, 40, 0.62)",
                "borderColor": "#da1e28",
                "borderRadius": 8,
            },
        ],
        "is_empty": sum(completed_series) + sum(missed_series) <= 0,
    }

    marketer_rows = []
    for marketer_id, bucket in sorted(by_marketer.items(), key=lambda item: item[1]["marketer_name"].lower()):
        marketer_rows.append(
            {
                "marketer_id": marketer_id,
                "marketer_name": bucket["marketer_name"],
                "total_logs": int(bucket["total_logs"]),
                "completed": int(bucket["completed"]),
                "missed": int(bucket["missed"]),
                "activities": int(bucket["activities"]),
            }
        )

    return render_template(
        "marketer_activity/reports.html",
        marketers=marketers,
        filters={
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "marketer_user_id": str(selected_marketer_id or ""),
        },
        metrics=report_metrics,
        charts={"status": status_counts, "job_type": job_type_counts},
        trend_graph=trend_graph,
        completion_graph=completion_graph,
        marketer_rows=marketer_rows,
    )


@marketer_activity_bp.get("/marketer-activity/reports/export.csv")
@login_required
@roles_required("owner", "admin", "marketer")
def reports_export_csv():
    is_admin = _is_admin_user()
    selected_marketer_id = _resolve_marketer_filter_id(is_admin=is_admin)
    if not is_admin:
        selected_marketer_id = current_user.id

    today = date.today()
    from_date = parse_date(request.args.get("from_date")) or (today - timedelta(days=29))
    to_date = parse_date(request.args.get("to_date")) or today
    if from_date > to_date:
        from_date, to_date = to_date, from_date

    query = MarketerDailyLog.query.filter(
        MarketerDailyLog.log_date >= from_date,
        MarketerDailyLog.log_date <= to_date,
    )
    if selected_marketer_id:
        query = query.filter(MarketerDailyLog.marketer_user_id == selected_marketer_id)

    logs = query.order_by(MarketerDailyLog.log_date.desc()).all()
    rows = [
        [
            str(log.id),
            str(log.marketer_user_id),
            log.marketer.full_name if log.marketer else "",
            log.log_date.isoformat(),
            log.status,
            str(log.jobs_applied),
            str(log.follow_ups),
            str(log.interviews_scheduled),
            str(log.pay_discussions),
            log.job_type,
            "" if log.hourly_rate_min is None else str(log.hourly_rate_min),
            "" if log.hourly_rate_max is None else str(log.hourly_rate_max),
            "" if log.project_duration_weeks is None else str(log.project_duration_weeks),
            log.notes or "",
        ]
        for log in logs
    ]

    add_activity("export", "marketer_report", None, "Exported marketer activity CSV")
    db.session.commit()

    return csv_response(
        "marketer_activity.csv",
        [
            "id",
            "marketer_user_id",
            "marketer_name",
            "log_date",
            "status",
            "jobs_applied",
            "follow_ups",
            "interviews_scheduled",
            "pay_discussions",
            "job_type",
            "hourly_rate_min",
            "hourly_rate_max",
            "project_duration_weeks",
            "notes",
        ],
        rows,
    )


@marketer_activity_bp.route("/marketer-activity/onboard", methods=["GET", "POST"])
@login_required
@roles_required("owner", "admin")
def onboard_marketer():
    """Onboard a new marketer user with profile setup."""
    from werkzeug.security import generate_password_hash
    
    if request.method == "POST":
        # Get form data
        username = (request.form.get("username") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        
        # Validation
        if not username or not full_name or not password:
            flash("Username, full name, and password are required.", "danger")
            return redirect(url_for("marketer_activity.onboard_marketer"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("marketer_activity.onboard_marketer"))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' already exists.", "danger")
            return redirect(url_for("marketer_activity.onboard_marketer"))
        
        # Check if email already exists (if provided)
        if email and User.query.filter_by(email=email).first():
            flash(f"Email '{email}' already exists.", "danger")
            return redirect(url_for("marketer_activity.onboard_marketer"))
        
        # Get marketer role
        marketer_role = Role.query.filter_by(name="marketer").first()
        if not marketer_role:
            flash("Marketer role not found. Please initialize the database.", "danger")
            return redirect(url_for("marketer_activity.onboard_marketer"))
        
        # Create user
        new_user = User(
            username=username,
            full_name=full_name,
            email=email if email else None,
            password_hash=generate_password_hash(password),
            role_id=marketer_role.id,
            is_active=True,
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Get profile settings from form
        timezone = (request.form.get("timezone") or "").strip() or "America/New_York"
        cutoff = parse_local_time(request.form.get("daily_cutoff_local_time") or "17:00")
        reminder_times = parse_reminder_times(request.form.get("reminder_times_local") or "09:00,15:00")
        escalation_after_misses = _to_int(request.form.get("escalation_after_misses")) or 2
        reminder_enabled = request.form.get("reminder_enabled") == "1"
        
        # Get workdays
        selected_workdays: set[int] = set()
        for day in range(7):
            if request.form.get(f"workday_{day}") == "1":
                selected_workdays.add(day)
        if not selected_workdays:
            selected_workdays = {0, 1, 2, 3, 4}  # Default to Mon-Fri
        
        manager_user_id = _to_int(request.form.get("manager_user_id"))
        
        # Create marketer profile
        profile = MarketerProfile(
            user_id=new_user.id,
            timezone=timezone,
            daily_cutoff_local_time=cutoff.strftime("%H:%M") if cutoff else "17:00",
            reminder_times_local=serialize_reminder_times(reminder_times),
            reminder_enabled=reminder_enabled,
            escalation_after_misses=escalation_after_misses,
            workdays_mask=format_workdays_mask(selected_workdays),
            manager_user_id=manager_user_id,
        )
        db.session.add(profile)
        
        add_activity(
            "create",
            "user",
            new_user.id,
            f"Onboarded new marketer: {full_name} ({username})",
        )
        
        db.session.commit()
        
        flash(f"Marketer '{full_name}' onboarded successfully! Username: {username}", "success")
        return redirect(url_for("marketer_activity.settings", user_id=new_user.id))
    
    # GET request - show onboarding form
    # Get potential managers (owner, admin users)
    potential_managers = User.query.join(Role).filter(
        Role.name.in_(["owner", "admin"]),
        User.is_active == True
    ).order_by(User.full_name.asc()).all()
    
    return render_template(
        "marketer_activity/onboard.html",
        potential_managers=potential_managers,
    )


@marketer_activity_bp.route("/marketer-activity/settings", methods=["GET", "POST"])
@login_required
@roles_required("owner", "admin")
def settings():
    profiles = ensure_profiles_for_all_marketers()
    marketers = _marketer_users()

    if not marketers:
        flash("No marketer users found. Create a marketer user to configure settings.", "warning")
        return redirect(url_for("marketer_activity.list_logs"))

    selected_user_id = _to_int(request.args.get("user_id")) or marketers[0].id

    if request.method == "POST":
        selected_user_id = _to_int(request.form.get("user_id")) or selected_user_id
        profile = ensure_marketer_profile(selected_user_id)

        timezone = (request.form.get("timezone") or "").strip() or profile.timezone
        cutoff = parse_local_time(request.form.get("daily_cutoff_local_time"))
        if cutoff is None:
            flash("Cutoff time must be in HH:MM 24-hour format.", "danger")
            return redirect(url_for("marketer_activity.settings", user_id=selected_user_id))

        reminder_times = parse_reminder_times(request.form.get("reminder_times_local"))
        escalation_after_misses = _to_int(request.form.get("escalation_after_misses"))
        if escalation_after_misses is None or escalation_after_misses < 1:
            flash("Escalation threshold must be at least 1.", "danger")
            return redirect(url_for("marketer_activity.settings", user_id=selected_user_id))

        selected_workdays: set[int] = set()
        for day in range(7):
            if request.form.get(f"workday_{day}") == "1":
                selected_workdays.add(day)
        if not selected_workdays:
            selected_workdays = {0, 1, 2, 3, 4}

        manager_user_id = _to_int(request.form.get("manager_user_id"))

        profile.timezone = timezone
        profile.daily_cutoff_local_time = cutoff.strftime("%H:%M")
        profile.reminder_times_local = serialize_reminder_times(reminder_times)
        profile.reminder_enabled = request.form.get("reminder_enabled") == "1"
        profile.escalation_after_misses = escalation_after_misses
        profile.workdays_mask = format_workdays_mask(selected_workdays)
        profile.manager_user_id = manager_user_id

        add_activity(
            "update",
            "marketer_profile",
            profile.id,
            f"Updated marketer profile settings for user {selected_user_id}",
        )
        db.session.commit()
        flash("Marketer settings updated.", "success")
        return redirect(url_for("marketer_activity.settings", user_id=selected_user_id))

    selected_profile = ensure_marketer_profile(selected_user_id)
    
    # Get potential managers (owner, admin users)
    potential_managers = User.query.join(Role).filter(
        Role.name.in_(["owner", "admin"]),
        User.is_active == True
    ).order_by(User.full_name.asc()).all()

    return render_template(
        "marketer_activity/settings.html",
        marketers=marketers,
        selected_user_id=selected_user_id,
        selected_profile=selected_profile,
        selected_workdays=parse_workdays_mask(selected_profile.workdays_mask),
        profiles=profiles,
        users=potential_managers,
    )


def _is_admin_user() -> bool:
    return bool(current_user.role and current_user.role.name in {"owner", "admin"})


def _resolve_marketer_filter_id(*, is_admin: bool) -> int | None:
    if not is_admin:
        return current_user.id
    return _to_int(request.args.get("marketer_user_id"))


def _resolve_marketer_id_for_form(*, is_admin: bool) -> int | None:
    if not is_admin:
        return current_user.id
    return _to_int(request.form.get("marketer_user_id"))


def _marketer_users() -> list[User]:
    role = Role.query.filter_by(name="marketer").first()
    if role is None:
        return []
    return (
        User.query.filter_by(role_id=role.id, is_active=True)
        .order_by(User.full_name.asc())
        .all()
    )


def _assert_log_access(log: MarketerDailyLog) -> None:
    is_admin = _is_admin_user()
    if is_admin:
        return
    if log.marketer_user_id != current_user.id:
        abort(403)


def _parse_log_form_payload() -> tuple[dict, list[str]]:
    errors: list[str] = []

    jobs_applied = _parse_non_negative_int(request.form.get("jobs_applied"), "Jobs applied", errors)
    follow_ups = _parse_non_negative_int(request.form.get("follow_ups"), "Follow-ups", errors)
    interviews_scheduled = _parse_non_negative_int(
        request.form.get("interviews_scheduled"), "Interviews scheduled", errors
    )
    pay_discussions = _parse_non_negative_int(
        request.form.get("pay_discussions"), "Pay discussions", errors
    )

    job_type = (request.form.get("job_type") or "unknown").strip().lower()
    if job_type not in MARKETER_JOB_TYPES:
        errors.append("Job type is required.")
        job_type = "unknown"

    hourly_rate_min = _parse_optional_float(request.form.get("hourly_rate_min"), "Hourly rate min", errors)
    hourly_rate_max = _parse_optional_float(request.form.get("hourly_rate_max"), "Hourly rate max", errors)
    if hourly_rate_min is not None and hourly_rate_max is not None and hourly_rate_min > hourly_rate_max:
        errors.append("Hourly rate min must be less than or equal to hourly rate max.")

    project_duration_weeks = _parse_optional_int(
        request.form.get("project_duration_weeks"), "Project duration", errors
    )

    notes = (request.form.get("notes") or "").strip()
    if jobs_applied + follow_ups + interviews_scheduled + pay_discussions == 0 and not notes:
        errors.append("Notes are required when all activity counts are 0.")

    payload = {
        "jobs_applied": jobs_applied,
        "follow_ups": follow_ups,
        "interviews_scheduled": interviews_scheduled,
        "pay_discussions": pay_discussions,
        "job_type": job_type,
        "hourly_rate_min": hourly_rate_min,
        "hourly_rate_max": hourly_rate_max,
        "project_duration_weeks": project_duration_weeks,
        "notes": notes or None,
    }
    return payload, errors


def _parse_non_negative_int(raw_value: str | None, label: str, errors: list[str]) -> int:
    if raw_value is None or raw_value.strip() == "":
        return 0
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be an integer.")
        return 0
    if value < 0:
        errors.append(f"{label} must be 0 or greater.")
        return 0
    return value


def _parse_optional_int(raw_value: str | None, label: str, errors: list[str]) -> int | None:
    if raw_value is None or raw_value.strip() == "":
        return None
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be an integer.")
        return None
    if value < 0:
        errors.append(f"{label} must be 0 or greater.")
        return None
    return value


def _parse_optional_float(raw_value: str | None, label: str, errors: list[str]) -> float | None:
    if raw_value is None or raw_value.strip() == "":
        return None
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        errors.append(f"{label} must be a number.")
        return None
    if value < 0:
        errors.append(f"{label} must be 0 or greater.")
        return None
    return value


def _expected_workdays(
    from_date: date,
    to_date: date,
    selected_marketer_id: int | None,
    marketers: list[User],
) -> int:
    if selected_marketer_id:
        profile = ensure_marketer_profile(selected_marketer_id)
        workdays = parse_workdays_mask(profile.workdays_mask)
        return _count_workdays_in_range(from_date, to_date, workdays)

    total = 0
    for marketer in marketers:
        profile = ensure_marketer_profile(marketer.id)
        workdays = parse_workdays_mask(profile.workdays_mask)
        total += _count_workdays_in_range(from_date, to_date, workdays)
    return total


def _count_workdays_in_range(start_date: date, end_date: date, workdays: set[int]) -> int:
    count = 0
    cursor = start_date
    while cursor <= end_date:
        if cursor.weekday() in workdays:
            count += 1
        cursor += timedelta(days=1)
    return count


def _activity_total(log: MarketerDailyLog) -> int:
    return log.jobs_applied + log.follow_ups + log.interviews_scheduled + log.pay_discussions


def _to_int(raw_value: str | None) -> int | None:
    if raw_value is None:
        return None
    raw_value = raw_value.strip()
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        return None
