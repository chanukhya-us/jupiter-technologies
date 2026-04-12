from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import JOB_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import Client, Job, Note, Submission, Task, User
from ..utils import add_activity, build_donut_chart

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/jobs")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def list_jobs():
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    query = Job.query

    status = request.args.get("status", "").strip()
    client_id = request.args.get("client_id", "").strip()
    owner_user_id = request.args.get("owner_user_id", "").strip()

    if status:
        query = query.filter(Job.status == status)
    if client_id.isdigit():
        query = query.filter(Job.client_id == int(client_id))
    if owner_user_id.isdigit():
        query = query.filter(Job.owner_user_id == int(owner_user_id))

    jobs = query.order_by(Job.updated_at.desc()).all()
    
    # Build trend data - show last 30 days or all data if limited
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=29)
    
    # Get all jobs to check data availability
    all_jobs = Job.query.all()
    
    # If we have jobs but none in last 30 days, expand the window
    if all_jobs:
        oldest_date = min(j.created_at.date() for j in all_jobs)
        # If oldest data is older than 30 days, use it
        if oldest_date < thirty_days_ago:
            days_back = min((today - oldest_date).days, 90)  # Max 90 days
            start_date = today - timedelta(days=days_back)
        else:
            start_date = thirty_days_ago
    else:
        start_date = thirty_days_ago
    
    # Get jobs in the date range
    trend_jobs = [j for j in all_jobs if j.created_at.date() >= start_date]
    
    # Group by date
    by_date = defaultdict(int)
    for job in trend_jobs:
        date_key = job.created_at.date()
        by_date[date_key] += 1
    
    # Build labels and data
    trend_labels = []
    trend_data = []
    current_date = start_date
    while current_date <= today:
        trend_labels.append(current_date.strftime("%m/%d"))
        trend_data.append(by_date.get(current_date, 0))
        current_date += timedelta(days=1)
    
    # Sample labels if too many
    if len(trend_labels) > 30:
        step = len(trend_labels) // 15
        display_labels = [label if i % step == 0 else '' for i, label in enumerate(trend_labels)]
    else:
        display_labels = trend_labels
    
    trend_graph = {
        "labels": display_labels,
        "datasets": [{
            "type": "line",
            "label": "New Jobs",
            "data": trend_data,
            "borderColor": "#24a148",
            "backgroundColor": "rgba(36, 161, 72, 0.1)",
            "fill": True,
            "tension": 0.4,
        }],
        "is_empty": len(all_jobs) == 0,  # Only empty if NO jobs at all
        "total": sum(trend_data),
        "days": len(trend_labels),
    }
    
    charts = {
        "status": build_donut_chart(
            [job.status for job in jobs],
            preferred_order=JOB_STATUSES,
        ),
        "owner": build_donut_chart(
            [job.owner.full_name if job.owner else None for job in jobs],
            empty_label="Unassigned",
            top_n=6,
        ),
    }
    clients = Client.query.order_by(Client.company_name.asc()).all()
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()

    return render_template(
        "jobs/list.html",
        jobs=jobs,
        charts=charts,
        trend_graph=trend_graph,
        clients=clients,
        recruiters=recruiters,
        job_statuses=JOB_STATUSES,
        filters={
            "status": status,
            "client_id": client_id,
            "owner_user_id": owner_user_id,
        },
    )


@jobs_bp.get("/jobs/new")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def new_job():
    clients = Client.query.order_by(Client.company_name.asc()).all()
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template("jobs/new.html", clients=clients, recruiters=recruiters)


@jobs_bp.post("/jobs")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def create_job():
    title = request.form.get("title", "").strip()
    client_id = _to_int(request.form.get("client_id"))

    if not title or not client_id:
        flash("Job title and client are required.", "danger")
        return redirect(url_for("jobs.new_job"))

    job = Job(
        job_code=request.form.get("job_code") or None,
        client_id=client_id,
        title=title,
        location=request.form.get("location") or None,
        work_type=request.form.get("work_type") or None,
        employment_type=request.form.get("employment_type") or None,
        required_skills=request.form.get("required_skills") or None,
        min_experience=_to_float(request.form.get("min_experience")),
        max_experience=_to_float(request.form.get("max_experience")),
        salary_or_rate=request.form.get("salary_or_rate") or None,
        status=request.form.get("status") or "open",
        owner_user_id=_to_int(request.form.get("owner_user_id")),
        description=request.form.get("description") or None,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(job)
    db.session.flush()
    add_activity("create", "job", job.id, f"Created job {job.title}")
    db.session.commit()

    flash("Job created.", "success")
    return redirect(url_for("jobs.job_detail", job_id=job.id))


@jobs_bp.get("/jobs/<int:job_id>")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def job_detail(job_id: int):
    job = Job.query.get_or_404(job_id)
    submissions = Submission.query.filter_by(job_id=job.id).order_by(Submission.created_at.desc()).all()
    notes = Note.query.filter_by(entity_type="job", entity_id=job.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="job", entity_id=job.id).order_by(Task.created_at.desc()).all()
    clients = Client.query.order_by(Client.company_name.asc()).all()
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template(
        "jobs/detail.html",
        job=job,
        submissions=submissions,
        notes=notes,
        tasks=tasks,
        clients=clients,
        recruiters=recruiters,
    )


@jobs_bp.post("/jobs/<int:job_id>/update")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def update_job(job_id: int):
    job = Job.query.get_or_404(job_id)
    job.title = request.form.get("title", job.title).strip() or job.title
    job.job_code = request.form.get("job_code") or None
    job.client_id = _to_int(request.form.get("client_id")) or job.client_id
    job.location = request.form.get("location") or None
    job.work_type = request.form.get("work_type") or None
    job.employment_type = request.form.get("employment_type") or None
    job.required_skills = request.form.get("required_skills") or None
    job.min_experience = _to_float(request.form.get("min_experience"))
    job.max_experience = _to_float(request.form.get("max_experience"))
    job.salary_or_rate = request.form.get("salary_or_rate") or None

    status = request.form.get("status", job.status)
    if status in JOB_STATUSES:
        job.status = status

    job.owner_user_id = _to_int(request.form.get("owner_user_id"))
    job.description = request.form.get("description") or None
    job.updated_by = current_user.id

    add_activity("update", "job", job.id, f"Updated job {job.title}")
    db.session.commit()
    flash("Job updated.", "success")
    return redirect(url_for("jobs.job_detail", job_id=job.id))


@jobs_bp.post("/jobs/<int:job_id>/close")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def close_job(job_id: int):
    job = Job.query.get_or_404(job_id)
    job.status = "closed"
    job.updated_by = current_user.id
    add_activity("status_change", "job", job.id, f"Closed job {job.title}")
    db.session.commit()
    flash("Job closed.", "warning")
    return redirect(url_for("jobs.job_detail", job_id=job.id))


@jobs_bp.post("/jobs/<int:job_id>/reopen")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def reopen_job(job_id: int):
    job = Job.query.get_or_404(job_id)
    job.status = "open"
    job.updated_by = current_user.id
    add_activity("status_change", "job", job.id, f"Reopened job {job.title}")
    db.session.commit()
    flash("Job reopened.", "success")
    return redirect(url_for("jobs.job_detail", job_id=job.id))


def _to_int(value: str | None) -> int | None:
    if value and value.isdigit():
        return int(value)
    return None


def _to_float(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
