from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import CANDIDATE_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import Candidate, CandidateStatusHistory, Note, Submission, Task, User
from ..utils import add_activity, build_donut_chart, save_uploaded_file

candidates_bp = Blueprint("candidates", __name__)


@candidates_bp.get("/candidates")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def list_candidates():
    query = Candidate.query

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    source = request.args.get("source", "").strip()
    location = request.args.get("location", "").strip()
    owner_user_id = request.args.get("owner_user_id", "").strip()

    if search:
        query = query.filter(Candidate.full_name.ilike(f"%{search}%"))
    if status:
        query = query.filter(Candidate.status == status)
    if source:
        query = query.filter(Candidate.source.ilike(f"%{source}%"))
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
    if owner_user_id.isdigit():
        query = query.filter(Candidate.owner_user_id == int(owner_user_id))

    candidates = query.order_by(Candidate.updated_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            [candidate.status for candidate in candidates],
            preferred_order=CANDIDATE_STATUSES,
        ),
        "source": build_donut_chart(
            [candidate.source for candidate in candidates],
            empty_label="Unknown source",
            top_n=6,
        ),
    }
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template(
        "candidates/list.html",
        candidates=candidates,
        charts=charts,
        recruiters=recruiters,
        filters={
            "search": search,
            "status": status,
            "source": source,
            "location": location,
            "owner_user_id": owner_user_id,
        },
    )


@candidates_bp.get("/candidates/new")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def new_candidate():
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template("candidates/new.html", recruiters=recruiters)


@candidates_bp.post("/candidates")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def create_candidate():
    full_name = request.form.get("full_name", "").strip()
    if not full_name:
        flash("Candidate name is required.", "danger")
        return redirect(url_for("candidates.new_candidate"))

    candidate = Candidate(
        full_name=full_name,
        first_name=request.form.get("first_name") or None,
        last_name=request.form.get("last_name") or None,
        phone=request.form.get("phone") or None,
        email=request.form.get("email") or None,
        location=request.form.get("location") or None,
        primary_skills=request.form.get("primary_skills") or None,
        years_experience=_to_float(request.form.get("years_experience")),
        source=request.form.get("source") or None,
        status=request.form.get("status") or "new",
        owner_user_id=_to_int(request.form.get("owner_user_id")),
        notes_summary=request.form.get("notes_summary") or None,
        created_by=current_user.id,
        updated_by=current_user.id,
    )

    upload = request.files.get("resume")
    if upload:
        try:
            candidate.resume_file_path = save_uploaded_file(upload, subfolder="resumes")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("candidates.new_candidate"))

    db.session.add(candidate)
    db.session.flush()
    history = CandidateStatusHistory(
        candidate_id=candidate.id,
        old_status=None,
        new_status=candidate.status,
        changed_by=current_user.id,
        remarks="Initial status",
    )
    db.session.add(history)
    add_activity("create", "candidate", candidate.id, f"Created candidate {candidate.full_name}")
    db.session.commit()

    flash("Candidate created.", "success")
    return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))


@candidates_bp.get("/candidates/<int:candidate_id>")
@login_required
def candidate_detail(candidate_id: int):
    candidate = Candidate.query.get_or_404(candidate_id)
    if current_user.role.name == "employee":
        return _forbidden_redirect()

    notes = Note.query.filter_by(entity_type="candidate", entity_id=candidate.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="candidate", entity_id=candidate.id).order_by(Task.created_at.desc()).all()
    submissions = Submission.query.filter_by(candidate_id=candidate.id).order_by(Submission.created_at.desc()).all()
    status_history = (
        CandidateStatusHistory.query.filter_by(candidate_id=candidate.id)
        .order_by(CandidateStatusHistory.changed_at.desc())
        .all()
    )

    return render_template(
        "candidates/detail.html",
        candidate=candidate,
        notes=notes,
        tasks=tasks,
        submissions=submissions,
        status_history=status_history,
    )


@candidates_bp.get("/candidates/<int:candidate_id>/edit")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def edit_candidate(candidate_id: int):
    candidate = Candidate.query.get_or_404(candidate_id)
    recruiters = User.query.join(User.role).filter(User.role.has(name="recruiter")).all()
    return render_template("candidates/edit.html", candidate=candidate, recruiters=recruiters)


@candidates_bp.post("/candidates/<int:candidate_id>/update")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def update_candidate(candidate_id: int):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.full_name = request.form.get("full_name", candidate.full_name).strip() or candidate.full_name
    candidate.first_name = request.form.get("first_name") or None
    candidate.last_name = request.form.get("last_name") or None
    candidate.phone = request.form.get("phone") or None
    candidate.email = request.form.get("email") or None
    candidate.location = request.form.get("location") or None
    candidate.primary_skills = request.form.get("primary_skills") or None
    candidate.years_experience = _to_float(request.form.get("years_experience"))
    candidate.source = request.form.get("source") or None
    candidate.owner_user_id = _to_int(request.form.get("owner_user_id"))
    candidate.notes_summary = request.form.get("notes_summary") or None
    candidate.updated_by = current_user.id

    upload = request.files.get("resume")
    if upload and upload.filename:
        try:
            candidate.resume_file_path = save_uploaded_file(upload, subfolder="resumes")
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("candidates.edit_candidate", candidate_id=candidate.id))

    add_activity("update", "candidate", candidate.id, f"Updated candidate {candidate.full_name}")
    db.session.commit()
    flash("Candidate updated.", "success")
    return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))


@candidates_bp.post("/candidates/<int:candidate_id>/status")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def update_candidate_status(candidate_id: int):
    candidate = Candidate.query.get_or_404(candidate_id)
    new_status = request.form.get("status", "").strip()
    remarks = request.form.get("remarks", "").strip()

    if new_status not in CANDIDATE_STATUSES:
        flash("Invalid candidate status.", "danger")
        return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))

    old_status = candidate.status
    candidate.status = new_status
    candidate.updated_by = current_user.id
    history = CandidateStatusHistory(
        candidate_id=candidate.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        remarks=remarks or None,
    )
    db.session.add(history)
    add_activity(
        "status_change",
        "candidate",
        candidate.id,
        f"Candidate {candidate.full_name} moved from {old_status} to {new_status}",
    )
    db.session.commit()
    flash("Candidate status updated.", "success")
    return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))


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


def _forbidden_redirect():
    flash("You do not have permission for this area.", "danger")
    return redirect(url_for("reports.dashboard"))
