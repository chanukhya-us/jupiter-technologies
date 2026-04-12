from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import ENTITY_TYPES, TASK_PRIORITIES, TASK_STATUSES
from ..extensions import db
from ..models import Task, User
from ..utils import add_activity, build_donut_chart, parse_date

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/tasks")
@login_required
def list_tasks():
    query = Task.query

    if current_user.role.name == "employee":
        query = query.filter(Task.assigned_user_id == current_user.id)

    status = request.args.get("status", "").strip()
    assigned_user_id = request.args.get("assigned_user_id", "").strip()

    if status:
        query = query.filter(Task.status == status)
    if assigned_user_id.isdigit() and current_user.role.name != "employee":
        query = query.filter(Task.assigned_user_id == int(assigned_user_id))

    tasks = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            [task.status for task in tasks],
            preferred_order=TASK_STATUSES,
        ),
        "priority": build_donut_chart(
            [task.priority for task in tasks],
            preferred_order=TASK_PRIORITIES,
        ),
    }
    users = User.query.order_by(User.full_name.asc()).all()
    today = datetime.now(tz=UTC).date()

    return render_template(
        "tasks/list.html",
        tasks=tasks,
        charts=charts,
        users=users,
        today=today,
        filters={"status": status, "assigned_user_id": assigned_user_id},
    )


@tasks_bp.post("/tasks")
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title is required.", "danger")
        return redirect(request.referrer or url_for("tasks.list_tasks"))

    assigned_user_id = _to_int(request.form.get("assigned_user_id"))
    if current_user.role.name == "employee":
        assigned_user_id = current_user.id

    entity_type = request.form.get("entity_type") or "general"
    if entity_type not in ENTITY_TYPES:
        entity_type = "general"

    task = Task(
        title=title,
        description=request.form.get("description") or None,
        entity_type=entity_type,
        entity_id=_to_int(request.form.get("entity_id")),
        assigned_user_id=assigned_user_id,
        priority=request.form.get("priority") if request.form.get("priority") in TASK_PRIORITIES else "medium",
        due_date=parse_date(request.form.get("due_date")),
        status=request.form.get("status") if request.form.get("status") in TASK_STATUSES else "open",
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(task)
    db.session.flush()
    add_activity("create", "task", task.id, f"Created task {task.title}")
    db.session.commit()
    flash("Task created.", "success")

    redirect_target = request.form.get("redirect_to")
    if redirect_target:
        return redirect(redirect_target)
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.post("/tasks/<int:task_id>/update")
@login_required
def update_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if current_user.role.name == "employee" and task.assigned_user_id != current_user.id:
        flash("You can only update your own tasks.", "danger")
        return redirect(url_for("tasks.list_tasks"))

    if task.status == "done" and current_user.role.name == "employee":
        flash("Completed tasks are read-only for employees.", "warning")
        return redirect(url_for("tasks.list_tasks"))

    task.title = request.form.get("title", task.title).strip() or task.title
    task.description = request.form.get("description") or None

    entity_type = request.form.get("entity_type") or task.entity_type
    if entity_type in ENTITY_TYPES:
        task.entity_type = entity_type

    if current_user.role.name != "employee":
        task.assigned_user_id = _to_int(request.form.get("assigned_user_id"))

    priority = request.form.get("priority")
    if priority in TASK_PRIORITIES:
        task.priority = priority

    status = request.form.get("status")
    if status in TASK_STATUSES:
        task.status = status

    task.entity_id = _to_int(request.form.get("entity_id"))
    task.due_date = parse_date(request.form.get("due_date"))
    task.updated_by = current_user.id

    add_activity("update", "task", task.id, f"Updated task {task.title}")
    db.session.commit()
    flash("Task updated.", "success")

    redirect_target = request.form.get("redirect_to")
    if redirect_target:
        return redirect(redirect_target)
    return redirect(url_for("tasks.list_tasks"))


@tasks_bp.post("/tasks/<int:task_id>/complete")
@login_required
def complete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    if current_user.role.name == "employee" and task.assigned_user_id != current_user.id:
        flash("You can only complete your own tasks.", "danger")
        return redirect(url_for("tasks.list_tasks"))

    task.status = "done"
    task.updated_by = current_user.id
    add_activity("status_change", "task", task.id, f"Completed task {task.title}")
    db.session.commit()
    flash("Task marked as complete.", "success")

    redirect_target = request.form.get("redirect_to")
    if redirect_target:
        return redirect(redirect_target)
    return redirect(url_for("tasks.list_tasks"))


def _to_int(value: str | None) -> int | None:
    if value and value.isdigit():
        return int(value)
    return None
