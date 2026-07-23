# AI-Powered Customer Complaint Management System (Pharma)

A complaint intake system for API/FDF pharmaceutical manufacturing. A user pastes/uploads a
complaint (email, PDF, DOCX, TXT, or free text), a LangGraph agent pipeline (running on Groq's
LLMs) extracts the structured complaint details, asks for anything missing, then reasons about
severity/priority/risk/suggested-action using pharmaceutical QMS principles, and auto-fills an
editable complaint form for QA to review and save.

```
frontend/          React + Redux UI (two-panel dashboard)
backend/
  main.py           FastAPI app & all endpoints
  agents/           LangGraph nodes, graph, Groq client, duplicate-check
  prompts/          System prompts for each LLM agent
  database/         SQLAlchemy models + connection
  parsers.py        PDF/DOCX/EML/TXT text extraction
sample_documents/   Example complaints to test with
uploads/            Uploaded files land here at runtime
```

---

## 0. Prerequisites

You'll need:
- **Python 3.10+**
- **Node.js 18+** (for the frontend)
- A **Groq API key** (free) — see Step 1
- **PostgreSQL** — optional at first; see Step 2 (you can start with SQLite, zero setup)

---

## 1. Get a free Groq API key

Groq hosts the LLMs (gemma2-9b-it for fast extraction, llama-3.3-70b-versatile for QMS
reasoning) and has a generous free tier.

1. Go to **https://console.groq.com** and sign up (Google/GitHub login works).
2. In the left sidebar, click **API Keys**.
3. Click **Create API Key**, give it a name (e.g. `pharma-complaint-app`), and copy the key
   immediately — it starts with `gsk_...` and is only shown once.
4. Keep it somewhere safe for now — you'll paste it into `backend/.env` in Step 3.

That's it — no billing details needed for the free tier as of writing, but check the console for
current limits.

---

## 2. Set up the database

You have two options. **Start with SQLite** (zero install) to get the app running today, then
switch to Postgres once you're comfortable.

### Option A — SQLite (recommended to start, zero setup)
Nothing to install. The backend will create a `complaints.db` file automatically the first time
it runs. Skip to Step 3 and leave `DATABASE_URL=sqlite:///./complaints.db` in your `.env`.

### Option B — PostgreSQL (matches the assignment's mandatory stack)

**On Ubuntu/Debian (or WSL):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

**On macOS (with Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Windows:** download the installer from https://www.postgresql.org/download/windows/ and
run it (remember the password you set for the `postgres` superuser).

**Then create the database and a user** (run `psql` as the postgres superuser):
```bash
sudo -u postgres psql
```
Inside the `psql` prompt:
```sql
CREATE DATABASE complaint_db;
CREATE USER complaint_user WITH PASSWORD 'complaint_pass';
GRANT ALL PRIVILEGES ON DATABASE complaint_db TO complaint_user;
\q
```

Then in `backend/.env`, set:
```
DATABASE_URL=postgresql+psycopg2://complaint_user:complaint_pass@localhost:5432/complaint_db
```

You don't need to create tables manually — SQLAlchemy creates them automatically on backend
startup (`Base.metadata.create_all` in `main.py`).

---

## 3. Backend setup

```bash
cd pharma-complaint-system
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r backend/requirements.txt

cp backend/.env.example backend/.env
# now open backend/.env and paste your real GROQ_API_KEY,
# and set DATABASE_URL if you're using Postgres
```

Run the API (from the project root, so the `backend` package resolves correctly):
```bash
uvicorn backend.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** — you should see the interactive FastAPI Swagger docs with
all endpoints (`/chat`, `/upload`, `/complaints`, etc). Try `GET /` first — it should return
`{"status": "ok", ...}`.

---

## 4. Frontend setup

In a **second terminal**:
```bash
cd pharma-complaint-system/frontend
npm install
npm run dev
```

Visit **http://localhost:3000**. The Vite dev server proxies `/api/*` requests to your FastAPI
backend on port 8000 (see `frontend/vite.config.js`), so both servers need to be running.

---

## 5. Try it out

On the right panel ("AI Complaint Intake Assistant"), try one of these:

**A. Paste text directly** into the chat box and hit send:
> Apollo Pharmacy reported discolored capsules in Amoxicillin Capsules 500mg. Batch number
> AMX240602. Manufacturing date March 2026. Expiry date February 2028. 12 out of 28 capsules
> in a sealed bottle were affected. Please log this complaint.

You should see the progress bar animate, then the left-hand form auto-populate with customer,
product, batch, dates, complaint type/description, and — after the QMS reasoning step — a
suggested Severity, Priority, and Risk Assessment.

**B. Upload one of the sample documents** in `sample_documents/`:
- `complaint_1_discoloration.txt` — the same scenario as above, as a file.
- `complaint_2_packaging.eml` — a damaged-packaging complaint (email format).
- `complaint_3_labeling_error.txt` — a labeling discrepancy (tests the "Critical" severity path).
- `complaint_4_incomplete.txt` — **missing batch number and expiry date on purpose** — the AI
  assistant should ask you a follow-up question for exactly those missing fields before it
  finishes extraction. Answer in the chat box (e.g. "Batch is IBU230501, expiry is May 2026") and
  it will continue and complete the form.

Once the form is filled, review/edit any field, then click **Save Complaint** to persist it to
the database. Use `GET /complaints` (via the Swagger docs or a `curl`) to confirm it saved.

---

## How the AI pipeline works (LangGraph)

```
User message / uploaded doc text
        │
        ▼
 [extraction]        Groq gemma2-9b-it — merges new info into the running JSON,
        │             never overwrites known fields with null, never hallucinates.
        ▼
 [completeness]      Groq gemma2-9b-it — checks 8 mandatory fields.
        │             If something's missing → asks the user, ends this turn.
        │             (Next user reply re-enters at [extraction] and loops back here.)
        ▼ (once complete)
 [qms_reasoning]     Groq llama-3.3-70b-versatile — applies pharma QMS heuristics
        │             (contamination → Critical, discoloration → Major + packaging
        │              investigation, labeling error → Critical/Major, etc.) to set
        │              Severity, Priority, Risk Assessment, Suggested Action.
        ▼
 [summary]           Groq llama-3.3-70b-versatile — writes a QA-log-style summary.
        ▼
     Form auto-filled, ready for human review + Save.
```

Session state (the running extraction + missing fields) is kept **in-memory** per `session_id`
in `backend/main.py` (`SESSIONS` dict) for simplicity. For production, persist it in the
`conversations` table instead so it survives a server restart.

## Bonus features implemented

1. **Complaint Completeness Checker** — the `completeness` LangGraph node (see above);
   loops the conversation until all 8 mandatory fields are present.
2. **Duplicate Complaint Detection** — `backend/agents/duplicate_check.py`. When you fetch a
   single complaint (`GET /complaints/{id}`), it flags other complaints against the same batch
   number in the last 30 days so QA can spot a trending batch issue.

## Data validation

Enforced server-side in `backend/schemas.py` (Pydantic validators) before anything reaches the
database: Expiry Date must be after Manufacturing Date, Complaint Date can't be in the future,
Quantity Affected must be a positive integer, and Batch Number / Product Name / Customer Name /
Description are all mandatory (`ComplaintCreate` will reject the request otherwise, and the
frontend also blocks Save client-side with a toast telling you what's missing).

## Known simplifications (documented on purpose, not hidden)

- Sessions are in-memory, not persisted across backend restarts (see above).
- No OCR — scanned/image-only PDFs won't extract text (matches the assignment: "Production-grade
  OCR or document parsing is not required").
- No auth/login layer — add one before deploying anywhere real.
- Duplicate detection is a rule-based heuristic, not an embedding-similarity search — good enough
  to demo, upgradeable later with a vector store if you want to go further.
