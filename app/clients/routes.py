from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..decorators import roles_required
from ..extensions import db
from ..models import Client, Job, Note, Project, Task
from ..utils import add_activity, build_donut_chart

clients_bp = Blueprint("clients", __name__)


@clients_bp.get("/clients")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def list_clients():
    search = request.args.get("search", "").strip()
    query = Client.query
    if search:
        query = query.filter(Client.company_name.ilike(f"%{search}%"))
    clients = query.order_by(Client.updated_at.desc()).all()
    charts = {
        "status": build_donut_chart(
            ["active" if client.is_active else "inactive" for client in clients],
            preferred_order=["active", "inactive"],
        ),
        "contact": build_donut_chart(
            ["with contact" if client.contact_person else "missing contact" for client in clients],
            preferred_order=["with contact", "missing contact"],
        ),
    }
    return render_template("clients/list.html", clients=clients, search=search, charts=charts)


@clients_bp.get("/clients/new")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def new_client():
    return render_template("clients/new.html")


@clients_bp.post("/clients")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def create_client():
    company_name = request.form.get("company_name", "").strip()
    if not company_name:
        flash("Company name is required.", "danger")
        return redirect(url_for("clients.new_client"))

    client = Client(
        company_name=company_name,
        client_code=request.form.get("client_code") or None,
        contact_person=request.form.get("contact_person") or None,
        email=request.form.get("email") or None,
        phone=request.form.get("phone") or None,
        address=request.form.get("address") or None,
        notes=request.form.get("notes") or None,
        is_active=bool(request.form.get("is_active", "1") == "1"),
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    db.session.add(client)
    db.session.flush()
    add_activity("create", "client", client.id, f"Created client {client.company_name}")
    db.session.commit()
    flash("Client created.", "success")
    return redirect(url_for("clients.client_detail", client_id=client.id))


@clients_bp.get("/clients/<int:client_id>")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def client_detail(client_id: int):
    client = Client.query.get_or_404(client_id)
    jobs = Job.query.filter_by(client_id=client.id).order_by(Job.created_at.desc()).all()
    projects = Project.query.filter_by(client_id=client.id).order_by(Project.created_at.desc()).all()
    notes = Note.query.filter_by(entity_type="client", entity_id=client.id).order_by(Note.created_at.desc()).all()
    tasks = Task.query.filter_by(entity_type="client", entity_id=client.id).order_by(Task.created_at.desc()).all()
    return render_template(
        "clients/detail.html",
        client=client,
        jobs=jobs,
        projects=projects,
        notes=notes,
        tasks=tasks,
    )


@clients_bp.post("/clients/<int:client_id>/update")
@login_required
@roles_required("owner", "admin", "recruiter", "hr")
def update_client(client_id: int):
    client = Client.query.get_or_404(client_id)
    client.company_name = request.form.get("company_name", client.company_name).strip() or client.company_name
    client.client_code = request.form.get("client_code") or None
    client.contact_person = request.form.get("contact_person") or None
    client.email = request.form.get("email") or None
    client.phone = request.form.get("phone") or None
    client.address = request.form.get("address") or None
    client.notes = request.form.get("notes") or None
    client.is_active = bool(request.form.get("is_active", "1") == "1")
    client.updated_by = current_user.id

    add_activity("update", "client", client.id, f"Updated client {client.company_name}")
    db.session.commit()
    flash("Client updated.", "success")
    return redirect(url_for("clients.client_detail", client_id=client.id))
