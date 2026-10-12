# Product Requirements Document (PRD)
## Project Name: The Lenny Growth Assistant

---

### 1. Executive Summary
**The Lenny Growth Assistant** is an AI-powered growth and product management assistant built on transcripts from *Lenny's Podcast*. It provides product managers, founders, and growth leaders with evidence-grounded answers to strategic questions, generates structured 1,250-word Ship 30 for 30-style essays, and renders interactive Markdown and safe HTML/CSS artifacts directly inside the workspace.

---

### 2. User & Problem Statement
* **Target Audience**: Product Managers, Growth Leads, Tech Founders, and Strategic Marketers.
* **Core Problem**: *Lenny's Podcast* contains hundreds of hours of high-signal advice from world-class product leaders (e.g., Brian Chesky, Shreyas Doshi, Elad Gil, Elena Verna). However, searching through audio or raw transcripts to find actionable frameworks, quotes, and specific advice is slow and unreliable. Generic AI chatbots often hallucinate frameworks or misattribute quotes.
* **Solution**: A RAG-grounded AI assistant running on local LLMs (Ollama) or configurable cloud LLMs (Anthropic Claude, OpenAI) that retrieves actual podcast transcript passages, provides clickable citations, generates publication-ready growth essays, and displays rich interactive artifacts in a split-screen view.

---

### 3. Key Goals & Measurable Success Metrics
1. **Fact Grounding & Citation Accuracy**: 100% of facts and quotes in standard Q&A must cite valid chunk sources from ingested transcripts. If evidence is lacking, the assistant must explicitly abstain.
2. **Local First**: Out-of-the-box operation using Ollama without requiring external API keys.
3. **Artifact Render Time**: Side-by-side artifact rendering under 500ms once generated.
4. **Ship 30 for 30 Essay Quality**: Dedicated skill tool generating ~1,250 word essays featuring a hook, narrative progression, actionable bullet points, and grounded transcript quotes.
5. **Security & Isolation**: 100% sandboxed iframe rendering for generated HTML artifacts with zero parent DOM injection or unauthorized script execution.

---

### 4. Required Technology Stack
* **Frontend**: React 18, TypeScript, Vite, Vanilla/Modern CSS, Lucide icons.
* **Backend**: Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
* **Database**: PostgreSQL with `pgvector` / vector similarity indexing for RAG chunk retrieval.
* **Local LLM**: Ollama (`llama3.2` default model).
* **Cloud LLM Adapters**: Anthropic (`claude-3-5-sonnet-20241022`), OpenAI (`gpt-4o-mini`).
* **Agent Framework**: Official **Pi Coding Agent SDK (`pi-coding-agent`)** and Anthropic Claude Agent SDK (`claude_agent_sdk`) with `ToolRegistry` and `Sandbox` isolation.
* **Containerization**: Docker Compose (`docker-compose.yml`).
* **Testing**: Pytest for backend API/RAG/Providers/Agent SDK; Vitest / Testing Library for frontend.

---

### 5. Scope & Feature Requirements

#### A. Session & Chat Management
* Generate UUID session IDs.
* Maintain independent conversation contexts in PostgreSQL.
* Retrieve session history, supporting multi-turn follow-up queries.
* Handle loading, timeout, retry, and error states gracefully.

#### B. Transcript Knowledge Base & RAG Pipeline
* Repeatable ingestion CLI (`python -m app.services.ingestion`) and API endpoint (`POST /api/v1/ingest`).
* Chunking of transcripts with metadata (episode title, guest name, episode URL, chunk index).
* Embedding generation and vector index storage in PostgreSQL.
* Citation generation: returned passages link directly to podcast episode metadata.
* Strict evidence fallback: "The available Lenny's Podcast transcripts do not contain sufficient evidence to answer this question reliably."

#### C. Ship 30 for 30 Essay Generation Skill
* Reusable skill/tool producing structured ~1,250-word essays.
* Elements required:
  - Strong opening hook statement.
  - Clear narrative progression & section headers.
  - Actionable takeaways and bold key phrases.
  - Verifiable transcript citations and verbatim quotes.

#### D. Interactive Artifact Viewer
* Side-by-side rendering beside chat panel.
* Markdown document preview & raw source view.
* HTML/CSS document rendering in a sandboxed `<iframe>` with strict Content Security Policy (`default-src 'none'; style-src 'unsafe-inline'`).
* One-click Copy to Clipboard and Download actions.

#### E. Model & Provider Configuration
* Dynamic provider selection (`ollama`, `anthropic`, `openai`) visible in UI header/selector.
* No silent fallbacks: explicit, actionable error messages if Ollama is unreachable or cloud keys are missing.

---

### 6. Acceptance Criteria
* [x] Fresh `docker compose up --build` boots up database, backend, and frontend.
* [x] Ingestion populates vector database with sample podcast transcripts.
* [x] Assistant answers questions with exact transcript citations.
* [x] Unsupported queries trigger clean abstention responses.
* [x] Essay prompt invokes Ship 30 for 30 tool and generates formatted output.
* [x] Generated HTML artifacts open in sandboxed iframe without errors.
* [x] Automated test suite passes (backend pytest & frontend vitest).
