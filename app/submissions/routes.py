from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import SUBMISSION_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import (
    Candidate,
    Job,
    Note,
    Submission,
    SubmissionStatusHistory,
    Task,
    User,
)
from ..utils import add_activity, build_donut_chart, parse_datetime

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.get("/submissions")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def list_submissions():
    query = Submission.query

    recruiter_user_id = request.args.get("recruiter_user_id", "").strip()
    job_id = request.args.get("job_id", "").strip()
    status = request.args.get("status", "").strip()

    if recruiter_user_id.isdigit():
        query = query.filter(Submission.recruiter_user_id == int(recruiter_user_id))
    if job_id.isdigit():
        query = query.filter(Submission.job_id == int(job_id))
    if status:
        query = query.filter(Submission.status == status)

    submissions = query.order_by(Submission.created_at.desc()).all()
    
    # Calculate metrics
    total_submissions = len(submissions)
    interview_count = len([s for s in submissions if s.status == 'interview'])
    selected_count = len([s for s in submissions if s.status in ['selected', 'offered', 'joined']])
    rejected_count = len([s for s in submissions if s.status == 'rejected'])
    conversion_rate = round((selected_count / total_submissions * 100), 1) if total_submissions > 0 else 0
    
    metrics = {
        "total": total_submissions,
        "interviews": interview_count,
        "selected": selected_count,
        "rejected": rejected_count,
        "conversion_rate": conversion_rate,
    }
    
    charts = {
        "status": build_donut_chart(
            [submission.status for submission in submissions],
            preferred_order=SUBMISSION_STATUSES,
        ),
        "recruiter": build_donut_chart(
            [submission.recruiter.full_name if submission.recruiter else None for submission in submissions],
            empty_label="Unassigned",
            top_n=6,
        ),
    }
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    jobs = Job.query.order_by(Job.title.asc()).all()
    return render_template(
        "submissions/list.html",
        submissions=submissions,
        charts=charts,
        metrics=metrics,
        recruiters=recruiters,
        jobs=jobs,
        submission_statuses=SUBMISSION_STATUSES,
        filters={
            "recruiter_user_id": recruiter_user_id,
            "job_id": job_id,
            "status": status,
        },
    )


@submissions_bp.get("/submissions/new")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def new_submission():
    candidates = Candidate.query.order_by(Candidate.full_name.asc()).all()
    jobs = Job.query.filter(Job.status != "closed").order_by(Job.title.asc()).all()
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template(
        "submissions/new.html",
        candidates=candidates,
        jobs=jobs,
        recruiters=recruiters,
    )


@submissions_bp.post("/submissions")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def create_submission():
    candidate_id = _to_int(request.form.get("candidate_id"))
    job_id = _to_int(request.form.get("job_id"))
    recruiter_user_id = _to_int(request.form.get("recruiter_user_id")) or current_user.id

    if not candidate_id or not job_id:
        flash("Candidate and job are required.", "danger")
        return redirect(url_for("submissions.new_submission"))

    job = Job.query.get_or_404(job_id)
    if job.status == "closed":
        flash("Closed jobs cannot accept new submissions.", "danger")
        return redirect(url_for("submissions.new_submission"))

    duplicate = Submission.query.filter_by(candidate_id=candidate_id, job_id=job_id).first()
    if duplicate is not None:
        flash("Duplicate submission detected for this candidate and job.", "warning")
        return redirect(url_for("submissions.submission_detail", submission_id=duplicate.id))

    submission = Submission(
        candidate_id=candidate_id,
        job_id=job_id,
        recruiter_user_id=recruiter_user_id,
        status=request.form.get("status") or "submitted",
        interview_date=parse_datetime(request.form.get("interview_date")),
        feedback=request.form.get("feedback") or None,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(submission)
    db.session.flush()

    history = SubmissionStatusHistory(
        submission_id=submission.id,
        old_status=None,
        new_status=submission.status,
        changed_by=current_user.id,
        remarks="Initial status",
    )
    db.session.add(history)
    add_activity(
        "create",
        "submission",
        submission.id,
        f"Submitted candidate {submission.candidate_id} to job {submission.job_id}",
    )
    db.session.commit()
    flash("Submission created.", "success")
    return redirect(url_for("submissions.submission_detail", submission_id=submission.id))


@submissions_bp.get("/submissions/<int:submission_id>")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def submission_detail(submission_id: int):
    submission = Submission.query.get_or_404(submission_id)
    notes = Note.query.filter_by(entity_type="submission", entity_id=submission.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="submission", entity_id=submission.id).order_by(Task.created_at.desc()).all()
    status_history = (
        SubmissionStatusHistory.query.filter_by(submission_id=submission.id)
        .order_by(SubmissionStatusHistory.changed_at.desc())
        .all()
    )
    return render_template(
        "submissions/detail.html",
        submission=submission,
        notes=notes,
        tasks=tasks,
        status_history=status_history,
    )


@submissions_bp.post("/submissions/<int:submission_id>/status")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def submission_status(submission_id: int):
    submission = Submission.query.get_or_404(submission_id)
    new_status = request.form.get("status", "").strip()
    remarks = request.form.get("remarks", "").strip()

    if new_status not in SUBMISSION_STATUSES:
        flash("Invalid submission status.", "danger")
        return redirect(url_for("submissions.submission_detail", submission_id=submission.id))

    old_status = submission.status
    submission.status = new_status
    submission.interview_date = parse_datetime(request.form.get("interview_date"))
    submission.feedback = request.form.get("feedback") or submission.feedback
    submission.updated_by = current_user.id

    history = SubmissionStatusHistory(
        submission_id=submission.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        remarks=remarks or None,
    )
    db.session.add(history)
    add_activity(
        "status_change",
        "submission",
        submission.id,
        f"Submission {submission.id} moved from {old_status} to {new_status}",
    )
    db.session.commit()
    flash("Submission status updated.", "success")
    return redirect(url_for("submissions.submission_detail", submission_id=submission.id))


def _to_int(value: str | None) -> int | None:
    if value and value.isdigit():
        return int(value)
    return None
