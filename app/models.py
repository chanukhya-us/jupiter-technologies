from __future__ import annotations

from datetime import UTC, date, datetime

from flask_login import UserMixin

from .extensions import db


def now_utc() -> datetime:
    return datetime.now(tz=UTC)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc
    )


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    role = db.relationship("Role")


class Candidate(TimestampMixin, db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    candidate_code = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    full_name = db.Column(db.String(240), nullable=False, index=True)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255), index=True)
    location = db.Column(db.String(255))
    primary_skills = db.Column(db.Text)
    years_experience = db.Column(db.Float)
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, index=True, default="new")
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    resume_file_path = db.Column(db.String(500))
    notes_summary = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    owner = db.relationship("User", foreign_keys=[owner_user_id])


class CandidateStatusHistory(db.Model):
    __tablename__ = "candidate_status_history"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False, index=True)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    remarks = db.Column(db.Text)

    candidate = db.relationship("Candidate")
    user = db.relationship("User")


class Client(TimestampMixin, db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(50), unique=True)
    company_name = db.Column(db.String(240), nullable=False, index=True)
    contact_person = db.Column(db.String(200))
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))


class Job(TimestampMixin, db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    job_code = db.Column(db.String(50), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    title = db.Column(db.String(240), nullable=False)
    location = db.Column(db.String(255))
    work_type = db.Column(db.String(100))
    employment_type = db.Column(db.String(100))
    required_skills = db.Column(db.Text)
    min_experience = db.Column(db.Float)
    max_experience = db.Column(db.Float)
    salary_or_rate = db.Column(db.String(100))
    status = db.Column(db.String(50), nullable=False, default="open", index=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    client = db.relationship("Client")
    owner = db.relationship("User", foreign_keys=[owner_user_id])


class Submission(TimestampMixin, db.Model):
    __tablename__ = "submissions"
    __table_args__ = (
        db.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job_submission"),
    )

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    recruiter_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    status = db.Column(db.String(50), nullable=False, default="submitted", index=True)
    interview_date = db.Column(db.DateTime(timezone=True))
    feedback = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    candidate = db.relationship("Candidate")
    job = db.relationship("Job")
    recruiter = db.relationship("User", foreign_keys=[recruiter_user_id])


class SubmissionStatusHistory(db.Model):
    __tablename__ = "submission_status_history"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=False, index=True)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    remarks = db.Column(db.Text)

    submission = db.relationship("Submission")


class Employee(TimestampMixin, db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(50), unique=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), unique=True, index=True)
    full_name = db.Column(db.String(240), nullable=False)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(50))
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), index=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    employment_type = db.Column(db.String(50), default="employee")
    reporting_manager = db.Column(db.String(240))
    status = db.Column(db.String(50), nullable=False, default="active", index=True)
    billing_status = db.Column(db.String(50), nullable=False, default="pending")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    candidate = db.relationship("Candidate")
    client = db.relationship("Client")


class Project(TimestampMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(50), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), index=True)
    project_name = db.Column(db.String(240), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default="active", index=True)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    client = db.relationship("Client")


class EmployeeProject(TimestampMixin, db.Model):
    __tablename__ = "employee_projects"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    assigned_from = db.Column(db.Date)
    assigned_to = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default="active")
    notes = db.Column(db.Text)

    employee = db.relationship("Employee")
    project = db.relationship("Project")


class Timesheet(TimestampMixin, db.Model):
    __tablename__ = "timesheets"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "week_start", "week_end", name="uq_employee_week_range"),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    total_hours = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="draft", index=True)
    submitted_at = db.Column(db.DateTime(timezone=True))
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    reviewed_at = db.Column(db.DateTime(timezone=True))
    review_comments = db.Column(db.Text)

    employee = db.relationship("Employee")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])


class Task(TimestampMixin, db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), nullable=False)
    description = db.Column(db.Text)
    entity_type = db.Column(db.String(50), nullable=False, default="general")
    entity_id = db.Column(db.Integer)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    priority = db.Column(db.String(50), nullable=False, default="medium")
    due_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default="open", index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    assigned_user = db.relationship("User", foreign_keys=[assigned_user_id])


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    note_type = db.Column(db.String(50), nullable=False, default="internal")
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)

    user = db.relationship("User")


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(120))
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, index=True)
    message = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)

    user = db.relationship("User")


class MarketerProfile(TimestampMixin, db.Model):
    __tablename__ = "marketer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True, index=True)
    manager_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    timezone = db.Column(db.String(100), nullable=False, default="America/New_York")
    workdays_mask = db.Column(db.String(20), nullable=False, default="1,1,1,1,1,0,0")
    daily_cutoff_local_time = db.Column(db.String(5), nullable=False, default="18:00")
    reminder_enabled = db.Column(db.Boolean, nullable=False, default=True)
    reminder_times_local = db.Column(db.Text, nullable=False, default="16:00,17:30")
    escalation_after_misses = db.Column(db.Integer, nullable=False, default=3)

    user = db.relationship("User", foreign_keys=[user_id])
    manager = db.relationship("User", foreign_keys=[manager_user_id])


class MarketerDailyLog(TimestampMixin, db.Model):
    __tablename__ = "marketer_daily_logs"
    __table_args__ = (
        db.UniqueConstraint("marketer_user_id", "log_date", name="uq_marketer_daily_log_date"),
        db.Index(
            "ix_marketer_daily_logs_marketer_date_status",
            "marketer_user_id",
            "log_date",
            "status",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    marketer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="draft", index=True)
    jobs_applied = db.Column(db.Integer, nullable=False, default=0)
    follow_ups = db.Column(db.Integer, nullable=False, default=0)
    interviews_scheduled = db.Column(db.Integer, nullable=False, default=0)
    pay_discussions = db.Column(db.Integer, nullable=False, default=0)
    job_type = db.Column(db.String(20), nullable=False, default="unknown", index=True)
    hourly_rate_min = db.Column(db.Float)
    hourly_rate_max = db.Column(db.Float)
    project_duration_weeks = db.Column(db.Integer)
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime(timezone=True))
    submitted_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    marketer = db.relationship("User", foreign_keys=[marketer_user_id])
    submitted_by = db.relationship("User", foreign_keys=[submitted_by_user_id])


class MarketerNotification(TimestampMixin, db.Model):
    __tablename__ = "marketer_notifications"
    __table_args__ = (
        db.UniqueConstraint("idempotency_key", name="uq_marketer_notification_idempotency"),
        db.Index("ix_marketer_notifications_marketer_date", "marketer_user_id", "target_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    marketer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    target_date = db.Column(db.Date, nullable=False, index=True)
    notification_type = db.Column(db.String(20), nullable=False, index=True)
    channel = db.Column(db.String(20), nullable=False, default="in_app")
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    idempotency_key = db.Column(db.String(255), nullable=False)
    payload_json = db.Column(db.Text)
    message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime(timezone=True))
    read_at = db.Column(db.DateTime(timezone=True))

    user = db.relationship("User", foreign_keys=[user_id])
    marketer = db.relationship("User", foreign_keys=[marketer_user_id])
