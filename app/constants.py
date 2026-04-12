from __future__ import annotations

ROLES = ["owner", "admin", "recruiter", "hr", "employee"]

CANDIDATE_STATUSES = [
    "new",
    "screening",
    "submitted",
    "interview",
    "selected",
    "joined",
    "rejected",
    "on_hold",
]

JOB_STATUSES = ["open", "on_hold", "closed"]

SUBMISSION_STATUSES = [
    "submitted",
    "under_review",
    "interview",
    "rejected",
    "offered",
    "joined",
]

EMPLOYEE_STATUSES = ["active", "inactive", "completed", "on_hold"]
EMPLOYMENT_TYPES = ["employee", "contractor"]

PROJECT_STATUSES = ["active", "completed", "on_hold"]

TIMESHEET_STATUSES = ["draft", "submitted", "approved", "rejected"]

TASK_PRIORITIES = ["low", "medium", "high"]
TASK_STATUSES = ["open", "in_progress", "done", "cancelled"]

NOTE_TYPES = ["call", "email", "internal", "feedback", "followup"]

ENTITY_TYPES = ["candidate", "client", "job", "submission", "employee", "project", "general"]

ALLOWED_ATTACHMENT_ENTITY_TYPES = ["candidate", "employee", "submission", "project"]
