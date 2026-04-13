# candidates — Candidate Management Module

Manages the full candidate lifecycle from creation through placement, including status tracking, resume uploads, and pipeline analytics.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/candidates` | `list_candidates()` | owner, admin, recruiter, hr |
| GET | `/candidates/new` | `new_candidate()` | owner, admin, recruiter, hr |
| POST | `/candidates` | `create_candidate()` | owner, admin, recruiter, hr |
| GET | `/candidates/<id>` | `candidate_detail()` | owner, admin, recruiter, hr |
| GET | `/candidates/<id>/edit` | `edit_candidate()` | owner, admin, recruiter, hr |
| POST | `/candidates/<id>/update` | `update_candidate()` | owner, admin, recruiter, hr |
| POST | `/candidates/<id>/status` | `update_candidate_status()` | owner, admin, recruiter, hr |

---

## Flow Diagrams

### List Candidates

```
GET /candidates
      │
      ▼
Read query params: search, status, source, location, owner_user_id
      │
      ▼
Build SQLAlchemy query with filters
      │
      ▼
Calculate trend graph (30–90 day window):
  ├── Get all candidates
  ├── Find oldest date → determine window
  ├── Group by date → daily counts
  └── Build labels + data arrays
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(source distribution, top_n=6)
      │
      ▼
render candidates/list.html
  ├── Filter bar
  ├── Trend line chart
  ├── Status donut chart
  ├── Source donut chart
  └── Candidates table
```

### Create Candidate

```
POST /candidates
      │
      ▼
Validate full_name (required)
      │
      ├── Missing → flash error → redirect /candidates/new
      │
      ▼
Create Candidate(full_name, phone, email, location,
                 primary_skills, years_experience, source,
                 status, owner_user_id, notes_summary)
      │
      ▼
Handle resume upload (optional):
  ├── Validate extension (UPLOAD_EXTENSIONS)
  ├── Generate UUID filename
  └── Save to uploads/resumes/
      │
      ▼
db.session.add(candidate)
db.session.flush()  ← get candidate.id
      │
      ▼
Create CandidateStatusHistory(old_status=None, new_status=status)
      │
      ▼
add_activity("create", "candidate", candidate.id, ...)
db.session.commit()
      │
      ▼
redirect → /candidates/<id>
```

### Update Candidate Status

```
POST /candidates/<id>/status
      │
      ▼
Validate new_status in CANDIDATE_STATUSES
      │
      ├── Invalid → flash error → redirect detail
      │
      ▼
old_status = candidate.status
candidate.status = new_status
      │
      ▼
Create CandidateStatusHistory(
  old_status=old_status,
  new_status=new_status,
  changed_by=current_user.id,
  remarks=remarks
)
      │
      ▼
add_activity("status_change", "candidate", ...)
db.session.commit()
      │
      ▼
redirect → /candidates/<id>
```

---

## Status Lifecycle

```
new → screening → submitted → interview → selected → joined
                                        └──────────────────► rejected
                                        └──────────────────► on_hold
```

---

## Models Used

- `Candidate` — core record
- `CandidateStatusHistory` — every status change logged
- `Note` — notes attached to candidate
- `Task` — tasks linked to candidate
- `Submission` — submissions for this candidate
- `User` — owner assignment
