from __future__ import annotations

from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from ..constants import ENTITY_TYPES, NOTE_TYPES
from ..extensions import db
from ..models import Note
from ..utils import add_activity

notes_bp = Blueprint("notes", __name__)


@notes_bp.post("/notes")
@login_required
def create_note():
    entity_type = request.form.get("entity_type", "").strip()
    entity_id = request.form.get("entity_id", "").strip()
    note_type = request.form.get("note_type", "internal").strip()
    content = request.form.get("content", "").strip()
    redirect_to = request.form.get("redirect_to")

    if entity_type not in ENTITY_TYPES or not entity_id.isdigit() or not content:
        flash("Valid note entity and content are required.", "danger")
        return redirect(redirect_to or url_for("reports.dashboard"))

    if note_type not in NOTE_TYPES:
        note_type = "internal"

    note = Note(
        entity_type=entity_type,
        entity_id=int(entity_id),
        note_type=note_type,
        content=content,
        created_by=current_user.id,
    )
    db.session.add(note)
    db.session.flush()
    add_activity(
        "create",
        "note",
        note.id,
        f"Added {note.note_type} note to {entity_type}:{entity_id}",
    )
    db.session.commit()
    flash("Note added.", "success")

    return redirect(redirect_to or url_for("reports.dashboard"))


@notes_bp.post("/notes/<int:note_id>/delete")
@login_required
def delete_note(note_id: int):
    note = Note.query.get_or_404(note_id)
    if current_user.role.name not in {"owner", "admin"}:
        flash("Only owner/admin can delete notes.", "danger")
        return redirect(request.form.get("redirect_to") or url_for("reports.dashboard"))

    db.session.delete(note)
    add_activity("delete", "note", note.id, f"Deleted note {note.id}")
    db.session.commit()
    flash("Note deleted.", "warning")
    return redirect(request.form.get("redirect_to") or url_for("reports.dashboard"))
