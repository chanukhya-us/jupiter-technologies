from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, url_for
from flask_login import current_user
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import BACKUP_DIR, UPLOAD_DIR, config_by_name

from .cli import register_cli_commands
from .constants import (
    CANDIDATE_STATUSES,
    EMPLOYEE_STATUSES,
    EMPLOYMENT_TYPES,
    ENTITY_TYPES,
    JOB_STATUSES,
    NOTE_TYPES,
    PROJECT_STATUSES,
    ROLES,
    SUBMISSION_STATUSES,
    TASK_PRIORITIES,
    TASK_STATUSES,
    TIMESHEET_STATUSES,
)
from .extensions import db, login_manager
from .models import User


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    register_cli_commands(app)

    from .auth.routes import auth_bp
    from .audit.routes import audit_bp
    from .candidates.routes import candidates_bp
    from .clients.routes import clients_bp
    from .employees.routes import employees_bp
    from .jobs.routes import jobs_bp
    from .notes.routes import notes_bp
    from .projects.routes import projects_bp
    from .reports.routes import reports_bp
    from .submissions.routes import submissions_bp
    from .tasks.routes import tasks_bp
    from .timesheets.routes import timesheets_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(timesheets_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(audit_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("reports.dashboard"))
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_shared_options():
        user_options = []
        if current_user.is_authenticated:
            user_options = User.query.order_by(User.full_name.asc()).all()
        return {
            "roles": ROLES,
            "candidate_statuses": CANDIDATE_STATUSES,
            "job_statuses": JOB_STATUSES,
            "submission_statuses": SUBMISSION_STATUSES,
            "employee_statuses": EMPLOYEE_STATUSES,
            "employment_types": EMPLOYMENT_TYPES,
            "project_statuses": PROJECT_STATUSES,
            "timesheet_statuses": TIMESHEET_STATUSES,
            "task_priorities": TASK_PRIORITIES,
            "task_statuses": TASK_STATUSES,
            "note_types": NOTE_TYPES,
            "entity_types": ENTITY_TYPES,
            "users": user_options,
        }

    return app
