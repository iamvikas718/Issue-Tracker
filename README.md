# Issue Tracker Lite

A small, well-structured issue tracking system demonstrating clear architectural boundaries, enforced business rules, and safe API design.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React, single HTML file)                      │
│  Pure UI: renders state, calls API, shows transitions    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (REST)
┌──────────────────────▼──────────────────────────────────┐
│  API Layer — app.py                                      │
│  Thin routes: parse HTTP → call service → return JSON    │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Service Layer — services.py                             │
│  Orchestrates: validates inputs, calls domain + DB       │
└──────────┬───────────────────────┬──────────────────────┘
           │                       │
┌──────────▼──────────┐  ┌────────▼──────────────────────┐
│  Domain — domain.py │  │  Database — database.py        │
│  Pure business rules│  │  Raw SQL only, no logic        │
│  Status state machine│  │  Returns sqlite3.Row objects  │
└─────────────────────┘  └───────────────────────────────┘
```

### The Key Principle: Business Rules Live in ONE Place

The status transition machine lives **only** in `domain.py`:

```
OPEN → IN_PROGRESS → DONE
```

Invalid transitions (e.g., `OPEN → DONE`, any backward move) are **blocked by the server**, not trusted to UI hints. The API returns a `422` error with a clear message. The database also has a `CHECK` constraint as a final backstop.

---

## Project Structure

```
issue-tracker/
├── backend/
│   ├── domain.py        ← Business rules & state machine
│   ├── database.py      ← SQLite queries (no logic)
│   ├── services.py      ← Orchestration layer
│   ├── app.py           ← Flask routes (thin)
│   └── requirements.txt
└── frontend/
    └── index.html       ← React SPA (single file)
```

---

## Setup & Run

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000
```

### Frontend

```bash
# Just open in a browser:
open frontend/index.html
# Or serve with any static server:
python -m http.server 8080 --directory frontend
```

---

## API Reference

All responses follow `{ "ok": true, "data": ... }` or `{ "ok": false, "error": "..." }`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/projects` | List all projects |
| `POST` | `/api/projects` | Create a project `{ name }` |
| `GET` | `/api/projects/:id` | Get a project |
| `GET` | `/api/projects/:id/issues` | List issues for a project |
| `POST` | `/api/projects/:id/issues` | Create an issue `{ title, description? }` |
| `POST` | `/api/issues/:id/transition` | Change status `{ status }` — enforced by state machine |

### Status Transitions

```
OPEN  ──→  IN_PROGRESS  ──→  DONE
```

**Any other transition returns HTTP 422.**

Example:
```bash
# ✅ Valid
curl -X POST http://localhost:5000/api/issues/1/transition \
  -H 'Content-Type: application/json' \
  -d '{"status": "IN_PROGRESS"}'

# ❌ Invalid — returns 422
curl -X POST http://localhost:5000/api/issues/1/transition \
  -H 'Content-Type: application/json' \
  -d '{"status": "DONE"}'
# → {"ok": false, "error": "Cannot transition from OPEN to DONE. Allowed: ['IN_PROGRESS']."}
```

---

## Design Decisions

- **Domain is pure Python** — no imports from Flask or SQLite. Testable in isolation.
- **Database layer returns raw rows** — services convert them to dicts. DB is swappable.
- **Services are the only callers of domain** — routes never touch `validate_transition()`.
- **SQLite CHECK constraint** on status as a defense-in-depth backstop.
- **Single-file frontend** — zero build tooling, loads React from CDN.


## Deployment
- Backend: deploy directly from this GitHub repo using Render or Railway.
- Frontend: served via GitHub Pages from the `/docs` folder.
