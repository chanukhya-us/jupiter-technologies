# employees — Employee Management Module

Manages active employees, their project assignments, and timesheets. Employees can be converted from candidates.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/employees` | `list_employees()` | all roles |
| POST | `/employees/convert-from-candidate/<id>` | `convert_from_candidate()` | owner, admin, hr |
| GET | `/employees/<id>` | `employee_detail()` | all roles |
| POST | `/employees/<id>/update` | `update_employee()` | all roles (limited for employee role) |

---

## Flow Diagrams

### List Employees

```
GET /employees
      │
      ▼
Role check:
  ├── employee role → filter to own record only
  └── other roles  → all employees
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(employment_type distribution)
      │
      ▼
render employees/list.html
  ├── Status donut chart
  ├── Employment type donut chart
  └── Employees table
```

### Convert Candidate to Employee

```
POST /employees/convert-from-candidate/<candidate_id>
      │
      ▼
Load Candidate or 404
      │
      ▼
Create Employee(
  candidate_id = candidate.id,
  full_name    = candidate.full_name,
  email        = candidate.email,
  phone        = candidate.phone,
  status       = "active",
  employment_type, client_id, start_date, billing_rate, ...
)
      │
      ▼
add_activity("create", "employee", employee.id, ...)
db.session.commit()
      │
      ▼
redirect → /employees/<id>
```

### Update Employee

```
POST /employees/<id>/update
      │
      ▼
Role check:
  ├── employee role → can only update phone + manager
  └── admin/hr     → can update all fields
      │
      ▼
Update fields
add_activity("update", "employee", ...)
db.session.commit()
      │
      ▼
redirect → /employees/<id>
```

---

## Status Lifecycle

```
active → on_hold → active
  │
  └──────────────────► inactive
  └──────────────────► completed
```

---

## Models Used

- `Employee` — core record
- `Candidate` — optional source (converted from)
- `EmployeeProject` — project assignments
- `Timesheet` — weekly timesheets
- `Note` — notes on employee
- `Task` — tasks linked to employee
