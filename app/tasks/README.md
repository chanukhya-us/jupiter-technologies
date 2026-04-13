# tasks — Task Tracking Module

Manages tasks linked to any entity (candidate, job, client, employee, project, submission, or general). Supports priority levels and status tracking.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/tasks` | `list_tasks()` | all roles |
| POST | `/tasks` | `create_task()` | all roles |
| POST | `/tasks/<id>/update` | `update_task()` | all roles |
| POST | `/tasks/<id>/complete` | `complete_task()` | all roles |

---

## Flow Diagrams

### List Tasks

```
GET /tasks
      │
      ▼
Role check:
  ├── employee → filter to own assigned tasks only
  └── others  → all tasks (filterable by status + assigned_user)
      │
      ▼
Read query params: status, assigned_user_id
      │
      ▼
Order by: due_date ASC (nulls last), created_at DESC
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(priority distribution)
      │
      ▼
render tasks/list.html
  ├── Status donut chart
  ├── Priority donut chart
  ├── Filter bar
  └── Tasks table (overdue tasks highlighted)
```

### Create Task

```
POST /tasks
      │
      ▼
Validate title (required)
      │
      ├── Missing → flash error → redirect back
      │
      ▼
Create Task(
  title, description,
  entity_type, entity_id,
  assigned_user_id,
  priority (low/medium/high),
  due_date,
  status = "open"
)
      │
      ▼
add_activity("create", "task", task.id, ...)
db.session.commit()
      │
      ▼
redirect → redirect_to param or /tasks
```

### Update / Complete Task

```
POST /tasks/<id>/update
      │
      ▼
Role check:
  ├── employee → can only update own tasks, cannot edit completed tasks
  └── others  → full update
      │
      ▼
Update fields: title, description, status, priority, due_date, assigned_user_id
add_activity("update", "task", ...)
db.session.commit()

POST /tasks/<id>/complete
      │
      ▼
task.status = "done"
task.completed_at = now
add_activity("complete", "task", ...)
db.session.commit()
```

---

## Status Lifecycle

```
open → in_progress → done
  │                   ▲
  └──────────────────►│
  └──────────────────► cancelled
```

## Priority Levels

`low` → `medium` → `high`

---

## Entity Types

Tasks can be linked to: `candidate`, `client`, `job`, `submission`, `employee`, `project`, `general`

---

## Models Used

- `Task` — core record
- `User` — assigned user
