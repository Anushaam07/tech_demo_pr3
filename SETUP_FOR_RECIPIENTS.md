# Quick Setup Guide for Recipients

This guide is for someone who received this project as a ZIP file.

## 🚀 Quick Start (5-Minute Checklist)

```powershell
# 1. Extract ZIP and navigate
cd C:\YourPath\rag_api

# 2. Install dependencies
npm install

# 3. Create .env file with your Azure credentials
# (Copy template from Step 2 below)

# 4. Build and start services
docker compose build
docker compose up -d
Start-Sleep -Seconds 10

# 5. Upload test documents (CRITICAL!)
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/sample-policy.txt" `
  -F "file_id=testid1" `
  -F "entity_id=test-user"

curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/product-specs.txt" `
  -F "file_id=testid2" `
  -F "entity_id=test-user"

# 6. Run tests
npm run test:baseline
npm run view
```

**⚠️ Most Common Mistake:** Forgetting to upload test documents (step 5) before running tests. All tests will fail if documents aren't uploaded!

---

## Prerequisites

Before starting, ensure you have:

1. **Docker Desktop** - Download from https://www.docker.com/products/docker-desktop
   - After install, verify: `docker --version`
   
2. **Node.js 18+** - Download from https://nodejs.org/
   - After install, verify: `node --version` and `npm --version`
   
3. **Azure OpenAI Access** - You need:
   - Embeddings endpoint (text-embedding-3-small)
   - Chat endpoint (gpt-4o-mini)
   - API keys for both

## Step-by-Step Setup

### 1. Extract the ZIP
Extract to a clean directory, for example:
```
C:\Projects\rag_api
```

### 2. Configure Environment Variables

1. Create a `.env` file in the root directory
2. Copy this template and fill in your Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration for Embeddings
EMBEDDINGS_PROVIDER=azure
EMBEDDINGS_MODEL=text-embedding-3-small
AZURE_OPENAI_API_KEY=your_embeddings_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
RAG_AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure OpenAI Configuration for Chat (GPT-4o-mini)
AZURE_CHAT_API_KEY=your_chat_api_key_here
AZURE_CHAT_ENDPOINT=https://your-chat-endpoint.openai.azure.com
AZURE_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_CHAT_API_VERSION=2024-12-01-preview

# Database Configuration (Leave as-is for Docker)
DB_HOST=db
POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword

# Vector Database
VECTOR_DB_TYPE=pgvector
COLLECTION_NAME=testcollection
```

**Important:** Replace `your_*_here` with your actual Azure credentials.

### 3. Install Node Dependencies
```powershell
npm install
```

This installs Promptfoo and all testing dependencies (~30 seconds).

### 4. Start Docker Services
```powershell
# Build containers
docker compose build

# Start services in background
docker compose up -d

# Wait for services to initialize
Start-Sleep -Seconds 10
```

### 5. Verify Services Are Running
```powershell
# Check Docker containers
docker compose ps

# Check API health
curl http://localhost:8000/health
```

Expected response: `{"status":"UP"}`

### 6. Upload Test Documents (⚠️ CRITICAL STEP - DO THIS BEFORE TESTING!)

**Why this matters:** All Promptfoo tests reference specific documents by `file_id`. Without uploading these files first, **every test will fail** with empty results.

#### Required Test Files:

The project includes two test documents in `test-documents/`:

1. **`sample-policy.txt`** (file_id: `testid1`)
   - Company policies, remote work rules, vacation policies
   - Used by: baseline tests, guardrails tests, prompt optimization

2. **`product-specs.txt`** (file_id: `testid2`)
   - CloudSync Pro product specifications
   - Used by: multi-endpoint tests, dataset tests

#### Upload Commands:

```powershell
# Upload policy document (testid1)
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/sample-policy.txt" `
  -F "file_id=testid1" `
  -F "entity_id=test-user"

# Upload product specs (testid2)
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/product-specs.txt" `
  -F "file_id=testid2" `
  -F "entity_id=test-user"
```

**Expected response for each:**
```json
{
  "message": "File uploaded successfully",
  "file_id": "testid1",
  "chunks_created": 12
}
```

#### Verify Upload Worked:

```powershell
# Test query against uploaded policy document
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{\"query\":\"What is the remote work policy?\",\"entity_id\":\"test-user\",\"file_id\":\"testid1\",\"k\":2}'
```

**Expected:** JSON response with 2 chunks containing policy text.

**If you get empty results `[]`:**
- Documents weren't uploaded successfully
- Check API logs: `docker compose logs fastapi`
- Re-run upload commands above

### 7. Run Promptfoo Tests

#### Understanding How Tests Work:

Each `npm run test:*` command executes a Promptfoo YAML configuration:

```powershell
npm run test:baseline
# ↓ Runs this:
promptfoo eval --config promptfoo.config.yaml
```

The YAML file defines:
- **Target API endpoint** (e.g., `/query` or `/query_with_summary`)
- **Test cases** with sample queries
- **Assertions** to validate responses

#### Quick Start Tests (~30 seconds total):

```powershell
# Test 1: Core functionality (3 tests, ~1s)
npm run test:baseline
# Uses: promptfoo.config.yaml
# Tests: Document summarization, secret prevention, policy compliance

# Test 2: Quality guardrails (9 tests, ~2s)
npm run test:guardrails
# Uses: promptfoo.guardrails.yaml
# Tests: PII prevention, factual accuracy, toxicity detection

# Test 3: LLM output quality (9 tests, ~10s)
npm run test:llm-quality
# Uses: promptfoo.llm-quality.yaml
# Tests: Hallucination detection, citation quality, relevance
```

#### View Results:

```powershell
npm run view
```

Opens browser at http://localhost:15500 with interactive test results:
- ✅ Pass/fail status for each test
- 📊 Token usage and costs
- ⏱️ Performance metrics
- 🔍 Side-by-side comparison of runs

#### All Functional Tests (~35 seconds total):

```powershell
npm run test:baseline            # 3 tests, ~1s
npm run test:multi-endpoint       # 2 tests, ~1s
npm run test:dataset              # 4 tests, ~2s
npm run test:performance          # 6 tests, ~2s
npm run test:compare              # 12 tests, ~3s (A/B testing)
npm run test:guardrails           # 9 tests, ~2s
npm run test:llm-quality          # 9 tests, ~10s
npm run test:prompt-optimization  # 8 tests, ~15s (prompt A/B testing)
```

**Expected results:** 100% pass rate (53/53 tests)

### 8. Optional: Security Tests (Red Team)

⚠️ **Warning:** These tests take 5-10+ minutes and may timeout on slow networks.

```powershell
# RAG endpoint security (25-40 tests, ~5-10 minutes)
npm run test:redteam
# Uses: promptfoo.redteam.yaml
# Tests: Prompt injection, data exfiltration, SSRF attacks

# LLM endpoint security (12-18 tests, ~2-3 minutes)
npm run test:redteam:llm
# Uses: promptfoo.redteam-llm.yaml
# Tests: Jailbreak attempts, system prompt injection, hallucination exploitation
```

**Expected:** 75-85% pass rate (adversarial tests are meant to probe weaknesses)

**If tests timeout:**
- Skip red team tests initially
- Or reduce test count: Edit `promptfoo.redteam.yaml` → change `numTests: 5` to `numTests: 3`
- See "Common Issues" below

## Common Issues

### Issue 1: Tests Return Empty Results
**Cause:** Test documents not uploaded

**Solution:**
```powershell
# Re-upload test documents (see Step 6 above)
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/sample-policy.txt" `
  -F "file_id=testid1" `
  -F "entity_id=test-user"
```

### Issue 2: Red Team Tests Timeout
**Cause:** Slow network, VPN, or corporate firewall

**Solution:** Skip red team tests or reduce test count:

Edit `promptfoo.redteam.yaml`:
```yaml
redteam:
  numTests: 3  # Reduced from 5 (faster)
```

Or increase timeout:
```yaml
defaultTest:
  options:
    timeout: 60000  # 60 seconds instead of 30
```

### Issue 3: SSL Certificate Errors
**Symptom:** Tests show SSL errors but still pass

**Explanation:** This is expected on corporate networks. The app includes SSL workarounds.

**Action:** If tests **pass**, ignore SSL errors. If tests **fail**, contact IT for corporate CA certificate.

### Issue 4: Docker Build Fails
**Symptom:** SSL errors during `docker compose build`

**Solution:**
```powershell
docker compose build --no-cache
```

### Issue 5: API Not Responding
**Symptom:** `curl http://localhost:8000/health` fails

**Solution:**
```powershell
# Check container status
docker compose ps

# View API logs for errors
docker compose logs fastapi

# Restart services
docker compose restart
```

## Complete Setup Workflow Summary

Here's the **exact order** to set everything up from scratch:

### 1️⃣ Initial Setup (One Time)
```powershell
# Navigate to extracted folder
cd D:\YourPath\rag_api  # Change to your path

# Install Node dependencies
npm install

# Build Docker images
docker compose build
```

### 2️⃣ Start Services (Every Time)
```powershell
# Start containers in background
docker compose up -d

# Wait for startup
Start-Sleep -Seconds 10

# Verify API is running
curl http://localhost:8000/health
```

**Expected:** `{"status":"UP"}`

### 3️⃣ Upload Test Data (One Time)
```powershell
# Upload policy document
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/sample-policy.txt" `
  -F "file_id=testid1" `
  -F "entity_id=test-user"

# Upload product specs
curl -X POST "http://localhost:8000/upload" `
  -F "file=@test-documents/product-specs.txt" `
  -F "file_id=testid2" `
  -F "entity_id=test-user"

# Verify upload worked
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{\"query\":\"remote work policy\",\"entity_id\":\"test-user\",\"file_id\":\"testid1\",\"k\":1}'
```

### 4️⃣ Run Tests (Any Time)
```powershell
# Quick validation
npm run test:baseline
npm run test:guardrails

# View results
npm run view
```

### 5️⃣ Stop Services (When Done)
```powershell
docker compose down
```

## Understanding Promptfoo YAML Configs

All test configurations are in the root directory with naming pattern `promptfoo.*.yaml`:

### How They Work:

1. **`targets:`** - Defines which API endpoint to test
   ```yaml
   targets:
     - id: http
       config:
         url: http://127.0.0.1:8000/query  # The endpoint
         body:
           entity_id: test-user  # Which documents to query
           file_id: testid1      # Specific document
   ```

2. **`tests:`** - Defines test cases
   ```yaml
   tests:
     - name: "Test remote work policy"
       vars:
         user_query: "What is the remote work policy?"
       assertions:
         - type: contains
           value: "remote"  # Response must contain "remote"
   ```

3. **Running a config:**
   ```powershell
   # Run specific config
   promptfoo eval --config promptfoo.baseline.yaml
   
   # Or use npm shortcuts
   npm run test:baseline
   ```

### Customizing Tests:

**Example: Add your own test to `promptfoo.config.yaml`**

```yaml
tests:
  - name: "My custom test"
    vars:
      user_query: "Your question here"
      file_id: testid1
      entity_id: test-user
    assertions:
      - type: contains
        value: "expected text in response"
```

Then run: `npm run test:baseline`

## Next Steps

Once everything works:

1. **Explore the code** - Check `app/routes/` for API endpoints
2. **Read the docs** - See `PROMPTFOO_SETUP.md` for detailed testing guide
3. **Customize tests** - Modify `promptfoo.*.yaml` files for your use case
4. **Try the summarization endpoint** - POST to `/query_with_summary`

## Getting Help

If you encounter issues:

1. Check `PROMPTFOO_SETUP.md` → "Troubleshooting" section
2. View container logs: `docker compose logs fastapi`
3. Check Promptfoo logs: `.promptfoo/logs/`
4. Verify `.env` has correct Azure credentials
5. Contact the person who shared this project

## Stopping Services

When done testing:
```powershell
docker compose down
```

To start again later:
```powershell
docker compose up -d
```

---

**Setup Time:** ~10 minutes  
**Test Time:** ~30 seconds (quick tests) or ~35 seconds (all except red team)  
**Red Team:** ~5-10 minutes (optional, may timeout on slow networks)

**Last Updated:** November 24, 2025
