# ScamGraph AI — Intelligent Scam Investigation Platform

[![Status](https://img.shields.io/badge/Status-Operational-00F0FF?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115+-009688?style=flat-square)](#)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square)](#)
[![Three.js](https://img.shields.io/badge/Three.js-3D%20Globe-black?style=flat-square)](#)
[![Tests](https://img.shields.io/badge/Pytest-21%2F21%20Passing-emerald?style=flat-square)](#)

**ScamGraph AI** is a premium, cyber-intelligence grade investigation platform engineered to dismantle fraudulent recruitment campaigns, fake internship offers, predatory job rackets, and interconnected digital crime syndicates.

Moving far beyond basic keyword spam checkers, ScamGraph AI analyzes behavioral threat vectors, extracts high-fidelity digital entities (domains, RFC emails, phones, UPI handles), searches historical evidence, visualizes cross-campaign syndicates on an **Interactive 3D Threat Globe**, and provides customized legal & emergency incident playbooks for victims.

---

## Key Highlights & Architectural Features

### 1. Futuristic Cyber Command Interface
- Dark navy/cyber black palette (`#030712`, `#0F172A`) with electric cyan (`#00F0FF`), violet (`#A855F7`), amber (`#F59E0B`), and restrained red accents (`#EF4444`).
- Glassmorphism panels, subtle glow shaders, responsive layouts, and smooth micro-interactions.
- 7 Dedicated Functional Hubs:
  1. **Investigation Dashboard** — Real-time telemetry, threat radar, and KPI metrics.
  2. **Live Network** — Interactive 3D Scam Network Globe and 2D Force Layout.
  3. **New Investigation** — Multi-stage intake pipeline with live progress terminal.
  4. **Investigation History** — Filterable case archives with delete and search capabilities.
  5. **Evidence Explorer** — Forensic indicator quotes and OSINT source provenance.
  6. **Safety & Response** — Personalized victim response advisor with Indian portals.
  7. **Settings** — TinyFish adapter and LLM API key controls.

### 2. Interactive 3D Scam Network Globe & Force Graph
- **Three.js WebGL 3D Globe**: Evidence-based spatial layout. Geocoded entities are pinned to documented coordinates; non-geocoded nodes orbit on a spherical Fibonacci grid without fabricating coordinates.
- **Dynamic Arc Connections**: Correlations between cases (e.g. shared UPI IDs, identical domains, shared phones) project as elevated curved arcs.
- **Topological Shortest Path Finder**: Discovers the shortest evidence-backed chain linking two suspicious entities across different campaigns.
- **Ego-Cluster Expansion**: Isolates connected sub-graphs around an entity.
- **Tactical Controls**: Auto-rotation toggle, zoom, reset view, and node type filters.

### 3. Explainable Scam Analysis Engine
Evaluates submissions across 8 threat vectors:
1. **Upfront Payment Demands**: Registration fees, training charges, refundable uniform/kit deposits.
2. **Artificial Time Urgency**: Pressure to pay within hours, limited slots, FOMO tactics.
3. **Legal Threats & Coercion**: Blacklisting intimidation, contract breach threats.
4. **Credential Harvesting**: Demands for OTPs, netbanking passwords, PINs, or Aadhaar scans with OTP.
5. **Misleading Domains & Disposable Hosting**: Free subdomains (`.web.app`, `.vercel.app`), suspicious TLDs (`.xyz`, `.top`).
6. **Unrealistic Payouts**: Guaranteed selection without interview, 100% joining letters, task-based scams.
7. **Persona Inconsistencies**: Claiming established corporate identities while emailing from free `@gmail.com` addresses.
8. **Off-Platform Redirection**: Forcing applicants into encrypted Telegram bots or private WhatsApp chats.

### 4. TinyFish Web Intelligence Adapter
- Unified adapter service at `backend/app/services/tinyfish_service.py`.
- **SSRF Defense**: Automatically blocks loopback addresses (`127.0.0.1`), local hostnames, private RFC1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), and AWS/GCP cloud metadata (`169.254.169.254`).
- **Graceful Fallback**: When TinyFish is unconfigured or offline, the platform seamlessly continues operating using local heuristics and database correlation, with clear audit messages.

### 5. Safety & Response Assistant (Indian Cybercrime Resources)
- Personalized triage questionnaire based on victim compromise state (paid vs unpaid, OTP leaked, ID leaked, link clicked).
- Verified official helplines and reporting resources:
  - **National Cyber Financial Fraud Helpline**: **1930** (with Golden Hour triage)
  - **National Cyber Crime Reporting Portal**: [cybercrime.gov.in](https://cybercrime.gov.in)
  - **Chakshu / Sanchar Saathi Portal**: [sancharsaathi.gov.in/sfc/](https://sancharsaathi.gov.in/sfc/)
  - **RBI Complaint Management System**: [cms.rbi.org.in](https://cms.rbi.org.in)
  - **UIDAI Biometric Lock**: [myaadhaar.uidai.gov.in](https://myaadhaar.uidai.gov.in)
- Clear legal disclaimer emphasizing that recovery cannot be guaranteed.

---

## Project Structure

```
ScamGraph-AI-master/
├── backend/
│   ├── app/
│   │   ├── config.py                 # Pydantic BaseSettings, SSRF policies
│   │   ├── main.py                   # FastAPI application & static server
│   │   ├── database/
│   │   │   ├── session.py            # SQLite WAL mode & sessionmaker
│   │   │   └── seed_data.py          # Preloaded realistic cross-case syndicates
│   │   ├── models/
│   │   │   └── investigation.py      # SQLAlchemy declarative models
│   │   ├── schemas/
│   │   │   ├── investigation.py      # Pydantic v2 schemas
│   │   │   ├── graph.py              # 3D Node & Edge schemas
│   │   │   └── safety.py             # Safety & configuration schemas
│   │   ├── services/
│   │   │   ├── normalizer.py         # Digital indicator normalizer & SSRF check
│   │   │   ├── scam_engine.py        # Threat vector rule engine
│   │   │   ├── relationship_engine.py# NetworkX cross-case correlation
│   │   │   ├── tinyfish_service.py   # TinyFish API adapter
│   │   │   └── safety_service.py     # Incident response guidance & portals
│   │   └── routers/
│   │       ├── dashboard.py          # Analytics & KPI endpoints
│   │       ├── investigations.py     # 10-stage submission & case CRUD
│   │       ├── graph.py              # 3D Globe, shortest path, entity details
│   │       ├── evidence.py           # Forensic quotes & artifacts
│   │       ├── safety.py             # Interactive safety advisor
│   │       └── settings.py           # Safe settings configuration
│   └── tests/
│       ├── test_scamgraph.py         # Normalization, SSRF, rules, & links tests
│       └── test_api_endpoints.py     # FastAPI TestClient endpoint integration tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx            # Cyber command header
│   │   │   ├── Sidebar.tsx           # 7-tab navigation
│   │   │   ├── Globe3D.tsx           # Three.js 3D Scam Network Globe
│   │   │   ├── ForceGraphView.tsx    # 2D/3D Force-directed layout
│   │   │   └── NodeDetailsModal.tsx  # Entity dossier inspector drawer
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # Overview & threat radar
│   │   │   ├── LiveNetwork.tsx       # 3D Globe & shortest path finder
│   │   │   ├── NewInvestigation.tsx  # Intake form & real-time stage terminal
│   │   │   ├── InvestigationHistory.tsx # Case archive & search
│   │   │   ├── EvidenceExplorer.tsx  # Forensic quotes & artifacts
│   │   │   ├── SafetyResponse.tsx    # Victim triage & Indian helplines
│   │   │   └── Settings.tsx          # TinyFish & AI settings
│   │   ├── api/client.ts             # Axios API client
│   │   └── types/index.ts            # TypeScript interfaces
│   ├── dist/                         # Compiled production frontend build
│   └── vite.config.ts                # Vite config with Tailwind & proxy
├── data/
│   └── scamgraph_v2.db               # SQLite database (auto-created)
├── .env.example                      # Configuration template
├── requirements.txt                  # Python production dependencies
├── run.py                            # Unified application runner
├── start.bat                         # One-click Windows startup script
└── README.md                         # This documentation
```

---

## Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ (for frontend development)

### 1. Running the Complete Platform (Single Command)
The frontend is already built and pre-compiled into `frontend/dist`. You can start both backend and frontend together with one command:

```powershell
# Using the pre-configured virtual environment
& .venv\Scripts\python.exe run.py
```

Or double-click `start.bat` on Windows!

The platform will be live at:
- **Interactive Cyber Dashboard & 3D Globe**: [http://localhost:8000](http://localhost:8000)
- **FastAPI Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## Development Mode

If you wish to modify the React frontend with hot-module replacement (HMR):

### 1. Start Backend in Terminal 1:
```powershell
& .venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8000 --reload
```

### 2. Start Frontend in Terminal 2:
```powershell
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser. All API requests are proxied automatically to `http://localhost:8000`.

---

## Running the Automated Test Suite

The test suite covers:
- Digital indicator normalization (domains, RFC emails, phones, UPI handles)
- SSRF prevention and dangerous IP/hostname blocking
- Exact-match relationship detection across investigations
- Unconnected entities isolation (verifying no spurious links are generated)
- Multi-indicator matching
- Scam analysis engine pattern detection
- TinyFish fallback behavior when unconfigured
- Safety & Response assistant scenario generation
- Full REST API integration with FastAPI TestClient

Run the test suite:
```powershell
& .venv\Scripts\python.exe -m pytest backend/tests -v
```

All **21/21 tests pass** reliably.

---

## Pre-Loaded Sample Dataset

The platform initializes automatically with labeled, interconnected sample investigations to demonstrate multi-case syndicate correlation:
1. **Syndicate Alpha (Case SG-2026-001)**: Fake TCS Recruitment demanding Rs 4,999 refundable deposit to UPI `hr.recruit@axisbank` via phone `+919876543210`.
2. **Syndicate Alpha (Case SG-2026-002)**: Fake Infosys Internship scam sharing the **exact same UPI (`hr.recruit@axisbank`)** and **phone (`+919876543210`)**, establishing a cross-campaign syndicate link.
3. **Syndicate Beta (Case SG-2026-003)**: Task-based YouTube video review Ponzi scam hosted on `work-task-earn.xyz` with UPI `taskmaster@ybl`.
4. **Benign Case (Case SG-2026-004)**: Authentic university placement notification with zero red flags, demonstrating isolated, unconnected entity handling.

---

## Security & Privacy Policies
- **SSRF Defense**: Any user-supplied URL undergoes IP and hostname resolution. Prohibited ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`) are immediately blocked.
- **Untrusted Web Content**: External webpages fetched via TinyFish are treated as raw text and sanitized.
- **Secret Management**: API keys for TinyFish or LLMs are kept server-side in environment variables and are never leaked to frontend clients or logs.
