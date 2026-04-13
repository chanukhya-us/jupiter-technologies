# audit — Audit Log Module

Provides a read-only view of all system activity for compliance and debugging. Restricted to owner and admin roles.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/activity-logs` | `activity_logs()` | owner, admin |

---

## Flow Diagram

```
GET /activity-logs
      │
      ▼
@roles_required("owner", "admin")
  └── Other roles → 403 Forbidden
      │
      ▼
ActivityLog.query
  .order_by(created_at DESC)
  .limit(500)
  .all()
      │
      ▼
render audit/logs.html
  └── Table: when | user | action | entity | message
```

---

## ActivityLog Schema

Every action in the system writes to `ActivityLog`:

| Field | Description |
|-------|-------------|
| `user_id` | Who performed the action (null for system) |
| `action_type` | login, logout, create, update, delete, status_change, submit, approve, reject, export, assign |
| `entity_type` | candidate, job, submission, employee, project, timesheet, task, note, marketer_log, user, report |
| `entity_id` | ID of the affected record |
| `message` | Human-readable description |
| `metadata_json` | Optional extra data |
| `created_at` | Timestamp (UTC) |

---

## How Activity Gets Logged

Every route that modifies data calls `add_activity()` from `utils.py`:

```python
add_activity(
    action_type="create",
    entity_type="candidate",
    entity_id=candidate.id,
    message=f"Created candidate {candidate.full_name}"
)
```

This is called **before** `db.session.commit()` so it's part of the same transaction.

---

## Models Used

- `ActivityLog` — core record (read-only in this module)
