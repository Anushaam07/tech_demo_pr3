# Promptfoo Testing Suite for RAG API

This directory contains comprehensive Promptfoo configurations for testing the RAG API's security, quality, and compliance.

## Test Configurations

### 1. **promptfoo.config.yaml** - Baseline Evaluations
Basic regression tests for core functionality:
- Query response validation
- Secret/password leak prevention
- Basic guardrail checks

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.config.yaml
# or: npm run test:baseline
```

### 2. **promptfoo.multi-endpoint.yaml** - Multi-Endpoint Testing
Tests all major API endpoints:
- `/query` - Document retrieval
- `/embed` - File upload and embedding
- `/text` - Text extraction

Covers file upload validation, path traversal prevention, and injection resistance.

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.multi-endpoint.yaml
# or: npm run test:multi-endpoint
```

### 3. **promptfoo.guardrails.yaml** - Advanced Guardrails
LLM-graded quality and policy enforcement:
- Factuality and hallucination detection
- PII protection
- Business policy compliance (no competitor endorsements, unauthorized commitments)
- Toxicity handling
- RBAC enforcement

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.guardrails.yaml
# or: npm run test:guardrails
```

### 4. **promptfoo.performance.yaml** - Performance & Load Testing
Measures latency, cost, and scalability:
- Response time benchmarks (<2s fast, <5s complex)
- Token/cost efficiency tracking
- Concurrent request handling
- Cache effectiveness validation
- Large retrieval set performance (k=50)
- Edge case performance (empty results, non-existent files)

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.performance.yaml
# or: npm run test:performance
```

### 5. **promptfoo.dataset-driven.yaml** - Dataset-Driven Testing
Executes tests from CSV and YAML datasets:
- Loads test cases from `promptfoo/datasets/sample_queries.csv`
- Includes edge cases from `promptfoo/datasets/edge_cases.yaml`
- Uses custom Python grader for quality scoring
- Validates expected topics/keywords from data

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.dataset-driven.yaml
# or: npm run test:dataset
```

### 6. **promptfoo.compare.yaml** - A/B Comparison Testing
Compares different RAG configurations side-by-side:
- Production config (k=4) vs. optimized (k=8) vs. conservative (k=2)
- Measures latency/quality tradeoffs
- Precision vs. recall analysis
- Helps optimize retrieval parameters

**Run:**
```bash
npx promptfoo@latest eval --config promptfoo.compare.yaml
# or: npm run test:compare
```

### 7. **promptfoo.redteam.yaml** - Focused Red Team
Lightweight red-team suite targeting RAG-specific vulnerabilities:
- RAG document exfiltration
- Prompt extraction
- SSRF attacks
- Basic jailbreaks

**Run:**
```bash
npx promptfoo@latest redteam run --config promptfoo.redteam.yaml
# or: npm run test:redteam
```

### 8. **promptfoo.redteam-comprehensive.yaml** - Comprehensive Red Team
Full-spectrum security testing with 40+ plugins:
- OWASP LLM/API Top 10
- NIST AI RMF
- MITRE ATLAS
- Multi-turn conversation attacks
- Multilingual safety (EN/ES/FR)
- Encoding obfuscation (base64, ROT13, leetspeak)

**Run:**
```bash
npx promptfoo@latest redteam run --config promptfoo.redteam-comprehensive.yaml
# or: npm run test:redteam:full
```

## Providers

Custom Python providers bridge Promptfoo to RAG API endpoints:

- **rag_http_target.py** - `/query` endpoint (GET/POST queries)
- **rag_embed_target.py** - `/embed` endpoint (file uploads)
- **rag_text_target.py** - `/text` endpoint (text extraction)

Each provider is configurable via environment variables.

## Custom Graders

**`promptfoo/graders/rag_quality.py`** - Multi-dimensional quality scorer:
- **Relevance**: Query-response keyword alignment
- **Completeness**: Sufficient detail without verbosity
- **Conciseness**: Unique word ratio (low repetition)
- **Factuality**: Hedging detection, fabrication prevention

Returns named scores for each dimension plus overall pass/fail.

**Usage in configs:**
```yaml
assertions:
  - metric: python
    value: file://promptfoo/graders/rag_quality.py
```

## Custom Plugins

**`promptfoo/plugins/custom-rag-attacks.yaml`** - RAG-specific adversarial tests:
- Vector similarity exploits (semantic collision)
- Embedding dimension manipulation
- Chunking boundary attacks
- Homoglyph filter bypass
- Resource exhaustion (max chunks retrieval)
- Metadata injection (file_id, entity_id tampering)
- Cross-tenant semantic similarity leaks
- RAG template/system instruction extraction

**Usage:**
```bash
npx promptfoo redteam run --config promptfoo.redteam.yaml --plugins file://promptfoo/plugins/custom-rag-attacks.yaml
# or: npm run test:redteam:custom
```

## Datasets

**`promptfoo/datasets/sample_queries.csv`** - Sample query variations:
- Columns: user_query, file_id, entity_id, expected_topic
- 8 diverse test cases covering summarization, extraction, analysis

**`promptfoo/datasets/edge_cases.yaml`** - Boundary condition tests:
- Empty queries
- Extremely long inputs (>10k chars)
- Non-existent file_ids
- XSS/injection attempts
- Unicode/emoji handling
- Invalid k parameters (negative, excessive)
- Missing entity_id

**Usage in configs:**
```yaml
tests: file://promptfoo/datasets/sample_queries.csv
```

## Environment Setup

Set these variables before running tests:

```powershell
# Required
$env:PROMPTFOO_RAG_BASE_URL = "http://127.0.0.1:8000"

# Optional - for authenticated endpoints
$env:PROMPTFOO_RAG_JWT = "<your_jwt_token>"

# Optional - for LLM-graded assertions
$env:OPENAI_API_KEY = "<your_openai_key>"

# Optional - defaults
$env:PROMPTFOO_RAG_FILE_ID = "testid1"
$env:PROMPTFOO_RAG_ENTITY_ID = "promptfoo"
$env:PROMPTFOO_RAG_K = "4"
$env:PROMPTFOO_RAG_TIMEOUT = "30"
```

## Global Configuration

**`.promptfoorc.yaml`** - Project-wide defaults:
- Output path: `./promptfoo-output`
- Caching enabled (`./.promptfoo-cache`)
- Default timeout: 30s
- Max concurrency: 4 parallel tests
- Telemetry: Disabled
- Result formats: HTML, JSON, table
- Red team delay: 100ms (rate limit protection)

## Quick Start

1. **Start the RAG API**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Install Promptfoo**
   ```bash
   npm install -g promptfoo@latest
   ```

3. **Set environment variables**
   ```bash
   export PROMPTFOO_RAG_BASE_URL=http://127.0.0.1:8000
   ```

4. **Run a test suite**
   ```bash
   # Quick baseline check
   npx promptfoo@latest eval --config promptfoo.config.yaml
   
   # Full security scan
   npx promptfoo@latest redteam run --config promptfoo.redteam-comprehensive.yaml
   ```

5. **View results**
   - HTML report path printed in terminal
   - Or run: `npx promptfoo@latest view`

## Test Coverage Matrix

| Feature | Config File | Plugins/Assertions | Test Count |
|---------|-------------|-------------------|------------|
| Baseline regression | config.yaml | 3 assertions | 3 tests |
| Multi-endpoint | multi-endpoint.yaml | 3 providers, 8 tests | 8 tests |
| Guardrails | guardrails.yaml | llm-rubric, moderation | 9 tests |
| Performance | performance.yaml | latency, cost metrics | 8 tests |
| Dataset-driven | dataset-driven.yaml | CSV loader, custom grader | 16+ tests |
| A/B comparison | compare.yaml | 3 provider variants | 4 tests |
| RAG security | redteam.yaml | 7 plugins, 2 strategies | 5 per plugin |
| Full red team | redteam-comprehensive.yaml | 40+ plugins, 9 strategies | 10 per plugin |
| **Total Coverage** | **8 configs** | **50+ unique tests** | **400+ variations** |

## Extending Tests

### Add custom test cases
Edit any YAML config and add to the `tests:` array:

```yaml
tests:
  - name: "My custom test"
    vars:
      user_query: "Test prompt"
      file_id: custom-id
    assertions:
      - metric: contains
        value: "expected output"
```

### Add custom graders
Use `llm-rubric` for semantic validation:

```yaml
assertions:
  - metric: llm-rubric
    value: |
      Grade 1 if response is helpful and safe, 0 otherwise.
```

### Add custom plugins
Create `promptfoo/plugins/my-plugin.yaml`:

```yaml
generator: |
  Generate adversarial prompts for [your scenario]

grader: |
  Grade the output based on [your criteria]
```

Reference in config:
```yaml
plugins:
  - file://promptfoo/plugins/my-plugin.yaml
```

## Troubleshooting

**"Connection refused"**  
→ Ensure RAG API is running on correct host/port

**"401 Unauthorized"**  
→ Set `PROMPTFOO_RAG_JWT` environment variable

**"Module not found: promptfoo"**  
→ Install with `npm install -g promptfoo@latest`

**Red team tests timeout**  
→ Increase `PROMPTFOO_RAG_TIMEOUT` or reduce `numTests`

**OpenAI API errors in guardrails**  
→ Set `OPENAI_API_KEY` for LLM-graded assertions

## Best Practices

1. **Start small**: Run `npm run test:baseline` first to verify basic setup
2. **Iterate**: Add tests incrementally as you find issues
3. **Automate**: Let CI catch regressions automatically
4. **Review reports**: HTML reports highlight failures clearly
5. **Track trends**: Compare runs over time to measure security posture
6. **Multilingual**: Test in multiple languages to catch safety gaps
7. **Update regularly**: New Promptfoo plugins are added frequently
8. **Performance first**: Run performance tests before security to establish baselines
9. **Cost awareness**: Red team tests can be expensive - run on schedule, not every commit
10. **Custom graders**: Use Python graders for domain-specific quality metrics
11. **Dataset testing**: Maintain CSV datasets for regression tracking
12. **A/B testing**: Compare config changes before deploying to production

## Resources

- [Promptfoo Docs](https://www.promptfoo.dev/docs/)
- [Red Team Guide](https://www.promptfoo.dev/docs/red-team/)
- [Plugin Reference](https://www.promptfoo.dev/docs/red-team/plugins/)
- [Assertion Types](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
