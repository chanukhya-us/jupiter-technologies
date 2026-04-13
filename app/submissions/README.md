# submissions — Submission Tracking Module

Tracks candidate-to-job submissions through the interview pipeline with status history and KPI metrics.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/submissions` | `list_submissions()` | owner, admin, recruiter, hr |
| GET | `/submissions/new` | `new_submission()` | owner, admin, recruiter, hr |
| POST | `/submissions` | `create_submission()` | owner, admin, recruiter, hr |
| GET | `/submissions/<id>` | `submission_detail()` | owner, admin, recruiter, hr |
| POST | `/submissions/<id>/status` | `update_submission_status()` | owner, admin, recruiter, hr |

---

## Flow Diagrams

### List Submissions

```
GET /submissions
      │
      ▼
Read query params: recruiter_user_id, job_id, status
      │
      ▼
Build filtered SQLAlchemy query
      │
      ▼
Calculate KPI metrics:
  ├── total_submissions
  ├── interview_count
  ├── selected_count (selected/offered/joined)
  ├── rejected_count
  └── conversion_rate = selected / total * 100
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(recruiter distribution)
      │
      ▼
render submissions/list.html
  ├── KPI metric cards
  ├── Filter bar
  ├── Status donut chart
  ├── Recruiter donut chart
  └── Submissions table
```

### Create Submission

```
POST /submissions
      │
      ▼
Validate candidate_id + job_id (both required)
      │
      ├── Missing → flash error → redirect /submissions/new
      │
      ▼
Check for duplicate (same candidate + job already submitted)
      │
      ├── Duplicate → flash warning → redirect /submissions/new
      │
      ▼
Create Submission(candidate_id, job_id, recruiter_user_id,
                  status="submitted", submitted_at=now,
                  interview_date, notes)
      │
      ▼
Create SubmissionStatusHistory(old_status=None, new_status="submitted")
      │
      ▼
add_activity("create", "submission", submission.id, ...)
db.session.commit()
      │
      ▼
redirect → /submissions/<id>
```

### Update Submission Status

```
POST /submissions/<id>/status
      │
      ▼
Validate new_status in SUBMISSION_STATUSES
      │
      ▼
old_status = submission.status
submission.status = new_status
      │
      ▼
Create SubmissionStatusHistory(
  old_status, new_status, changed_by, remarks
)
      │
      ▼
add_activity("status_change", "submission", ...)
db.session.commit()
      │
      ▼
redirect → /submissions/<id>
```

---

## Status Lifecycle

```
submitted → under_review → interview → offered → joined
                         └──────────────────────────────► rejected
```

---

## KPI Metrics

| Metric | Calculation |
|--------|-------------|
| Total Submissions | Count of filtered submissions |
| In Interview | Count where status = "interview" |
| Selected / Offered | Count where status in (selected, offered, joined) |
| Conversion Rate | selected / total × 100% |

---

## Models Used

- `Submission` — core record
- `SubmissionStatusHistory` — every status change logged
- `Candidate` — the candidate being submitted
- `Job` — the job being applied to
- `User` — recruiter assignment
- `Note` — notes on submission
- `Task` — tasks linked to submission
