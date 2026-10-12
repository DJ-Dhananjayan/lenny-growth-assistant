# The Lenny Growth Assistant 🚀

**The Lenny Growth Assistant** is an evidence-grounded AI assistant designed for Product Managers, Growth Leads, and Founders. Powered by transcripts from *Lenny's Podcast*, it answers strategic product and growth questions with verbatim citations, generates publication-ready ~1,250-word **Ship 30 for 30** style essays, and renders interactive Markdown/HTML artifacts in a side-by-side workspace view.

---

## 🌟 Key Features

1. **Local-First LLM & RAG Engine**: Default local inference using **Ollama** (`qwen2.5:0.5b` / `llama3.2`) with zero required cloud API keys out-of-the-box.
2. **Transcript Knowledge Base & Citation System**: Vector embedding search across high-signal Lenny's Podcast episodes (e.g. Brian Chesky, Shreyas Doshi, Elad Gil, Elena Verna) with clickable episode citations.
3. **Strict Abstention Guarantee**: If ingested transcripts do not support a reliable answer, the assistant clearly states: *"The available Lenny's Podcast transcripts do not contain sufficient evidence to answer this question reliably."*
4. **Ship 30 for 30 Writing Skill**: Dedicated agent tool generating structured ~1,250-word growth essays complete with an opening hook, narrative progression, 3-4 framework pillars, bold key takeaways, and transcript evidence quotes.
5. **Interactive Artifact Viewer**: Split-panel rendering of Markdown and safe HTML documents.
6. **Sandboxed HTML Rendering**: Generated HTML components run inside a sandboxed `<iframe>` with strict Content Security Policy (`default-src 'none'; style-src 'unsafe-inline'`), preventing unauthorized script execution or DOM manipulation.
7. **Dynamic Provider Selection**: Toggle seamlessly between local Ollama and cloud providers (Anthropic Claude, OpenAI GPT) via the UI header.

---

## 🏗️ Tech Stack

* **Frontend**: React 18, TypeScript, Vite, Vanilla CSS, Lucide icons, Vitest.
* **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Pytest.
* **Database**: PostgreSQL with `pgvector` vector similarity search support (with automatic SQLite fallback for lightweight local dev).
* **Inference**: Ollama (Local default), Anthropic API (`claude-3-5-sonnet-20241022`), OpenAI API (`gpt-4o-mini`).
* **Containerization**: Docker Compose (`docker-compose.yml`).

---

## 🚀 Quick Start (Single-Command Launch)

### Prerequisites
1. **Python**: Python 3.10+ (tested on Python 3.10 through 3.14)
2. **Node.js**: Node 18+ & npm
3. **Ollama**: [Ollama](https://ollama.com/) for offline local inference
4. **Docker & Docker Compose**: (Optional) For containerized PostgreSQL database

---

### Clean-Machine Setup Instructions

#### Step 1: Clone Repository & Configure Environment
```bash
git clone <repository-url>
cd "project ai for company"
cp .env.example .env
```
*(No cloud API keys are required for default local Ollama execution).*

#### Step 2: Database Setup (PostgreSQL with pgvector or Automatic Fallback)
* **Option A (Recommended Docker PostgreSQL)**:
  ```bash
  docker compose up -d db
  ```
  This starts PostgreSQL with `pgvector` on port 5432.
* **Option B (Zero-dependency SQLite Fallback)**:
  If Docker is not running or PostgreSQL is offline, the backend automatically falls back to `sqlite:///./lenny_growth_db.sqlite`.

#### Step 3: Ollama Local Model Setup
Ensure Ollama is installed and running:
```bash
ollama serve
```
In another terminal, pull a supported local model:
```bash
ollama pull qwen2.5:0.5b
# OR
ollama pull llama3.2
```
*The provider adapter automatically queries Ollama's `/api/tags` endpoint and selects the best installed local model.*

#### Step 4: Transcript Ingestion (Populate Vector Database)
Install backend dependencies and run the transcript ingestion script:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend python -m app.services.ingestion
```
*This parses all sample podcast transcripts in `backend/data/sample_transcripts/`, splits them into semantic chunks, generates vector embeddings, and stores them in the database.*

#### Step 5: Provider Configuration (Optional Cloud Keys)
If you wish to use cloud models in addition to local Ollama, update `.env`:
* **Anthropic**: Set `ANTHROPIC_API_KEY=sk-ant-...`
* **OpenAI**: Set `OPENAI_API_KEY=sk-...`
Switch between providers anytime directly from the UI header dropdown.

---

### 1. Launching the Application

Run the automated one-command startup script:
```bash
./start.sh
```
*This boots the FastAPI backend on port 8000 and the Vite frontend on port 5173.*

Once started, open:
* **🌐 Web Application UI**: [http://localhost:5173](http://localhost:5173)
* **⚙️ Backend Swagger API**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **🏥 Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 2. Stopping and Terminating Background Processes
To terminate all background containers, servers, and processes:
```bash
./end.sh
```

---

## 🧪 Testing & Verification

### Running Backend Pytest Suite
```bash
source .venv/bin/activate
PYTHONPATH=backend python -m pytest backend/tests -v
```
* **Command Output**:
  ```
  backend/tests/test_agent_sdk.py::test_agent_sdk_tool_registration PASSED [  7%]
  backend/tests/test_agent_sdk.py::test_actual_agent_sdk_invocation_and_tool_execution PASSED [ 14%]
  backend/tests/test_agent_sdk.py::test_agent_sdk_essay_tool_execution PASSED [ 21%]
  backend/tests/test_agent_sdk.py::test_anthropic_provider_has_agent_sdk_enabled PASSED [ 28%]
  backend/tests/test_artifacts.py::test_artifact_retrieval PASSED          [ 35%]
  backend/tests/test_chat.py::test_chat_unsupported_question_abstention PASSED [ 42%]
  backend/tests/test_chat.py::test_chat_grounded_answer PASSED             [ 50%]
  backend/tests/test_health.py::test_health_endpoint PASSED                [ 57%]
  backend/tests/test_providers.py::test_provider_factory PASSED            [ 64%]
  backend/tests/test_providers.py::test_invalid_provider_raises_error PASSED [ 71%]
  backend/tests/test_rag.py::test_transcript_search_relevance PASSED       [ 78%]
  backend/tests/test_rag.py::test_transcript_search_brian_chesky PASSED    [ 85%]
  backend/tests/test_sessions.py::test_session_lifecycle PASSED            [ 92%]
  backend/tests/test_ship30.py::test_ship30_essay_generation PASSED        [100%]
  ======================= 14 passed in 1.97s =======================
  ```

### Running Frontend Vitest Suite & Production Build
```bash
cd frontend
npm run test -- --run
npm run build
```
* **Vitest Output**:
  ```
   ✓ src/tests/SandboxedFrame.test.tsx (1)
   ✓ src/tests/App.test.tsx (1)
   ✓ src/tests/ArtifactViewer.test.tsx (4)
   Test Files  3 passed (3)
        Tests  6 passed (6)
     Duration  3.40s
  ```
* **Production Build Output**:
  ```
  vite v5.4.21 building for production...
  ✓ 1749 modules transformed.
  dist/index.html                   0.76 kB │ gzip:   0.42 kB
  dist/assets/index-CixWC2L0.css    6.07 kB │ gzip:   1.79 kB
  dist/assets/index-Cbox2eLm.js   324.22 kB │ gzip: 100.78 kB
  ✓ built in 2.82s
  ```

---

## 🔒 Security & Artifact Sandboxing

* **Secret Hygiene**: Zero hardcoded API keys or secrets in source code. `.env` and `.env.local` are strictly excluded in `.gitignore`.
* **Hardened HTML Sandbox**: Generated HTML snippets are rendered inside an `<iframe>` using the `srcDoc` attribute with `sandbox=""` (both `allow-same-origin` and `allow-scripts` are strictly prohibited).
* **Content Security Policy (CSP)**:
  `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https:;">`
  Guarantees zero JavaScript execution, no network exfiltration, no cookie theft, and no parent DOM tampering.
* **Safe Markdown Preview**: Dedicated typography layout styling for Markdown artifacts in dark mode, with safe fallback clipboard copy and structured artifact inspection.

---

## 🤖 Agent Architecture & SDK Integration

The assistant uses an autonomous agent harness powered by **Pi Coding Agent (`pi-coding-agent`)** and the official **Anthropic Claude Agent SDK**:
* **Autonomous Tool Loop**: Employs `pi_agent.agent.Agent` with `ToolRegistry` and `Sandbox` isolation. Dispatches tools (`search_transcripts`, `generate_ship30_essay`, `create_artifact`), collects execution event traces (`tool_call`, `tool_result`), and synthesizes grounded answers.
* **SDK Compatibility**: In `backend/app/services/providers/anthropic_provider.py`, the system detects `pi-coding-agent` and `claude_agent_sdk`, prioritizing autonomous agent SDK execution over bare request-response loops.
* **Direct SDK Execution**: `LennyGrowthAgent.run_with_agent_sdk()` enables autonomous multi-turn execution with full event logging and database chunk grounding.

## 📋 Manual Verification Flows

1. **Greeting Check**:
   - Prompt: `"hi"`
   - Expected Output: Friendly greeting and suggested question shortcuts.
2. **Grounded Q&A Test**:
   - Prompt: *"What is the LNO Framework by Shreyas Doshi?"*
   - Expected Output: Clear explanation of Leverage (10x), Neutral (7/10), and Overhead (5/10) tasks with clickable citation badges linking to Shreyas Doshi's episode.
3. **Abstention Test**:
   - Prompt: *"What is the quantum physics formula for black hole thermodynamics?"*
   - Expected Output: Clean abstention explaining that transcripts do not contain sufficient evidence.
4. **Ship 30 for 30 Essay Test**:
   - Prompt: *"Write a Ship 30 for 30 essay on Product-Led Growth loops"*
   - Expected Output: Invokes Ship 30 writing skill tool, generates ~1,250-word essay, and opens Markdown artifact side panel.
5. **HTML Artifact Test**:
   - Prompt: *"Generate an HTML dashboard card widget for PLG metrics"*
   - Expected Output: Opens side panel rendering HTML inside a sandboxed iframe.

---

## 📁 Repository Deliverables & Structure

```
project ai for company/
├── README.md                      # Comprehensive guide, run instructions, and audit report
├── PRD.md                         # Product Requirements Document
├── design.md                      # UI/UX design specifications & layout guidelines
├── architecture.md                # System architecture, schemas, and RAG sequence flows
├── .env.example                   # Environment configuration template
├── .env                           # Local environment config
├── .gitignore                     # Git exclusion rules
├── start.sh                       # Single-command application launcher
├── end.sh                         # Single-command cleanup & kill script
├── docker-compose.yml             # Docker orchestration (Postgres, Backend, Frontend)
├── agent-transcripts/             # Development agent logs & execution traces
│   ├── dev_agent_log_01.jsonl
│   └── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                    # Database migrations
│   ├── data/sample_transcripts/    # Lenny's Podcast JSON transcripts
│   ├── app/                        # FastAPI source code
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── agent/
│   │   └── api/
│   └── tests/                     # Pytest suite
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx                # Main React workspace layout
        ├── components/            # Sidebar, ChatPanel, ArtifactViewer, SandboxedFrame, CitationsList
        └── tests/                 # Vitest React UI tests
```
