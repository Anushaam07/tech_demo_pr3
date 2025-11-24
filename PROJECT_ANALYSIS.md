# RAG API with Promptfoo Integration - Complete Project Analysis

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Flow Diagram](#architecture-flow-diagram)
3. [How to Run the Project](#how-to-run-the-project)
4. [RAG Application Endpoints](#rag-application-endpoints)
5. [Promptfoo Integration Features](#promptfoo-integration-features)
6. [Running Promptfoo Tests](#running-promptfoo-tests)
7. [Feature Summary & Commands](#feature-summary--commands)

---

## Project Overview

### What is this Project?

This is a **RAG (Retrieval-Augmented Generation) API** built with FastAPI that provides:

1. **Document Embedding Service**: Upload documents (PDF, DOCX, TXT, etc.) and convert them to vector embeddings
2. **Semantic Search**: Query documents using natural language and retrieve relevant chunks
3. **LLM Summarization**: Use Azure OpenAI GPT-4o-mini to generate intelligent summaries from retrieved context
4. **Multi-tenant Security**: User/entity isolation with JWT authentication

### Key Technologies
- **Backend**: FastAPI (Python 3.10+)
- **Vector Database**: PGVector (PostgreSQL) or MongoDB Atlas
- **Embeddings**: OpenAI, Azure, HuggingFace, Ollama, Google, AWS Bedrock
- **LLM**: Azure OpenAI (GPT-4o-mini)
- **Testing**: Promptfoo (LLM evaluation, red teaming, security testing)

---

## Architecture Flow Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT APPLICATIONS                             │
│                    (LibreChat, Custom Apps, Promptfoo Tests)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI APPLICATION                             │
│                            (main.py - Port 8000)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   Middleware    │  │   CORS Handler  │  │    Log Middleware           │  │
│  │  (JWT Auth)     │  │   (All Origins) │  │    (Request/Response)       │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘  │
│           └────────────────────┼────────────────────────────┘                │
│                                ▼                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                          ROUTE HANDLERS                                │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │  │
│  │  │ document_routes  │  │   llm_routes     │  │  pgvector_routes     │ │  │
│  │  │ (Core RAG APIs)  │  │ (LLM Summary)    │  │  (Debug - optional)  │ │  │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                        ┌──────────────┼──────────────┐
                        ▼              ▼              ▼
            ┌───────────────┐  ┌─────────────┐  ┌─────────────┐
            │   EMBEDDING   │  │   VECTOR    │  │    LLM      │
            │   PROVIDERS   │  │   STORES    │  │  PROVIDERS  │
            ├───────────────┤  ├─────────────┤  ├─────────────┤
            │ • OpenAI      │  │ • PGVector  │  │ • Azure     │
            │ • Azure       │  │ • MongoDB   │  │   OpenAI    │
            │ • HuggingFace │  │   Atlas     │  │   GPT-4o    │
            │ • Ollama      │  └─────────────┘  └─────────────┘
            │ • Bedrock     │
            │ • Google      │
            └───────────────┘
```

### Document Embedding Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   UPLOAD     │     │    LOAD      │     │   PROCESS    │     │    STORE     │
│   DOCUMENT   │────▶│   DOCUMENT   │────▶│   DOCUMENT   │────▶│  IN VECTOR   │
│              │     │              │     │              │     │   DATABASE   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ POST /embed  │     │ Detect file  │     │ Text split   │     │ Generate     │
│ or           │     │ type & load  │     │ into chunks  │     │ embeddings   │
│ POST /embed- │     │ with correct │     │ (1000 chars) │     │ Store with   │
│ upload       │     │ loader       │     │ Clean text   │     │ metadata     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘

Supported Formats: PDF, DOCX, TXT, CSV, XLSX, PPTX, MD, HTML, JSON, XML
```

### Query/Retrieval Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    USER      │     │   CONVERT    │     │   VECTOR     │     │   RETURN     │
│    QUERY     │────▶│   TO VECTOR  │────▶│   SEARCH     │────▶│   RESULTS    │
│              │     │              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ POST /query  │     │ Embed query  │     │ Find top-k   │     │ Document     │
│ {query,      │     │ using same   │     │ similar      │     │ chunks with  │
│  file_id,    │     │ embedding    │     │ chunks by    │     │ scores and   │
│  entity_id}  │     │ model        │     │ cosine sim   │     │ metadata     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### RAG with LLM Summarization Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     POST /query_with_summary                                │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   STEP 1      │          │   STEP 2      │          │   STEP 3      │
│   Retrieve    │          │   Build       │          │   Call LLM    │
│   Chunks      │────────▶ │   Context     │────────▶ │   for Summary │
└───────────────┘          └───────────────┘          └───────────────┘
       │                          │                          │
       ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ Vector search │          │ Concatenate   │          │ Azure OpenAI  │
│ with filters  │          │ chunks into   │          │ GPT-4o-mini   │
│ (file_id,     │          │ context       │          │ generates     │
│ entity_id)    │          │ [Chunk 1]...  │          │ grounded      │
│ Get top-k     │          │ [Chunk N]     │          │ summary       │
└───────────────┘          └───────────────┘          └───────────────┘
                                                             │
                                                             ▼
                                                    ┌───────────────┐
                                                    │   RESPONSE    │
                                                    │ {summary,     │
                                                    │  chunks,      │
                                                    │  metadata}    │
                                                    └───────────────┘
```

---

## How to Run the Project

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+** (for Promptfoo)
3. **Docker & Docker Compose** (recommended)
4. **PostgreSQL with pgvector** OR MongoDB Atlas account

### Step-by-Step Setup

#### Option A: Using Docker Compose (Recommended)

```bash
# 1. Clone/navigate to project
cd /home/user/tech_demo_pr3

# 2. Create .env file with required variables
cp .env.example .env  # If exists, or create manually

# 3. Edit .env with your credentials (see Environment Variables section below)

# 4. Start the services
docker-compose up -d

# 5. Check logs
docker-compose logs -f fastapi

# 6. API available at http://localhost:8000
```

#### Option B: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install test dependencies (optional)
pip install -r test_requirements.txt

# 4. Start PostgreSQL with pgvector (separate terminal)
docker-compose -f db-compose.yaml up -d

# 5. Create .env file with required variables
# See Environment Variables section below

# 6. Run the application
python main.py

# API available at http://localhost:8000
```

### Required Environment Variables

Create a `.env` file with these variables:

```bash
# === Vector Database (choose one) ===
VECTOR_DB_TYPE=pgvector  # or 'atlas-mongo'

# PostgreSQL (PGVector)
DB_HOST=localhost
DB_PORT=5433
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=mydatabase

# OR MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/

# === Embeddings Provider ===
EMBEDDINGS_PROVIDER=openai  # Options: openai, azure, huggingface, ollama, bedrock, google

# OpenAI (default)
OPENAI_API_KEY=sk-your-api-key

# OR Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# === LLM for Summarization (Azure) ===
AZURE_CHAT_API_KEY=your-azure-chat-key
AZURE_CHAT_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_CHAT_DEPLOYMENT=gpt-4o-mini

# === Application Settings ===
RAG_HOST=0.0.0.0
RAG_PORT=8000
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
DEBUG_MODE=false
```

### Install Promptfoo (for Testing)

```bash
# Install Node.js dependencies
npm install

# Verify Promptfoo is installed
npx promptfoo --version
```

---

## RAG Application Endpoints

### Core Document Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check - returns UP/DOWN status |
| `/embed` | POST | Upload file and create embeddings |
| `/embed-upload` | POST | Alternative file upload endpoint |
| `/local/embed` | POST | Embed a file already on server |
| `/text` | POST | Extract text without creating embeddings |
| `/query` | POST | Semantic search on embeddings |
| `/query_multiple` | POST | Query across multiple file IDs |
| `/query_with_summary` | POST | RAG with LLM summarization |
| `/documents` | GET | Get documents by IDs |
| `/documents` | DELETE | Delete documents by IDs |
| `/documents/{id}/context` | GET | Get full document context |
| `/ids` | GET | List all document IDs |

### Endpoint Details & Examples

#### 1. Upload and Embed Document
```bash
curl -X POST "http://localhost:8000/embed" \
  -F "file=@document.pdf" \
  -F "file_id=doc123" \
  -F "entity_id=user1"
```

Response:
```json
{
  "status": true,
  "message": "File processed successfully.",
  "file_id": "doc123",
  "filename": "document.pdf",
  "known_type": "application/pdf"
}
```

#### 2. Query Documents (Semantic Search)
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features?",
    "file_id": "doc123",
    "entity_id": "user1",
    "k": 4
  }'
```

Response:
```json
[
  [
    {
      "page_content": "The main features include...",
      "metadata": {"file_id": "doc123", "page": 1}
    },
    0.85  // similarity score
  ]
]
```

#### 3. RAG with LLM Summary
```bash
curl -X POST "http://localhost:8000/query_with_summary" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize the key recommendations",
    "file_id": "doc123",
    "entity_id": "user1",
    "k": 4,
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

Response:
```json
{
  "query": "Summarize the key recommendations",
  "summary": "Based on the document, the key recommendations are...",
  "retrieved_chunks": [
    {"content": "Chunk 1 content...", "file_id": "doc123", "page": 1}
  ],
  "metadata": {
    "model": "gpt-4o-mini",
    "retrieval_latency_ms": 45.2,
    "llm_latency_ms": 1234.5,
    "total_latency_ms": 1279.7,
    "chunks_retrieved": 4,
    "tokens_total": 850,
    "cost_usd": 0.000127
  }
}
```

#### 4. Extract Text Only (No Embeddings)
```bash
curl -X POST "http://localhost:8000/text" \
  -F "file=@document.pdf" \
  -F "file_id=doc123" \
  -F "entity_id=user1"
```

---

## Promptfoo Integration Features

### Overview

Promptfoo is integrated for comprehensive LLM testing including:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMPTFOO TESTING FRAMEWORK                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │   BASELINE    │  │  GUARDRAILS   │  │   RED TEAM    │  │ PERFORMANCE  │ │
│  │   TESTING     │  │   & QUALITY   │  │   SECURITY    │  │   TESTING    │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘ │
│         │                  │                  │                  │          │
│         ▼                  ▼                  ▼                  ▼          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ • Regression  │  │ • PII Filter  │  │ • OWASP LLM   │  │ • Latency    │ │
│  │ • Sanity      │  │ • Factuality  │  │ • NIST AI     │  │ • Load Test  │ │
│  │ • Policy      │  │ • Toxicity    │  │ • MITRE ATLAS │  │ • Concurrent │ │
│  │ • Leak Test   │  │ • RBAC        │  │ • Jailbreak   │  │ • Edge Cases │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Feature Breakdown

#### 1. Model Evaluation (`promptfoo.config.yaml`)
- **Purpose**: Basic regression testing
- **Tests**:
  - Document summarization quality
  - Secret/API key leak prevention
  - Policy compliance

#### 2. Guardrails (`promptfoo.guardrails.yaml`)
Tests safety and compliance:

| Test Category | What It Checks |
|---------------|----------------|
| **Factuality** | Responses based on knowledge base only |
| **Hallucination** | Prevents making up citations |
| **PII Protection** | Refuses to leak emails, SSNs, phone numbers |
| **Toxicity Handling** | Professional response to toxic inputs |
| **Business Policy** | No competitor endorsements, unauthorized commitments |
| **RBAC** | Respects user access boundaries |

#### 3. Red Teaming (`promptfoo.redteam.yaml`)
Security testing with attack simulations:

| Plugin | Attack Type |
|--------|-------------|
| `rag-document-exfiltration` | Cross-tenant data access |
| `rag-poisoning` | Vector database corruption |
| `prompt-extraction` | System prompt leakage |
| `system-prompt-override` | Jailbreak attempts |
| `ssrf` | Server-side request forgery |
| `pii:session` | Session-based PII leaks |
| `contracts` | Unauthorized business commitments |

#### 4. Comprehensive Red Team (`promptfoo.redteam-comprehensive.yaml`)
Full security assessment:

| Category | Plugins |
|----------|---------|
| **RAG Vulnerabilities** | Document exfiltration, poisoning, prompt extraction |
| **Authorization** | BOLA, BFLA, RBAC, cross-session leak |
| **Injection Attacks** | SQL, shell, indirect prompt injection |
| **Data Privacy** | PII (direct, session, social, API-DB) |
| **Network Security** | SSRF, debug access |
| **Business Logic** | Contracts, competitors, excessive agency |
| **Harmful Content** | Hate, harassment, privacy, specialized advice |

**Frameworks Covered**:
- OWASP LLM Top 10
- OWASP API Security
- NIST AI Risk Management Framework
- MITRE ATLAS

**Attack Strategies**:
- Jailbreak attempts
- Prompt injection
- Multi-turn conversations (crescendo, GOAT)
- Encoding obfuscation (Base64, ROT13, leetspeak, homoglyph)
- Multilingual testing (EN, ES, FR)

#### 5. LLM Quality Testing (`promptfoo.llm-quality.yaml`)
Tests the `/query_with_summary` endpoint:

| Test | Purpose |
|------|---------|
| Grounded answers | Summary based on retrieved chunks only |
| Hallucination detection | Acknowledges missing information |
| Citation accuracy | Uses chunks correctly |
| Query relevance | Answers the actual question |
| Conciseness | Not overly verbose |
| Latency | Response within acceptable time |

#### 6. Performance Testing (`promptfoo.performance.yaml`)
| Test | Target |
|------|--------|
| Fast response | < 2 seconds |
| Complex query | < 5 seconds |
| Large retrieval (k=50) | < 10 seconds |
| Concurrent handling | Multiple simultaneous requests |

---

## Running Promptfoo Tests

### Quick Reference Commands

```bash
# Start the RAG API first!
docker-compose up -d
# OR
python main.py
```

### Individual Test Suites

```bash
# 1. Baseline Regression Tests (3 tests)
npm run test:baseline

# 2. Multi-Endpoint Tests (8 tests)
npm run test:multi-endpoint

# 3. Guardrails & Quality (9 tests)
npm run test:guardrails

# 4. Performance & Latency (8+ tests)
npm run test:performance

# 5. Dataset-Driven Tests (16+ tests)
npm run test:dataset

# 6. A/B Comparison Tests (4 tests)
npm run test:compare

# 7. LLM Quality Tests (9 tests)
npm run test:llm-quality

# 8. Prompt Optimization Tests
npm run test:prompt-optimization
```

### Security/Red Team Tests

```bash
# Basic Red Team (35+ tests)
npm run test:redteam

# LLM-based Red Team
npm run test:redteam:llm

# Comprehensive Red Team (400+ variations)
npm run test:redteam:full

# Custom RAG Attack Plugins
npm run test:redteam:custom
```

### Combined Test Suites

```bash
# All basic quality tests
npm run test:all

# Quality + Dataset tests
npm run test:quality

# All security tests
npm run test:security

# Full nightly suite (everything)
npm run test:nightly
```

### Viewing Results

```bash
# Open web UI to view results
npm run view

# View latest run only
npm run view:latest

# Clear cache
npm run cache:clear
```

### Understanding Test Output

When you run a test, Promptfoo shows:

```
┌────────────────────────────────────────────────────────────────┐
│ Test Results                                                    │
├─────────────────┬───────────┬───────────┬─────────────────────┤
│ Test Name       │ Pass/Fail │ Latency   │ Assertions          │
├─────────────────┼───────────┼───────────┼─────────────────────┤
│ Summarize       │ ✓ PASS    │ 1.2s      │ 2/2 passed          │
│ Secret leak     │ ✓ PASS    │ 0.8s      │ 1/1 passed          │
│ PII protection  │ ✓ PASS    │ 0.5s      │ 2/2 passed          │
└─────────────────┴───────────┴───────────┴─────────────────────┘

Total: 3 passed, 0 failed
```

For web UI (`npm run view`):
- Interactive dashboard
- Detailed assertion results
- Response comparisons
- Historical trends

---

## Feature Summary & Commands

### Complete Test Matrix

| Feature | Config File | Command | Tests |
|---------|-------------|---------|-------|
| **Baseline Regression** | `promptfoo.config.yaml` | `npm run test:baseline` | 3 |
| **Multi-Endpoint** | `promptfoo.multi-endpoint.yaml` | `npm run test:multi-endpoint` | 8 |
| **Guardrails (PII, Toxicity, RBAC)** | `promptfoo.guardrails.yaml` | `npm run test:guardrails` | 9 |
| **Performance** | `promptfoo.performance.yaml` | `npm run test:performance` | 8+ |
| **Dataset-Driven** | `promptfoo.dataset-driven.yaml` | `npm run test:dataset` | 16+ |
| **A/B Comparison** | `promptfoo.compare.yaml` | `npm run test:compare` | 4 |
| **LLM Quality** | `promptfoo.llm-quality.yaml` | `npm run test:llm-quality` | 9 |
| **Prompt Optimization** | `promptfoo.prompt-optimization.yaml` | `npm run test:prompt-optimization` | - |
| **Basic Red Team** | `promptfoo.redteam.yaml` | `npm run test:redteam` | 35+ |
| **LLM Red Team** | `promptfoo.redteam-llm.yaml` | `npm run test:redteam:llm` | - |
| **Comprehensive Red Team** | `promptfoo.redteam-comprehensive.yaml` | `npm run test:redteam:full` | 400+ |

### Security Features Tested

| Security Category | Test Type | Config |
|-------------------|-----------|--------|
| **Model Security** | Prompt injection, jailbreak | Red Team configs |
| **Evaluation** | Factuality, hallucination, quality | `llm-quality.yaml`, `guardrails.yaml` |
| **Red Teaming** | OWASP LLM, MITRE ATLAS attacks | `redteam-comprehensive.yaml` |
| **Guardrails** | PII, toxicity, RBAC, business policy | `guardrails.yaml` |
| **Data Privacy** | PII detection, cross-tenant leakage | All red team configs |

### RAG Endpoint Testing Matrix

| Endpoint | Tested In |
|----------|-----------|
| `POST /query` | baseline, guardrails, redteam, performance |
| `POST /embed` | multi-endpoint |
| `POST /text` | multi-endpoint |
| `POST /query_with_summary` | llm-quality |
| `GET /health` | multi-endpoint |

---

## Recommended Test Workflow

### 1. First-Time Setup
```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Upload test documents
curl -X POST "http://localhost:8000/embed" \
  -F "file=@test-documents/sample-policy.txt" \
  -F "file_id=testid1" \
  -F "entity_id=test-user"
```

### 2. Run Basic Tests
```bash
# Quick sanity check
npm run test:baseline

# View results
npm run view:latest
```

### 3. Run Quality Tests
```bash
npm run test:quality
```

### 4. Run Security Tests
```bash
# Start with focused red team
npm run test:redteam

# Then comprehensive (takes longer)
npm run test:redteam:full
```

### 5. Run Performance Tests
```bash
npm run test:performance
```

### 6. Full Nightly Suite
```bash
npm run test:nightly
```

---

## Output Locations

- **Promptfoo Results**: `~/.promptfoo/output/`
- **Web UI**: `http://localhost:15500` (when running `npm run view`)
- **API Logs**: Console output or Docker logs
- **Test Documents**: `./test-documents/`

---

## Summary

This project is a **production-grade RAG API** with:

1. **Core Functionality**: Document embedding, semantic search, LLM summarization
2. **Multi-Provider Support**: 8+ embedding providers, 2 vector stores
3. **Security**: JWT auth, tenant isolation, RBAC
4. **Comprehensive Testing**: 500+ test variations via Promptfoo
5. **Security Evaluation**: OWASP, NIST, MITRE ATLAS frameworks
6. **Quality Guardrails**: PII protection, hallucination detection, toxicity handling

Run `npm run test:all` for basic quality assurance, or `npm run test:nightly` for full security and performance validation.
