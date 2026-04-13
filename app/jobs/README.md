# jobs — Job Requisition Module

Manages job postings linked to clients, tracks open positions, and provides trend analytics on job creation.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/jobs` | `list_jobs()` | owner, admin, recruiter, hr |
| GET | `/jobs/new` | `new_job()` | owner, admin, recruiter, hr |
| POST | `/jobs` | `create_job()` | owner, admin, recruiter, hr |
| GET | `/jobs/<id>` | `job_detail()` | owner, admin, recruiter, hr |
| POST | `/jobs/<id>/update` | `update_job()` | owner, admin, recruiter, hr |
| POST | `/jobs/<id>/close` | `close_job()` | owner, admin, recruiter, hr |
| POST | `/jobs/<id>/reopen` | `reopen_job()` | owner, admin, recruiter, hr |

---

## Flow Diagrams

### List Jobs

```
GET /jobs
      │
      ▼
Read query params: status, client_id, owner_user_id
      │
      ▼
Build filtered SQLAlchemy query
      │
      ▼
Calculate trend graph (30–90 day window):
  ├── Get all jobs
  ├── Find oldest date → determine window
  ├── Group by date → daily counts
  └── Build labels + data arrays
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(owner distribution, top_n=6)
      │
      ▼
render jobs/list.html
  ├── Filter bar
  ├── Trend line chart
  ├── Status donut chart
  ├── Owner donut chart
  └── Jobs table
```

### Create Job

```
POST /jobs
      │
      ▼
Validate title + client_id (both required)
      │
      ├── Missing → flash error → redirect /jobs/new
      │
      ▼
Create Job(job_code, client_id, title, location,
           work_type, employment_type, required_skills,
           min_experience, max_experience, salary_or_rate,
           status, owner_user_id, description)
      │
      ▼
add_activity("create", "job", job.id, ...)
db.session.commit()
      │
      ▼
redirect → /jobs/<id>
```

### Close / Reopen Job

```
POST /jobs/<id>/close          POST /jobs/<id>/reopen
      │                               │
      ▼                               ▼
job.status = "closed"          job.status = "open"
      │                               │
      ▼                               ▼
add_activity(...)              add_activity(...)
db.session.commit()            db.session.commit()
      │                               │
      ▼                               ▼
redirect → /jobs/<id>          redirect → /jobs/<id>
```

---

## Status Lifecycle

```
open ──► on_hold ──► open
 │
 └──────────────────► closed ──► open (reopen)
```

---

## Models Used

- `Job` — core record
- `Client` — job belongs to a client
- `User` — owner assignment
- `Submission` — submissions against this job
- `Note` — notes attached to job
- `Task` — tasks linked to job
