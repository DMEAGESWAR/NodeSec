# CLAUDE.md — NodeSec Master Development Blueprint

> **Attack Surface Intelligence Platform**
> This file is the single source of truth for all engineering decisions on NodeSec.
> Every developer, AI agent, and CI pipeline must read and follow this document before writing a single line of code.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Folder Structure](#2-folder-structure)
3. [Frontend Standards](#3-frontend-standards)
4. [Backend Standards](#4-backend-standards)
5. [Middleware Configuration](#5-middleware-configuration)
6. [Database Standards](#6-database-standards)
7. [Security Standards](#7-security-standards)
8. [DevOps & Deployment](#8-devops--deployment)
9. [Testing Strategy](#9-testing-strategy)
10. [Developer Roles & Skills](#10-developer-roles--skills)
11. [AI Agent Rules (Claude Code)](#11-ai-agent-rules-claude-code)
12. [Coding Standards](#12-coding-standards)
13. [Performance Optimization](#13-performance-optimization)

---

## 1. Project Overview

### What NodeSec Is

NodeSec is a **passive attack surface intelligence platform** built for non-expert IT administrators at colleges, hospitals, and small organizations. It accepts a domain name, passively collects open-source intelligence (OSINT) from public sources, builds an interactive visual attack graph, runs a deterministic rule engine to detect chained attack paths, and outputs plain-language risk explanations with specific remediation commands.

### What NodeSec Is NOT

- Not an active penetration testing tool (no exploit payloads sent)
- Not an AI chatbot wrapper (all risk logic is deterministic rule-based)
- Not a competitor to enterprise ASM tools — it democratizes their output for non-experts

### Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│   Vite + React Flow + TanStack Query + Framer Motion + Zustand  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP / SSE (Server-Sent Events)
┌─────────────────────▼───────────────────────────────────────────┐
│                      FastAPI Backend                            │
│   Routers → Services → OSINT Pipeline → Rule Engine → DB Layer  │
└────────┬──────────────────────────────────────────┬────────────┘
         │                                          │
┌────────▼────────┐                      ┌──────────▼──────────┐
│   PostgreSQL    │                      │  External (Passive)  │
│   (SQLAlchemy   │                      │  crt.sh, dnspython  │
│    async ORM)   │                      │  HIBP, Shodan (opt) │
└─────────────────┘                      └─────────────────────┘
```

### Core Data Flow

```
User inputs domain
       ↓
POST /scan/start → creates Scan record (status: pending)
       ↓
Background worker: run_full_scan()
       ↓
Async OSINT pipeline (concurrent):
  subdomain_discovery() → crt.sh
  dns_records()         → dnspython
  port_scan()           → asyncio socket
  ssl_check()           → Python ssl lib
  check_domain_breach() → HIBP API (optional)
       ↓
Each discovered asset → saved as Node → SSE event → React Flow node appears
       ↓
RuleEngine.evaluate() → 11 IF-THEN chain rules → triggered chains
       ↓
scorer.overall_score() → risk score 0-100
       ↓
SSE complete event → frontend renders final state
       ↓
Scan persisted to PostgreSQL for history + delta comparison
```

---

## 2. Folder Structure

### Complete Monorepo Structure

```
nodesec/
├── nodesec-backend/                  # FastAPI Python backend
│   ├── main.py                       # App entry point, lifespan, CORS, routers
│   ├── config.py                     # Pydantic BaseSettings from .env
│   ├── database.py                   # Async SQLAlchemy engine + session factory
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                 # Migration files (never edit manually)
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                 # All SQLAlchemy async models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py                # All Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                   # /auth/register, /auth/login
│   │   ├── domains.py                # /domains/add, /domains/verify
│   │   ├── scan.py                   # /scan/start, /scan/{id}/stream, /scan/{id}/result
│   │   ├── findings.py               # /findings/{scan_id}, PATCH /findings/{id}
│   │   └── reports.py                # /reports/{scan_id}/pdf
│   ├── services/                     # Business logic layer (routers call services)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── domain_service.py
│   │   ├── scan_service.py
│   │   └── finding_service.py
│   ├── osint/
│   │   ├── __init__.py
│   │   ├── pipeline.py               # subdomain_discovery, dns_records, port_scan, ssl_check
│   │   └── hibp.py                   # HaveIBeenPwned integration
│   ├── rule_engine/
│   │   ├── __init__.py
│   │   └── engine.py                 # RuleEngine class with 11 IF-THEN rules
│   ├── scoring/
│   │   ├── __init__.py
│   │   └── scorer.py                 # overall_score() function
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── scan_worker.py            # run_full_scan() background orchestrator
│   │   ├── scheduler.py              # APScheduler weekly scans
│   │   ├── delta_engine.py           # compare_scans(), auto_verify_findings()
│   │   ├── email_alerts.py           # SendGrid email notifications
│   │   └── verification_worker.py    # verify_single_finding()
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py          # WeasyPrint PDF generation
│   │   └── templates/
│   │       └── report.html           # Jinja2 HTML report template
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py            # JWT create + verify
│   ├── demo/
│   │   ├── __init__.py
│   │   └── demo_data.py              # DEMO_SCAN constant for demo_college.edu
│   └── utils/
│       ├── __init__.py
│       └── graph_builder.py          # build_graph_json() unified output
│
├── nodesec-frontend/                 # React Vite frontend
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   ├── .env.example                  # VITE_API_URL=http://localhost:8000
│   └── src/
│       ├── main.jsx                  # React root, QueryClientProvider
│       ├── App.jsx                   # Router setup, auth guard
│       ├── index.css                 # CSS variables + Tailwind base
│       ├── api/
│       │   ├── axiosInstance.js      # Axios with JWT interceptor
│       │   ├── auth.js
│       │   ├── domains.js
│       │   ├── scan.js
│       │   ├── findings.js
│       │   └── history.js
│       ├── store/
│       │   └── authStore.js          # Zustand auth store
│       ├── hooks/
│       │   ├── useSSE.js             # Custom SSE hook (fetch + ReadableStream)
│       │   ├── useScan.js            # TanStack Query scan hooks
│       │   └── useAuth.js            # Login/logout/register logic
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Navbar.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   └── PageWrapper.jsx
│       │   ├── graph/
│       │   │   ├── AttackGraph.jsx
│       │   │   ├── CustomNodes.jsx
│       │   │   ├── CustomEdges.jsx
│       │   │   ├── GraphControls.jsx
│       │   │   └── AttackPathHighlight.jsx
│       │   ├── scan/
│       │   │   ├── DomainInput.jsx
│       │   │   ├── ScanProgress.jsx
│       │   │   └── ScanStatus.jsx
│       │   ├── risk/
│       │   │   ├── RiskPanel.jsx
│       │   │   ├── ChainCard.jsx
│       │   │   ├── RiskScore.jsx
│       │   │   └── SeverityBadge.jsx
│       │   ├── fixes/
│       │   │   ├── FixPanel.jsx
│       │   │   └── FixCard.jsx
│       │   ├── findings/
│       │   │   ├── FindingsTable.jsx
│       │   │   └── FindingRow.jsx
│       │   ├── timeline/
│       │   │   └── PostureTimeline.jsx
│       │   └── ui/
│       │       ├── Card.jsx
│       │       ├── Button.jsx
│       │       ├── Badge.jsx
│       │       ├── Spinner.jsx
│       │       ├── Modal.jsx
│       │       └── EmptyState.jsx
│       └── pages/
│           ├── LoginPage.jsx
│           ├── RegisterPage.jsx
│           ├── DashboardPage.jsx
│           ├── ScanPage.jsx
│           ├── ResultPage.jsx
│           ├── HistoryPage.jsx
│           ├── FindingsPage.jsx
│           └── NotFoundPage.jsx
│
├── docker-compose.yml                # Full stack orchestration
├── docker-compose.prod.yml           # Production overrides
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Lint + test on every PR
│       └── deploy.yml                # Deploy on merge to main
└── CLAUDE.md                         # This file
```

---

## 3. Frontend Standards

### 3.1 Component Architecture

**Rule:** Every component has exactly one responsibility. If a component does two things, split it.

```
Pattern: Atomic Design
  ui/          → atoms (Button, Badge, Spinner — no business logic)
  components/  → molecules (ChainCard, FixCard — composed from atoms)
  pages/       → organisms (full pages, compose molecules)
```

**Component file structure:**
```jsx
// 1. Imports (external libraries first, then internal)
// 2. TypeScript/PropTypes interface (if applicable)
// 3. Component function
// 4. Sub-components (if small and tightly coupled)
// 5. Default export

// Example: ChainCard.jsx
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import SeverityBadge from '../ui/Badge';

export default function ChainCard({ chain, onViewPath, onSeeFixes }) {
  // implementation
}
```

**Rules:**
- No component file exceeds 200 lines — extract sub-components if it does
- No inline styles — use Tailwind classes or CSS variables only
- No hardcoded colors — all colors reference CSS variables
- No `useEffect` for data fetching — use TanStack Query hooks only

### 3.2 State Management

```
Local UI state     → React useState / useReducer
Server state       → TanStack Query (@tanstack/react-query v5)
Global auth state  → Zustand (authStore.js)
Graph state        → React Flow internal state via useNodesState / useEdgesState
```

**TanStack Query conventions:**
```js
// Always define query keys as constants
export const QUERY_KEYS = {
  scan: (id) => ['scan', id],
  scanChains: (id) => ['scan', id, 'chains'],
  findings: (scanId) => ['findings', scanId],
  history: (domainId) => ['history', domainId],
};

// Always separate query hooks into hooks/ folder
// useScan.js
export function useScanResult(scanId) {
  return useQuery({
    queryKey: QUERY_KEYS.scan(scanId),
    queryFn: () => getScanResult(scanId),
    enabled: !!scanId,
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
}
```

**Zustand auth store rules:**
- Token persisted to localStorage
- Always call `clearAuth()` on 401 response in Axios interceptor
- Never store sensitive data beyond JWT token and basic user object

### 3.3 API Handling

```js
// axiosInstance.js — the only place Axios is configured
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
});

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — handle 401
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**Rules:**
- All API functions live in `src/api/` — never call axios directly from a component
- All API errors shown via `react-hot-toast` — never `console.error` in production
- SSE connections use `fetch` + `ReadableStream` (not `EventSource`) because EventSource does not support Authorization headers

### 3.4 Design System

**CSS Variables (index.css):**
```css
:root {
  --bg-primary:   #0D1117;
  --bg-secondary: #161B22;
  --bg-tertiary:  #1C2128;
  --accent-blue:  #1F6FEB;
  --accent-cyan:  #58A6FF;
  --red-critical: #FF4444;
  --amber-high:   #F0A500;
  --green-safe:   #3FB950;
  --text-primary: #E6EDF3;
  --text-muted:   #8B949E;
  --border:       #30363D;
  --radius-card:  8px;
  --radius-input: 4px;
}
```

**Typography:**
- Font: Inter (Google Fonts, preloaded)
- Headings: font-weight 600-700
- Body: font-weight 400, line-height 1.6
- Code/commands: `Courier New` or `monospace`, inside dark `--bg-tertiary` blocks

**Severity color mapping (used everywhere):**
```js
export const SEVERITY_COLORS = {
  critical: 'var(--red-critical)',
  high:     'var(--amber-high)',
  medium:   '#58A6FF',
  low:      'var(--green-safe)',
};
```

### 3.5 React Flow Graph Standards

**Node types registration (AttackGraph.jsx):**
```js
const nodeTypes = {
  domain:    DomainNode,
  subdomain: SubdomainNode,
  port:      PortNode,
  breach:    BreachNode,
  ssl_issue: SslNode,
};
```

**Node visual rules:**
```
domain:    Navy border (#1F6FEB 2px), Globe icon, always center of graph
subdomain: Default border, Server icon
port:      Amber border, Wifi icon
breach:    Red border 2px + pulsing glow animation, AlertTriangle icon
ssl_issue: Amber border, Lock icon
```

**Graph interaction rules:**
- Click ChainCard → highlight chain nodes (red glow) + fade all other nodes to 0.2 opacity
- Click canvas → clear all highlights
- Click node → open NodeDetailDrawer (Framer Motion slide from right)
- Escape key → close drawer OR exit focus mode
- Severity filter buttons → fade non-matching nodes to 0.15 opacity (do not remove)
- Before/After toggle → animate fade-out of critical/high nodes (opacity 1→0, 0.5s)

### 3.6 Animation Rules

**All animations use Framer Motion. Rules:**
```js
// Page transitions — every page wrapped in:
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>

// Node entry — staggered:
<motion.div
  initial={{ scale: 0, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  transition={{ duration: 0.4, delay: index * 0.05 }}
>

// Drawer slide-in:
<motion.div
  initial={{ x: '100%' }}
  animate={{ x: 0 }}
  exit={{ x: '100%' }}
  transition={{ type: 'spring', damping: 25 }}
>

// Score count-up: use Framer Motion useAnimate or a counter hook
// Risk score circle: SVG stroke-dasharray animated via Framer Motion
```

**Rules:**
- Never animate layout shifts (no animating width/height — use opacity/transform only)
- Duration cap: no animation exceeds 600ms
- Reduced motion: respect `prefers-reduced-motion` media query

### 3.7 Responsive Design

```
Breakpoints (Tailwind):
  sm:  640px   → mobile landscape
  md:  768px   → tablet
  lg:  1024px  → desktop (primary design target)
  xl:  1280px  → wide desktop

Mobile behavior:
  - Sidebar collapses to bottom navigation on mobile
  - Graph is horizontally scrollable on mobile
  - Risk panel and Fix panel stack vertically below graph
  - All touch targets minimum 44×44px
```

### 3.8 Accessibility

- All interactive elements have `aria-label` or visible text
- Keyboard navigation: Tab order follows visual layout
- Color is never the only indicator of severity — always pair with icon + text
- Focus rings: visible on all interactive elements (`focus:ring-2 focus:ring-blue-500`)
- Screen reader: severity badges have `role="status"` and `aria-live` where dynamic

---

## 4. Backend Standards

### 4.1 Architecture Pattern

```
Router → Service → Repository (DB operations)

routers/scan.py     → thin: parse request, call service, return response
services/scan_service.py → business logic, orchestration
models/models.py    → SQLAlchemy models only (no business logic)
```

**Rules:**
- Routers never touch the database directly — always via services
- Services never import from routers
- Models never contain business logic — only schema definitions and relationships

### 4.2 Router Standards

```python
# Every router file follows this pattern:
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.jwt_handler import get_current_user
from schemas.schemas import ScanStartRequest, ScanResultResponse
from services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["scan"])

@router.post("/start", response_model=ScanStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    request: ScanStartRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a new scan for a verified domain.
    If domain_name is demo_college.edu, returns pre-loaded demo data.
    """
    return await ScanService.start_scan(request, current_user.id, db)
```

**Rules:**
- Every route has a docstring explaining what it does
- Every route has `response_model` specified
- Every route has explicit `status_code`
- Protected routes always have `Depends(get_current_user)`
- No business logic in routers — only request parsing and service delegation

### 4.3 Service Layer

```python
# services/scan_service.py
class ScanService:

    @staticmethod
    async def start_scan(request: ScanStartRequest, user_id: UUID, db: AsyncSession) -> ScanStartResponse:
        # 1. Validate domain belongs to user
        domain = await DomainService.get_user_domain(request.domain_id, user_id, db)
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")

        # 2. Create scan record
        scan = await ScanRepository.create_scan(domain.id, request.is_demo, db)

        # 3. Launch background task
        asyncio.create_task(run_full_scan(scan.id, domain.domain_name, db))

        return ScanStartResponse(scan_id=scan.id, status="pending")
```

### 4.4 Error Handling

**Standard HTTP error responses:**
```python
# Always raise HTTPException with detail string — never return error dicts
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Scan not found or does not belong to this user"
)

raise HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail="Domain not verified. Please confirm domain ownership first."
)
```

**Global exception handler in main.py:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."}
    )
```

**Rules:**
- Never expose stack traces in production responses
- Always log the full exception server-side
- OSINT pipeline functions must never raise — return empty results on failure
- The scan worker catches all exceptions and marks scan as "failed"

### 4.5 Logging

```python
# config/logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("nodesec")
```

**Logging rules:**
- `INFO`: scan started, scan completed, user registered, domain added
- `WARNING`: OSINT source failed, rate limit hit, scan took >60s
- `ERROR`: DB write failed, background task crashed, email send failed
- Never log passwords, tokens, or raw user data
- In production: ship logs to structured logging (JSON format for Railway)

### 4.6 API Versioning

All routes are prefixed `/api/v1/` in production:
```python
# main.py
app.include_router(auth_router,     prefix="/api/v1")
app.include_router(domain_router,   prefix="/api/v1")
app.include_router(scan_router,     prefix="/api/v1")
app.include_router(finding_router,  prefix="/api/v1")
app.include_router(report_router,   prefix="/api/v1")
```

Frontend Axios baseURL: `VITE_API_URL/api/v1`

### 4.7 Validation Strategy

**All input validated via Pydantic schemas:**
```python
# schemas/schemas.py
from pydantic import BaseModel, EmailStr, field_validator
import re

class DomainAddRequest(BaseModel):
    domain_name: str

    @field_validator('domain_name')
    @classmethod
    def validate_domain(cls, v):
        pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid domain name format')
        return v.lower().strip()

class ScanStartRequest(BaseModel):
    domain_id: UUID
    is_demo: bool = False
```

**Rules:**
- Every request body has a Pydantic schema — no `dict` parameters in routes
- Email fields use `EmailStr` from pydantic
- Domain names validated with regex before any DB or OSINT operation
- UUIDs validated as `UUID` type — never raw strings

---

## 5. Middleware Configuration

### 5.1 CORS

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Rules:**
- Development: allow `http://localhost:5173`
- Production: allow only the deployed frontend URL (set via env var)
- Never use `allow_origins=["*"]` in production
- `allow_credentials=True` required for SSE with Authorization header

### 5.2 Auth Middleware (JWT)

```python
# auth/jwt_handler.py
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserRepository.get_by_id(UUID(user_id), db)
    if user is None:
        raise credentials_exception
    return user
```

### 5.3 Rate Limiting

```python
# Install: slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Apply per route:
@router.post("/scan/start")
@limiter.limit("5/minute")         # Max 5 scans per minute per IP
async def start_scan(request: Request, ...):
    ...

@router.post("/auth/login")
@limiter.limit("10/minute")        # Max 10 login attempts per minute
async def login(request: Request, ...):
    ...
```

### 5.4 Request Logging Middleware

```python
# middleware/request_logger.py
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} ({duration}ms)"
        )
        return response
```

### 5.5 SSE Headers Middleware

SSE endpoints require specific headers:
```python
# In the SSE route:
return StreamingResponse(
    generate_scan_events(scan_id, db),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",       # Critical for Nginx proxying
        "Connection": "keep-alive",
    }
)
```

---

## 6. Database Standards

### 6.1 Schema Conventions

```python
# All models follow this base pattern:
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base

class BaseModel(Base):
    __abstract__ = True

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Naming conventions:**
```
Tables:         snake_case plural     (users, domains, scans, nodes, edges, chains)
Columns:        snake_case            (user_id, domain_name, overall_score)
Foreign keys:   {table_singular}_id  (user_id, domain_id, scan_id)
Indexes:        ix_{table}_{column}  (ix_scans_domain_id)
Enums:          snake_case values     (status: pending, running, completed, failed)
```

### 6.2 Full Table Definitions

```python
# models/models.py — all models

class User(BaseModel):
    __tablename__ = "users"
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    org_name      = Column(String, nullable=False)

class Domain(BaseModel):
    __tablename__ = "domains"
    user_id       = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain_name   = Column(String, nullable=False)
    verified      = Column(Boolean, default=False)
    demo_mode     = Column(Boolean, default=False)

class Scan(BaseModel):
    __tablename__ = "scans"
    domain_id     = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    started_at    = Column(DateTime, default=datetime.utcnow)
    completed_at  = Column(DateTime, nullable=True)
    overall_score = Column(Integer, nullable=True)
    status        = Column(String, default="pending")   # pending|running|completed|failed
    is_demo       = Column(Boolean, default=False)

class Node(BaseModel):
    __tablename__ = "nodes"
    scan_id       = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    node_type     = Column(String, nullable=False)       # domain|subdomain|port|breach|ssl_issue
    label         = Column(String, nullable=False)
    ip            = Column(String, nullable=True)
    port          = Column(Integer, nullable=True)
    severity      = Column(String, default="low")        # low|medium|high|critical
    raw_data      = Column(JSONB, default={})

class Edge(BaseModel):
    __tablename__ = "edges"
    scan_id            = Column(UUID(as_uuid=True), ForeignKey("scans.id"))
    source_node_id     = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    target_node_id     = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    relationship_type  = Column(String, nullable=False)  # has_subdomain|has_port|has_breach|has_ssl_issue

class Chain(BaseModel):
    __tablename__ = "chains"
    scan_id       = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    rule_id       = Column(String, nullable=False)        # RULE_01 through RULE_11
    severity      = Column(String, nullable=False)
    title         = Column(String, nullable=False)
    explanation   = Column(String, nullable=False)
    node_ids      = Column(JSONB, default=[])

class Fix(BaseModel):
    __tablename__ = "fixes"
    chain_id      = Column(UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False)
    step_number   = Column(Integer, nullable=False)
    command       = Column(String, nullable=False)
    description   = Column(String, nullable=False)

class Finding(BaseModel):
    __tablename__ = "findings"
    scan_id       = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    chain_id      = Column(UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False)
    status        = Column(String, default="open")        # open|in_progress|resolved|verified
    assigned_to   = Column(String, nullable=True)
    due_date      = Column(DateTime, nullable=True)
    verified_at   = Column(DateTime, nullable=True)
```

### 6.3 Indexing Strategy

```sql
-- Applied via Alembic migrations:

-- Most common query: get all scans for a domain
CREATE INDEX ix_scans_domain_id ON scans (domain_id);

-- Get all nodes for a scan (used in every graph build)
CREATE INDEX ix_nodes_scan_id ON nodes (scan_id);

-- Get all chains for a scan
CREATE INDEX ix_chains_scan_id ON chains (scan_id);

-- Get all findings by status (used in FindingsPage filter)
CREATE INDEX ix_findings_status ON findings (status);

-- User lookup by email (login)
CREATE UNIQUE INDEX ix_users_email ON users (email);

-- Domain lookup by user
CREATE INDEX ix_domains_user_id ON domains (user_id);
```

### 6.4 Migration Workflow

```bash
# Create a new migration after changing models.py:
alembic revision --autogenerate -m "add_ssl_check_fields_to_nodes"

# Apply migrations:
alembic upgrade head

# Rollback one step:
alembic downgrade -1

# Never edit migration files after they are committed
# Never apply migrations manually in production — use CI/CD pipeline
```

**Rules:**
- One migration per logical change — never batch multiple schema changes
- Migration files are committed to git and never edited after commit
- Production migrations run automatically in the CI/CD deploy step
- Always test `alembic downgrade -1` before pushing a migration

### 6.5 Async Session Pattern

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## 7. Security Standards

### 7.1 JWT Security

```python
# config.py
SECRET_KEY = os.getenv("SECRET_KEY")           # Min 32 chars, random
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24          # 24 hours

# jwt_handler.py
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Rules:**
- JWT payload contains only `sub` (user_id as string), `exp`, `iat`
- Never store sensitive data in JWT payload
- Token expiry: 24 hours (configurable via env)
- No refresh tokens in v1 — user re-authenticates after expiry
- `SECRET_KEY` must be minimum 32 random characters — never a dictionary word

### 7.2 Password Hashing

```python
# auth/jwt_handler.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

**Rules:**
- bcrypt with default cost factor (12)
- Minimum password length: 8 characters (validated in Pydantic schema)
- Never log passwords — not even hashed
- Never compare passwords with `==` — always use `verify_password()`

### 7.3 SQL Injection Prevention

```python
# Always use SQLAlchemy ORM or parameterized queries
# CORRECT:
result = await db.execute(select(User).where(User.email == email))

# NEVER DO:
query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL injection
```

**Rules:**
- Zero raw SQL strings in the entire codebase — use SQLAlchemy ORM exclusively
- JSONB fields use SQLAlchemy JSONB column type — never string interpolation
- All user input passes through Pydantic validation before touching the DB

### 7.4 OSINT Legal Safety

```python
# osint/pipeline.py — every function must include this check:
async def subdomain_discovery(domain: str) -> list[str]:
    """
    Passive subdomain discovery via certificate transparency logs.
    Only reads publicly available data from crt.sh.
    No active probing. No requests sent to the target domain.
    """
    ...
```

**Rules:**
- All OSINT is passive — no requests to the target domain itself
- Domain verification checkbox required before any scan
- Demo mode is the only mode that runs without verification
- Log every scan with domain, user_id, and timestamp for audit trail

### 7.5 Environment Variable Rules

```bash
# .env.example — all required variables:
DATABASE_URL=postgresql+asyncpg://nodesec:password@localhost:5432/nodesec
SECRET_KEY=generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:5173
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
FRONTEND_URL=http://localhost:5173
HIBP_API_KEY=optional-hibp-key
SHODAN_API_KEY=optional-shodan-key
```

**Rules:**
- `.env` is in `.gitignore` — never committed
- `.env.example` is committed with placeholder values only
- Production secrets stored in Railway environment variables (never in code)
- `config.py` uses Pydantic `BaseSettings` — fails fast if required vars missing

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    allowed_origins: str = "http://localhost:5173"
    sendgrid_api_key: str = ""
    frontend_url: str = "http://localhost:5173"
    hibp_api_key: str = ""
    shodan_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
```

### 7.6 XSS Prevention

- Frontend: React's JSX escapes all content by default — never use `dangerouslySetInnerHTML`
- The only exception: the PDF report template (Jinja2) — escape all user-provided domain names with `{{ domain | e }}`
- Content-Security-Policy header: set in production nginx config

---

## 8. DevOps & Deployment

### 8.1 Docker Setup

**docker-compose.yml (development):**
```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: nodesec
      POSTGRES_PASSWORD: password
      POSTGRES_DB: nodesec
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nodesec"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./nodesec-backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://nodesec:password@db:5432/nodesec
    env_file: ./nodesec-backend/.env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./nodesec-backend:/app

  frontend:
    build: ./nodesec-frontend
    command: npm run dev -- --host
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./nodesec-frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

### 8.2 CI/CD Pipeline

**.github/workflows/ci.yml:**
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
          POSTGRES_DB: nodesec_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: "3.11" }
      - run: cd nodesec-backend && pip install -r requirements.txt
      - run: cd nodesec-backend && pytest tests/ -v --cov=. --cov-report=xml
      - run: cd nodesec-backend && ruff check .

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd nodesec-frontend && npm ci
      - run: cd nodesec-frontend && npm run lint
      - run: cd nodesec-frontend && npm run test
      - run: cd nodesec-frontend && npm run build
```

**.github/workflows/deploy.yml:**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: railway up --service nodesec-backend
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd nodesec-frontend && npm ci && npm run build
      - name: Deploy to Vercel
        run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

### 8.3 Environments

```
Development:
  Backend:  http://localhost:8000
  Frontend: http://localhost:5173
  DB:       localhost:5432 (Docker)

Staging (optional):
  Backend:  https://api-staging.nodesec.app
  Frontend: https://staging.nodesec.app
  DB:       Railway PostgreSQL (staging instance)

Production:
  Backend:  https://api.nodesec.app   (Railway)
  Frontend: https://nodesec.app       (Vercel)
  DB:       Railway PostgreSQL (production instance)
```

### 8.4 Monitoring & Logging

```
Production logging:
  - Backend: Railway built-in logs + structured JSON format
  - Error tracking: Sentry (add sentry-sdk to requirements.txt)
  - Uptime monitoring: UptimeRobot (free tier, check /health every 5 minutes)

Health check endpoint:
  GET /health → {"status": "ok", "db": "connected", "version": "1.0.0"}

Sentry integration:
  import sentry_sdk
  sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)
```

### 8.5 Backup Strategy

```bash
# Automated daily PostgreSQL backup (Railway cron or GitHub Actions):
pg_dump $DATABASE_URL | gzip > backup_$(date +%Y%m%d).sql.gz

# Retention: 7 daily backups, 4 weekly backups
# Storage: upload to S3 or Railway volumes
# Test restores monthly
```

---

## 9. Testing Strategy

### 9.1 Backend Testing (pytest)

**File structure:**
```
nodesec-backend/tests/
├── conftest.py              # Shared fixtures (test DB, test client, mock user)
├── unit/
│   ├── test_rule_engine.py  # Test all 11 chain rules
│   ├── test_scorer.py       # Test scoring function
│   └── test_delta_engine.py # Test compare_scans()
├── integration/
│   ├── test_auth.py         # Register + login + protected route
│   ├── test_scan.py         # Full scan flow (mock OSINT)
│   └── test_findings.py     # CRUD findings
└── osint/
    └── test_pipeline.py     # Test each OSINT function with mock responses
```

**Rule engine tests (must be exhaustive):**
```python
# tests/unit/test_rule_engine.py
import pytest
from rule_engine.engine import RuleEngine

class TestRuleEngine:
    def test_rule_01_triggers_when_ssh_open_and_breach(self):
        scan_data = {
            "open_ports": [22],
            "breach_found": True,
            "subdomains": ["portal.test.com"],
            "ssl_status": {"is_valid": True}
        }
        engine = RuleEngine()
        chains = engine.evaluate(scan_data)
        rule_ids = [c["rule_id"] for c in chains]
        assert "RULE_01" in rule_ids

    def test_rule_01_does_not_trigger_without_breach(self):
        scan_data = {"open_ports": [22], "breach_found": False, "subdomains": [], "ssl_status": {}}
        chains = RuleEngine().evaluate(scan_data)
        assert not any(c["rule_id"] == "RULE_01" for c in chains)

    # Test all 11 rules: positive case + negative case each
```

**Mock OSINT for integration tests:**
```python
# conftest.py
@pytest.fixture
def mock_osint(monkeypatch):
    async def mock_subdomain_discovery(domain):
        return ["portal.test.com", "admin.test.com"]

    async def mock_port_scan(host, ports):
        return [22, 80]

    monkeypatch.setattr("osint.pipeline.subdomain_discovery", mock_subdomain_discovery)
    monkeypatch.setattr("osint.pipeline.port_scan", mock_port_scan)
```

### 9.2 Frontend Testing (Vitest + React Testing Library)

```
nodesec-frontend/src/tests/
├── components/
│   ├── ChainCard.test.jsx      # Renders correctly, click triggers callback
│   ├── RiskScore.test.jsx      # Score animation, color thresholds
│   └── SeverityBadge.test.jsx  # Color mapping per severity
├── hooks/
│   ├── useSSE.test.js          # SSE connection, event parsing, cleanup
│   └── useAuth.test.js         # Login/logout state changes
└── pages/
    ├── LoginPage.test.jsx      # Form validation, submit, redirect
    └── DashboardPage.test.jsx  # Domain list renders, new scan button
```

**Component test pattern:**
```jsx
// ChainCard.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import ChainCard from '../components/risk/ChainCard';

const mockChain = {
  id: 'uuid-1',
  rule_id: 'RULE_01',
  severity: 'critical',
  title: 'Remote Credential Attack',
  explanation: 'SSH is open and credentials are leaked.',
  node_ids: ['node-1', 'node-2'],
};

test('renders chain title and severity badge', () => {
  render(<ChainCard chain={mockChain} onViewPath={() => {}} onSeeFixes={() => {}} />);
  expect(screen.getByText('Remote Credential Attack')).toBeInTheDocument();
  expect(screen.getByText('critical')).toBeInTheDocument();
});

test('calls onViewPath when View Attack Path clicked', () => {
  const onViewPath = vi.fn();
  render(<ChainCard chain={mockChain} onViewPath={onViewPath} onSeeFixes={() => {}} />);
  fireEvent.click(screen.getByText('View Attack Path'));
  expect(onViewPath).toHaveBeenCalledWith(mockChain.node_ids);
});
```

### 9.3 Coverage Requirements

```
Backend:
  Rule engine:     100% coverage (every rule has positive + negative test)
  Services:         80% coverage
  Routers:          70% coverage (via integration tests)
  OSINT functions:  60% coverage (mocked external calls)

Frontend:
  UI components:    70% coverage
  Custom hooks:     80% coverage
  API functions:    60% coverage (mocked axios)
```

### 9.4 Running Tests

```bash
# Backend
cd nodesec-backend
pytest tests/ -v                          # All tests
pytest tests/unit/ -v                     # Unit tests only
pytest tests/ --cov=. --cov-report=html   # With coverage report

# Frontend
cd nodesec-frontend
npm run test                              # All tests (Vitest)
npm run test:coverage                     # With coverage
npm run test:ui                           # Vitest UI (browser)
```

---

## 10. Developer Roles & Skills

### Frontend Developer

**Responsibilities:**
- Build and maintain all React components in `src/components/` and `src/pages/`
- Implement React Flow graph with all interaction modes (highlight, filter, focus, before/after)
- Build SSE streaming integration via `useSSE.js`
- Implement all Framer Motion animations
- Ensure responsive design across all breakpoints
- Write component and hook tests (Vitest + RTL)

**Required Skills:**
- React 18 (hooks, context, concurrent features)
- React Flow (@xyflow/react) — custom nodes, edges, layout
- TanStack Query v5
- Framer Motion
- Tailwind CSS
- Zustand
- Vitest + React Testing Library

**Coding Expectations:**
- No component exceeds 200 lines
- Every component has a corresponding test file
- All colors reference CSS variables — zero hardcoded hex values
- All data fetching via TanStack Query — zero `useEffect` data fetching

---

### Backend Developer

**Responsibilities:**
- Build and maintain all FastAPI routes, services, and models
- Implement and test the 11-rule chain engine
- Build and maintain the async OSINT pipeline
- Manage PostgreSQL schema via Alembic migrations
- Implement SSE streaming endpoint
- Write unit and integration tests (pytest)

**Required Skills:**
- Python 3.11+ async/await
- FastAPI (routing, Depends, middleware)
- SQLAlchemy async ORM + asyncpg
- Alembic migrations
- Pydantic v2 schemas
- pytest + pytest-asyncio
- dnspython, httpx, asyncio sockets

**Coding Expectations:**
- Zero raw SQL — SQLAlchemy ORM only
- Every route has response_model and status_code
- OSINT functions never raise — return empty on failure
- All 11 chain rules have passing positive AND negative tests

---

### Full Stack Developer

**Responsibilities:**
- End-to-end features that span both frontend and backend
- SSE pipeline: from background worker to React Flow node animation
- Demo mode: backend demo_data.py + frontend demo UX flow
- PDF export: backend WeasyPrint + frontend @react-pdf/renderer
- API contract maintenance: schemas stay in sync with frontend types

**Required Skills:**
- All skills from Frontend and Backend Developer roles
- Understanding of SSE protocol and streaming responses
- WeasyPrint + Jinja2 templating
- Docker + docker-compose

---

### DevOps Engineer

**Responsibilities:**
- Maintain Docker and docker-compose configurations
- Manage CI/CD pipelines (GitHub Actions)
- Configure Railway (backend) and Vercel (frontend) deployments
- Set up monitoring (Sentry, UptimeRobot)
- Manage environment variables and secrets
- Database backup automation

**Required Skills:**
- Docker + docker-compose
- GitHub Actions
- Railway platform
- Vercel platform
- PostgreSQL administration
- Nginx configuration
- Linux server administration

---

### QA Engineer

**Responsibilities:**
- Write and maintain integration and E2E tests
- Test all 11 chain rules with edge cases
- Validate SSE streaming under slow network conditions
- Test demo mode end-to-end
- Test PDF export output quality
- Regression testing before every release

**Required Skills:**
- pytest + pytest-asyncio
- Vitest + React Testing Library
- Playwright or Cypress (E2E)
- API testing (httpx test client)
- Understanding of OSINT concepts to design realistic test data

---

### Security Engineer

**Responsibilities:**
- Audit all OSINT operations for legal compliance (passive only)
- Review JWT implementation and token security
- Audit domain verification flow
- Review rate limiting configuration
- Dependency vulnerability scanning (pip-audit, npm audit)
- Review environment variable handling

**Required Skills:**
- Application security fundamentals
- OWASP Top 10
- JWT security best practices
- Python security tooling (bandit, pip-audit)
- Understanding of OSINT legal boundaries

---

### Database Engineer

**Responsibilities:**
- Design and maintain PostgreSQL schema
- Write and review all Alembic migrations
- Define and implement indexing strategy
- Monitor query performance (EXPLAIN ANALYZE)
- Manage backup and restore procedures
- Optimize slow queries

**Required Skills:**
- PostgreSQL 15+
- SQLAlchemy async ORM
- Alembic migration workflow
- Query optimization (EXPLAIN, indexes, JSONB operators)
- asyncpg driver

---

## 11. AI Agent Rules (Claude Code)

When Claude Code generates any code for NodeSec, these rules are **non-negotiable**:

### Code Generation Rules

```
1.  MODULAR FIRST
    Every function does exactly one thing.
    If a function has more than 30 lines, consider splitting it.

2.  NO DUPLICATE LOGIC
    Before generating a utility function, check if it already exists.
    Rule engine logic lives ONLY in rule_engine/engine.py.
    Graph building logic lives ONLY in utils/graph_builder.py.

3.  ASYNC ALL THE WAY
    Every DB operation is async. Every OSINT function is async.
    Never call asyncio.run() inside a FastAPI route.

4.  SCHEMA-FIRST
    Every API change starts with updating schemas/schemas.py.
    Frontend API functions are updated to match immediately after.

5.  NO SECURITY SHORTCUTS
    Never hardcode secrets. Never use allow_origins=["*"] in production.
    Never use raw SQL strings. Never skip Pydantic validation.

6.  OSINT SAFETY
    Every OSINT function must: handle exceptions gracefully,
    return empty results on failure (never raise),
    and never send requests to the target domain itself.

7.  DETERMINISTIC RULE ENGINE
    The 11 chain rules are the core innovation.
    Never replace IF-THEN rule logic with an AI/LLM call.
    Every rule must have explicit test coverage.

8.  COMPLETE IMPLEMENTATIONS
    Never generate placeholder comments like "# TODO: implement this"
    or "# add logic here". Every function must be fully implemented.

9.  FOLLOW THE FOLDER STRUCTURE
    New files go in their designated folder.
    Never create files outside the defined structure without discussion.

10. COMMENT STRATEGICALLY
    Comment the WHY, not the WHAT.
    GOOD: # crt.sh returns duplicate entries — deduplicate before saving
    BAD:  # loop through subdomains

11. PRODUCTION-READY ONLY
    No debug print statements. No hardcoded test data (except demo_data.py).
    No development-only shortcuts in production code paths.

12. SEPARATE CONCERNS
    Router logic never touches the database.
    Service logic never builds HTTP responses.
    OSINT functions never save to the database.
    React components never call axios directly.
```

### What Claude Code Should Never Do

```
✗ Import SQLAlchemy models in routers directly
✗ Add business logic to Pydantic schema files
✗ Use synchronous SQLAlchemy in an async context
✗ Call external APIs from within a Pydantic validator
✗ Add inline styles to React components
✗ Use dangerouslySetInnerHTML anywhere
✗ Import axios directly in a React component (use api/ layer)
✗ Add new npm packages without updating package.json and this file
✗ Create new database columns without an Alembic migration
✗ Replace the rule engine with an LLM/AI call
✗ Expose internal error details in HTTP responses
✗ Commit .env files or any secrets
```

---

## 12. Coding Standards

### 12.1 Python (Backend)

```python
# File naming: snake_case
# rule_engine/engine.py ✓     RuleEngine.py ✗

# Class naming: PascalCase
class RuleEngine:             # ✓
class rule_engine:            # ✗

# Function naming: snake_case
async def evaluate_chains():  # ✓
async def EvaluateChains():   # ✗

# Constants: SCREAMING_SNAKE_CASE
DEMO_SCAN = {...}             # ✓
demo_scan = {...}             # ✗

# Type hints: required on all function signatures
async def get_user(user_id: UUID, db: AsyncSession) -> User | None:

# Docstrings: required on all public functions
def overall_score(chains: list, open_ports: list, subdomains: list) -> int:
    """
    Calculate overall risk score from 0 to 100.
    100 = maximum risk (critical chains + many exposed assets).
    0 = completely clean (no chains, no open ports).
    """
```

**Linting and formatting:**
```bash
# Install: ruff (replaces flake8 + isort + black)
ruff check .             # Lint
ruff format .            # Format
ruff check --fix .       # Auto-fix fixable issues

# ruff.toml:
line-length = 100
target-version = "py311"
```

### 12.2 JavaScript/React (Frontend)

```js
// File naming:
// Components:  PascalCase  → ChainCard.jsx ✓
// Hooks:       camelCase   → useSSE.js ✓
// API files:   camelCase   → scan.js ✓
// Utils:       camelCase   → graphBuilder.js ✓

// Component naming: PascalCase
function ChainCard({ chain }) {}    // ✓
function chainCard({ chain }) {}    // ✗

// Hook naming: starts with "use"
function useSSE(scanId) {}          // ✓
function SSEHook(scanId) {}         // ✗

// Constants: SCREAMING_SNAKE_CASE
const SEVERITY_COLORS = {...}       // ✓

// Props: destructure at function signature
function ChainCard({ chain, onViewPath, onSeeFixes }) {   // ✓
function ChainCard(props) { const { chain } = props; }    // ✗
```

**Linting:**
```bash
# ESLint + Prettier
npm run lint          # ESLint check
npm run format        # Prettier format

# .eslintrc.js: extends eslint:recommended, plugin:react/recommended
# .prettierrc: { "semi": true, "singleQuote": true, "tabWidth": 2 }
```

### 12.3 Git Commit Conventions

```
Format: <type>(<scope>): <description>

Types:
  feat      New feature
  fix       Bug fix
  refactor  Code change that neither fixes a bug nor adds a feature
  test      Adding or updating tests
  docs      Documentation only
  chore     Build process, dependencies, config
  perf      Performance improvement

Examples:
  feat(rule-engine): add RULE_11 full kill chain detection
  fix(sse): close SSE connection on component unmount
  refactor(scan-service): extract domain validation to helper
  test(rule-engine): add negative test cases for all 11 rules
  docs(readme): add local development setup instructions
  chore(deps): upgrade react-flow to v12
```

**Branch naming:**
```
feature/rule-engine-rule-11
fix/sse-memory-leak
refactor/scan-service-extraction
```

**PR rules:**
- Every PR requires at least one reviewer
- CI must pass before merge
- No force-pushing to `main`
- Squash merge preferred for feature branches

---

## 13. Performance Optimization

### 13.1 Backend Performance

**Async pipeline concurrency:**
```python
# Run all OSINT sources concurrently — never sequentially
subdomains, dns_data, ssl_status = await asyncio.gather(
    subdomain_discovery(domain),
    dns_records(domain),
    ssl_check(domain),
    return_exceptions=True          # Don't fail all if one fails
)

# Port scan all subdomains concurrently (with semaphore to limit):
semaphore = asyncio.Semaphore(10)   # Max 10 concurrent port scans
async def bounded_port_scan(host):
    async with semaphore:
        return await port_scan(host)

port_results = await asyncio.gather(*[bounded_port_scan(s) for s in subdomains])
```

**Database query optimization:**
```python
# Use selectinload for relationships (avoid N+1)
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Scan)
    .options(selectinload(Scan.nodes), selectinload(Scan.chains))
    .where(Scan.id == scan_id)
)

# Use specific column selection for large result sets
result = await db.execute(
    select(Node.id, Node.label, Node.severity)   # Not select(Node)
    .where(Node.scan_id == scan_id)
)
```

**Connection pooling:**
```python
# database.py — tune for production load
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # Persistent connections
    max_overflow=20,        # Burst capacity
    pool_pre_ping=True,     # Detect stale connections
    pool_recycle=3600,      # Recycle connections after 1 hour
)
```

### 13.2 Frontend Performance

**Code splitting — every page is lazy loaded:**
```jsx
// App.jsx
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ScanPage      = lazy(() => import('./pages/ScanPage'));
const ResultPage    = lazy(() => import('./pages/ResultPage'));

// Wrap routes in Suspense with Spinner fallback
<Suspense fallback={<Spinner />}>
  <Routes>
    <Route path="/dashboard" element={<DashboardPage />} />
    ...
  </Routes>
</Suspense>
```

**React Flow optimization (large graphs):**
```jsx
// AttackGraph.jsx — memoize node and edge arrays
const nodes = useMemo(() => buildNodes(scanData), [scanData]);
const edges = useMemo(() => buildEdges(scanData), [scanData]);

// Use React Flow's built-in virtualization for large graphs
<ReactFlow
  nodes={nodes}
  edges={edges}
  nodesDraggable
  nodesConnectable={false}
  elevateNodesOnSelect={false}   // Performance
/>
```

**TanStack Query caching:**
```js
// Scan results are immutable after completion — cache forever
useQuery({
  queryKey: QUERY_KEYS.scan(scanId),
  queryFn: () => getScanResult(scanId),
  staleTime: Infinity,          // Never refetch completed scans
  gcTime: 30 * 60 * 1000,       // Keep in memory 30 minutes
})
```

**Bundle size rules:**
```bash
# Check bundle size before every release:
npm run build && npx vite-bundle-visualizer

# Targets:
# Initial JS bundle:  < 200KB gzipped
# React Flow chunk:   < 150KB gzipped
# Total page load:    < 500KB gzipped
```

### 13.3 Database Performance

```sql
-- Analyze slow queries in production:
EXPLAIN ANALYZE
SELECT n.* FROM nodes n
WHERE n.scan_id = 'uuid-here'
ORDER BY n.severity;

-- Expected: Index Scan on ix_nodes_scan_id
-- If Seq Scan appears: index is missing or not being used

-- JSONB query optimization (raw_data field):
-- If querying inside JSONB frequently, add GIN index:
CREATE INDEX ix_nodes_raw_data_gin ON nodes USING GIN (raw_data);
```

**Query performance targets:**
```
GET /scan/{id}/result    → < 100ms  (indexed scan_id lookup)
GET /history/{domain_id} → < 200ms  (indexed domain_id lookup)
POST /scan/start         → < 50ms   (creates 1 row, launches background task)
SSE first node event     → < 3s     (crt.sh response time dependent)
```

---

## Quick Reference

### Start Development

```bash
# Clone and start everything:
git clone https://github.com/your-org/nodesec
cd nodesec
cp nodesec-backend/.env.example nodesec-backend/.env
# Edit .env with your values
docker-compose up -d db
cd nodesec-backend && alembic upgrade head && cd ..
docker-compose up
# Backend:  http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

### Test Demo Mode

```bash
# No API keys needed:
# 1. Register at http://localhost:5173/register
# 2. Click "Run Demo Scan" on dashboard
# 3. Watch graph build for demo_college.edu
# 4. Explore chains, fixes, and risk score
```

### Run All Tests

```bash
# Backend:
cd nodesec-backend && pytest tests/ -v

# Frontend:
cd nodesec-frontend && npm run test

# Both via CI locally:
act pull_request          # Requires 'act' (GitHub Actions local runner)
```

---

*NodeSec CLAUDE.md — Last updated: 2025*
*Maintained by the NodeSec engineering team.*
*All contributors must read this document before making any changes to the codebase.*
