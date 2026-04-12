from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import PROJECT_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import Client, Employee, EmployeeProject, Note, Project, Task
from ..utils import add_activity, build_donut_chart, parse_date

projects_bp = Blueprint("projects", __name__)


@projects_bp.get("/projects")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def list_projects():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            [project.status for project in projects],
            preferred_order=PROJECT_STATUSES,
        ),
        "client": build_donut_chart(
            [project.client.company_name if project.client else None for project in projects],
            empty_label="Unassigned",
            top_n=6,
        ),
    }
    clients = Client.query.order_by(Client.company_name.asc()).all()
    return render_template("projects/list.html", projects=projects, clients=clients, charts=charts)


@projects_bp.post("/projects")
@login_required
@roles_required("owner", "admin", "hr")
def create_project():
    project_name = request.form.get("project_name", "").strip()
    if not project_name:
        flash("Project name is required.", "danger")
        return redirect(url_for("projects.list_projects"))

    project = Project(
        project_name=project_name,
        project_code=request.form.get("project_code") or None,
        client_id=_to_int(request.form.get("client_id")),
        start_date=parse_date(request.form.get("start_date")),
        end_date=parse_date(request.form.get("end_date")),
        status=request.form.get("status") or "active",
        notes=request.form.get("notes") or None,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(project)
    db.session.flush()
    add_activity("create", "project", project.id, f"Created project {project.project_name}")
    db.session.commit()
    flash("Project created.", "success")
    return redirect(url_for("projects.project_detail", project_id=project.id))


@projects_bp.get("/projects/<int:project_id>")
@login_required
@roles_required("owner", "admin", "recruiter", "hr", "employee")
def project_detail(project_id: int):
    project = Project.query.get_or_404(project_id)
    assignments = EmployeeProject.query.filter_by(project_id=project.id).order_by(EmployeeProject.created_at.desc()).all()
    notes = Note.query.filter_by(entity_type="project", entity_id=project.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="project", entity_id=project.id).order_by(Task.created_at.desc()).all()
    employees = Employee.query.order_by(Employee.full_name.asc()).all()
    return render_template(
        "projects/detail.html",
        project=project,
        assignments=assignments,
        notes=notes,
        tasks=tasks,
        employees=employees,
    )


@projects_bp.post("/projects/<int:project_id>/assign-employee")
@login_required
@roles_required("owner", "admin", "hr")
def assign_employee(project_id: int):
    project = Project.query.get_or_404(project_id)
    employee_id = _to_int(request.form.get("employee_id"))
    if not employee_id:
        flash("Employee is required.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project.id))

    assignment = EmployeeProject(
        employee_id=employee_id,
        project_id=project.id,
        assigned_from=parse_date(request.form.get("assigned_from")),
        assigned_to=parse_date(request.form.get("assigned_to")),
        status=request.form.get("status") or "active",
        notes=request.form.get("notes") or None,
    )
    db.session.add(assignment)
    db.session.flush()
    add_activity(
        "create",
        "employee_project",
        assignment.id,
        f"Assigned employee {assignment.employee_id} to project {project.project_name}",
    )
    db.session.commit()
    flash("Employee assigned.", "success")
    return redirect(url_for("projects.project_detail", project_id=project.id))


def _to_int(value: str | None) -> int | None:
    if value and value.isdigit():
        return int(value)
    return None
