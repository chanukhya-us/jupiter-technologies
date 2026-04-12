<div align="center">
  <img src="app/static/images/brand/jupiter-technologies-logo-light.png" alt="Jupiter Technologies" width="280"/>
  <h1>Jupiter Technologies</h1>
  <p>Recruiting &amp; Delivery Tracking System</p>

  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.0+-green.svg" alt="Flask"/>
  <img src="https://img.shields.io/badge/Tests-20%2F20%20Passing-brightgreen.svg" alt="Tests"/>
  <img src="https://img.shields.io/badge/Release-v1.0.0-orange.svg" alt="Release"/>
</div>

---

## Overview

Jupiter Technologies is a full-featured staffing and recruiting management platform that streamlines the entire recruitment lifecycle — from candidate sourcing to employee onboarding and project delivery.

---

## Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

*Real-time operational snapshot with KPI metrics, hiring activity trends, timesheet velocity, and submission funnel charts.*

### Marketer Activity

![Marketer Activity](docs/screenshots/marketer-activity.png)

*Daily activity logging and compliance tracking with log status mix and job type distribution charts.*

---

## Features

- **Candidate Management** — Full pipeline tracking with status history, resume uploads, and owner assignment
- **Job Requisitions** — Manage open positions linked to clients with skills and salary info
- **Submissions** — Track candidate-to-job submissions through interview stages
- **Employees & Projects** — Active roster, project assignments, and timesheet management
- **Marketer Activity** — Daily log compliance, onboarding workflow, and visual analytics
- **Analytics & Charts** — Interactive donut, line, and bar charts across all pages
- **Role-Based Access** — Owner, Admin, Recruiter, HR, Marketer, Employee roles
- **Audit Logging** — Complete activity trail for compliance
- **CSV Exports** — Candidates, submissions, and timesheets

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.0, SQLAlchemy, Flask-Login |
| Database | SQLite (PostgreSQL/MySQL ready) |
| Frontend | Bootstrap 5.3, Chart.js 4.4 |
| Auth | bcrypt, Flask-WTF CSRF |
| Testing | pytest (20 tests) |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/chanukhya-us/jupiter-technologies.git
cd jupiter-technologies

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed database
flask cli seed-db

# 5. Run
flask run --port 5001
```

Open **http://127.0.0.1:5001**

---

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Owner / Admin | admin@jupiter.tech | admin123 |
| Recruiter | recruiter@jupiter.tech | password123 |
| HR | hr@jupiter.tech | password123 |
| Marketer | marketer@jupiter.tech | password123 |
| Employee | employee@jupiter.tech | password123 |

---

## Project Structure

```
jupiter-technologies/
├── app/
│   ├── auth/            # Authentication
│   ├── candidates/      # Candidate management
│   ├── jobs/            # Job requisitions
│   ├── submissions/     # Submission tracking
│   ├── employees/       # Employee roster
│   ├── projects/        # Project management
│   ├── timesheets/      # Timesheet workflow
│   ├── marketer/        # Marketer activity & onboarding
│   ├── tasks/           # Task tracking
│   ├── notes/           # Entity notes
│   ├── clients/         # Client management
│   ├── reports/         # Dashboard & analytics
│   ├── audit/           # Audit logs
│   ├── static/
│   │   ├── css/         # Styles & design tokens
│   │   ├── js/          # charts.js
│   │   ├── images/      # Brand, icons, partners
│   │   └── vendor/      # Chart.js
│   └── templates/       # Jinja2 templates
├── tests/               # pytest test suite
├── docs/                # Documentation & screenshots
├── migrations/          # Alembic migrations
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
pytest tests/ -v
```

All 20 tests pass with zero regressions.

---

## Deployment

```bash
# Install gunicorn
pip install gunicorn

# Run production server
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

For production, set these environment variables:

```bash
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key
DATABASE_URL=postgresql://user:pass@host/dbname
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  Made with ❤️ by the Jupiter Technologies Team
</div>
