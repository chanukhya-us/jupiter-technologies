# clients — Client Management Module

Manages client companies that post jobs and host projects.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| GET | `/clients` | `list_clients()` | owner, admin, recruiter, hr |
| GET | `/clients/new` | `new_client()` | owner, admin, recruiter, hr |
| POST | `/clients` | `create_client()` | owner, admin, recruiter, hr |
| GET | `/clients/<id>` | `client_detail()` | owner, admin, recruiter, hr |
| POST | `/clients/<id>/update` | `update_client()` | owner, admin, recruiter, hr |

---

## Flow Diagrams

### List Clients

```
GET /clients
      │
      ▼
Read query param: search (company_name ilike)
      │
      ▼
Build filtered query
      │
      ▼
build_donut_chart(active vs inactive)
build_donut_chart(with contact vs missing contact)
      │
      ▼
render clients/list.html
  ├── Search bar
  ├── Active/Inactive donut chart
  ├── Contact coverage donut chart
  └── Clients table
```

### Create Client

```
POST /clients
      │
      ▼
Validate company_name (required)
      │
      ├── Missing → flash error → redirect /clients/new
      │
      ▼
Create Client(company_name, contact_person, email,
              phone, address, notes, is_active=True)
      │
      ▼
add_activity("create", "client", client.id, ...)
db.session.commit()
      │
      ▼
redirect → /clients/<id>
```

### Client Detail

```
GET /clients/<id>
      │
      ▼
Load client or 404
      │
      ▼
Load related:
  ├── jobs (Job.query.filter_by(client_id=id))
  ├── projects (Project.query.filter_by(client_id=id))
  ├── notes (entity_type="client")
  └── tasks (entity_type="client")
      │
      ▼
render clients/detail.html
```

---

## Models Used

- `Client` — core record
- `Job` — jobs posted by this client
- `Project` — projects for this client
- `Note` — notes on client
- `Task` — tasks linked to client
