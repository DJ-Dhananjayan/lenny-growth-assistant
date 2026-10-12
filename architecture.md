# Technical Architecture
## Project Name: The Lenny Growth Assistant

---

### 1. High-Level System Architecture

```
                                 +------------------------------+
                                 |       React + Vite UI        |
                                 | (Chat, Artifacts, Providers) |
                                 +--------------+---------------+
                                                |
                                                | HTTP / REST API
                                                v
                                 +------------------------------+
                                 |       FastAPI Backend        |
                                 +--------------+---------------+
                                                |
               +--------------------------------+--------------------------------+
               |                                |                                |
               v                                v                                v
     +-------------------+            +-------------------+            +-------------------+
     | Model Provider    |            | Agent Engine &    |            | Database Layer    |
     | Adapters          |            | RAG Ingestion     |            | (SQLAlchemy 2.0)  |
     +---------+---------+            +---------+---------+            +---------+---------+
               |                                |                                |
     +---------+---------+            +---------+---------+            +---------+---------+
     | Ollama (Local)    |            | Vector Embedding  |            | PostgreSQL DB   |
     | Anthropic (Cloud) |            | & Chunk Search    |            | & pgvector      |
     | OpenAI (Cloud)    |            +-------------------+            +-------------------+
     +-------------------+
```

---

### 2. Component Design & Responsibilities

#### 2.1 Backend Layer (`/backend`)
* **`app.config.Settings`**: Environment variable parsing, default providers, database URL configuration.
* **`app.db`**: Database session factory (`session.py`), SQLAlchemy ORM models (`models.py`) for `Session`, `Message`, `Transcript`, `TranscriptChunk`.
* **`app.services.providers`**: Unified interface `BaseLLMProvider` with concrete implementations:
  - `OllamaProvider`: Calls local Ollama REST API (`/api/generate` or `/api/chat`).
  - `AnthropicProvider`: Integrated with the official **Pi Coding Agent (`pi_agent`)** and Anthropic Claude Agent SDK (`claude_agent_sdk`) for autonomous multi-turn tool loops with `ToolRegistry` and `Sandbox` isolation.
  - `OpenAIProvider`: Calls OpenAI Chat Completions API (`gpt-4o-mini`).
* **`app.services.embedding`**: Generates dense vector embeddings using local sentence transformer / lightweight embedding pipeline or Ollama embeddings.
* **`app.services.vector_store`**: Manages vector insertion and top-$k$ cosine similarity search over transcript chunks in PostgreSQL.
* **`app.agent.engine`**: Core agentic execution harness (`LennyGrowthAgent`). Integrates `search_transcripts`, `generate_ship30_essay`, and `create_artifact` tools into `ToolRegistry`, supports `run_with_agent_sdk()`, and synthesizes grounded answers with citations and sandboxed artifacts.
* **`app.api`**: Clean FastAPI endpoints with validated Pydantic models:
  - `/api/v1/health`: Readiness & database connectivity check.
  - `/api/v1/sessions`: CRUD operations for chat sessions.
  - `/api/v1/chat`: Send message, execute agent RAG loop, return message + citations + artifacts.
  - `/api/v1/providers`: List available LLM providers & current active config.
  - `/api/v1/artifacts`: Retrieve artifact content by ID.
  - `/api/v1/ingest`: Trigger transcript ingestion status & run ingestion.

#### 2.2 Frontend Layer (`/frontend`)
* **State Management**: React state hooks managing active session, messages, selected provider, active artifact, loading & error states.
* **`Sidebar.tsx`**: Renders new session button, existing chat sessions, and delete session options.
* **`ProviderSelector.tsx`**: UI control to inspect and switch between Ollama, Anthropic, and OpenAI providers.
* **`ChatPanel.tsx`**: Manages message feed, stream rendering, and user input.
* **`CitationsList.tsx`**: Renders clickable source badges for retrieved transcript chunks (Title, Guest, URL).
* **`ArtifactViewer.tsx`**: Split panel component offering side-by-side Markdown & HTML artifact preview with source toggle, copy, and download capabilities.
* **`SandboxedFrame.tsx`**: Renders untrusted HTML inside a sandboxed `<iframe>` with strict Content Security Policy.

---

### 3. Database Schema

```sql
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL DEFAULT 'ollama',
    model VARCHAR(100) NOT NULL DEFAULT 'llama3.2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    citations_json JSONB,
    artifact_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transcripts (
    id VARCHAR(36) PRIMARY KEY,
    episode_title VARCHAR(255) NOT NULL,
    guest VARCHAR(255) NOT NULL,
    episode_url VARCHAR(512),
    episode_num INT,
    publish_date VARCHAR(50),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transcript_chunks (
    id VARCHAR(36) PRIMARY KEY,
    transcript_id VARCHAR(36) NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata_json JSONB,
    embedding vector(384) -- pgvector 384-dimensional vector
);
```

---

### 4. RAG & Agent Flow Sequence

```
User Query ---> API (/chat) ---> Agent Engine
                                    |
                                    v
                         Search Transcripts Tool
                                    |
                        Vector Store Cosine Search
                                    |
                        Returns Top-K Chunks + Metadata
                                    |
                        Insufficient Evidence?
                         /                  \
                       YES                   NO
                        |                     |
         Abstain with Clear State      Synthesize Answer + Citations
                                              |
                                     Ship 30 Essay Requested?
                                       /              \
                                     YES              NO
                                      |                |
                          Invoke Ship30 Skill   Standard Response
                                      \                /
                                       v              v
                                      Persist to Postgres
                                              |
                                      Return to React UI
```

---

### 5. Security & Isolation Boundaries
1. **Local First Security**: Ollama runs entirely offline on the local network; no transcript data is transmitted to third parties unless cloud providers are explicitly configured.
2. **HTML Artifact Sandboxing**: Generated HTML artifacts are rendered inside an isolated `<iframe>` using the `srcDoc` attribute. The iframe is strictly hardened with `sandbox=""` (removing both `allow-same-origin` and `allow-scripts`) and a Content Security Policy meta header (`default-src 'none'; style-src 'unsafe-inline'`), preventing script execution, cookie access, and parent DOM navigation.
3. **Secret Hygiene**: All cloud API keys are read from environment variables; keys are excluded from git logs, database storage, and API responses.
