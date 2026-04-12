from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..constants import TIMESHEET_STATUSES
from ..decorators import roles_required
from ..extensions import db
from ..models import Employee, Timesheet
from ..utils import add_activity, build_donut_chart, parse_date, utcnow

timesheets_bp = Blueprint("timesheets", __name__)


@timesheets_bp.get("/timesheets")
@login_required
def list_timesheets():
    if current_user.role.name == "employee":
        employee = _employee_record_for_current_user()
        if employee is None:
            flash("No employee profile linked to this account.", "warning")
            charts = {
                "status": build_donut_chart([], preferred_order=TIMESHEET_STATUSES),
                "employee": build_donut_chart([], empty_label="Unassigned"),
            }
            return render_template("timesheets/list.html", timesheets=[], charts=charts)
        timesheets = Timesheet.query.filter_by(employee_id=employee.id).order_by(Timesheet.created_at.desc()).all()
        charts = {
            "status": build_donut_chart(
                [timesheet.status for timesheet in timesheets],
                preferred_order=TIMESHEET_STATUSES,
            ),
            "employee": build_donut_chart(
                [timesheet.employee.full_name if timesheet.employee else None for timesheet in timesheets],
                empty_label="Unassigned",
                top_n=6,
            ),
        }
        return render_template("timesheets/list.html", timesheets=timesheets, charts=charts)

    timesheets = Timesheet.query.order_by(Timesheet.created_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            [timesheet.status for timesheet in timesheets],
            preferred_order=TIMESHEET_STATUSES,
        ),
        "employee": build_donut_chart(
            [timesheet.employee.full_name if timesheet.employee else None for timesheet in timesheets],
            empty_label="Unassigned",
            top_n=6,
        ),
    }
    return render_template("timesheets/list.html", timesheets=timesheets, charts=charts)


@timesheets_bp.get("/timesheets/new")
@login_required
def new_timesheet():
    if current_user.role.name == "employee":
        employees = [e for e in [_employee_record_for_current_user()] if e is not None]
    else:
        employees = Employee.query.order_by(Employee.full_name.asc()).all()
    return render_template("timesheets/new.html", employees=employees)


@timesheets_bp.post("/timesheets")
@login_required
def create_timesheet():
    employee_id = _to_int(request.form.get("employee_id"))
    if current_user.role.name == "employee":
        own = _employee_record_for_current_user()
        if own is None:
            flash("No employee profile linked to this account.", "danger")
            return redirect(url_for("timesheets.new_timesheet"))
        employee_id = own.id

    if not employee_id:
        flash("Employee is required.", "danger")
        return redirect(url_for("timesheets.new_timesheet"))

    week_start = parse_date(request.form.get("week_start"))
    week_end = parse_date(request.form.get("week_end"))
    total_hours = _to_float(request.form.get("total_hours"))

    if not week_start or not week_end or total_hours is None:
        flash("Week start, week end, and total hours are required.", "danger")
        return redirect(url_for("timesheets.new_timesheet"))

    duplicate = Timesheet.query.filter_by(
        employee_id=employee_id,
        week_start=week_start,
        week_end=week_end,
    ).first()
    if duplicate is not None:
        flash("Timesheet already exists for this employee and week.", "warning")
        return redirect(url_for("timesheets.timesheet_detail", timesheet_id=duplicate.id))

    timesheet = Timesheet(
        employee_id=employee_id,
        week_start=week_start,
        week_end=week_end,
        total_hours=total_hours,
        status="draft",
    )
    db.session.add(timesheet)
    db.session.flush()

    add_activity("create", "timesheet", timesheet.id, f"Created timesheet {timesheet.id}")
    db.session.commit()
    flash("Timesheet created in draft state.", "success")
    return redirect(url_for("timesheets.timesheet_detail", timesheet_id=timesheet.id))


@timesheets_bp.get("/timesheets/<int:timesheet_id>")
@login_required
def timesheet_detail(timesheet_id: int):
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    if current_user.role.name == "employee":
        own = _employee_record_for_current_user()
        if own is None or own.id != timesheet.employee_id:
            flash("You can only view your own timesheets.", "danger")
            return redirect(url_for("timesheets.list_timesheets"))
    return render_template("timesheets/detail.html", timesheet=timesheet)


@timesheets_bp.post("/timesheets/<int:timesheet_id>/submit")
@login_required
def submit_timesheet(timesheet_id: int):
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    if current_user.role.name == "employee":
        own = _employee_record_for_current_user()
        if own is None or own.id != timesheet.employee_id:
            flash("You can only submit your own timesheet.", "danger")
            return redirect(url_for("timesheets.list_timesheets"))

    if timesheet.status == "approved":
        flash("Approved timesheets are read-only.", "warning")
        return redirect(url_for("timesheets.timesheet_detail", timesheet_id=timesheet.id))

    timesheet.status = "submitted"
    timesheet.submitted_at = utcnow()
    add_activity("status_change", "timesheet", timesheet.id, f"Submitted timesheet {timesheet.id}")
    db.session.commit()
    flash("Timesheet submitted.", "success")
    return redirect(url_for("timesheets.timesheet_detail", timesheet_id=timesheet.id))


@timesheets_bp.post("/timesheets/<int:timesheet_id>/approve")
@login_required
@roles_required("owner", "admin", "hr")
def approve_timesheet(timesheet_id: int):
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    timesheet.status = "approved"
    timesheet.reviewed_by = current_user.id
    timesheet.reviewed_at = utcnow()
    timesheet.review_comments = request.form.get("review_comments") or None
    add_activity("status_change", "timesheet", timesheet.id, f"Approved timesheet {timesheet.id}")
    db.session.commit()
    flash("Timesheet approved.", "success")
    return redirect(url_for("timesheets.timesheet_detail", timesheet_id=timesheet.id))


@timesheets_bp.post("/timesheets/<int:timesheet_id>/reject")
@login_required
@roles_required("owner", "admin", "hr")
def reject_timesheet(timesheet_id: int):
    timesheet = Timesheet.query.get_or_404(timesheet_id)
    timesheet.status = "rejected"
    timesheet.reviewed_by = current_user.id
    timesheet.reviewed_at = utcnow()
    timesheet.review_comments = request.form.get("review_comments") or None
    add_activity("status_change", "timesheet", timesheet.id, f"Rejected timesheet {timesheet.id}")
    db.session.commit()
    flash("Timesheet rejected.", "warning")
    return redirect(url_for("timesheets.timesheet_detail", timesheet_id=timesheet.id))


def _employee_record_for_current_user() -> Employee | None:
    if not current_user.email:
        return None
    return Employee.query.filter_by(email=current_user.email).first()


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
