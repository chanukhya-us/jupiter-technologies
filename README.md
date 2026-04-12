# Jupiter Technologies

A simplified recruitment tracking web application built with Flask + SQLite.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Installation](#installation)
- [Test Data](#test-data)
- [Usage](#usage)
- [CLI Commands](#cli-commands)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Scripts](#scripts)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
flask --app app.py init-db

# 4. Create owner account
flask --app app.py create-owner
# Enter: username=admin, password=admin123

# 5. Load test data (479+ records)
python scripts/load_test_data.py
# Enter: y to confirm

# 6. Run application
flask --app app.py run --debug
```

**Access:** http://127.0.0.1:5000  
**Login:** `admin` / `admin123`

---

## Features

### Core Functionality
- **Role-based authentication** - owner, admin, recruiter, hr, employee
- **Candidate management** - Track candidates through recruitment pipeline
- **Client management** - Manage client companies and contacts
- **Job management** - Create and track job openings
- **Submission tracking** - Link candidates to jobs with status tracking
- **Employee management** - Convert candidates to employees
- **Project tracking** - Assign employees to client projects
- **Timesheet management** - Submit and approve employee timesheets
- **Task management** - Create and track action items
- **Notes & attachments** - Add notes to any entity
- **Activity logging** - Complete audit trail
- **Dashboard** - KPIs and operational metrics
- **Reports** - Export data to CSV

### UI Features
- Modern, responsive design (mobile-friendly)
- Color-coded status indicators
- Sidebar navigation
- Filterable and searchable lists
- Status chips and badges
- KPI cards on dashboard

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Terminal/Command line access

### Setup Options

#### Option 1: With Test Data (Recommended for Development)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask --app app.py init-db

# Create owner user
flask --app app.py create-owner

# Load test data (479+ records)
python scripts/load_test_data.py

# Run application
flask --app app.py run --debug
```

**Login:** `admin` / `admin123`

#### Option 2: Clean Setup (Production-like)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask --app app.py init-db

# Create owner user
flask --app app.py create-owner

# Run application
flask --app app.py run --debug
```

---

## Test Data

### Overview

The test data loader creates **479+ records** across all entities, providing a realistic dataset for development and testing.

### What's Included

| Entity | Count | Description |
|--------|-------|-------------|
| **Users** | 36 | Recruiters (15), HR (8), Admins (5), Employees (7), Owner (1) |
| **Clients** | 35 | Companies across various industries |
| **Jobs** | 40 | Open (25), Filled (5), On Hold (5), Closed (5) |
| **Candidates** | 55 | Distributed across 8 lifecycle stages |
| **Submissions** | 40 | Linking candidates to jobs with interviews |
| **Employees** | 14 | Converted candidates with assignments |
| **Projects** | 35 | Active (26), Completed (3), On Hold (3), Cancelled (3) |
| **Tasks** | 55 | Various priorities with overdue alerts |
| **Timesheets** | 42 | Draft (8), Submitted (9), Approved (8), Rejected (8), Pending (9) |
| **Notes** | 56 | Internal, client, interview, and reference notes |
| **Activity Logs** | 57 | Audit trail over last 60 days |

### Loading Test Data

**Method 1: Interactive Script (Recommended)**
```bash
python scripts/load_test_data.py
```

**Method 2: CLI Command**
```bash
flask --app app.py seed-demo-data
```

### Test User Accounts

**Owner Account:**
- Username: `admin`
- Password: `admin123`

**Test Users (all use password: `password123`):**
- `recruiter1` - Sarah Johnson
- `recruiter2` - Mike Chen
- `hr1` - Emily Davis
- `hr2` - Robert Wilson
- `admin1` - Jessica Martinez
- `user5` through `user34` - Various roles

### Data Characteristics

**Geographic Coverage:**
- 35+ US cities (San Francisco, New York, Boston, Chicago, Austin, Seattle, Denver, Atlanta, Miami, Portland, Phoenix, etc.)

**Industries:**
- Technology, Finance, Healthcare, Retail, Education, Manufacturing, Logistics, Media, Energy, Telecom

**Skills:**
- Frontend: React, Angular, Vue.js, TypeScript
- Backend: Python, Java, Node.js, Go, Ruby, PHP, .NET
- Mobile: React Native, iOS, Android, Flutter
- Cloud: AWS, Azure, GCP, Kubernetes, Terraform
- Data: ML, Data Science, Big Data, Analytics
- DevOps: CI/CD, Docker, Jenkins, Ansible
- Specialized: Blockchain, Game Development, Security, IoT

**Experience Levels:** 1-15 years  
**Salary Ranges:** $80k-$220k (full-time), $60-$120/hr (contract)

### Test Scenarios

✓ **Recruitment Pipeline** - Candidates in all stages from new to joined  
✓ **Interview Scheduling** - Submissions with scheduled interview dates  
✓ **Employee Onboarding** - Candidate-to-employee conversion  
✓ **Timesheet Approval** - Workflow with draft, submitted, approved, rejected  
✓ **Task Management** - Tasks with overdue alerts  
✓ **Project Assignments** - Employees assigned to projects  
✓ **Activity Tracking** - Comprehensive audit logs  
✓ **Reporting** - Meaningful data for CSV exports

---

## Usage

### Dashboard
View KPIs, recent activity, and operational queues.

### Candidates
- Browse 55 candidates
- Filter by status, location, source, owner
- View candidate details and history
- Add notes and tasks
- Convert to employee

### Jobs
- View 40 job openings
- Filter by status, client, type
- Create new jobs
- Track submissions

### Submissions
- Link candidates to jobs
- Schedule interviews
- Track submission status
- View feedback

### Employees
- Manage 14 employees
- Assign to projects
- Track timesheets
- View employment history

### Projects
- View 35 projects
- Assign employees
- Track project status
- Add notes

### Timesheets
- Submit timesheets
- Approve/reject submissions
- Track hours
- Review comments

### Tasks
- Create action items
- Assign to users
- Set priorities and due dates
- Track completion

### Reports
- Export candidates to CSV
- Export jobs to CSV
- Export submissions to CSV
- View dashboard metrics

### Activity Logs (Admin Only)
- View all system actions
- Filter by user, action type, entity
- Audit trail

---

## CLI Commands

### Database Management
```bash
# Initialize database and seed roles
flask --app app.py init-db
```

### User Management
```bash
# Create owner user (interactive)
flask --app app.py create-owner

# Create admin user (interactive)
flask --app app.py create-admin

# Create user with specific role (interactive)
flask --app app.py create-user --role recruiter
flask --app app.py create-user --role hr
flask --app app.py create-user --role employee
```

### Test Data
```bash
# Load comprehensive test data (479+ records)
flask --app app.py seed-demo-data

# Interactive script (recommended)
python scripts/load_test_data.py
```

### Reset Database
```bash
# Stop the application first (Ctrl+C)

# Remove database
rm instance/app.db

# Reinitialize
flask --app app.py init-db

# Create owner
flask --app app.py create-owner

# Load test data (optional)
python scripts/load_test_data.py

# Restart application
flask --app app.py run --debug
```

---

## Architecture

### Technology Stack
- **Framework:** Flask 3.1.0
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask-Login
- **Frontend:** Bootstrap 5.3.3 + Custom CSS
- **Testing:** pytest 8.3.4

### Project Structure
```
.
├── app/                    # Application package
│   ├── __init__.py        # App factory
│   ├── models.py          # Database models
│   ├── cli.py             # CLI commands
│   ├── constants.py       # Constants
│   ├── decorators.py      # Custom decorators
│   ├── extensions.py      # Flask extensions
│   ├── utils.py           # Utility functions
│   ├── static/            # Static files
│   │   └── css/           # Custom CSS (tokens.css, app.css)
│   ├── templates/         # Jinja2 templates
│   │   ├── base.html      # Base template
│   │   └── [modules]/     # Module templates
│   ├── auth/              # Authentication module
│   ├── candidates/        # Candidates module
│   ├── clients/           # Clients module
│   ├── jobs/              # Jobs module
│   ├── submissions/       # Submissions module
│   ├── employees/         # Employees module
│   ├── projects/          # Projects module
│   ├── timesheets/        # Timesheets module
│   ├── tasks/             # Tasks module
│   ├── notes/             # Notes module
│   ├── reports/           # Reports module
│   └── audit/             # Audit logs module
├── scripts/               # Utility scripts
│   ├── load_test_data.py  # Load test data
│   ├── backup_db.py       # Backup database
│   ├── init_db.py         # Initialize database
│   ├── seed_demo_data.py  # Seed demo data
│   └── zip_uploads.py     # Backup uploads
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   ├── test_auth.py       # Authentication tests
│   ├── test_submissions.py # Submission tests
│   └── test_workflows.py  # Workflow tests
├── instance/              # Instance folder (database)
├── uploads/               # File uploads
├── backups/               # Database backups
├── app.py                 # Application entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
└── README.md              # This file
```

---

## Database Schema

### Core Entities

**Users**
- System users with role-based access
- Fields: username, full_name, email, password_hash, role_id, is_active
- Relationships: role, owned candidates, owned jobs, created submissions

**Roles**
- User roles: owner, admin, recruiter, hr, employee
- Fields: name, description

**Candidates**
- Job candidates in the pipeline
- Fields: candidate_code, full_name, email, phone, location, skills, experience, source, status, owner_user_id
- Statuses: new, screening, interview, submitted, selected, joined, rejected, on_hold
- Relationships: owner, submissions, status history

**Clients**
- Client companies
- Fields: client_code, company_name, contact_person, email, phone, address, is_active
- Relationships: jobs, employees, projects

**Jobs**
- Job openings
- Fields: job_code, client_id, title, location, employment_type, skills, experience, salary, status, owner_user_id
- Statuses: open, filled, on_hold, closed
- Relationships: client, owner, submissions

**Submissions**
- Candidate submissions to jobs
- Fields: candidate_id, job_id, recruiter_user_id, status, interview_date, feedback
- Statuses: submitted, interview, selected, joined, rejected, withdrawn
- Relationships: candidate, job, recruiter, status history

**Employees**
- Converted candidates (hired)
- Fields: employee_code, candidate_id, full_name, email, client_id, start_date, end_date, employment_type, status
- Statuses: active, on_leave, terminated
- Relationships: candidate, client, timesheets, project assignments

**Projects**
- Client projects
- Fields: project_code, client_id, project_name, start_date, end_date, status
- Statuses: active, completed, on_hold, cancelled
- Relationships: client, employee assignments

**Timesheets**
- Employee time tracking
- Fields: employee_id, week_start, week_end, total_hours, status, reviewed_by
- Statuses: draft, submitted, pending, approved, rejected
- Relationships: employee, reviewer

**Tasks**
- Action items
- Fields: title, description, entity_type, entity_id, assigned_user_id, priority, due_date, status
- Priorities: low, medium, high, urgent
- Statuses: open, in_progress, completed, overdue, cancelled
- Relationships: assigned user

**Notes**
- Entity notes
- Fields: entity_type, entity_id, note_type, content, created_by
- Types: internal, client, interview, reference
- Relationships: user

**ActivityLog**
- Audit trail
- Fields: user_id, action_type, entity_type, entity_id, message, metadata_json
- Actions: create, update, delete, view, approve, reject, submit
- Relationships: user

### Relationships

```
Users ──┬─→ Candidates (owner)
        ├─→ Jobs (owner)
        ├─→ Submissions (recruiter)
        ├─→ Tasks (assigned)
        └─→ Activity Logs

Clients ──┬─→ Jobs
          ├─→ Employees
          └─→ Projects

Candidates ──┬─→ Submissions
             └─→ Employees (conversion)

Jobs ──→ Submissions

Employees ──┬─→ Timesheets
            └─→ Project Assignments

Projects ──→ Employee Assignments

All Entities ──┬─→ Notes
               └─→ Tasks
```

---

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `POST /logout` - Logout user

### Candidates
- `GET /candidates` - List candidates (with filters)
- `GET /candidates/<id>` - Candidate detail
- `GET /candidates/new` - New candidate form
- `POST /candidates/new` - Create candidate
- `GET /candidates/<id>/edit` - Edit candidate form
- `POST /candidates/<id>/edit` - Update candidate
- `POST /candidates/<id>/convert` - Convert to employee

### Clients
- `GET /clients` - List clients
- `GET /clients/<id>` - Client detail
- `GET /clients/new` - New client form
- `POST /clients/new` - Create client

### Jobs
- `GET /jobs` - List jobs (with filters)
- `GET /jobs/<id>` - Job detail
- `GET /jobs/new` - New job form
- `POST /jobs/new` - Create job
- `GET /jobs/<id>/edit` - Edit job form
- `POST /jobs/<id>/edit` - Update job

### Submissions
- `GET /submissions` - List submissions (with filters)
- `GET /submissions/<id>` - Submission detail
- `GET /submissions/new` - New submission form
- `POST /submissions/new` - Create submission
- `POST /submissions/<id>/update-status` - Update status

### Employees
- `GET /employees` - List employees
- `GET /employees/<id>` - Employee detail

### Projects
- `GET /projects` - List projects
- `GET /projects/<id>` - Project detail

### Timesheets
- `GET /timesheets` - List timesheets (with filters)
- `GET /timesheets/<id>` - Timesheet detail
- `GET /timesheets/new` - New timesheet form
- `POST /timesheets/new` - Create timesheet
- `POST /timesheets/<id>/approve` - Approve timesheet
- `POST /timesheets/<id>/reject` - Reject timesheet

### Tasks
- `GET /tasks` - List tasks (with filters)
- `POST /tasks/new` - Create task
- `POST /tasks/<id>/complete` - Complete task
- `POST /tasks/<id>/delete` - Delete task

### Notes
- `POST /notes/new` - Create note
- `POST /notes/<id>/delete` - Delete note

### Reports
- `GET /dashboard` - Dashboard with KPIs
- `GET /reports` - Reports home
- `GET /reports/candidates.csv` - Export candidates
- `GET /reports/jobs.csv` - Export jobs
- `GET /reports/submissions.csv` - Export submissions

### Admin
- `GET /activity-logs` - Activity logs (admin/owner only)

---

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

### Test Suite

**test_auth.py**
- Login required for dashboard
- Successful login
- Invalid login

**test_submissions.py**
- Duplicate submission blocked
- Closed job rejects submission

**test_workflows.py**
- Candidate conversion rule
- Timesheet unique and approval flow
- Note delete restricted to owner/admin
- CSV report exports

### Test Data

The test data loader creates realistic data for comprehensive testing:
- 479+ records across all entities
- Various statuses and workflows
- Realistic relationships
- Time-based data (past and future dates)

---

## Scripts

### load_test_data.py

Interactive script to load comprehensive test data.

```bash
python scripts/load_test_data.py
```

**Features:**
- Interactive confirmation prompt
- Shows what will be loaded
- Displays login credentials after completion
- Idempotent (safe to run multiple times)

### backup_db.py

Create timestamped backup of the database.

```bash
python scripts/backup_db.py
```

Backups saved to `backups/app_YYYYMMDD_HHMMSS.db`

### zip_uploads.py

Create zip archive of uploads directory.

```bash
python scripts/zip_uploads.py
```

Archives saved to `backups/uploads_YYYYMMDD_HHMMSS.zip`

### Backup and Restore

**Backup:**
```bash
python scripts/backup_db.py
python scripts/zip_uploads.py
```

**Restore:**
```bash
# Stop the application
# Restore database
cp backups/app_YYYYMMDD_HHMMSS.db instance/app.db
# Restore uploads
unzip backups/uploads_YYYYMMDD_HHMMSS.zip -d .
# Restart application
```

---

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
flask --app app.py run --debug --port 5001
```

### Database Locked

```bash
# Stop all running instances
# Remove and reinitialize database
rm instance/app.db
flask --app app.py init-db
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Permission Denied

```bash
# Check file permissions
ls -la instance/
chmod 644 instance/app.db
```

### Database Issues

```bash
# Reset database
rm instance/app.db
flask --app app.py init-db
flask --app app.py create-owner
python scripts/load_test_data.py
```

### Virtual Environment Issues

```bash
# Deactivate and recreate
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Deployment

### Production Considerations

1. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

2. **Set environment variables**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export DATABASE_URL="postgresql://user:pass@localhost/dbname"
   ```

3. **Use PostgreSQL or MySQL** instead of SQLite
   - Update `config.py` with production database URL
   - Install appropriate database driver

4. **Enable HTTPS**
   - Use reverse proxy (nginx, Apache)
   - Configure SSL certificates

5. **Set up logging**
   - Configure application logging
   - Set up log rotation

6. **Configure backups**
   - Schedule regular database backups
   - Backup uploads directory
   - Store backups off-site

7. **Use environment-specific configs**
   - Development, staging, production configs
   - Separate settings for each environment

### Example Production Setup

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Set environment variables
export FLASK_ENV=production
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/jupiter"

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable HTTPS
- [ ] Use production database
- [ ] Set up firewall rules
- [ ] Configure CORS if needed
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review file permissions

---

## Development

### Adding a New Module

1. Create module directory: `app/new_module/`
2. Create `__init__.py` and `routes.py`
3. Define routes in `routes.py`
4. Register blueprint in `app/__init__.py`
5. Create templates in `app/templates/new_module/`
6. Add tests in `tests/test_new_module.py`

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused
- Use meaningful variable names
- Add comments for complex logic

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure tests pass
6. Submit a pull request

---

## License

See LICENSE file for details.

---

## Support

For issues and questions:
- Check this README
- Review Flask debug output
- Check activity logs in the application
- Review test data structure

---

**Happy Recruiting! 🚀**
