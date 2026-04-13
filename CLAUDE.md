# CLAUDE.md — Developer Standards for Jupiter Technologies

This file defines mandatory standards that must be followed for every change made to this codebase.

---

## 1. Documentation Requirements

### For Every New Module or Blueprint

When adding a new blueprint or module under `app/`, you MUST create `app/<module>/README.md` containing:

- **Overview** — what the module does in 1–2 sentences
- **Routes table** — Method, URL, function name, allowed roles
- **Flow diagrams** — ASCII flowchart for every route showing the full request path
- **Status lifecycle** — if the module has status transitions, diagram them
- **Models used** — list every model the module reads or writes

### For Every Change to an Existing Module

When modifying routes, models, or business logic in an existing module:

- Update `app/<module>/README.md` to reflect the change
- If a new route is added, add it to the routes table and add a flow diagram
- If a status is added/removed, update the lifecycle diagram

### Architecture File

`ARCHITECTURE.md` at the root must be kept up to date:

- If a new blueprint is added, add it to the Module Map table
- If a new model or relationship is added, update the Database Schema section
- If a new shared utility is added, add it to the Shared Utilities table

---

## 2. Git Workflow

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<name>` | `feature/candidate-bulk-import` |
| Bug fix | `fix/<name>` | `fix/timesheet-approval-bug` |
| Documentation | `docs/<name>` | `docs/developer-guide` |
| Release | `release/v<N>` | `release/v2` |

### Every Change Must

1. Be on a **feature branch** — never commit directly to `main`
2. Include a **Pull Request** targeting `main`
3. Have a clear PR description explaining what changed and why
4. Keep `main` and `release/v<N>` in sync after merge

### Commit Message Format

```
<type>: <short description>

Types: feat, fix, docs, refactor, test, chore
```

Examples:
```
feat: add bulk candidate import from CSV
fix: correct timesheet approval role check
docs: update candidates README with new filter route
```

---

## 3. Code Standards

### Python

- Use type hints on all function signatures
- Use `from __future__ import annotations` at top of every file
- All routes must have `@login_required` and `@roles_required(...)` where applicable
- All data-modifying routes must call `add_activity(...)` before `db.session.commit()`
- Use `db.session.flush()` before accessing auto-generated IDs
- Never commit directly to `db.session` without calling `add_activity` first

### Templates

- All JSON data passed to Chart.js canvas elements must use **single-quoted HTML attributes**:
  ```html
  data-labels='{{ data.labels | tojson }}'   ✓
  data-labels="{{ data.labels | tojson }}"   ✗  (breaks JSON with double quotes)
  ```
- Every list page with data should have at least one chart visualization
- Use `{% if chart['total'] > 0 %}` before rendering canvas elements

### JavaScript

- All chart initialization goes through `charts.js` — do not add inline `<script>` chart code
- Use `safeJSONParse()` for any JSON parsing from data attributes
- Bump the `?v=N` cache-busting version on `charts.js` in `base.html` after any JS change

---

## 4. Testing

- Write tests for every new route in `tests/`
- Run `pytest tests/ -v` before opening a PR — all tests must pass
- Test both the happy path and error cases (missing required fields, wrong role, etc.)

---

## 5. PR Checklist

Before opening a Pull Request, verify:

- [ ] Feature branch created (not committing to main)
- [ ] `app/<module>/README.md` created or updated
- [ ] `ARCHITECTURE.md` updated if models/blueprints changed
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] No hardcoded credentials or secrets
- [ ] `add_activity()` called for all data-modifying operations
- [ ] Chart data attributes use single quotes in templates
- [ ] Commit messages follow the format above
