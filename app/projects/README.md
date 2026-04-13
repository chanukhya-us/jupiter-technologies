# projects — Project Management Module

Manages client projects and employee assignments to those projects.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/projects` | `list_projects()` | owner, admin, recruiter, hr |
| POST | `/projects` | `create_project()` | owner, admin, hr |
| GET | `/projects/<id>` | `project_detail()` | owner, admin, recruiter, hr |
| POST | `/projects/<id>/update` | `update_project()` | owner, admin, hr |
| POST | `/projects/<id>/assign-employee` | `assign_employee()` | owner, admin, hr |
| POST | `/projects/<id>/remove-employee/<emp_id>` | `remove_employee()` | owner, admin, hr |

---

## Flow Diagrams

### List Projects

```
GET /projects
      │
      ▼
Project.query.order_by(updated_at.desc())
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(client distribution, top_n=6)
      │
      ▼
render projects/list.html
  ├── Status donut chart
  ├── Client donut chart
  └── Projects table
```

### Create Project

```
POST /projects
      │
      ▼
Validate project_name (required)
      │
      ├── Missing → flash error → redirect /projects
      │
      ▼
Create Project(project_name, project_code, client_id,
               start_date, end_date, status, description)
      │
      ▼
add_activity("create", "project", project.id, ...)
db.session.commit()
      │
      ▼
redirect → /projects/<id>
```

### Assign Employee to Project

```
POST /projects/<id>/assign-employee
      │
      ▼
Validate employee_id (required)
      │
      ▼
Check for existing assignment (prevent duplicates)
      │
      ├── Already assigned → flash warning → redirect detail
      │
      ▼
Create EmployeeProject(
  employee_id, project_id,
  start_date, end_date, role_on_project
)
      │
      ▼
add_activity("assign", "project", ...)
db.session.commit()
      │
      ▼
redirect → /projects/<id>
```

---

## Status Lifecycle

```
active → on_hold → active
  │
  └──────────────────► completed
```

---

## Models Used

- `Project` — core record
- `Client` — project belongs to a client
- `EmployeeProject` — employee assignments (join table with extra fields)
- `Employee` — assigned employees
- `Note` — notes on project
- `Task` — tasks linked to project
