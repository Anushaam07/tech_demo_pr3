# RAG API - Comprehensive Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Testing Framework](#testing-framework)
6. [Deployment](#deployment)
7. [Configuration](#configuration)
8. [Commands Reference](#commands-reference)

---

## Overview

### What is RAG API?
The RAG (Retrieval-Augmented Generation) API is a FastAPI-based service that provides document indexing, embedding, and retrieval capabilities using vector databases. It integrates LangChain with PostgreSQL/pgvector for efficient semantic search.

### Why was it implemented?
- **File-level organization**: Documents are organized by `file_id` for targeted retrieval
- **LibreChat integration**: Primary use case is integration with LibreChat for conversational AI
- **Scalability**: Asynchronous operations for high-performance document processing
- **Multi-provider support**: Supports multiple embedding providers (OpenAI, Azure, HuggingFace, etc.)
- **Security**: JWT-based authentication and authorization

### How does it help?
- **Semantic search**: Find relevant document chunks based on meaning, not just keywords
- **Multi-tenant support**: User-level isolation with entity_id support
- **Flexible storage**: Supports pgvector and MongoDB Atlas
- **Production-ready**: Comprehensive testing, security scanning, and monitoring

---

## Architecture

### High-Level Architecture

```
┌─────────────┐
│   Client    │
│ (LibreChat) │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌───────────────────────────────┐  │
│  │   Security Middleware (JWT)   │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │     Document Routes           │  │
│  │  /embed, /query, /text, etc.  │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Document Loader Service     │  │
│  │  (PDF, DOCX, TXT, etc.)       │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Embedding Service           │  │
│  │  (OpenAI, Azure, HF, etc.)    │  │
│  └───────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│      Vector Store (pgvector)        │
│   PostgreSQL with vector extension  │
└─────────────────────────────────────┘
```

### Technology Stack
- **Framework**: FastAPI (async Python web framework)
- **Vector Database**: PostgreSQL with pgvector extension
- **Embeddings**: LangChain integration with multiple providers
- **Authentication**: JWT token verification
- **Document Processing**: Unstructured, PyPDF, docx2txt, pypandoc
- **Testing**: Promptfoo (security & quality testing)

---

## Core Components

### 1. Main Application (`main.py`)

**What it does**: Entry point for the FastAPI application

**Key features**:
- Lifespan management (startup/shutdown)
- Thread pool executor for async operations
- CORS middleware configuration
- Request validation error handling
- Vector database initialization

**How it works**:
```python
# Thread pool is created on startup
max_workers = min(os.cpu_count(), 8)
app.state.thread_pool = ThreadPoolExecutor(max_workers=max_workers)

# Vector indexes are ensured on startup
if VECTOR_DB_TYPE == VectorDBType.PGVECTOR:
    await PSQLDatabase.get_pool()
    await ensure_vector_indexes()
```

### 2. Configuration (`app/config.py`)

**What it does**: Centralized configuration management

**Key components**:
- Environment variable loading
- Embedding provider initialization
- Vector store setup
- Logging configuration (JSON/text formats)

**Supported Embedding Providers**:
| Provider | Model Default | Use Case |
|----------|---------------|----------|
| OpenAI | text-embedding-3-small | Production, high quality |
| Azure OpenAI | text-embedding-3-small | Enterprise, compliance |
| HuggingFace | all-MiniLM-L6-v2 | Self-hosted, cost-effective |
| Ollama | nomic-embed-text | Local development |
| AWS Bedrock | amazon.titan-embed-text-v1 | AWS ecosystem |
| Google VertexAI | text-embedding-004 | GCP ecosystem |

**How it helps**: Single source of truth for all configuration, easy to switch providers

### 3. Document Routes (`app/routes/document_routes.py`)

**What it does**: Handles all document-related API operations

**Key endpoints**:

- `POST /embed` - Upload and embed documents
- `POST /query` - Query embeddings by file_id
- `POST /text` - Extract text without embedding
- `GET /documents` - Retrieve documents by IDs
- `DELETE /documents` - Delete documents
- `GET /ids` - Get all file IDs
- `GET /health` - Health check

**How it works**:
1. File upload → Save to temp directory
2. Load content using appropriate loader (PDF, DOCX, etc.)
3. Split into chunks (default: 1500 chars, 100 overlap)
4. Generate embeddings
5. Store in vector database with metadata
6. Clean up temp files

### 4. Vector Store (`app/services/vector_store/`)

**What it does**: Abstraction layer for vector database operations

**Implementations**:
- `AsyncPgVector` - Async PostgreSQL with pgvector
- `ExtendedPgVector` - Sync PostgreSQL with pgvector
- `AtlasMongoVector` - MongoDB Atlas vector search

**Key operations**:
- `aadd_documents()` - Add documents with embeddings
- `asimilarity_search_with_score_by_vector()` - Search by embedding
- `get_documents_by_ids()` - Retrieve by file_id
- `delete()` - Remove documents

**How it helps**: 
- Consistent interface across different vector stores
- Async operations for better performance
- Built-in filtering by file_id and user_id

### 5. Document Loader (`app/utils/document_loader.py`)

**What it does**: Loads and processes various document formats

**Supported formats**:
- PDF (with optional image extraction)
- DOCX, DOC
- TXT, MD, CSV
- XLSX, XLS
- PPTX
- HTML
- EML (email)
- Code files (50+ extensions)

**How it works**:
```python
# Automatic loader selection based on file type
loader, known_type, file_ext = get_loader(filename, content_type, file_path)
data = await run_in_executor(executor, loader.load)

# PDF text cleaning
if file_ext == "pdf":
    text_content = clean_text(doc.page_content)
```

### 6. Middleware (`app/middleware.py`)

**What it does**: JWT authentication and authorization

**How it works**:
1. Extract Bearer token from Authorization header
2. Verify JWT signature using JWT_SECRET
3. Check token expiration
4. Attach user payload to request.state.user
5. Allow/deny request based on validation

**Security features**:
- Token expiration validation
- User-level document isolation
- Entity-based access control
- Public access support (when JWT_SECRET not set)

---

## API Endpoints

### POST /embed
**Purpose**: Upload and embed a document

**Request**:
```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "file_id=doc123" \
  -F "entity_id=user456"
```

**Response**:
```json
{
  "status": true,
  "message": "File processed successfully.",
  "file_id": "doc123",
  "filename": "document.pdf",
  "known_type": true
}
```

**How it works**:
1. Validates file upload
2. Saves to temporary directory
3. Loads content using appropriate loader
4. Splits into chunks (CHUNK_SIZE=1500, CHUNK_OVERLAP=100)
5. Generates embeddings for each chunk
6. Stores in vector DB with metadata (file_id, user_id, digest)
7. Returns success/failure status

### POST /query
**Purpose**: Query embeddings by file_id

**Request**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "file_id": "doc123",
    "k": 4,
    "entity_id": "user456"
  }'
```

**Response**:
```json
[
  [
    {
      "page_content": "Relevant text chunk...",
      "metadata": {
        "file_id": "doc123",
        "user_id": "user456",
        "digest": "abc123..."
      }
    },
    0.85
  ]
]
```

**How it works**:
1. Generates embedding for query text
2. Performs similarity search in vector DB
3. Filters by file_id
4. Checks user authorization (user_id or entity_id)
5. Returns top k results with similarity scores
6. Uses LRU cache for query embeddings (performance optimization)

### POST /text
**Purpose**: Extract text from document without creating embeddings

**Request**:
```bash
curl -X POST "http://localhost:8000/text" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "file_id=doc123"
```

**Response**:
```json
{
  "text": "Full extracted text content...",
  "file_id": "doc123",
  "filename": "document.pdf",
  "known_type": true
}
```

**Use case**: Text parsing, preview, or analysis without vector storage

### GET /documents
**Purpose**: Retrieve documents by IDs

**Request**:
```bash
curl -X GET "http://localhost:8000/documents?ids=doc123&ids=doc456" \
  -H "Authorization: Bearer <token>"
```

**Response**:
```json
[
  {
    "page_content": "Document content...",
    "metadata": {
      "file_id": "doc123",
      "user_id": "user456"
    }
  }
]
```

### DELETE /documents
**Purpose**: Delete documents by IDs

**Request**:
```bash
curl -X DELETE "http://localhost:8000/documents" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '["doc123", "doc456"]'
```

**Response**:
```json
{
  "message": "Documents for 2 files deleted successfully"
}
```

### GET /health
**Purpose**: Health check endpoint

**Request**:
```bash
curl -X GET "http://localhost:8000/health"
```

**Response**:
```json
{
  "status": "UP"
}
```

**How it works**: Checks vector database connectivity

---

## Testing Framework

### Promptfoo Integration

**What is Promptfoo?**
Promptfoo is a testing and evaluation framework for LLM applications, providing automated security scanning, quality assurance, and red-team testing.

**Why was it implemented?**
- Automated security testing (OWASP LLM Top 10)
- Quality assurance (factuality, PII protection)
- Performance benchmarking
- Regression prevention
- Compliance validation (NIST AI RMF, MITRE ATLAS)

### Test Suites Overview

#### 1. Baseline Tests (`promptfoo.config.yaml`)
**Purpose**: Quick regression checks

**Coverage**:
- Query response validation
- Secret leak prevention
- Basic guardrails

**Command**:
```bash
npm run test:baseline
# or
npx promptfoo@latest eval --config promptfoo.config.yaml
```

#### 2. Multi-Endpoint Tests (`promptfoo.multi-endpoint.yaml`)
**Purpose**: Test all API endpoints

**Coverage**:
- `/query` endpoint validation
- `/embed` file upload security
- `/text` extraction accuracy

**Command**:
```bash
npm run test:multi-endpoint
```

#### 3. Guardrails Tests (`promptfoo.guardrails.yaml`)
**Purpose**: LLM-graded quality checks

**Coverage**:
- Factuality and hallucination detection
- PII protection
- Toxicity handling
- Business policy compliance
- RBAC enforcement

**Command**:
```bash
npm run test:guardrails
```

**How it works**:
Uses OpenAI GPT-4 to grade responses based on rubrics:
```yaml
assertions:
  - metric: llm-rubric
    value: |
      Grade 1 if response contains no PII, 0 otherwise
```

#### 4. Performance Tests (`promptfoo.performance.yaml`)
**Purpose**: Latency and cost benchmarking

**Coverage**:
- Response time (<2s fast, <5s complex)
- Token/cost efficiency
- Concurrent request handling
- Cache effectiveness
- Large retrieval sets (k=50)

**Command**:
```bash
npm run test:performance
```

#### 5. Dataset-Driven Tests (`promptfoo.dataset-driven.yaml`)
**Purpose**: CSV/YAML-based test cases

**Coverage**:
- Sample queries from CSV
- Edge cases from YAML
- Custom Python graders

**Command**:
```bash
npm run test:dataset
```

**Dataset files**:
- `promptfoo/datasets/sample_queries.csv` - 8 diverse test cases
- `promptfoo/datasets/edge_cases.yaml` - Boundary conditions

#### 6. A/B Comparison Tests (`promptfoo.compare.yaml`)
**Purpose**: Compare different configurations

**Coverage**:
- Production (k=4) vs optimized (k=8) vs conservative (k=2)
- Latency/quality tradeoffs
- Precision vs recall

**Command**:
```bash
npm run test:compare
```

#### 7. Focused Red Team (`promptfoo.redteam.yaml`)
**Purpose**: RAG-specific security testing

**Coverage**:
- Document exfiltration
- Prompt extraction
- SSRF attacks
- Basic jailbreaks

**Command**:
```bash
npm run test:redteam
```

**Plugins tested**:
- `harmful:privacy` - PII leaks
- `harmful:specialized-advice` - Unauthorized advice
- `pii:direct` - Direct PII exposure
- `pii:session` - Session-based leaks
- `pii:social` - Social engineering
- `ssrf` - Server-side request forgery
- `rbac` - Role-based access control

#### 8. Comprehensive Red Team (`promptfoo.redteam-comprehensive.yaml`)
**Purpose**: Full security scan (40+ attack types)

**Coverage**:
- OWASP LLM Top 10
- OWASP API Top 10
- NIST AI RMF
- MITRE ATLAS
- Multi-turn attacks
- Multilingual safety (EN/ES/FR)
- Encoding obfuscation (base64, ROT13, leetspeak)

**Command**:
```bash
npm run test:redteam:full
```

**Attack categories**:
- Injection (prompt, SQL, shell, indirect)
- Authorization (BOLA, BFLA, RBAC)
- Privacy (PII leaks, cross-session, cross-tenant)
- Network (SSRF, debug access)
- Business logic (unauthorized commitments, competitor endorsements)

### Custom Components

#### Custom Providers
**Location**: `promptfoo/providers/`

**Purpose**: Bridge Promptfoo to RAG API endpoints

**Files**:
- `rag_http_target.py` - `/query` endpoint testing
- `rag_embed_target.py` - `/embed` file upload testing
- `rag_text_target.py` - `/text` extraction testing

**Configuration**: Via environment variables
```bash
export PROMPTFOO_RAG_BASE_URL=http://localhost:8000
export PROMPTFOO_RAG_JWT=<token>
export PROMPTFOO_RAG_FILE_ID=testid1
```

#### Custom Graders
**Location**: `promptfoo/graders/rag_quality.py`

**Purpose**: Multi-dimensional quality scoring

**Dimensions**:
- **Relevance**: Query-response keyword alignment
- **Completeness**: Sufficient detail without verbosity
- **Conciseness**: Unique word ratio (low repetition)
- **Factuality**: Hedging detection, fabrication prevention

**Usage**:
```yaml
assertions:
  - metric: python
    value: file://promptfoo/graders/rag_quality.py
```

#### Custom Plugins
**Location**: `promptfoo/plugins/custom-rag-attacks.yaml`

**Purpose**: RAG-specific adversarial tests

**Attack types**:
- Vector similarity exploits
- Embedding dimension manipulation
- Chunking boundary attacks
- Homoglyph filter bypass
- Resource exhaustion
- Metadata injection
- Cross-tenant leaks
- Template extraction

**Command**:
```bash
npm run test:redteam:custom
```

### Test Execution Flow

```
1. Start RAG API
   ↓
2. Set environment variables
   ↓
3. Run test suite
   ↓
4. Promptfoo executes tests
   ↓
5. Custom providers call API
   ↓
6. Assertions validate responses
   ↓
7. Generate HTML/JSON reports
   ↓
8. View results in browser
```

### Viewing Results

**HTML Report**:
```bash
npx promptfoo@latest view
# or
npm run view
```

**Latest Results**:
```bash
npm run view:latest
```

**Output location**: `./promptfoo-output/`

---

## Deployment

### Docker Compose Deployment

**What it does**: Orchestrates RAG API and PostgreSQL containers

**File**: `docker-compose.yaml`

**Services**:
1. **db** - PostgreSQL with pgvector extension
2. **fastapi** - RAG API application

**Command**:
```bash
# Start all services
docker compose up

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Database-Only Deployment

**File**: `db-compose.yaml`

**Command**:
```bash
docker compose -f ./db-compose.yaml up
```

**Use case**: Run database separately, API locally

### API-Only Deployment

**File**: `api-compose.yaml`

**Command**:
```bash
docker compose -f ./api-compose.yaml up
```

**Use case**: Use existing database, deploy only API

### Local Development

**Prerequisites**:
- Python 3.9+
- PostgreSQL with pgvector extension
- Virtual environment (recommended)

**Steps**:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run API
uvicorn main:app --host 0.0.0.0 --port 8000

# Run with auto-reload (development)
uvicorn main:app --reload
```

### AWS RDS Deployment

**Requirements**:
- PostgreSQL 12.16-R2+ / 13.12-R2+ / 14.9-R2+ / 15.4-R2+
- pgvector extension 0.5.0+

**Setup steps**:
1. Create RDS instance/cluster
2. Connect as master user
3. Create dedicated database:
   ```sql
   CREATE DATABASE rag_api;
   ```
4. Create dedicated role:
   ```sql
   CREATE ROLE rag;
   ```
5. Switch to database:
   ```sql
   \c rag_api
   ```
6. Enable vector extension:
   ```sql
   CREATE EXTENSION vector;
   ```
7. Configure connection string in `.env`:
   ```
   DB_HOST=<rds-endpoint>
   DB_PORT=5432
   POSTGRES_DB=rag_api
   POSTGRES_USER=rag
   POSTGRES_PASSWORD=<password>
   ```

### MongoDB Atlas Deployment

**Configuration**:
```env
VECTOR_DB_TYPE=atlas-mongo
ATLAS_MONGO_DB_URI=mongodb+srv://...
COLLECTION_NAME=rag_vectors
ATLAS_SEARCH_INDEX=vector_index
```

**Vector search index** (JSON):
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "file_id",
      "type": "filter"
    }
  ]
}
```

### Production Considerations

**Environment variables**:
- Set `DEBUG_RAG_API=False` in production
- Use `CONSOLE_JSON=True` for cloud logging
- Configure `JWT_SECRET` for authentication
- Set appropriate `CHUNK_SIZE` and `CHUNK_OVERLAP`

**Performance tuning**:
- Adjust `RAG_THREAD_POOL_SIZE` (default: CPU count, max 8)
- Configure `EMBEDDINGS_CHUNK_SIZE` (default: 200)
- Enable `DEBUG_PGVECTOR_QUERIES=True` for query optimization

**Security**:
- Use HTTPS in production
- Rotate JWT secrets regularly
- Implement rate limiting
- Monitor for suspicious queries

---

## Configuration

### Environment Variables Reference

#### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RAG_OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `POSTGRES_DB` | Database name | `mydatabase` |
| `POSTGRES_USER` | Database user | `myuser` |
| `POSTGRES_PASSWORD` | Database password | `mypassword` |

#### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_HOST` | `0.0.0.0` | API host |
| `RAG_PORT` | `8000` | API port |
| `DB_HOST` | `db` | Database host |
| `DB_PORT` | `5432` | Database port |
| `VECTOR_DB_TYPE` | `pgvector` | Vector DB type |
| `COLLECTION_NAME` | `testcollection` | Collection name |
| `CHUNK_SIZE` | `1500` | Text chunk size |
| `CHUNK_OVERLAP` | `100` | Chunk overlap |
| `RAG_UPLOAD_DIR` | `./uploads/` | Upload directory |
| `PDF_EXTRACT_IMAGES` | `False` | Extract PDF images |
| `DEBUG_RAG_API` | `False` | Debug mode |
| `CONSOLE_JSON` | `False` | JSON logging |
| `JWT_SECRET` | (none) | JWT secret key |

#### Embedding Provider Variables

**OpenAI**:
```env
EMBEDDINGS_PROVIDER=openai
RAG_OPENAI_API_KEY=sk-...
RAG_OPENAI_BASEURL=https://api.openai.com/v1
EMBEDDINGS_MODEL=text-embedding-3-small
```

**Azure OpenAI**:
```env
EMBEDDINGS_PROVIDER=azure
RAG_AZURE_OPENAI_API_KEY=...
RAG_AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
RAG_AZURE_OPENAI_API_VERSION=2023-05-15
EMBEDDINGS_MODEL=text-embedding-3-small
```

**HuggingFace**:
```env
EMBEDDINGS_PROVIDER=huggingface
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_TOKEN=hf_...
```

**Ollama**:
```env
EMBEDDINGS_PROVIDER=ollama
EMBEDDINGS_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://ollama:11434
```

**AWS Bedrock**:
```env
EMBEDDINGS_PROVIDER=bedrock
EMBEDDINGS_MODEL=amazon.titan-embed-text-v1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

**Google VertexAI**:
```env
EMBEDDINGS_PROVIDER=vertexai
EMBEDDINGS_MODEL=text-embedding-004
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Configuration Files

#### `.env`
Main configuration file for environment variables

#### `docker-compose.yaml`
Docker orchestration configuration

#### `.promptfoorc.yaml`
Promptfoo global configuration:
- Output paths
- Caching settings
- Default timeouts
- Concurrency limits

---

## Commands Reference

### Application Commands

#### Start API (Local)
```bash
# Basic
uvicorn main:app

# With host and port
uvicorn main:app --host 0.0.0.0 --port 8000

# With auto-reload (development)
uvicorn main:app --reload

# With log level
uvicorn main:app --log-level debug
```

#### Start API (Docker)
```bash
# All services
docker compose up

# Detached mode
docker compose up -d

# Rebuild images
docker compose up --build

# Database only
docker compose -f ./db-compose.yaml up

# API only
docker compose -f ./api-compose.yaml up
```

#### Stop Services
```bash
# Stop containers
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop specific service
docker compose stop fastapi
```

### Testing Commands

#### Baseline Tests
```bash
npm run test:baseline
# or
npx promptfoo@latest eval --config promptfoo.config.yaml
```

#### Multi-Endpoint Tests
```bash
npm run test:multi-endpoint
```

#### Guardrails Tests
```bash
npm run test:guardrails
```

#### Performance Tests
```bash
npm run test:performance
```

#### Dataset-Driven Tests
```bash
npm run test:dataset
```

#### A/B Comparison Tests
```bash
npm run test:compare
```

#### Security Tests
```bash
# Focused red team
npm run test:redteam

# Comprehensive red team
npm run test:redteam:full

# Custom RAG attacks
npm run test:redteam:custom
```

#### Combined Test Suites
```bash
# All evaluation tests
npm run test:all

# Quality tests
npm run test:quality

# Security tests
npm run test:security

# Nightly full suite
npm run test:nightly
```

#### View Results
```bash
# Open web UI
npm run view

# View latest results
npm run view:latest
```

#### Utility Commands
```bash
# Clear cache
npm run cache:clear

# Clean output files
npm run clean
```

### Database Commands

#### Connect to PostgreSQL
```bash
# Via Docker
docker compose exec db psql -U myuser -d mydatabase

# Local
psql -h localhost -p 5433 -U myuser -d mydatabase
```

#### Enable pgvector Extension
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### Check Vector Data
```sql
-- List collections
SELECT DISTINCT cmetadata->>'collection_name' 
FROM langchain_pg_embedding;

-- Count documents by file_id
SELECT cmetadata->>'file_id', COUNT(*) 
FROM langchain_pg_embedding 
GROUP BY cmetadata->>'file_id';

-- View embeddings
SELECT id, cmetadata, document 
FROM langchain_pg_embedding 
LIMIT 10;
```

### Development Commands

#### Install Dependencies
```bash
# Production
pip install -r requirements.txt

# Development (includes testing)
pip install -r test_requirements.txt

# Lite version (minimal dependencies)
pip install -r requirements.lite.txt
```

#### Code Formatting
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Run Tests
```bash
# Unit tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_main.py

# Verbose output
pytest -v
```

### API Testing Commands

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Upload Document
```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "file_id=doc123" \
  -F "entity_id=user456"
```

#### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "file_id": "doc123",
    "k": 4
  }'
```

#### Extract Text
```bash
curl -X POST "http://localhost:8000/text" \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "file_id=doc123"
```

#### Get All IDs
```bash
curl -X GET "http://localhost:8000/ids" \
  -H "Authorization: Bearer <token>"
```

#### Delete Documents
```bash
curl -X DELETE "http://localhost:8000/documents" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '["doc123", "doc456"]'
```

### Monitoring Commands

#### View Logs
```bash
# Docker logs
docker compose logs -f

# Specific service
docker compose logs -f fastapi

# Last 100 lines
docker compose logs --tail=100 fastapi
```

#### Check Container Status
```bash
docker compose ps
```

#### Resource Usage
```bash
docker stats
```

---

## Troubleshooting

### Common Issues

#### Connection Refused
**Symptom**: Cannot connect to API

**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health

# Check Docker containers
docker compose ps

# View logs
docker compose logs fastapi
```

#### Database Connection Error
**Symptom**: `psycopg2.OperationalError`

**Solution**:
```bash
# Check database is running
docker compose ps db

# Verify connection string
echo $DB_HOST $DB_PORT $POSTGRES_DB

# Test connection
docker compose exec db psql -U myuser -d mydatabase
```

#### Embedding Provider Error
**Symptom**: `Invalid API key` or `Provider not found`

**Solution**:
```bash
# Check environment variables
echo $EMBEDDINGS_PROVIDER
echo $RAG_OPENAI_API_KEY

# Verify .env file
cat .env | grep EMBEDDINGS
```

#### File Upload Error
**Symptom**: `Failed to save uploaded file`

**Solution**:
```bash
# Check upload directory exists
ls -la ./uploads/

# Check permissions
chmod 755 ./uploads/

# Check disk space
df -h
```

#### JWT Authentication Error
**Symptom**: `401 Unauthorized`

**Solution**:
```bash
# Verify JWT_SECRET is set
echo $JWT_SECRET

# Check token format
# Should be: Authorization: Bearer <token>

# Verify token expiration
# Use jwt.io to decode token
```

---

## Best Practices

### Development
1. Use virtual environments
2. Enable debug mode locally (`DEBUG_RAG_API=True`)
3. Use auto-reload during development
4. Run tests before committing
5. Use pre-commit hooks for code formatting

### Production
1. Disable debug mode (`DEBUG_RAG_API=False`)
2. Enable JSON logging (`CONSOLE_JSON=True`)
3. Set strong JWT secrets
4. Use HTTPS
5. Implement rate limiting
6. Monitor resource usage
7. Regular security scans
8. Backup vector database

### Testing
1. Start with baseline tests
2. Run performance tests before security tests
3. Use dataset-driven tests for regression tracking
4. Run comprehensive red team tests on schedule
5. Review HTML reports for failures
6. Track trends over time

### Security
1. Rotate JWT secrets regularly
2. Validate all file uploads
3. Sanitize user inputs
4. Implement RBAC
5. Monitor for suspicious queries
6. Use entity_id for multi-tenancy
7. Regular security audits

---

## Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [pgvector Docs](https://github.com/pgvector/pgvector)
- [Promptfoo Docs](https://www.promptfoo.dev/docs/)

### Related Projects
- [LibreChat](https://librechat.ai) - Primary integration target
- [Unstructured](https://unstructured.io/) - Document processing
- [Sentence Transformers](https://www.sbert.net/) - HuggingFace embeddings

### Support
- GitHub Issues: [Report bugs or request features]
- Documentation: [README.md](./README.md)
- Testing Guide: [promptfoo/README.md](./promptfoo/README.md)

---

## Appendix

### File Structure
```
rag_api/
├── app/
│   ├── routes/
│   │   ├── document_routes.py    # API endpoints
│   │   └── pgvector_routes.py    # Debug routes
│   ├── services/
│   │   ├── vector_store/         # Vector DB implementations
│   │   ├── database.py           # PostgreSQL connection
│   │   └── mongo_client.py       # MongoDB connection
│   ├── utils/
│   │   ├── document_loader.py    # File processing
│   │   └── health.py             # Health checks
│   ├── config.py                 # Configuration
│   ├── middleware.py             # JWT auth
│   └── models.py                 # Pydantic models
├── promptfoo/
│   ├── datasets/                 # Test datasets
│   ├── graders/                  # Custom graders
│   ├── plugins/                  # Custom plugins
│   └── providers/                # Custom providers
├── tests/                        # Unit tests
├── main.py                       # Application entry
├── docker-compose.yaml           # Docker orchestration
├── requirements.txt              # Python dependencies
├── package.json                  # NPM scripts
└── .env                          # Environment config
```

### Glossary

- **RAG**: Retrieval-Augmented Generation
- **Embedding**: Vector representation of text
- **Vector Store**: Database optimized for similarity search
- **pgvector**: PostgreSQL extension for vector operations
- **Chunk**: Text segment for embedding
- **file_id**: Unique identifier for documents
- **entity_id**: User/tenant identifier
- **JWT**: JSON Web Token for authentication
- **LLM**: Large Language Model
- **OWASP**: Open Web Application Security Project

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: RAG API Team
