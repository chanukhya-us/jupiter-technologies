# auth — Authentication Module

Handles user login and logout with session management and activity logging.

---

## Routes

| Method | URL | Function | Access |
|--------|-----|----------|--------|
| GET | `/login` | `login()` | Public |
| POST | `/login` | `login_post()` | Public |
| POST | `/logout` | `logout()` | Authenticated |

---

## Flow Diagrams

### Login Flow

```
GET /login
      │
      ├── Already logged in? → redirect /dashboard
      └── Not logged in → render login.html

POST /login
      │
      ▼
Extract username + password from form
      │
      ▼
User.query.filter_by(username=..., is_active=True)
      │
      ├── User not found or inactive
      │         └── flash "Invalid credentials" → redirect /login
      │
      ▼
check_password_hash(user.password_hash, password)
      │
      ├── Wrong password
      │         └── flash "Invalid credentials" → redirect /login
      │
      ▼
login_user(user)  ← Flask-Login sets session cookie
      │
      ▼
add_activity("login", "user", user.id, ...)
db.session.commit()
      │
      ▼
flash "Welcome back" → redirect /dashboard
```

### Logout Flow

```
POST /logout
      │
      ▼
Capture user.id and username (before logout clears session)
      │
      ▼
logout_user()  ← Flask-Login clears session
      │
      ▼
add_activity("logout", "user", user_id, ...)
db.session.commit()
      │
      ▼
flash "Logged out" → redirect /login
```

---

## Key Notes

- Passwords are stored as bcrypt hashes — never plain text
- `is_active=False` users cannot log in even with correct password
- All login/logout events are written to `ActivityLog`
- After login, Flask-Login stores `user.id` in the session cookie
- `@login_required` on any route redirects unauthenticated users to `/login`
