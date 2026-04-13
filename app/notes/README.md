# notes — Entity Notes Module

Provides a simple note-taking system that can be attached to any entity in the system. Notes are created inline from entity detail pages.

---

## Routes

| Method | URL | Function | Roles |
|--------|-----|----------|-------|
| POST | `/notes` | `create_note()` | all authenticated |
| POST | `/notes/<id>/delete` | `delete_note()` | owner, admin only |

---

## Flow Diagrams

### Create Note

```
POST /notes  (submitted from entity detail page)
      │
      ▼
Validate:
  ├── entity_type in ENTITY_TYPES
  ├── entity_id is a digit
  └── content is not empty
      │
      ├── Invalid → flash error → redirect back
      │
      ▼
Validate note_type in NOTE_TYPES
  └── Invalid type → default to "internal"
      │
      ▼
Create Note(
  entity_type, entity_id,
  note_type (call/email/internal/feedback/followup),
  content,
  created_by = current_user.id
)
      │
      ▼
add_activity("create", "note", note.id, ...)
db.session.commit()
      │
      ▼
flash "Note added" → redirect to redirect_to param
```

### Delete Note

```
POST /notes/<id>/delete
      │
      ▼
Load Note or 404
      │
      ▼
Role check:
  ├── Not owner/admin → flash error → redirect back
  │
  ▼
db.session.delete(note)
add_activity("delete", "note", note.id, ...)
db.session.commit()
      │
      ▼
flash "Note deleted" → redirect to redirect_to param
```

---

## Note Types

| Type | Use Case |
|------|----------|
| `call` | Phone call summary |
| `email` | Email correspondence |
| `internal` | Internal team note |
| `feedback` | Interview or client feedback |
| `followup` | Follow-up reminder note |

---

## Entity Types

Notes can be attached to: `candidate`, `client`, `job`, `submission`, `employee`, `project`, `general`

---

## Models Used

- `Note` — core record
- `User` — note creator
