from __future__ import annotations

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.constants import ROLES
from app.extensions import db
from app.models import Candidate, Client, Job, Role, User


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        for role_name in ROLES:
            db.session.add(Role(name=role_name, description=f"{role_name} role"))
        db.session.flush()

        owner_role = Role.query.filter_by(name="owner").first()
        recruiter_role = Role.query.filter_by(name="recruiter").first()
        hr_role = Role.query.filter_by(name="hr").first()
        employee_role = Role.query.filter_by(name="employee").first()

        owner = User(
            full_name="Owner User",
            username="owner",
            email="owner@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=owner_role.id,
        )
        recruiter = User(
            full_name="Recruiter User",
            username="recruiter",
            email="recruiter@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=recruiter_role.id,
        )
        hr = User(
            full_name="HR User",
            username="hr",
            email="hr@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=hr_role.id,
        )
        employee_user = User(
            full_name="Employee User",
            username="employee",
            email="employee@example.com",
            password_hash=generate_password_hash("password123"),
            role_id=employee_role.id,
        )
        db.session.add_all([owner, recruiter, hr, employee_user])
        db.session.flush()

        client = Client(
            company_name="Acme Corp",
            created_by=owner.id,
            updated_by=owner.id,
        )
        db.session.add(client)
        db.session.flush()

        candidate = Candidate(
            full_name="John Candidate",
            email="john@example.com",
            status="selected",
            owner_user_id=recruiter.id,
            created_by=recruiter.id,
            updated_by=recruiter.id,
        )
        db.session.add(candidate)
        db.session.flush()

        job = Job(
            client_id=client.id,
            title="Backend Engineer",
            status="open",
            owner_user_id=recruiter.id,
            created_by=recruiter.id,
            updated_by=recruiter.id,
        )
        db.session.add(job)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username: str, password: str = "password123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
