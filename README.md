# Trekking Management Application

A web application built with **Vue 3** and **Flask** to manage trekking activities involving trek organizers, staff, and participants. Uses **Celery** + **Redis** for background job processing and **MailHog** for local email testing.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite, Pinia, Vue Router, Bootstrap 5 |
| Backend | Flask, Flask-Security, Flask-SQLAlchemy |
| Database | SQLite |
| Task Queue | Celery 5 |
| Message Broker | Redis |
| Email (Dev) | MailHog |

---

## Project Structure

```
trekking-management-application/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models.py            # SQLAlchemy models (User, Trek, Booking, etc.)
│   │   ├── extensions.py        # Flask extensions (db, security)
│   │   ├── forms.py             # Registration form
│   │   ├── signals.py           # Flask-Security signal handlers
│   │   ├── routes/
│   │   │   └── api/
│   │   │       ├── admin/       # Admin endpoints (treks, users, staff, search)
│   │   │       ├── staff/       # Staff endpoints (assigned treks)
│   │   │       └── user/        # User endpoints (auth, bookings, treks, export)
│   │   └── tasks/
│   │       ├── reminders.py     # Daily reminder emails
│   │       ├── reports.py       # Monthly admin activity report
│   │       └── export.py        # Async CSV export of trekking history
│   ├── app.py                   # Entry point — creates app, seeds admin user
│   ├── celery_app.py            # Celery app factory + Beat schedules
│   ├── requirements.txt
│   └── exports/                 # Generated CSV exports (auto-created)
├── frontend/
│   ├── src/
│   └── package.json
├── docker-compose.yaml          # Redis, Redis Commander, MailHog
├── .env                         # Environment variables (not committed)
└── .env.example                 # Template for .env
```

---

## Prerequisites

- **Python** 3.11+
- **Node.js** 22+ (see `frontend/package.json` engines)
- **Docker** & **Docker Compose** (for Redis, MailHog)

---

## Getting Started

### 1. Clone & Configure

```bash
git clone <repository-url>
cd trekking-management-application
cp .env.example .env
```

Edit `.env` and set your values:

```env
SECRET_KEY='your-secret-key'
SECURITY_PASSWORD_SALT='your-salt'
SQLALCHEMY_DATABASE_URI='sqlite:///database.sqlite'
ADMIN_EMAIL='admin@example.com'
ADMIN_PASSWORD='password'
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/1'
SMTP_HOST='localhost'
SMTP_PORT=1025
SMTP_FROM='noreply@trekking.app'
```

### 2. Start Docker Services

```bash
docker compose up -d
```

This starts:
- **Redis** on port `6379`
- **Redis Commander** on [http://localhost:8081](http://localhost:8081)
- **MailHog** SMTP on port `1025`, Web UI on [http://localhost:8025](http://localhost:8025)

### 3. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Initialize Database & Start Server

```bash
python app.py
```

This will:
- Create all database tables
- Seed the admin user (from `ADMIN_EMAIL` / `ADMIN_PASSWORD` in `.env`)
- Start the Flask dev server on [http://localhost:5000](http://localhost:5000)

### 5. Start Celery Worker & Beat

Open two additional terminals (with the venv activated):

```bash
# Terminal 2 — Task worker
cd backend
source .venv/bin/activate
celery -A celery_app worker --loglevel=info
```

```bash
# Terminal 3 — Scheduled tasks (Beat)
cd backend
source .venv/bin/activate
celery -A celery_app beat --loglevel=info
```

### 6. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server starts on [http://localhost:5173](http://localhost:5173).

---

## Background Jobs (Celery)

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Description |
|------|----------|-------------|
| `send_daily_reminders` | Every day at 08:00 UTC | Emails all users who have a booked trek coming up |
| `generate_monthly_report` | 1st of every month at 06:00 UTC | Sends an HTML activity report to the admin |

### On-Demand Tasks

| Task | Trigger | Description |
|------|---------|-------------|
| `export_trekking_history` | `POST /api/user/export` | Generates a CSV of the user's booking history and emails it |

### Export API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/user/export` | Start an async export — returns `{ "task_id": "..." }` |
| `GET` | `/api/user/export/<task_id>` | Poll task status (`PENDING` / `STARTED` / `SUCCESS` / `FAILURE`) |
| `GET` | `/api/user/export/<task_id>/download` | Download the completed CSV file |

### Manual Testing

You can manually dispatch background tasks directly using the included `trigger_tasks.py` script:

```bash
cd backend
source .venv/bin/activate

# Trigger daily reminders
python trigger_tasks.py --reminders

# Trigger monthly admin report
python trigger_tasks.py --report

# Trigger CSV export for user ID 1
python trigger_tasks.py --export 1

# Trigger both reminders and report
python trigger_tasks.py --all
```

Check sent emails at [http://localhost:8025](http://localhost:8025) (MailHog).

---

## User Roles

| Role | Access |
|------|--------|
| `admin` | Full management — treks, users, staff, reports |
| `staff` | View/manage assigned treks, mark treks complete |
| `user` | Browse open treks, book/cancel, export history |

---

## API Overview

### Admin (`/api/admin/`) — requires `admin` role

- `GET/POST` `/treks` — List / Create treks
- `GET/PUT/DELETE` `/treks/<id>` — View / Update / Delete a trek
- `PUT` `/treks/<id>/assign` — Assign staff to a trek
- `GET` `/treks/<id>/users` — List registered users for a trek
- `GET/POST` `/staff` — List / Add staff
- `GET/PUT` `/staff/<id>` — View / Update staff
- `PUT` `/staff/<id>/status` — Update staff status
- `GET` `/users` — List users
- `GET` `/users/<id>` — View user
- `PUT` `/users/<id>/status` — Update user status/roles
- `GET` `/search_users?q=` `/search_staff?q=` `/search_treks?q=` — Search

### Staff (`/api/staff/`) — requires `staff` role

- `GET` `/treks` — List assigned treks
- `GET/PUT` `/treks/<id>` — View / Update assigned trek
- `GET` `/treks/<id>/users` — List registered users
- `PUT` `/treks/<id>/complete` — Mark trek as completed

### User (`/api/user/`)

- `GET/PUT` `/profile` — View / Update profile
- `GET` `/treks` — Browse open treks
- `GET` `/treks/<id>` — View trek details
- `POST` `/bookings` — Book a trek
- `GET` `/bookings` — List bookings
- `GET` `/bookings/<id>` — View booking
- `PUT` `/bookings/<id>/cancel` — Cancel booking
- `POST` `/export` — Trigger CSV export
- `GET` `/export/<task_id>` — Check export status
- `GET` `/export/<task_id>/download` — Download CSV

---

## Dev Tools

| Tool | URL | Purpose |
|------|-----|---------|
| Flask Dev Server | [http://localhost:5000](http://localhost:5000) | Backend API |
| Vite Dev Server | [http://localhost:5173](http://localhost:5173) | Frontend |
| MailHog | [http://localhost:8025](http://localhost:8025) | Captured emails |
| Redis Commander | [http://localhost:8081](http://localhost:8081) | Redis key inspector |
