# Jupiter Technologies — Application Architecture

## Overview

Jupiter Technologies is a Flask-based staffing and recruiting management platform. It follows a **blueprint-based modular architecture** where each feature area is an isolated module with its own routes, templates, and logic.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser / Client                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP
┌─────────────────────────▼───────────────────────────────────────┐
│                      Flask Application                          │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │   auth   │  │candidates│  │   jobs   │  │  submissions │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ clients  │  │employees │  │ projects │  │  timesheets  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  tasks   │  │  notes   │  │ reports  │  │   marketer   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
│  ┌──────────┐                                                   │
│  │  audit   │                                                   │
│  └──────────┘                                                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Shared Layer                               │   │
│  │  utils.py │ models.py │ decorators.py │ constants.py   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SQLAlchemy ORM
┌─────────────────────────▼───────────────────────────────────────┐
│                     SQLite Database                             │
│              (PostgreSQL / MySQL ready)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Lifecycle

```
Browser Request
      │
      ▼
Flask Router  ──► @login_required  ──► Not logged in? → /login
      │
      ▼
@roles_required(*roles)  ──► Wrong role? → 403 Forbidden
      │
      ▼
Route Handler
      │
      ├── Query DB via SQLAlchemy
      ├── Build chart data (utils.build_donut_chart)
      ├── add_activity() → writes to ActivityLog
      ├── db.session.commit()
      │
      ▼
render_template(...)  ──► Jinja2 → HTML Response
```

---

## Authentication Flow

```
POST /login
      │
      ▼
User.query.filter_by(username=..., is_active=True)
      │
      ├── Not found or wrong password → flash error → redirect /login
      │
      ▼
check_password_hash(user.password_hash, password)
      │
      ▼
login_user(user)  ──► Flask-Login sets session cookie
      │
      ▼
add_activity("login", "user", user.id, ...)
      │
      ▼
redirect → /dashboard
```

---

## Role-Based Access Control

```
Roles (least → most privileged):
  employee   → own timesheets, own tasks, own employee record
  marketer   → marketer-activity module only
  hr         → employees, projects, timesheets + recruiter access
  recruiter  → candidates, jobs, submissions, clients
  admin      → all modules + audit logs + user management
  owner      → full access (same as admin)

@roles_required("owner", "admin", "recruiter")
      │
      ▼
current_user.role.name in required_roles?
      ├── No  → abort(403)
      └── Yes → proceed
```

---

## Database Schema & Relationships

```
Role ◄──── User
            │
            ├──► Candidate ──► CandidateStatusHistory
            │         │
            │         ▼
            │      Submission ──► SubmissionStatusHistory
            │         │
            │         ▼
            │        Job ◄──── Client
            │                    │
            │                    ▼
            │                 Project ◄──── EmployeeProject
            │                                     │
            ├──► Employee ◄───────────────────────┘
            │         │
            │         ▼
            │      Timesheet
            │
            ├──► Task  (linked to any entity)
            ├──► Note  (linked to any entity)
            ├──► ActivityLog
            │
            └──► MarketerProfile
                      │
                      ▼
                 MarketerDailyLog
                      │
                      ▼
                 MarketerNotification
```

---

## Module Map

| Blueprint | URL Prefix | Roles Allowed | README |
|-----------|-----------|---------------|--------|
| auth | `/login`, `/logout` | public | [auth/README.md](app/auth/README.md) |
| candidates | `/candidates` | owner, admin, recruiter, hr | [candidates/README.md](app/candidates/README.md) |
| jobs | `/jobs` | owner, admin, recruiter, hr | [jobs/README.md](app/jobs/README.md) |
| submissions | `/submissions` | owner, admin, recruiter, hr | [submissions/README.md](app/submissions/README.md) |
| clients | `/clients` | owner, admin, recruiter, hr | [clients/README.md](app/clients/README.md) |
| employees | `/employees` | all roles | [employees/README.md](app/employees/README.md) |
| projects | `/projects` | owner, admin, recruiter, hr | [projects/README.md](app/projects/README.md) |
| timesheets | `/timesheets` | all roles | [timesheets/README.md](app/timesheets/README.md) |
| tasks | `/tasks` | all roles | [tasks/README.md](app/tasks/README.md) |
| notes | `/notes` | all roles | [notes/README.md](app/notes/README.md) |
| marketer | `/marketer-activity` | owner, admin, marketer | [marketer/README.md](app/marketer/README.md) |
| reports | `/dashboard`, `/reports` | all except marketer | [reports/README.md](app/reports/README.md) |
| audit | `/activity-logs` | owner, admin | [audit/README.md](app/audit/README.md) |

---

## Recruitment Pipeline Flow

```
Client Created
      │
      ▼
Job Created (linked to Client)
      │
      ▼
Candidate Created
      │
      ▼
Submission Created (Candidate → Job)
      │
      ▼
Status Progression:
  submitted → under_review → interview → offered → joined
                                       └─────────────────► rejected
      │
      ▼ (on joined)
Convert Candidate → Employee
      │
      ▼
Assign Employee → Project
      │
      ▼
Employee submits Timesheet (weekly)
      │
      ▼
HR/Admin approves or rejects Timesheet
```

---

## Marketer Activity Flow

```
Admin onboards Marketer (creates User + MarketerProfile)
      │
      ▼
Configure Profile (timezone, cutoff time, workdays, reminders)
      │
      ▼
Each workday:
  Marketer creates DailyLog (today or yesterday before cutoff)
      │
      ▼
  Marketer submits log
      │
      ├── Before cutoff → status: "submitted"
      └── After cutoff  → status: "late"
      │
      ▼
Background scheduler (process_marketer_reminders):
  ├── Send reminders at configured times
  ├── After cutoff: mark unsubmitted logs as "missed"
  └── If missed streak ≥ threshold → create escalation notification
```

---

## Shared Utilities

| Function | Location | Purpose |
|----------|----------|---------|
| `build_donut_chart()` | utils.py | Build chart data dict for Chart.js |
| `add_activity()` | utils.py | Write to ActivityLog |
| `save_uploaded_file()` | utils.py | Save file with UUID, validate extension |
| `csv_response()` | utils.py | Stream CSV download |
| `parse_date()` | utils.py | Parse YYYY-MM-DD string |
| `parse_datetime()` | utils.py | Parse multiple datetime formats |
| `roles_required()` | decorators.py | RBAC decorator |
| `ensure_marketer_profile()` | marketer/service.py | Auto-create profile if missing |
| `submit_status_for_log()` | marketer/service.py | Determine submitted vs late |

---

## Frontend Architecture

```
base.html (layout shell)
    │
    ├── Bootstrap 5.3 (CSS framework)
    ├── tokens.css (design tokens / CSS variables)
    ├── app.css (custom styles + animations)
    ├── chart.umd.min.js (Chart.js 4.4)
    └── charts.js (Jupiter chart initializer)
            │
            ├── canvas.rt-donut-chart  → renderDonutChart()
            └── canvas.rt-series-chart → renderSeriesChart()

Data passed to charts via HTML data attributes:
    data-labels='[...]'    ← JSON array (single-quoted to avoid HTML escaping)
    data-values='[...]'
    data-datasets='[...]'
    data-chart-type="bar|line"
```

---

## File Structure

```
jupiter-technologies/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── models.py            # All SQLAlchemy models
│   ├── extensions.py        # db, login_manager instances
│   ├── constants.py         # All status/type enumerations
│   ├── decorators.py        # @roles_required
│   ├── utils.py             # Shared utility functions
│   ├── assets.py            # Static asset manifest loader
│   ├── cli.py               # flask cli seed-db command
│   │
│   ├── auth/                # Authentication
│   ├── candidates/          # Candidate management
│   ├── jobs/                # Job requisitions
│   ├── submissions/         # Submission tracking
│   ├── clients/             # Client management
│   ├── employees/           # Employee management
│   ├── projects/            # Project management
│   ├── timesheets/          # Timesheet workflow
│   ├── tasks/               # Task tracking
│   ├── notes/               # Entity notes
│   ├── marketer/            # Marketer activity + service layer
│   ├── reports/             # Dashboard + CSV exports
│   ├── audit/               # Audit log viewer
│   │
│   ├── static/
│   │   ├── css/             # tokens.css, app.css
│   │   ├── js/              # charts.js
│   │   ├── images/          # brand, icons, partners
│   │   └── vendor/          # chart.umd.min.js
│   │
│   └── templates/           # Jinja2 templates per module
│
├── tests/                   # pytest test suite
├── docs/                    # Screenshots, archive
├── migrations/              # Alembic migrations
├── config.py                # App configuration
├── ARCHITECTURE.md          # This file
└── README.md                # Project overview
```
