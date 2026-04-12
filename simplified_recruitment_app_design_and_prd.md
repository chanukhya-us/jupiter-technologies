# Simplified Recruitment Tracking Web Application
## Full Technical Design Document + Developer-Ready PRD + Phased Build Plan

Version: 1.0  
Prepared for: Local-first, low-cost deployment  
Primary goal: Build a simple, free-to-run recruitment tracking application using SQLite, with no AI features and no paid communication integrations  
Source basis: simplified from the attached AI-Powered Recruitment Operating System requirements, keeping only free and functional capabilities relevant to a lightweight implementation. fileciteturn0file0L1-L20

---

# Part 1. Executive Summary

This document defines a **simplified recruitment operations web application** intended for a small recruiting business, solo recruiter, or lean internal staffing team.

The system is deliberately constrained to:

- run locally or on a single low-cost server
- use SQLite as the database
- avoid AI and paid messaging services
- focus on manual tracking and operational visibility
- support candidate tracking, job tracking, submissions, employee conversion, timesheets, notes, tasks, and basic reporting

This version keeps the practical operational parts of the original concept such as ATS-style candidate flow, CRM-like client/job tracking, employee/project tracking, timesheets, and centralized notes, while removing costly capabilities such as AI workflows, WhatsApp automation, and external service dependencies. fileciteturn0file0L1-L24

---

# Part 2. Product Requirements Document (PRD)

## 2.1 Product name

**Jupiter Technologies**

Working alternatives:
- RecruitOps Local
- HireFlow Simple
- TalentDesk Lite

## 2.2 Product vision

Provide a simple and affordable web application that allows a small team to track the full recruitment lifecycle from candidate intake to placement and post-placement operational tracking, without requiring AI, paid APIs, or enterprise infrastructure.

## 2.3 Problem statement

Small recruiters and staffing teams often manage candidates, clients, jobs, submissions, employee placements, timesheets, and follow-ups across spreadsheets, email, and chat. This creates:

- poor visibility
- missed follow-ups
- duplicate data entry
- weak auditability
- inconsistent candidate and employee tracking

A lightweight local web application can centralize these workflows with minimal operating cost.

## 2.4 Product goals

The product should:

- centralize recruitment tracking in one place
- reduce spreadsheet dependence
- support a clear candidate-to-placement workflow
- track recruiter activity and ownership
- allow basic operational tracking after placement
- provide simple dashboards and exports
- remain low-cost and easy to self-host

## 2.5 Non-goals

The product will not initially include:

- AI ranking or matching
- resume parsing
- email or SMS sending
- WhatsApp integration
- payroll processing
- invoice automation
- accounting integration
- external CRM or ATS integrations
- workflow automation engines
- multi-tenant enterprise SaaS architecture

## 2.6 Target users

### Primary users
- Owner
- Admin
- Recruiter
- HR / Operations

### Secondary users
- Employee / Contractor

## 2.7 User roles and permissions

### Owner
- full access to all modules
- manage users and roles
- view reports and audit logs
- manage app settings

### Admin
- manage operational data across all modules
- maintain clients, jobs, candidates, employees, timesheets, and tasks
- cannot delete owner account

### Recruiter
- create and update candidates
- manage assigned jobs and submissions
- add notes and tasks
- update candidate and submission statuses
- view clients and jobs relevant to work

### HR / Operations
- manage employees and contractors
- manage project assignments
- review and approve timesheets
- update billing readiness

### Employee / Contractor
- log in to submit timesheets
- view own assignment details
- add limited notes if enabled

## 2.8 User stories

### Candidate tracking
- As a recruiter, I want to add a new candidate so I can track them centrally.
- As a recruiter, I want to assign a candidate to myself or another recruiter so ownership is clear.
- As a recruiter, I want to move a candidate through statuses so I can track progress.

### Job tracking
- As an admin, I want to create client jobs so recruiters can submit candidates against them.
- As a recruiter, I want to see all open jobs assigned to me.

### Submission tracking
- As a recruiter, I want to submit a candidate to a job and track interview and hiring outcomes.
- As an owner, I want to view submissions by recruiter and client.

### Placement tracking
- As HR, I want to convert a selected candidate into an employee or contractor record.
- As HR, I want to assign placed employees to projects.

### Timesheets
- As an employee, I want to submit weekly timesheets.
- As HR, I want to approve or reject timesheets.

### Tasks and notes
- As a recruiter, I want to create follow-up tasks so I do not miss candidate or client actions.
- As any internal user, I want to log notes for calls and updates.

### Reporting
- As an owner, I want dashboard summaries and CSV exports so I can track business activity.

## 2.9 Functional requirements

### FR-1 Authentication
- The app must support username/password login.
- The app must support role-based access control.
- Passwords must be securely hashed.

### FR-2 Candidate management
- Create, view, edit, search, and filter candidates.
- Track candidate status.
- Assign candidate owner.
- Store contact details and resume attachment reference.

### FR-3 Client management
- Create and manage client records.
- Associate jobs with clients.

### FR-4 Job management
- Create, update, close, and reopen jobs.
- Assign recruiter ownership.
- Link candidates to jobs through submissions.

### FR-5 Submission management
- Create submissions linking candidate and job.
- Track submission status.
- Add interview notes and decision updates.

### FR-6 Employee conversion
- Convert selected candidate into employee/contractor record.
- Preserve link to original candidate.

### FR-7 Project assignment
- Assign employees to client projects.
- Track active/inactive projects.

### FR-8 Timesheet management
- Allow employee submission of weekly timesheets.
- Allow admin/HR approval or rejection.

### FR-9 Tasks
- Create tasks tied to candidate, client, job, submission, employee, or project.
- Track due date, status, and priority.

### FR-10 Notes and communication log
- Allow users to record manual notes.
- Support note categories such as call, email, internal, and interview feedback.

### FR-11 Dashboard and reports
- Show summary metrics.
- Export selected data sets to CSV.

### FR-12 Audit trail
- Capture create/update/delete-like actions for key entities.
- Record actor, timestamp, entity, and action summary.

## 2.10 Non-functional requirements

### NFR-1 Simplicity
The app should be easy to install and run with minimal setup.

### NFR-2 Low cost
The app should run free locally and work on a single inexpensive VPS if hosted.

### NFR-3 Performance
The app should handle small-team usage and thousands of records on SQLite.

### NFR-4 Maintainability
The app should use simple CRUD patterns and a modular folder structure.

### NFR-5 Security
The app must hash passwords, validate file uploads, and enforce authorization.

### NFR-6 Backupability
Database and uploads folder must be easy to back up and restore.

## 2.11 MVP scope

The MVP includes:

- authentication and roles
- candidate management
- client management
- job management
- submission tracking
- notes
- tasks
- candidate-to-employee conversion
- project tracking
- timesheets
- dashboard
- CSV exports
- activity logs

---

# Part 3. Technical Design Document

## 3.1 Recommended technology stack

### Backend
- **Python 3.12+**
- **Flask** for simplicity
- SQLAlchemy ORM
- Flask-Login or custom session authentication
- WTForms or simple server-side validation

### Frontend
- Jinja2 server-rendered templates
- Bootstrap 5 for styling
- Optional small vanilla JavaScript for interactivity

### Database
- SQLite

### File storage
- local `uploads/` directory for resumes and attachments

### Export
- CSV generation using Python standard library or pandas if needed

### Deployment
- local machine or a single Linux VPS
- Gunicorn + Nginx if hosted

## 3.2 Why Flask + SQLite

This stack is the most suitable for the stated goals because it is:

- free
- easy to develop
- easy to understand
- lightweight
- sufficient for low to moderate internal usage

## 3.3 High-level architecture

```text
Browser
  |
  v
Flask Web App
  |-- Auth Module
  |-- Candidate Module
  |-- Client Module
  |-- Job Module
  |-- Submission Module
  |-- Employee Module
  |-- Project Module
  |-- Timesheet Module
  |-- Task Module
  |-- Notes Module
  |-- Reports Module
  |-- Audit Module
  |
  v
SQLite Database
  |
  v
Local Uploads Folder
```

## 3.4 Deployment modes

### Mode A: Local-only
- runs on one laptop or desktop
- best for personal or office use
- no external access unless manually exposed

### Mode B: Single VPS
- one cheap Linux server
- accessible through browser over HTTPS
- suitable for very small distributed teams

## 3.5 Project folder structure

```text
jupiter-technologies/
├── app.py
├── config.py
├── requirements.txt
├── instance/
│   └── app.db
├── uploads/
├── backups/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   ├── candidates/
│   ├── clients/
│   ├── jobs/
│   ├── submissions/
│   ├── employees/
│   ├── projects/
│   ├── timesheets/
│   ├── tasks/
│   ├── notes/
│   ├── reports/
│   ├── audit/
│   ├── templates/
│   └── static/
└── scripts/
    ├── init_db.py
    ├── backup_db.py
    └── seed_demo_data.py
```

## 3.6 Core modules

### 3.6.1 Auth module
Responsibilities:
- login/logout
- session handling
- role checks
- password reset later if needed

### 3.6.2 Candidate module
Responsibilities:
- CRUD for candidates
- status changes
- owner assignment
- resume attachment link
- candidate detail page with notes, tasks, submissions

### 3.6.3 Client module
Responsibilities:
- CRUD for clients
- contact information
- relationship to jobs and projects

### 3.6.4 Job module
Responsibilities:
- CRUD for jobs
- open/closed state
- recruiter owner
- required skills and rate details

### 3.6.5 Submission module
Responsibilities:
- link candidate and job
- track submission outcomes
- interview notes

### 3.6.6 Employee module
Responsibilities:
- convert selected candidate to employee
- employee status tracking
- link to projects and timesheets

### 3.6.7 Project module
Responsibilities:
- client project records
- employee assignments
- project status

### 3.6.8 Timesheet module
Responsibilities:
- weekly entry
- submit/approve/reject
- reporting export

### 3.6.9 Task module
Responsibilities:
- reminders and action tracking
- due dates and priorities
- entity linking

### 3.6.10 Notes module
Responsibilities:
- manual communication logs
- free-form notes
- categorized note types

### 3.6.11 Reports module
Responsibilities:
- dashboard metrics
- CSV exports
- filtered list reports

### 3.6.12 Audit module
Responsibilities:
- system activity logs
- entity change summaries

---

# Part 4. Database Schema Design

## 4.1 Design principles

- keep schema normalized enough for clean reporting
- keep joins manageable
- use foreign keys consistently
- store timestamps on all business tables
- avoid premature complexity

## 4.2 Entity relationship summary

```text
users ----< tasks
users ----< notes
users ----< activity_logs
users ----< candidates (owner)
users ----< jobs (owner)

clients ----< jobs
clients ----< projects

candidates ----< submissions >---- jobs
candidates ----1 employees

employees ----< timesheets
employees ----< employee_projects >---- projects

candidates/jobs/clients/submissions/employees/projects ----< notes
candidates/jobs/clients/submissions/employees/projects ----< tasks
```

## 4.3 Table definitions

### 4.3.1 roles

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT UNIQUE | owner, admin, recruiter, hr, employee |
| description | TEXT | |

### 4.3.2 users

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| full_name | TEXT | required |
| username | TEXT UNIQUE | required |
| email | TEXT UNIQUE | optional but recommended |
| password_hash | TEXT | required |
| role_id | INTEGER FK -> roles.id | required |
| is_active | BOOLEAN | default true |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.3 candidates

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| candidate_code | TEXT UNIQUE | optional human-readable ID |
| first_name | TEXT | |
| last_name | TEXT | |
| full_name | TEXT | denormalized convenience field |
| phone | TEXT | |
| email | TEXT | indexed |
| location | TEXT | |
| primary_skills | TEXT | comma-separated or plain text |
| years_experience | REAL | |
| source | TEXT | referral, linkedin, portal, etc. |
| status | TEXT | current candidate status |
| owner_user_id | INTEGER FK -> users.id | assigned recruiter |
| resume_file_path | TEXT | local upload path |
| notes_summary | TEXT | optional quick summary |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.4 candidate_status_history

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| candidate_id | INTEGER FK -> candidates.id | |
| old_status | TEXT | |
| new_status | TEXT | |
| changed_by | INTEGER FK -> users.id | |
| changed_at | DATETIME | |
| remarks | TEXT | |

### 4.3.5 clients

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| client_code | TEXT UNIQUE | optional |
| company_name | TEXT | required |
| contact_person | TEXT | |
| email | TEXT | |
| phone | TEXT | |
| address | TEXT | |
| notes | TEXT | |
| is_active | BOOLEAN | default true |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.6 jobs

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| job_code | TEXT UNIQUE | optional |
| client_id | INTEGER FK -> clients.id | required |
| title | TEXT | required |
| location | TEXT | |
| work_type | TEXT | onsite, remote, hybrid |
| employment_type | TEXT | full-time, contract |
| required_skills | TEXT | free text |
| min_experience | REAL | |
| max_experience | REAL | |
| salary_or_rate | TEXT | kept as text for flexibility |
| status | TEXT | open, on_hold, closed |
| owner_user_id | INTEGER FK -> users.id | recruiter owner |
| description | TEXT | |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.7 submissions

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| candidate_id | INTEGER FK -> candidates.id | required |
| job_id | INTEGER FK -> jobs.id | required |
| recruiter_user_id | INTEGER FK -> users.id | submission owner |
| submitted_at | DATETIME | |
| status | TEXT | submitted, under_review, interview, rejected, offered, joined |
| interview_date | DATETIME | optional |
| feedback | TEXT | |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Recommended unique constraint:
- `(candidate_id, job_id)` to reduce duplicate submissions to the same job

### 4.3.8 submission_status_history

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| submission_id | INTEGER FK -> submissions.id | |
| old_status | TEXT | |
| new_status | TEXT | |
| changed_by | INTEGER FK -> users.id | |
| changed_at | DATETIME | |
| remarks | TEXT | |

### 4.3.9 employees

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| employee_code | TEXT UNIQUE | optional |
| candidate_id | INTEGER FK -> candidates.id | unique if one-time conversion |
| full_name | TEXT | |
| email | TEXT | |
| phone | TEXT | |
| client_id | INTEGER FK -> clients.id | optional main client |
| start_date | DATE | |
| end_date | DATE | nullable |
| employment_type | TEXT | employee, contractor |
| reporting_manager | TEXT | |
| status | TEXT | active, inactive, completed, on_hold |
| billing_status | TEXT | pending, ready, billed |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.10 projects

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| project_code | TEXT UNIQUE | optional |
| client_id | INTEGER FK -> clients.id | |
| project_name | TEXT | required |
| start_date | DATE | |
| end_date | DATE | |
| status | TEXT | active, completed, on_hold |
| notes | TEXT | |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.11 employee_projects

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| employee_id | INTEGER FK -> employees.id | |
| project_id | INTEGER FK -> projects.id | |
| assigned_from | DATE | |
| assigned_to | DATE | |
| status | TEXT | active, completed |
| notes | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.12 timesheets

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| employee_id | INTEGER FK -> employees.id | required |
| week_start | DATE | required |
| week_end | DATE | required |
| total_hours | REAL | required |
| status | TEXT | draft, submitted, approved, rejected |
| submitted_at | DATETIME | |
| reviewed_by | INTEGER FK -> users.id | admin/hr reviewer |
| reviewed_at | DATETIME | |
| review_comments | TEXT | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Recommended unique constraint:
- `(employee_id, week_start, week_end)`

### 4.3.13 tasks

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| title | TEXT | required |
| description | TEXT | |
| entity_type | TEXT | candidate, client, job, submission, employee, project, general |
| entity_id | INTEGER | nullable polymorphic reference |
| assigned_user_id | INTEGER FK -> users.id | |
| priority | TEXT | low, medium, high |
| due_date | DATE | |
| status | TEXT | open, in_progress, done, cancelled |
| created_by | INTEGER FK -> users.id | |
| updated_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.3.14 notes

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| entity_type | TEXT | candidate, client, job, submission, employee, project |
| entity_id | INTEGER | |
| note_type | TEXT | call, email, internal, feedback, followup |
| content | TEXT | required |
| created_by | INTEGER FK -> users.id | |
| created_at | DATETIME | |

### 4.3.15 attachments

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| entity_type | TEXT | candidate, employee, submission, project |
| entity_id | INTEGER | |
| file_name | TEXT | |
| file_path | TEXT | local disk path |
| file_type | TEXT | mime or extension |
| uploaded_by | INTEGER FK -> users.id | |
| uploaded_at | DATETIME | |

### 4.3.16 activity_logs

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| user_id | INTEGER FK -> users.id | |
| action_type | TEXT | create, update, status_change, delete, login, export |
| entity_type | TEXT | |
| entity_id | INTEGER | |
| message | TEXT | human-readable summary |
| metadata_json | TEXT | optional serialized details |
| created_at | DATETIME | |

## 4.4 Suggested indexes

Create indexes on:

- `users.username`
- `users.email`
- `candidates.email`
- `candidates.owner_user_id`
- `candidates.status`
- `jobs.client_id`
- `jobs.owner_user_id`
- `jobs.status`
- `submissions.candidate_id`
- `submissions.job_id`
- `submissions.status`
- `employees.client_id`
- `employees.status`
- `timesheets.employee_id`
- `timesheets.status`
- `tasks.assigned_user_id`
- `tasks.status`
- `notes.entity_type, notes.entity_id`

## 4.5 Sample SQL schema starter

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_code TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    location TEXT,
    primary_skills TEXT,
    years_experience REAL,
    source TEXT,
    status TEXT NOT NULL,
    owner_user_id INTEGER,
    resume_file_path TEXT,
    notes_summary TEXT,
    created_by INTEGER,
    updated_by INTEGER,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (owner_user_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);
```

---

# Part 5. Business Rules

## 5.1 Candidate rules
- A candidate can exist without being submitted.
- A candidate may have only one current owner.
- Candidate status changes should be logged.

## 5.2 Job rules
- A job belongs to one client.
- A closed job should not accept new submissions unless reopened.

## 5.3 Submission rules
- One candidate should not be submitted multiple times to the same job unless explicitly allowed by admin.
- Submission status changes should be logged.

## 5.4 Employee conversion rules
- Only selected or joined candidates can be converted to employees.
- Candidate-to-employee conversion must preserve source candidate link.

## 5.5 Timesheet rules
- One employee can have only one timesheet per week range.
- Approved timesheets become read-only except for HR/admin override.

## 5.6 Task rules
- Tasks can be linked to a record or be standalone.
- Closed tasks remain visible in history.

## 5.7 Notes rules
- Notes are append-only by default.
- Deletion of notes should be restricted to admin/owner if allowed at all.

---

# Part 6. UI / UX Design

## 6.1 Design goals
- clean
- simple
- fast navigation
- form-heavy but easy to use
- mobile-friendly enough for basic updates

## 6.2 Main navigation
- Dashboard
- Candidates
- Clients
- Jobs
- Submissions
- Employees
- Projects
- Timesheets
- Tasks
- Reports
- Admin

## 6.3 Key screens

### Dashboard
Widgets:
- total candidates
- open jobs
- submissions this week
- interviews pending
- active employees
- pending timesheets
- overdue tasks

### Candidate list
- search bar
- filters: owner, status, source, location
- add candidate button

### Candidate detail
Tabs or sections:
- profile
- notes
- submissions
- tasks
- attachments
- status history

### Job list
- client filter
- owner filter
- open/closed filter

### Submission list
- by recruiter
- by job
- by status

### Employee detail
- profile
- assignments
- timesheets
- notes

### Timesheet review page
- pending queue
- approve/reject actions
- comment box

### Reports page
- downloadable CSV reports

---

# Part 7. API / Route Design

Server-rendered Flask app can use form posts and HTML routes, but a structured route plan helps development.

## 7.1 Example routes

### Auth
- `GET /login`
- `POST /login`
- `POST /logout`

### Dashboard
- `GET /dashboard`

### Candidates
- `GET /candidates`
- `GET /candidates/new`
- `POST /candidates`
- `GET /candidates/<id>`
- `GET /candidates/<id>/edit`
- `POST /candidates/<id>/update`
- `POST /candidates/<id>/status`

### Clients
- `GET /clients`
- `GET /clients/new`
- `POST /clients`
- `GET /clients/<id>`
- `POST /clients/<id>/update`

### Jobs
- `GET /jobs`
- `GET /jobs/new`
- `POST /jobs`
- `GET /jobs/<id>`
- `POST /jobs/<id>/update`
- `POST /jobs/<id>/close`

### Submissions
- `GET /submissions`
- `GET /submissions/new`
- `POST /submissions`
- `GET /submissions/<id>`
- `POST /submissions/<id>/status`

### Employees
- `GET /employees`
- `POST /employees/convert-from-candidate/<candidate_id>`
- `GET /employees/<id>`
- `POST /employees/<id>/update`

### Projects
- `GET /projects`
- `POST /projects`
- `GET /projects/<id>`
- `POST /projects/<id>/assign-employee`

### Timesheets
- `GET /timesheets`
- `GET /timesheets/new`
- `POST /timesheets`
- `GET /timesheets/<id>`
- `POST /timesheets/<id>/submit`
- `POST /timesheets/<id>/approve`
- `POST /timesheets/<id>/reject`

### Tasks
- `GET /tasks`
- `POST /tasks`
- `POST /tasks/<id>/update`
- `POST /tasks/<id>/complete`

### Notes
- `POST /notes`
- `POST /notes/<id>/delete`

### Reports
- `GET /reports`
- `GET /reports/candidates.csv`
- `GET /reports/submissions.csv`
- `GET /reports/timesheets.csv`

---

# Part 8. Security and Data Management

## 8.1 Authentication
- Use password hashing with Werkzeug or bcrypt.
- Use session cookies with secure settings in production.

## 8.2 Authorization
- Enforce role checks on routes.
- Restrict recruiter access where needed.
- Restrict employee access to their own data.

## 8.3 File upload security
- allow only selected file types such as pdf, doc, docx
- limit file size
- sanitize filenames
- store generated unique filenames

## 8.4 Backup strategy

### Minimum
- daily copy of SQLite DB file
- daily backup of uploads folder

### Suggested scripts
- `backup_db.py`
- `zip_uploads.py`

## 8.5 Restore strategy
- stop app
- replace `app.db`
- restore uploads directory
- start app

---

# Part 9. Developer-Ready Build Plan

## 9.1 Development principles
- build thin slices end to end
- avoid overengineering
- complete one workflow before starting the next
- keep database migrations simple
- prioritize usability over abstraction

## 9.2 Phase plan

## Phase 1: Foundation and Authentication
Duration: 3 to 5 days

### Scope
- project scaffolding
- configuration setup
- SQLite integration
- role and user models
- login/logout
- base layout and navigation

### Deliverables
- working app shell
- seeded default roles
- owner/admin user creation
- protected dashboard page

### Acceptance criteria
- user can log in
- unauthorized user cannot access protected routes
- roles exist and are stored in DB

## Phase 2: Candidate, Client, and Job Modules
Duration: 5 to 8 days

### Scope
- candidate CRUD
- client CRUD
- job CRUD
- list views with filters
- detail pages

### Deliverables
- candidate form
- client form
- job form
- list/detail/edit pages

### Acceptance criteria
- user can create and edit candidates, clients, jobs
- recruiter assignment is stored
- open/closed job state works

## Phase 3: Submission Tracking
Duration: 4 to 6 days

### Scope
- create submission
- prevent duplicates
- submission detail page
- interview and status updates
- status history logging

### Deliverables
- submission create flow
- submission list and filters
- submission status history

### Acceptance criteria
- recruiter can submit candidate to job
- duplicate submission warning works
- status changes are logged

## Phase 4: Notes and Tasks
Duration: 3 to 5 days

### Scope
- polymorphic notes system
- task creation and updates
- overdue task highlighting

### Deliverables
- add note from detail pages
- task board/list page
- linked notes/tasks on candidate and job pages

### Acceptance criteria
- user can add notes to entities
- user can create and complete tasks
- overdue tasks show on dashboard

## Phase 5: Employee Conversion, Projects, Timesheets
Duration: 6 to 9 days

### Scope
- candidate conversion to employee
- project CRUD
- employee-project assignment
- timesheet submission and review

### Deliverables
- convert candidate button
- employee module
- project assignment page
- timesheet entry and approval pages

### Acceptance criteria
- selected candidate can become employee
- employee can submit timesheet
- HR/admin can approve or reject timesheet

## Phase 6: Dashboard, Reports, Audit Logs, Polish
Duration: 4 to 7 days

### Scope
- summary dashboard
- CSV exports
- activity logs
- validation and cleanup
- backup scripts

### Deliverables
- dashboard widgets
- reports page
- activity log list
- backup utility scripts

### Acceptance criteria
- dashboard metrics load correctly
- exports generate valid CSV
- key actions appear in activity log

## 9.3 Total build estimate

### Solo developer
- approximately 4 to 7 weeks part-time
- approximately 2 to 4 weeks full-time

### Small team
- approximately 2 to 3 weeks for MVP

---

# Part 10. Development Task Breakdown

## 10.1 Backend tasks
- set up Flask app factory
- define SQLAlchemy models
- configure SQLite database
- create auth system
- implement CRUD routes
- implement validation
- add logging helpers
- implement CSV exports
- write backup scripts

## 10.2 Frontend tasks
- base template and navigation
- dashboard page
- list and detail templates
- create/edit forms
- search/filter UI
- status badges
- error/success message handling

## 10.3 QA checklist
- login works
- roles enforced
- duplicate submissions blocked
- candidate conversion works
- timesheet approval flow works
- notes save correctly
- tasks due dates behave correctly
- exports open in Excel/Sheets

---

# Part 11. Suggested Initial Backlog

## Priority 1
- app setup
- user auth
- roles
- candidates
- clients
- jobs

## Priority 2
- submissions
- notes
- tasks
- dashboard

## Priority 3
- employee conversion
- projects
- timesheets
- reports
- audit logs

## Priority 4
- search improvements
- attachment handling improvements
- admin settings
- backup UI

---

# Part 12. Risks and Mitigations

## Risk 1: SQLite limitations under concurrent usage
Mitigation:
- keep usage low-volume
- deploy as single app instance
- migrate to PostgreSQL later if needed

## Risk 2: Manual data entry quality
Mitigation:
- add required fields
- add status history
- add filters and duplicate warnings

## Risk 3: File management issues
Mitigation:
- enforce file naming and directory structure
- add upload limits
- include backup routine

## Risk 4: Over-scoping
Mitigation:
- keep MVP fixed
- do not add AI, messaging, or integrations in first version

---

# Part 13. Future Enhancements

These are optional later features, not part of MVP:

- email notifications
- calendar reminders
- invoice export
- bulk imports from CSV
- advanced search
- PostgreSQL support
- multi-organization support
- REST API for external integrations
- simple analytics charts

---

# Part 14. Recommended Next Step

Build this as a **Flask + SQLite modular monolith** and complete the MVP in slices:

1. authentication  
2. candidate/client/job tracking  
3. submissions  
4. notes/tasks  
5. employee and timesheet tracking  
6. reporting and logs

This gives a functional business tool quickly, while staying free to operate and easy to evolve.

---

# Part 15. One-Page Build Summary

**App type:** Local recruitment tracking web application  
**Stack:** Flask, SQLite, Bootstrap  
**Runs:** locally or on one cheap VPS  
**Main modules:** candidates, clients, jobs, submissions, employees, projects, timesheets, tasks, notes, reports  
**Excluded:** AI, WhatsApp, SMS, email sending, paid APIs  
**Primary value:** central tracking at almost zero operating cost  
**MVP timeline:** about 2 to 4 weeks full-time or 4 to 7 weeks part-time  
**Ongoing cost:** free locally; low monthly cost if hosted

