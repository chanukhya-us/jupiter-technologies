# Jupiter Technologies - Recruiting & Delivery Tracking System

<div align="center">
  <img src="app/static/images/brand/jupiter-technologies-logo-light.png" alt="Jupiter Technologies" width="300"/>
  
  <p><strong>A comprehensive staffing and recruiting management platform</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-brightgreen.svg)](tests/)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

Jupiter Technologies Tracking System is a full-featured staffing and recruiting management platform designed to streamline the entire recruitment lifecycle—from candidate sourcing to employee onboarding and project delivery.

### Key Capabilities

- **Candidate Management**: Track candidates through the entire recruitment pipeline
- **Job Requisition Management**: Manage open positions and client requirements
- **Submission Tracking**: Monitor candidate submissions and interview stages
- **Employee & Project Management**: Oversee active employees and project assignments
- **Timesheet Management**: Track billable hours and approve timesheets
- **Marketer Activity Tracking**: Monitor daily marketing activities and compliance
- **Analytics & Reporting**: Comprehensive dashboards with interactive charts
- **Audit Logging**: Complete activity tracking for compliance

---

## 📸 Screenshots

<details open>
<summary><strong>Dashboard</strong></summary>

<img src="https://github.com/user-attachments/assets/dashboard-screenshot.png" alt="Dashboard" width="100%"/>

*Real-time operational snapshot with KPI metrics, hiring trends, and submission funnels*

</details>

<details>
<summary><strong>Marketer Activity</strong></summary>

<img src="https://github.com/user-attachments/assets/marketer-activity-screenshot.png" alt="Marketer Activity" width="100%"/>

*Daily activity logging and compliance tracking for marketing team with visual analytics*

</details>

<details>
<summary><strong>Candidates Management</strong></summary>

*Advanced filtering, status tracking, and trend analysis for candidate pipeline*

</details>

<details>
<summary><strong>Jobs & Submissions</strong></summary>

*Job requisition management with submission tracking and interview scheduling*

</details>

---

## ✨ Features

### 🎨 Modern UI/UX
- **Clean, Professional Design**: Modern interface with smooth animations
- **Interactive Charts**: Powered by Chart.js with donut, line, and bar visualizations
- **Responsive Layout**: Mobile-friendly design that works on all devices
- **Real-time Updates**: Dynamic data visualization with hover effects

### 👥 User Management
- **Role-Based Access Control**: Owner, Admin, Recruiter, HR, Marketer, Employee roles
- **Secure Authentication**: Password hashing with bcrypt
- **Activity Logging**: Complete audit trail of all user actions

### 📊 Analytics & Reporting
- **Dashboard Analytics**:
  - Hiring activity trends (6-month view)
  - Timesheet velocity tracking (8-week view)
  - Submission funnel visualization
  - Status distribution charts
- **Trend Graphs**:
  - 30-90 day candidate growth trends
  - Job opening trends
  - Marketer activity compliance
- **Export Capabilities**: CSV export for candidates, submissions, and timesheets

### 🎯 Core Modules

#### Candidates
- Full candidate lifecycle management
- Resume upload and storage
- Status history tracking
- Skills and experience tracking
- Source attribution
- Owner assignment

#### Jobs
- Job requisition creation and management
- Client association
- Skills requirements
- Salary/rate information
- Status tracking (open, on-hold, closed)

#### Submissions
- Candidate-to-job submissions
- Interview scheduling
- Status progression tracking
- Recruiter assignment
- Notes and feedback

#### Employees
- Active employee roster
- Project assignments
- Timesheet management
- Performance tracking

#### Marketer Activity
- Daily activity logging
- Compliance tracking
- Job type distribution
- Completion rate monitoring
- Onboarding workflow for new marketers

#### Projects & Timesheets
- Project creation and management
- Weekly timesheet submission
- Approval workflow
- Billable hours tracking

#### Tasks & Notes
- Task assignment and tracking
- Due date management
- Entity-linked notes
- Priority levels

---

## 🛠 Technology Stack

### Backend
- **Framework**: Flask 3.0.3
- **Database**: SQLAlchemy ORM with SQLite (production-ready for PostgreSQL/MySQL)
- **Authentication**: Flask-Login with bcrypt password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Migrations**: Flask-Migrate (Alembic)

### Frontend
- **UI Framework**: Bootstrap 5.3.3
- **Charts**: Chart.js 4.4.0
- **Icons**: Bootstrap Icons
- **Styling**: Custom CSS with CSS variables and animations

### Development
- **Testing**: pytest with 20 comprehensive tests
- **Code Quality**: Type hints, docstrings, clean architecture
- **Version Control**: Git with structured branching

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/jupiter-tracking-system.git
cd jupiter-tracking-system
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Initialize the database with sample data
flask cli seed-db
```

This creates:
- Admin user: `admin@jupiter.tech` / `admin123`
- Sample users for each role
- Sample data for testing

### Step 5: Run the Application

```bash
flask run --port 5001
```

The application will be available at: **http://127.0.0.1:5001**

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///jupiter.db

# Upload Configuration
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Session Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Database Configuration

For production, update `config.py` to use PostgreSQL or MySQL:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://user:password@localhost/jupiter_db'
```

---

## 📖 Usage

### Default Login Credentials

After running `flask cli seed-db`:

| Role | Email | Password |
|------|-------|----------|
| Owner/Admin | admin@jupiter.tech | admin123 |
| Recruiter | recruiter@jupiter.tech | password123 |
| HR | hr@jupiter.tech | password123 |
| Marketer | marketer@jupiter.tech | password123 |
| Employee | employee@jupiter.tech | password123 |

### Common Workflows

#### 1. Adding a New Candidate
1. Navigate to **Candidates** → **Add Candidate**
2. Fill in candidate details (name, email, phone, skills)
3. Upload resume (optional)
4. Assign owner and set status
5. Click **Create Candidate**

#### 2. Creating a Job Requisition
1. Navigate to **Jobs** → **Add Job**
2. Select client and enter job details
3. Specify required skills and experience
4. Set salary/rate information
5. Click **Create Job**

#### 3. Submitting a Candidate
1. Navigate to **Submissions** → **New Submission**
2. Select candidate and job
3. Add submission notes
4. Click **Create Submission**

#### 4. Marketer Onboarding
1. Navigate to **Marketer Activity** → **Onboard Marketer**
2. Fill in marketer profile details
3. Set daily activity targets
4. Assign manager
5. Click **Create Profile**

#### 5. Logging Daily Activity (Marketer)
1. Navigate to **Marketer Activity** → **New Log**
2. Select date and job types
3. Enter activity counts
4. Add notes
5. Click **Submit Log**

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Module

```bash
pytest tests/test_marketer_activity.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Current Test Status

✅ **20/20 tests passing**

Test modules:
- `test_marketer_activity.py`: Marketer onboarding and activity logging
- Additional test coverage for all core modules

---

## 📁 Project Structure

```
jupiter-tracking-system/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # SQLAlchemy models
│   ├── extensions.py            # Flask extensions
│   ├── constants.py             # Application constants
│   ├── decorators.py            # Custom decorators
│   ├── utils.py                 # Utility functions
│   ├── cli.py                   # CLI commands
│   ├── assets.py                # Asset management
│   │
│   ├── auth/                    # Authentication blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── candidates/              # Candidates blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── jobs/                    # Jobs blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── submissions/             # Submissions blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── employees/               # Employees blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── projects/                # Projects blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── timesheets/              # Timesheets blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── marketer/                # Marketer activity blueprint
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   ├── tasks/                   # Tasks blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── notes/                   # Notes blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── clients/                 # Clients blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── reports/                 # Reports & dashboard blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── audit/                   # Audit logging blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── tokens.css       # Design tokens
│   │   │   └── app.css          # Application styles
│   │   ├── js/
│   │   │   └── charts.js        # Chart initialization
│   │   ├── images/
│   │   │   ├── brand/           # Logo and branding
│   │   │   ├── icons/           # Service icons
│   │   │   └── partners/        # Partner logos
│   │   ├── uploads/             # User uploads
│   │   └── vendor/              # Third-party libraries
│   │
│   └── templates/
│       ├── base.html            # Base template
│       ├── auth/                # Auth templates
│       ├── candidates/          # Candidate templates
│       ├── jobs/                # Job templates
│       ├── submissions/         # Submission templates
│       ├── employees/           # Employee templates
│       ├── projects/            # Project templates
│       ├── timesheets/          # Timesheet templates
│       ├── marketer_activity/   # Marketer templates
│       ├── tasks/               # Task templates
│       ├── notes/               # Note templates
│       ├── clients/             # Client templates
│       ├── reports/             # Report templates
│       ├── audit/               # Audit templates
│       └── partials/            # Reusable components
│
├── tests/
│   ├── conftest.py              # Test configuration
│   └── test_marketer_activity.py
│
├── migrations/                  # Database migrations
├── .venv/                       # Virtual environment
├── .gitignore
├── requirements.txt             # Python dependencies
├── config.py                    # Application configuration
├── run.py                       # Application entry point
├── README.md                    # This file
├── CHARTS_SYSTEM.md            # Chart system documentation
├── UI_ENHANCEMENTS.md          # UI enhancement details
└── FINAL_SUMMARY.md            # Project summary
```

---

## 🎨 Chart System

The application features a comprehensive chart system built with Chart.js:

### Chart Types

1. **Donut Charts**: Status distributions, source breakdowns
2. **Line Charts**: Trend analysis over time
3. **Bar Charts**: Comparative metrics, funnel visualization

### Key Features

- Automatic initialization on page load
- Responsive and mobile-friendly
- Interactive tooltips with detailed information
- Consistent color palette across all charts
- Empty state handling with friendly messages
- Console logging for debugging

### Usage Example

```html
<!-- Donut Chart -->
<canvas
  class="rt-donut-chart"
  data-labels='["Active", "Pending", "Completed"]'
  data-values='[25, 15, 40]'
  data-total="80"
></canvas>

<!-- Line Chart -->
<canvas
  class="rt-series-chart"
  data-chart-type="line"
  data-labels='["Mon", "Tue", "Wed"]'
  data-datasets='[{"label": "Candidates", "data": [10, 20, 15]}]'
></canvas>
```

For detailed documentation, see [CHARTS_SYSTEM.md](CHARTS_SYSTEM.md)

---

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Session Security**: Secure, HttpOnly, SameSite cookies
- **Role-Based Access**: Decorator-based authorization
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **File Upload Validation**: Extension and size restrictions
- **Audit Logging**: Complete activity tracking

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure production database (PostgreSQL/MySQL)
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up application server (gunicorn/uWSGI)
- [ ] Enable database backups
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Optimize static file serving (CDN)

### Example Production Setup (gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write/update tests
5. Ensure all tests pass: `pytest tests/ -v`
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write descriptive variable names

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/yourusername/jupiter-tracking-system/issues)
- **Email**: support@jupiter.tech
- **Documentation**: See additional docs in the repository

---

## 🙏 Acknowledgments

- **Flask**: Excellent Python web framework
- **Bootstrap**: Responsive UI framework
- **Chart.js**: Beautiful chart library
- **SQLAlchemy**: Powerful ORM
- **All Contributors**: Thank you for your contributions!

---

## 📊 Project Stats

- **Lines of Code**: ~15,000+
- **Test Coverage**: 20 tests passing
- **Modules**: 12 blueprints
- **Database Tables**: 20+ models
- **UI Components**: 50+ templates
- **Chart Visualizations**: 15+ interactive charts

---

<div align="center">
  <p>Made with ❤️ by the Jupiter Technologies Team</p>
  <p>
    <a href="#top">Back to Top ↑</a>
  </p>
</div>
