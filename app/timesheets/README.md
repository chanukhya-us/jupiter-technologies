# timesheets — Timesheet Workflow Module

Manages weekly timesheet submission and approval for employees. Supports draft → submitted → approved/rejected workflow.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/timesheets` | `list_timesheets()` | all roles |
| GET | `/timesheets/new` | `new_timesheet()` | all roles |
| POST | `/timesheets` | `create_timesheet()` | all roles |
| GET | `/timesheets/<id>` | `timesheet_detail()` | all roles |
| POST | `/timesheets/<id>/submit` | `submit_timesheet()` | all roles |
| POST | `/timesheets/<id>/approve` | `approve_timesheet()` | owner, admin, hr |
| POST | `/timesheets/<id>/reject` | `reject_timesheet()` | owner, admin, hr |

---

## Flow Diagrams

### List Timesheets

```
GET /timesheets
      │
      ▼
Role check:
  ├── employee → filter to own employee record only
  └── others  → all timesheets
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(employee distribution, top_n=6)
      │
      ▼
render timesheets/list.html
```

### Create Timesheet

```
POST /timesheets
      │
      ▼
Validate employee_id, week_start, week_end, total_hours
      │
      ├── Missing → flash error → redirect /timesheets/new
      │
      ▼
Create Timesheet(
  employee_id, week_start, week_end,
  total_hours, status="draft",
  notes, created_by
)
      │
      ▼
add_activity("create", "timesheet", ...)
db.session.commit()
      │
      ▼
redirect → /timesheets/<id>
```

### Approval Workflow

```
Draft Timesheet
      │
      ▼
POST /timesheets/<id>/submit
  timesheet.status = "submitted"
  add_activity("submit", ...)
      │
      ▼
POST /timesheets/<id>/approve        POST /timesheets/<id>/reject
  timesheet.status = "approved"        timesheet.status = "rejected"
  timesheet.reviewed_by = user.id      timesheet.reviewed_by = user.id
  timesheet.reviewed_at = now          timesheet.reviewed_at = now
  add_activity("approve", ...)         add_activity("reject", ...)
      │                                      │
      ▼                                      ▼
redirect → /timesheets/<id>          redirect → /timesheets/<id>
```

---

## Status Lifecycle

```
draft → submitted → approved
                 └──────────► rejected → submitted (resubmit)
```

---

## Models Used

- `Timesheet` — core record
- `Employee` — timesheet belongs to employee
- `User` — reviewer (approved/rejected by)
