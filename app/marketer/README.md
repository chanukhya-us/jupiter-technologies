# marketer — Marketer Activity Module

Tracks daily marketing activities for compliance, with timezone-aware cutoff enforcement, automated reminders, escalation notifications, and onboarding workflow.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/marketer-activity` | `home()` | owner, admin, marketer |
| GET | `/marketer-activity/logs` | `list_logs()` | owner, admin, marketer |
| GET | `/marketer-activity/logs/new` | `new_log()` | owner, admin, marketer |
| POST | `/marketer-activity/logs` | `create_log()` | owner, admin, marketer |
| GET | `/marketer-activity/logs/<id>` | `log_detail()` | owner, admin, marketer |
| POST | `/marketer-activity/logs/<id>` | `update_log()` | owner, admin, marketer |
| POST | `/marketer-activity/logs/<id>/submit` | `submit_log()` | owner, admin, marketer |
| GET | `/marketer-activity/reports` | `reports()` | owner, admin, marketer |
| GET | `/marketer-activity/reports/export.csv` | `export_csv()` | owner, admin, marketer |
| GET/POST | `/marketer-activity/onboard` | `onboard_marketer()` | owner, admin |
| GET/POST | `/marketer-activity/settings` | `settings()` | owner, admin, marketer |

---

## Flow Diagrams

### List Logs

```
GET /marketer-activity/logs
      │
      ▼
Resolve target marketer:
  ├── admin/owner → can filter by any marketer
  └── marketer    → always own logs
      │
      ▼
ensure_marketer_profile(target_marketer_id)
  └── Creates profile if missing
      │
      ▼
local_now_for_profile(profile)  ← timezone-aware
      │
      ▼
Default date range: last 30 days (local time)
Apply filters: from_date, to_date, status, marketer_user_id
      │
      ▼
Calculate metrics:
  ├── total_logs
  ├── submitted_logs
  ├── missed_logs
  ├── completion_rate = submitted / total * 100
  └── avg_activities_per_log
      │
      ▼
build_donut_chart(status distribution)
build_donut_chart(job_type distribution)
      │
      ▼
Check today/yesterday log availability:
  ├── can_log_today
  └── can_log_yesterday
      │
      ▼
render marketer_activity/list.html
```

### Create & Submit Log

```
GET /marketer-activity/logs/new
      │
      ▼
can_marketer_edit_date(profile, today)?
  ├── No  → flash "Cannot log for this date" → redirect list
  └── Yes → render new log form

POST /marketer-activity/logs
      │
      ▼
Validate log_date (today or yesterday only, before cutoff)
      │
      ▼
Check for duplicate log on same date
  └── Duplicate → flash warning → redirect

Create MarketerDailyLog(
  marketer_user_id, log_date,
  jobs_applied, follow_ups, interviews_scheduled,
  pay_discussions, job_type, hourly_rate_min/max,
  project_duration_weeks, notes,
  status = "draft"
)
      │
      ▼
add_activity("create", "marketer_log", ...)
db.session.commit()

POST /marketer-activity/logs/<id>/submit
      │
      ▼
submit_status_for_log(profile, log.log_date):
  ├── Before cutoff → "submitted"
  └── After cutoff  → "late"
      │
      ▼
log.status = determined_status
log.submitted_at = now
log.submitted_by = current_user.id
      │
      ▼
add_activity("submit", "marketer_log", ...)
db.session.commit()
```

### Onboard Marketer

```
GET /marketer-activity/onboard
      │
      ▼
Load all users (for manager dropdown)
render marketer_activity/onboard.html

POST /marketer-activity/onboard
      │
      ▼
Validate: full_name, username, email, password (all required)
      │
      ├── Missing → flash error → redirect onboard
      │
      ▼
Check username + email uniqueness
      │
      ├── Duplicate → flash error → redirect onboard
      │
      ▼
Create User(
  full_name, username, email,
  password_hash = generate_password_hash(password),
  role = "marketer",
  is_active = True
)
      │
      ▼
Create MarketerProfile(
  user_id, timezone, daily_cutoff_local_time,
  workdays_mask, reminder_times_local,
  manager_user_id, target_jobs_per_day,
  escalation_after_misses
)
      │
      ▼
add_activity("create", "marketer_profile", ...)
db.session.commit()
      │
      ▼
redirect → /marketer-activity/settings
```

### Background Scheduler (process_marketer_reminders)

```
Runs at configured times (cron/scheduler)
      │
      ▼
For each active marketer profile:
      │
      ▼
local_now = local_now_for_profile(profile)
      │
      ▼
Is it a workday? (is_workday(profile, today))
  └── No → skip
      │
      ▼
Has log been submitted today?
  ├── Yes → skip
  └── No  →
        │
        ▼
      Is it reminder time?
        └── Yes → create_notification(type="reminder", channel="in_app"+"email")
        │
        ▼
      Is it past cutoff?
        └── Yes → mark log as "missed"
                  │
                  ▼
                Count consecutive missed days
                  │
                  ▼
                missed_streak >= escalation_after_misses?
                  └── Yes → create_notification(type="escalation", to manager)
```

---

## Settings Configuration

| Setting | Description |
|---------|-------------|
| `timezone` | Marketer's local timezone (e.g. America/New_York) |
| `daily_cutoff_local_time` | Time after which log is "late" (e.g. 18:00) |
| `workdays_mask` | "1,1,1,1,1,0,0" = Mon–Fri |
| `reminder_times_local` | "16:00,17:30" = two daily reminders |
| `target_jobs_per_day` | Expected daily job applications |
| `escalation_after_misses` | Consecutive misses before escalation |
| `manager_user_id` | Who receives escalation notifications |

---

## Service Layer (service.py)

| Function | Purpose |
|----------|---------|
| `ensure_marketer_profile(user_id)` | Auto-create profile with defaults if missing |
| `local_now_for_profile(profile)` | Get current time in marketer's timezone |
| `is_workday(profile, date)` | Check workdays_mask for given date |
| `can_marketer_edit_date(profile, date)` | Today/yesterday before cutoff only |
| `can_marketer_edit_log(log, profile, is_admin)` | Admins can always edit |
| `submit_status_for_log(profile, log_date)` | "submitted" or "late" |
| `parse_workdays_mask(mask)` | "1,1,1,1,1,0,0" → {0,1,2,3,4} |
| `parse_reminder_times(str)` | "16:00,17:30" → [time(16,0), time(17,30)] |
| `create_notification(...)` | Idempotent notification creation |
| `send_email_safe(...)` | SMTP email with error handling |
| `process_marketer_reminders(run_at_utc)` | Full scheduler job |

---

## Models Used

- `MarketerProfile` — per-marketer configuration
- `MarketerDailyLog` — daily activity record
- `MarketerNotification` — reminders and escalations
- `User` — marketer user + manager
- `Role` — marketer role lookup
