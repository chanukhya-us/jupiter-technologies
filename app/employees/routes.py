from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import EMPLOYEE_STATUSES, EMPLOYMENT_TYPES
from ..decorators import roles_required
from ..extensions import db
from ..models import Candidate, Employee, EmployeeProject, Note, Task, Timesheet
from ..utils import add_activity, build_donut_chart, parse_date

employees_bp = Blueprint("employees", __name__)


@employees_bp.get("/employees")
@login_required
def list_employees():
    if current_user.role.name == "employee":
        employee = _employee_record_for_current_user()
        if employee is None:
            flash("No employee record linked to your account.", "warning")
            charts = {
                "status": build_donut_chart([], preferred_order=EMPLOYEE_STATUSES),
                "employment_type": build_donut_chart([], preferred_order=EMPLOYMENT_TYPES),
            }
            return render_template("employees/list.html", employees=[], charts=charts)
        employees = [employee]
        charts = {
            "status": build_donut_chart(
                [employee_item.status for employee_item in employees],
                preferred_order=EMPLOYEE_STATUSES,
            ),
            "employment_type": build_donut_chart(
                [employee_item.employment_type for employee_item in employees],
                preferred_order=EMPLOYMENT_TYPES,
            ),
        }
        return render_template("employees/list.html", employees=employees, charts=charts)

    employees = Employee.query.order_by(Employee.updated_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            [employee.status for employee in employees],
            preferred_order=EMPLOYEE_STATUSES,
        ),
        "employment_type": build_donut_chart(
            [employee.employment_type for employee in employees],
            preferred_order=EMPLOYMENT_TYPES,
        ),
    }
    return render_template("employees/list.html", employees=employees, charts=charts)


@employees_bp.post("/employees/convert-from-candidate/<int:candidate_id>")
@login_required
@roles_required("owner", "admin", "hr")
def convert_candidate(candidate_id: int):
    candidate = Candidate.query.get_or_404(candidate_id)

    if candidate.status not in {"selected", "joined"}:
        flash("Only selected or joined candidates can be converted.", "danger")
        return redirect(url_for("candidates.candidate_detail", candidate_id=candidate.id))

    existing = Employee.query.filter_by(candidate_id=candidate.id).first()
    if existing is not None:
        flash("Candidate already converted to employee.", "warning")
        return redirect(url_for("employees.employee_detail", employee_id=existing.id))

    employee = Employee(
        candidate_id=candidate.id,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        employment_type=request.form.get("employment_type") or "employee",
        start_date=parse_date(request.form.get("start_date")),
        status="active",
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(employee)
    db.session.flush()

    add_activity(
        "create",
        "employee",
        employee.id,
        f"Converted candidate {candidate.full_name} to employee {employee.full_name}",
    )
    db.session.commit()
    flash("Candidate converted to employee.", "success")
    return redirect(url_for("employees.employee_detail", employee_id=employee.id))


@employees_bp.get("/employees/<int:employee_id>")
@login_required
def employee_detail(employee_id: int):
    employee = Employee.query.get_or_404(employee_id)

    if current_user.role.name == "employee":
        own_record = _employee_record_for_current_user()
        if own_record is None or own_record.id != employee.id:
            flash("You can only view your own record.", "danger")
            return redirect(url_for("employees.list_employees"))

    assignments = EmployeeProject.query.filter_by(employee_id=employee.id).order_by(EmployeeProject.created_at.desc()).all()
    timesheets = Timesheet.query.filter_by(employee_id=employee.id).order_by(Timesheet.created_at.desc()).all()
    notes = Note.query.filter_by(entity_type="employee", entity_id=employee.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="employee", entity_id=employee.id).order_by(Task.created_at.desc()).all()
    return render_template(
        "employees/detail.html",
        employee=employee,
        assignments=assignments,
        timesheets=timesheets,
        notes=notes,
        tasks=tasks,
    )


@employees_bp.post("/employees/<int:employee_id>/update")
@login_required
def update_employee(employee_id: int):
    employee = Employee.query.get_or_404(employee_id)

    if current_user.role.name == "employee":
        own_record = _employee_record_for_current_user()
        if own_record is None or own_record.id != employee.id:
            flash("You can only update your own profile.", "danger")
            return redirect(url_for("employees.list_employees"))

    if current_user.role.name == "employee":
        employee.phone = request.form.get("phone") or employee.phone
        employee.reporting_manager = request.form.get("reporting_manager") or employee.reporting_manager
    else:
        employee.full_name = request.form.get("full_name", employee.full_name).strip() or employee.full_name
        employee.email = request.form.get("email") or None
        employee.phone = request.form.get("phone") or None
        employee.client_id = _to_int(request.form.get("client_id"))
        employee.start_date = parse_date(request.form.get("start_date"))
        employee.end_date = parse_date(request.form.get("end_date"))
        employee.employment_type = request.form.get("employment_type") or employee.employment_type
        employee.reporting_manager = request.form.get("reporting_manager") or None
        status = request.form.get("status", employee.status)
        if status in EMPLOYEE_STATUSES:
            employee.status = status
        employee.billing_status = request.form.get("billing_status") or employee.billing_status

    employee.updated_by = current_user.id
    add_activity("update", "employee", employee.id, f"Updated employee {employee.full_name}")
    db.session.commit()
    flash("Employee updated.", "success")
    return redirect(url_for("employees.employee_detail", employee_id=employee.id))


def _to_int(value: str | None) -> int | None:
    if value and value.isdigit():
        return int(value)
    return None


def _employee_record_for_current_user() -> Employee | None:
    if not current_user.email:
        return None
    return Employee.query.filter_by(email=current_user.email).first()
