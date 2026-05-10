# NodeSec — Attack Surface Intelligence Platform

NodeSec is a passive security scanning tool for non-expert IT admins. You give it a domain name, it quietly collects public information (no hacking, no active probing), builds a visual attack graph, and tells you exactly what's exposed and how to fix it.

> Built with FastAPI + React + PostgreSQL. Runs fully in Docker.

---

## What it does

- Discovers subdomains via certificate transparency logs (crt.sh, CertSpotter, OTX)
- Checks DNS records, SSL certificates, open ports (via Shodan InternetDB — passive, free)
- Checks email security posture (SPF, DKIM, DMARC)
- Optionally checks data breaches via HaveIBeenPwned
- Runs a deterministic rule engine to detect chained attack paths
- Visualizes everything as an interactive attack graph
- Gives plain-language explanations + exact remediation commands

---

## Prerequisites

You need these installed before anything else:

| Tool | Why | Download |
|------|-----|----------|
| **Docker Desktop** | Runs the whole stack | https://www.docker.com/products/docker-desktop |
| **Git** | Clone the repo | https://git-scm.com |
| **Node.js 20+** | Only needed to generate `package-lock.json` on first clone | https://nodejs.org |

That's it. You do **not** need Python, PostgreSQL, or anything else installed locally.

---

## First-time setup (do this once)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/NodeSec.git
cd NodeSec
```

### 2. Generate the frontend lockfile

This is only needed once after a fresh clone because `package-lock.json` is gitignored.

```bash
npm install --prefix nodesec-frontend
```

### 3. Set up environment variables

```bash
cp nodesec-backend/.env.example nodesec-backend/.env
cp nodesec-frontend/.env.example nodesec-frontend/.env
```

The defaults work out of the box for local development. You don't need to change anything to get started.

> **Optional:** If you want breach detection to work, get a free API key from https://haveibeenpwned.com/API/Key and add it to `nodesec-backend/.env` as `HIBP_API_KEY=your_key_here`

### 4. Start everything

```bash
docker compose up --build
```

First run takes 3-5 minutes to download images and install dependencies. Subsequent starts are fast.

### 5. Open the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

---

## Daily development workflow

```bash
# Start the stack
docker compose up

# Stop the stack
docker compose down

# Start in background (no log output)
docker compose up -d

# View logs when running in background
docker compose logs -f

# View logs for one service only
docker compose logs -f backend
```

### Do I need to rebuild?

Only run `docker compose up --build` when you change one of these:

- `nodesec-backend/requirements.txt`
- `nodesec-frontend/package.json`
- Either `Dockerfile`

For everything else (editing Python files, React components, etc.) just save the file — the backend and frontend both hot-reload automatically.

---

## Project structure

```
NodeSec/
├── nodesec-backend/          # FastAPI Python backend
│   ├── main.py               # App entry point
│   ├── config.py             # Settings loaded from .env
│   ├── database.py           # PostgreSQL async connection
│   ├── routers/              # API endpoints (auth, scan, domains, findings, reports)
│   ├── services/             # Business logic
│   ├── osint/                # Passive data collection (subdomains, DNS, SSL, ports)
│   ├── rule_engine/          # Deterministic attack chain detection (13 rules)
│   ├── scoring/              # Risk score calculation
│   ├── workers/              # Background scan orchestrator
│   ├── models/               # Database models
│   ├── schemas/              # Request/response validation
│   └── .env                  # Your local config (never commit this)
│
├── nodesec-frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── pages/            # Full page components
│   │   ├── components/       # Reusable UI components
│   │   ├── api/              # All API calls (axios)
│   │   ├── hooks/            # Custom React hooks
│   │   └── store/            # Zustand auth state
│   └── .env                  # VITE_API_URL (never commit this)
│
├── docker-compose.yml        # Local dev stack
├── docker-compose.prod.yml   # Production overrides
└── CLAUDE.md                 # Full engineering spec and standards
```

---

## Environment variables

### Backend (`nodesec-backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string — default works with Docker |
| `SECRET_KEY` | Yes | JWT signing key — change this in production |
| `ALGORITHM` | Yes | JWT algorithm — leave as `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Token lifetime — default 1440 (24h) |
| `ALLOWED_ORIGINS` | Yes | CORS origins — default allows localhost:5173 |
| `HIBP_API_KEY` | No | HaveIBeenPwned API key for breach detection |
| `SHODAN_API_KEY` | No | Not currently used (app uses free Shodan InternetDB) |
| `SENDGRID_API_KEY` | No | For email alerts — feature not yet active |

### Frontend (`nodesec-frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend URL — default `http://localhost:8000` |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, React Flow (@xyflow/react), TanStack Query, Zustand, Framer Motion |
| Backend | FastAPI, SQLAlchemy (async), Alembic, Pydantic v2 |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose) + bcrypt |
| OSINT | httpx, dnspython, Shodan InternetDB (free), crt.sh, CertSpotter, OTX |
| Container | Docker + Docker Compose |

---

## API overview

All endpoints are prefixed with `/api/v1/`. Full interactive docs at http://localhost:8000/docs.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login, get JWT token |
| GET | `/domains/` | List your domains |
| POST | `/domains/add` | Add a domain to monitor |
| POST | `/domains/{id}/verify` | Mark domain as verified |
| POST | `/scan/start` | Start a scan |
| GET | `/scan/{id}/stream` | SSE stream of live scan progress |
| GET | `/scan/{id}/result` | Get completed scan results |
| GET | `/scan/history/{domain_id}` | Scan history for a domain |
| GET | `/findings/{scan_id}` | Get findings for a scan |
| PATCH | `/findings/{id}` | Update finding status |
| GET | `/reports/{scan_id}/pdf` | Download PDF report |

---

## Running the demo scan

Don't have a domain to test with? Use the built-in demo:

1. Go to http://localhost:5173
2. Register an account
3. Click **New Scan**
4. Click **Run Demo**

This loads a pre-built scan for a fictional college domain with realistic vulnerabilities — no network requests made.

---

## Common issues

**`npm ci` fails when building Docker**
You need to generate `package-lock.json` first:
```bash
npm install --prefix nodesec-frontend
docker compose up --build
```

**Domain add returns 422**
The domain name must be a valid hostname — no `http://`, no underscores, no bare words.
- ✅ `github.com`, `example.edu`, `sub.domain.org`
- ❌ `http://github.com`, `my_domain.com`, `localhost`

**Scan shows "Failed"**
Old scans from before the SSL fix may show as failed. Start a new scan — it will work.

**PDF export downloads HTML instead of PDF**
WeasyPrint requires GTK native libraries which aren't available on bare Windows. It works correctly inside Docker on Linux. If you need PDF locally on Windows, install the [GTK runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer).

**Port 5432 already in use**
You have a local PostgreSQL running. Either stop it or change the port in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"   # use 5433 on host instead
```

---

## Making changes

### Backend (Python)
Edit any file in `nodesec-backend/` and save — uvicorn reloads automatically. No restart needed.

### Frontend (React)
Edit any file in `nodesec-frontend/src/` and save — Vite HMR updates the browser instantly.

### Database schema changes
After editing `nodesec-backend/models/models.py`:
```bash
# Connect to the backend container
docker compose exec backend bash

# Generate and apply migration
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

### Adding a Python package
1. Add it to `nodesec-backend/requirements.txt`
2. Rebuild: `docker compose up --build`

### Adding a frontend package
1. `npm install <package> --prefix nodesec-frontend`
2. Rebuild: `docker compose up --build`

---

## Running tests

```bash
# Backend unit tests
docker compose exec backend python -m pytest tests/ -v

# Frontend tests
docker compose exec frontend npm test
```

---

## Deployment

See `docker-compose.prod.yml` for production overrides. Key things to change before deploying:

- Set a strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Set `ALLOWED_ORIGINS` to your actual frontend URL
- Use a managed PostgreSQL instance (Railway, Supabase, Neon, etc.)
- Set `DATABASE_URL` to point to your production database

---

## Contributing

1. Read `CLAUDE.md` — it's the full engineering spec and coding standards
2. Branch off `main`: `git checkout -b feature/your-feature`
3. Make your changes
4. Test with `docker compose up`
5. Open a PR

---

## License

MIT
