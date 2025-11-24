# ID-based RAG FastAPI

## Overview
This project integrates Langchain with FastAPI in an Asynchronous, Scalable manner, providing a framework for document indexing and retrieval, using PostgreSQL/pgvector.

Files are organized into embeddings by `file_id`. The primary use case is for integration with [LibreChat](https://librechat.ai), but this simple API can be used for any ID-based use case.

The main reason to use the ID approach is to work with embeddings on a file-level. This makes for targeted queries when combined with file metadata stored in a database, such as is done by LibreChat.

The API will evolve over time to employ different querying/re-ranking methods, embedding models, and vector stores.

## Features
- **Document Management**: Methods for adding, retrieving, and deleting documents.
- **Vector Store**: Utilizes Langchain's vector store for efficient document retrieval.
- **Asynchronous Support**: Offers async operations for enhanced performance.

## Setup

### Getting Started

- **Configure `.env` file based on [section below](#environment-variables)**
- **Setup pgvector database:**
  - Run an existing PSQL/PGVector setup, or,
  - Docker: `docker compose up` (also starts RAG API)
    - or, use docker just for DB: `docker compose -f ./db-compose.yaml up`
- **Run API**:
  - Docker: `docker compose up` (also starts PSQL/pgvector)
    - or, use docker just for RAG API: `docker compose -f ./api-compose.yaml up`
  - Local:
    - Make sure to setup `DB_HOST` to the correct database hostname
    - Run the following commands (preferably in a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/))
```bash
pip install -r requirements.txt
uvicorn main:app
```

### Environment Variables

The following environment variables are required to run the application:

- `RAG_OPENAI_API_KEY`: The API key for OpenAI API Embeddings (if using default settings).
    - Note: `OPENAI_API_KEY` will work but `RAG_OPENAI_API_KEY` will override it in order to not conflict with LibreChat setting.
- `RAG_OPENAI_BASEURL`: (Optional) The base URL for your OpenAI API Embeddings
- `RAG_OPENAI_PROXY`: (Optional) Proxy for OpenAI API Embeddings
    - Note: When using with LibreChat, you can also set `HTTP_PROXY` and `HTTPS_PROXY` environment variables in the `docker-compose.override.yml` file (see [Proxy Configuration](#proxy-configuration) section below)
- `VECTOR_DB_TYPE`: (Optional) select vector database type, default to `pgvector`.
- `POSTGRES_USE_UNIX_SOCKET`: (Optional) Set to "True" when connecting to the PostgreSQL database server with Unix Socket.
- `POSTGRES_DB`: (Optional) The name of the PostgreSQL database, used when `VECTOR_DB_TYPE=pgvector`.
- `POSTGRES_USER`: (Optional) The username for connecting to the PostgreSQL database.
- `POSTGRES_PASSWORD`: (Optional) The password for connecting to the PostgreSQL database.
- `DB_HOST`: (Optional) The hostname or IP address of the PostgreSQL database server.
- `DB_PORT`: (Optional) The port number of the PostgreSQL database server.
- `RAG_HOST`: (Optional) The hostname or IP address where the API server will run. Defaults to "0.0.0.0"
- `RAG_PORT`: (Optional) The port number where the API server will run. Defaults to port 8000.
- `JWT_SECRET`: (Optional) The secret key used for verifying JWT tokens for requests.
  - The secret is only used for verification. This basic approach assumes a signed JWT from elsewhere.
  - Omit to run API without requiring authentication

- `COLLECTION_NAME`: (Optional) The name of the collection in the vector store. Default value is "testcollection".
- `CHUNK_SIZE`: (Optional) The size of the chunks for text processing. Default value is "1500".
- `CHUNK_OVERLAP`: (Optional) The overlap between chunks during text processing. Default value is "100".
- `RAG_UPLOAD_DIR`: (Optional) The directory where uploaded files are stored. Default value is "./uploads/".
- `PDF_EXTRACT_IMAGES`: (Optional) A boolean value indicating whether to extract images from PDF files. Default value is "False".
- `DEBUG_RAG_API`: (Optional) Set to "True" to show more verbose logging output in the server console, and to enable postgresql database routes
- `DEBUG_PGVECTOR_QUERIES`: (Optional) Set to "True" to enable detailed PostgreSQL query logging for pgvector operations. Useful for debugging performance issues with vector database queries.
- `CONSOLE_JSON`: (Optional) Set to "True" to log as json for Cloud Logging aggregations
- `EMBEDDINGS_PROVIDER`: (Optional) either "openai", "bedrock", "azure", "huggingface", "huggingfacetei", "google_genai", "vertexai", or "ollama", where "huggingface" uses sentence_transformers; defaults to "openai"
- `EMBEDDINGS_MODEL`: (Optional) Set a valid embeddings model to use from the configured provider.
    - **Defaults**
    - openai: "text-embedding-3-small"
    - azure: "text-embedding-3-small" (will be used as your Azure Deployment)
    - huggingface: "sentence-transformers/all-MiniLM-L6-v2"
    - huggingfacetei: "http://huggingfacetei:3000". Hugging Face TEI uses model defined on TEI service launch.
    - vertexai: "text-embedding-004"
    - ollama: "nomic-embed-text"
    - bedrock: "amazon.titan-embed-text-v1"
    - google_genai: "gemini-embedding-001"
- `RAG_AZURE_OPENAI_API_VERSION`: (Optional) Default is `2023-05-15`. The version of the Azure OpenAI API.
- `RAG_AZURE_OPENAI_API_KEY`: (Optional) The API key for Azure OpenAI service.
    - Note: `AZURE_OPENAI_API_KEY` will work but `RAG_AZURE_OPENAI_API_KEY` will override it in order to not conflict with LibreChat setting.
- `RAG_AZURE_OPENAI_ENDPOINT`: (Optional) The endpoint URL for Azure OpenAI service, including the resource.
    - Example: `https://YOUR_RESOURCE_NAME.openai.azure.com`.
    - Note: `AZURE_OPENAI_ENDPOINT` will work but `RAG_AZURE_OPENAI_ENDPOINT` will override it in order to not conflict with LibreChat setting.
- `HF_TOKEN`: (Optional) if needed for `huggingface` option.
- `OLLAMA_BASE_URL`: (Optional) defaults to `http://ollama:11434`.
- `ATLAS_SEARCH_INDEX`: (Optional) the name of the vector search index if using Atlas MongoDB, defaults to `vector_index`
- `MONGO_VECTOR_COLLECTION`: Deprecated for MongoDB, please use `ATLAS_SEARCH_INDEX` and `COLLECTION_NAME`
- `AWS_DEFAULT_REGION`: (Optional) defaults to `us-east-1`
- `AWS_ACCESS_KEY_ID`: (Optional) needed for bedrock embeddings
- `AWS_SECRET_ACCESS_KEY`: (Optional) needed for bedrock embeddings
- `GOOGLE_API_KEY`, `GOOGLE_KEY`, `RAG_GOOGLE_API_KEY`: (Optional) Google API key for Google GenAI embeddings. Priority order: RAG_GOOGLE_API_KEY > GOOGLE_KEY > GOOGLE_API_KEY
- `AWS_SESSION_TOKEN`: (Optional) may be needed for bedrock embeddings
- `GOOGLE_APPLICATION_CREDENTIALS`: (Optional) needed for Google VertexAI embeddings. This should be a path to a service account credential file in JSON format, as accepted by [langchain](https://python.langchain.com/api_reference/google_vertexai/index.html)
- `RAG_CHECK_EMBEDDING_CTX_LENGTH` (Optional) Default is true, disabling this will send raw input to the embedder, use this for custom embedding models.

Make sure to set these environment variables before running the application. You can set them in a `.env` file or as system environment variables.

### Promptfoo-based Testing & Security

This project includes comprehensive [Promptfoo](https://www.promptfoo.dev/) integration for automated testing, security scanning, and quality assurance. Five test suites cover everything from basic regressions to full red-team assessments.

#### Quick Start

1. **Install Promptfoo**
   ```bash
   npm install --global promptfoo@latest
   # or run ad-hoc with npx promptfoo@latest ...
   ```

2. **Start the RAG API** (ensure database is running)
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Configure environment variables**
   ```powershell
   $env:PROMPTFOO_RAG_BASE_URL = "http://127.0.0.1:8000"
   $env:PROMPTFOO_RAG_JWT = "<your_jwt_token>"  # if auth enabled
   $env:OPENAI_API_KEY = "<your_key>"           # for LLM-graded tests
   ```

4. **Run test suites**
   ```bash
   # Quick baseline regression tests
   npx promptfoo@latest eval --config promptfoo.config.yaml
   
   # Test all API endpoints (/query, /embed, /text)
   npx promptfoo@latest eval --config promptfoo.multi-endpoint.yaml
   
   # Advanced guardrails (factuality, PII, policy compliance)
   npx promptfoo@latest eval --config promptfoo.guardrails.yaml
   
   # Focused RAG security red team
   npx promptfoo@latest redteam run --config promptfoo.redteam.yaml
   
   # Comprehensive security scan (40+ attack types)
   npx promptfoo@latest redteam run --config promptfoo.redteam-comprehensive.yaml
   ```

5. **View results**
   - HTML reports are auto-generated (path shown in terminal)
   - Or run: `npx promptfoo@latest view`

#### Test Suites Overview

| Config File | Purpose | Coverage |
|-------------|---------|----------|
| `promptfoo.config.yaml` | Baseline regressions | Basic query validation, leak prevention |
| `promptfoo.multi-endpoint.yaml` | Multi-endpoint tests | `/query`, `/embed`, `/text` endpoints |
| `promptfoo.guardrails.yaml` | Quality & policy | LLM-graded factuality, PII, toxicity, RBAC |
| `promptfoo.performance.yaml` | Performance & load | Latency, cost, concurrency, caching |
| `promptfoo.dataset-driven.yaml` | Data-driven testing | CSV/YAML datasets, custom graders |
| `promptfoo.compare.yaml` | A/B comparison | Compare different RAG configurations |
| `promptfoo.redteam.yaml` | RAG security | 7 plugins, RAG-specific attacks |
| `promptfoo.redteam-comprehensive.yaml` | Full red team | 40+ plugins, OWASP/NIST/MITRE compliance |

#### NPM Scripts (Convenience Commands)

```bash
# Quality & Regression Tests
npm run test:baseline          # Quick baseline checks
npm run test:multi-endpoint    # All endpoint tests
npm run test:guardrails        # LLM-graded quality
npm run test:quality           # All quality tests combined

# Performance & Data
npm run test:performance       # Latency, cost, concurrency
npm run test:dataset           # CSV-driven test cases
npm run test:compare           # A/B config comparison

# Security Tests
npm run test:redteam           # Focused red team
npm run test:redteam:full      # Comprehensive scan
npm run test:redteam:custom    # Custom RAG attack plugin
npm run test:security          # All security tests

# Full Suites
npm run test:all               # All eval tests
npm run test:nightly           # Complete nightly suite

# Utilities
npm run view                   # Open web UI viewer
npm run view:latest            # View latest results
npm run cache:clear            # Clear Promptfoo cache
npm run clean                  # Remove output files
```

#### Custom Providers

Three Python providers enable endpoint-specific testing:
- `promptfoo/providers/rag_http_target.py` – `/query` endpoint
- `promptfoo/providers/rag_embed_target.py` – `/embed` file uploads
- `promptfoo/providers/rag_text_target.py` – `/text` extraction

All providers are configurable via environment variables (no code changes needed).

#### Security Coverage

Red team suites test for:
- **RAG-specific**: Document exfiltration, vector poisoning, prompt extraction, embedding attacks
- **Authorization**: BOLA/BFLA, RBAC, cross-session leaks, cross-tenant isolation
- **Injection**: Prompt, SQL, shell, indirect injection
- **Privacy**: PII leaks (direct, session, social engineering, API/DB)
- **Network**: SSRF, debug access
- **Business logic**: Unauthorized commitments, competitor endorsements
- **Compliance**: OWASP LLM/API Top 10, NIST AI RMF, MITRE ATLAS

#### Advanced Features

**Custom Graders**: Python-based quality scoring for RAG responses
- `promptfoo/graders/rag_quality.py` – Multi-dimensional quality analysis (relevance, completeness, conciseness, factuality)

**Custom Plugins**: RAG-specific attack patterns
- `promptfoo/plugins/custom-rag-attacks.yaml` – Vector database exploits, semantic collision, metadata manipulation

**Dataset Testing**: CSV/YAML-driven test cases
- `promptfoo/datasets/sample_queries.csv` – Sample query variations
- `promptfoo/datasets/edge_cases.yaml` – Boundary conditions and error scenarios

**Global Configuration**: `.promptfoorc.yaml` sets defaults for:
- Output paths, caching, telemetry preferences
- Default timeouts, concurrency limits
- Environment variable presets

#### Documentation

See [`promptfoo/README.md`](./promptfoo/README.md) for:
- Detailed test suite descriptions
- Environment variable reference
- Extending tests with custom cases/graders
- Troubleshooting guide
- Best practices### Use Atlas MongoDB as Vector Database

Instead of using the default pgvector, we could use [Atlas MongoDB](https://www.mongodb.com/products/platform/atlas-vector-search) as the vector database. To do so, set the following environment variables

```env
VECTOR_DB_TYPE=atlas-mongo
ATLAS_MONGO_DB_URI=<mongodb+srv://...>
COLLECTION_NAME=<vector collection>
ATLAS_SEARCH_INDEX=<vector search index>
```

The `ATLAS_MONGO_DB_URI` could be the same or different from what is used by LibreChat. Even if it is the same, the `$COLLECTION_NAME` collection needs to be a completely new one, separate from all collections used by LibreChat. In addition,  create a vector search index for collection above (remember to assign `$ATLAS_SEARCH_INDEX`) with the following json:

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

Follow one of the [four documented methods](https://www.mongodb.com/docs/atlas/atlas-vector-search/create-index/#procedure) to create the vector index.


### Proxy Configuration

When using the RAG API with LibreChat and you need to configure proxy settings, you can set the `HTTP_PROXY` and `HTTPS_PROXY` environment variables in the [`docker-compose.override.yml`](https://www.librechat.ai/docs/configuration/docker_override) file (from the LibreChat repository):

```yaml
rag_api:
    environment:
        - HTTP_PROXY=<your-proxy>
        - HTTPS_PROXY=<your-proxy>
```

This configuration will ensure that all HTTP/HTTPS requests from the RAG API container are routed through your specified proxy server.


### Cloud Installation Settings:

#### AWS:
Make sure your RDS Postgres instance adheres to this requirement:

`The pgvector extension version 0.5.0 is available on database instances in Amazon RDS running PostgreSQL 15.4-R2 and higher, 14.9-R2 and higher, 13.12-R2 and higher, and 12.16-R2 and higher in all applicable AWS Regions, including the AWS GovCloud (US) Regions.`

In order to setup RDS Postgres with RAG API, you can follow these steps:

* Create a RDS Instance/Cluster using the provided [AWS Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CreateDBInstance.html).
* Login to the RDS Cluster using the Endpoint connection string from the RDS Console or from your IaC Solution output.
* The login is via the *Master User*.
* Create a dedicated database for rag_api:
``` create database rag_api;```.
* Create a dedicated user\role for that database:
``` create role rag;```

* Switch to the database you just created: ```\c rag_api```
* Enable the Vector extension: ```create extension vector;```
* Use the documentation provided above to set up the connection string to the RDS Postgres Instance\Cluster.

Notes:
  * Even though you're logging with a Master user, it doesn't have all the super user privileges, that's why we cannot use the command: ```create role x with superuser;```
  * If you do not enable the extension, rag_api service will throw an error that it cannot create the extension due to the note above.

### Dev notes:

#### Installing pre-commit formatter

Run the following commands to install pre-commit formatter, which uses [black](https://github.com/psf/black) code formatter:

```bash
pip install pre-commit
pre-commit install
```

