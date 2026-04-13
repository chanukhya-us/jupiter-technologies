# reports — Dashboard & Reporting Module

Provides the main operational dashboard with KPI metrics, interactive charts, and CSV export capabilities.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/dashboard` | `dashboard()` | all except marketer |
| GET | `/reports` | `reports_home()` | all except marketer |
| GET | `/reports/candidates.csv` | `candidates_csv()` | all except marketer |
| GET | `/reports/submissions.csv` | `submissions_csv()` | all except marketer |
| GET | `/reports/timesheets.csv` | `timesheets_csv()` | all except marketer |
| GET | `/test-charts` | `test_charts()` | all authenticated |

---

## Flow Diagrams

### Dashboard

```
GET /dashboard
      │
      ▼
Calculate KPI metrics:
  ├── total_candidates (Candidate.query.count())
  ├── open_jobs (Job.query.filter_by(status="open").count())
  ├── submissions_this_week (since Monday)
  ├── interviews_pending (status="interview")
  ├── active_employees (status="active")
  ├── pending_timesheets (status="submitted")
  └── overdue_tasks (due_date < today, status in open/in_progress)
      │
      ▼
Build 5 donut charts:
  ├── candidate_status
  ├── job_status
  ├── submission_status
  ├── timesheet_status
  └── task_status
      │
      ▼
Build hiring activity trend (bar+line chart):
  ├── Infer month bucket count from oldest data
  ├── candidates added per month
  ├── submissions created per month
  └── jobs opened per month
      │
      ▼
Build timesheet velocity (bar+line chart):
  ├── Infer week bucket count from oldest data
  ├── hours logged per week
  └── timesheet count per week
      │
      ▼
Build submission funnel (horizontal bar):
  └── reuse submission_status chart data
      │
      ▼
Load recent_logs (last 10 ActivityLog entries)
      │
      ▼
render reports/dashboard.html
```

### CSV Exports

```
GET /reports/candidates.csv
      │
      ▼
Query all candidates ordered by created_at DESC
      │
      ▼
Build rows: [id, full_name, email, phone, status, location, source, owner_user_id]
      │
      ▼
add_activity("export", "report", ...)
db.session.commit()
      │
      ▼
csv_response("candidates.csv", headers, rows)  → stream download
```

---

## Chart Data Structure

All charts use `build_donut_chart()` from `utils.py`:

```python
{
  "labels": ["open", "on_hold", "closed"],
  "values": [25, 5, 10],
  "colors": ["#2563eb", "#10b981", "#f59e0b"],
  "items": [
    {"label": "open", "value": 25, "percentage": 62.5, "color": "#2563eb"},
    ...
  ],
  "total": 40
}
```

Series charts (hiring activity, timesheet velocity) use:

```python
{
  "labels": ["Nov '25", "Dec '25", ...],
  "datasets": [
    {"type": "bar", "label": "Candidates Added", "data": [...], ...},
    {"type": "line", "label": "Jobs Opened", "data": [...], ...}
  ],
  "totals": {"candidates": 55, "submissions": 40, "jobs": 40},
  "is_empty": False
}
```

---

## Helper Functions

| Function | Purpose |
|----------|---------|
| `_recent_month_buckets(anchor, count)` | Generate last N month labels |
| `_recent_week_starts(anchor, count)` | Generate last N week start dates |
| `_infer_month_bucket_count(anchor, datetimes)` | Auto-size chart window from data |
| `_infer_week_bucket_count(anchor, week_starts)` | Auto-size week chart window |
| `_count_datetimes_by_month(datetimes, buckets)` | Aggregate counts per month |
| `_series_total(*series)` | Sum all series values (for is_empty check) |
