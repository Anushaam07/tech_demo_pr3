# Testing Guide for LLM Summarization Feature

## Prerequisites
1. Update your `.env` file with Azure Chat credentials:
```bash
# AZURE_CHAT_API_KEY=your azure api key
# AZURE_CHAT_ENDPOINT=https://ai-40mini.cognitiveservices.azure.com/
AZURE_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_CHAT_API_VERSION=2024-12-01-preview
```

2. Start Docker Desktop

## Step-by-Step Testing

### 1. Rebuild and Start Services
```bash

# Rebuild with new code
docker compose build fastapi

# Start services
docker compose up -d

# Wait for startup
Start-Sleep -Seconds 10

# Verify health
curl http://localhost:8000/health
```

### 2. Manual Test - Basic Query
```bash
$body = @{
    query = "What are the main topics?"
    entity_id = "test-user"
    file_id = "testid1"
    k = 4
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/query_with_summary" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Expected Response:**
```json
{
  "query": "What are the main topics?",
  "summary": "[AI-generated summary based on your documents]",
  "retrieved_chunks": [...],
  "metadata": {
    "model": "gpt-4o-mini",
    "retrieval_latency_ms": 45.2,
    "llm_latency_ms": 892.5,
    "total_latency_ms": 937.7,
    "chunks_retrieved": 4,
    "tokens_total": 510,
    "cost_usd": 0.000115
  }
}
```

### 3. Test Hallucination Detection
```bash
# Query for information NOT in the documents
$body = @{
    query = "What is the CEO's favorite color?"
    entity_id = "test-user"
    file_id = "testid1"
    k = 4
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/query_with_summary" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# Check if it properly says "I don't have that information"
$response.summary
```

**Expected:** Should NOT hallucinate an answer, should say it doesn't know.

### 4. Test Custom System Prompt
```bash
$body = @{
    query = "Summarize the key points"
    entity_id = "test-user"
    file_id = "testid1"
    k = 4
    system_prompt = "You are a concise assistant. Answer in 2 sentences max."
    temperature = 0.3
    max_tokens = 100
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/query_with_summary" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response.summary
```

**Expected:** Very concise answer (2 sentences)

### 5. Run Promptfoo LLM Quality Tests
```bash
npm run test:llm-quality
```

**Expected Output:**
```
Duration: ~10s (concurrency: 4)
Successes: 8-9
Failures: 0-1
Pass Rate: 89-100%
```

**Tests validated:**
- ✅ Answers grounded in context
- ✅ No hallucination for missing info
- ✅ Retrieved chunks are used
- ✅ Answers are relevant
- ✅ Conciseness without verbosity
- ✅ Proper metadata tracking
- ✅ Acceptable latency (<5s)
- ✅ Reasonable cost (<$0.001/query)

### 6. Run Prompt Optimization Tests
```bash
npm run test:prompt-optimization
```

**Expected Output:**
```
Duration: ~15s (concurrency: 4)
Tests: 24 (8 tests × 3 prompt variants)
```

**Compares:**
- Conservative prompt (temp=0.3)
- Balanced prompt (temp=0.7)
- Detailed with citations (temp=0.5)

### 7. View Results in Web UI
```bash
npm run view
```

Opens browser at http://localhost:15500 showing:
- Side-by-side comparison of all 3 prompt variants
- Token usage per variant
- Cost comparison
- LLM-graded quality scores
- Latency metrics

### 8. Check Token Usage & Cost
```bash
# Get detailed metadata from response
$response.metadata | ConvertTo-Json -Depth 10
```

**Should show:**
```json
{
  "model": "gpt-4o-mini",
  "retrieval_latency_ms": 45.2,
  "llm_latency_ms": 892.5,
  "total_latency_ms": 937.7,
  "chunks_retrieved": 4,
  "tokens_prompt": 423,
  "tokens_completion": 87,
  "tokens_total": 510,
  "cost_usd": 0.000115,
  "temperature": 0.7,
  "max_tokens": 500
}
```

## Troubleshooting

### Issue: "Azure Chat OpenAI not configured"
**Fix:** Ensure `.env` has:
```bash
AZURE_CHAT_API_KEY=your azure api key
AZURE_CHAT_ENDPOINT=https://ai-40mini.cognitiveservices.azure.com/
AZURE_CHAT_DEPLOYMENT=gpt-4o-mini
```

### Issue: Import errors in logs
**Fix:** Rebuild container:
```bash
docker compose build --no-cache fastapi
docker compose up -d
```

### Issue: LLM tests fail
**Symptom:** Assertions fail in promptfoo tests

**Check:**
1. API is returning summaries: `$response.summary`
2. Chunks are retrieved: `$response.retrieved_chunks.Count`
3. Metadata is present: `$response.metadata`

### Issue: High latency (>10s)
**Normal:** First request may be slow (model loading)
**Workaround:** Run warmup request first

### Issue: Hallucination still occurs
**Expected:** Some edge cases may fail - review with:
```bash
promptfoo view
# Click on failing test to see details
```

## Success Criteria

✅ `/query_with_summary` endpoint responds with 200
✅ Response includes `summary`, `retrieved_chunks`, `metadata`
✅ Hallucination test returns "I don't know" for missing info
✅ Custom prompts affect output style
✅ `npm run test:llm-quality` passes 8-9/9 tests
✅ `npm run test:prompt-optimization` completes all 24 tests
✅ Web UI shows comparison of 3 prompt variants
✅ Cost per query < $0.001

## Next Steps After Testing

1. **Upload sample documents** to test with real data
2. **Tune system prompt** based on A/B test results
3. **Adjust temperature** for your use case (0.3=conservative, 0.9=creative)
4. **Set max_tokens** based on desired answer length
5. **Monitor costs** in production with metadata tracking

## Demo Script

```bash
# 1. Start everything
docker compose up -d
Start-Sleep -Seconds 10

# 2. Test basic summarization
curl -X POST http://localhost:8000/query_with_summary \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize the key points","entity_id":"demo","file_id":"testid1","k":4}'

# 3. Run LLM quality tests
npm run test:llm-quality

# 4. Run prompt optimization
npm run test:prompt-optimization

# 5. View results
npm run view
```

**Total demo time:** ~5 minutes
