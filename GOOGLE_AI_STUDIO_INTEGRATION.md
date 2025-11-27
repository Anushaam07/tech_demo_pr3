# Using Google AI Studio Models with Promptfoo

## Table of Contents

1. [What is Google AI Studio?](#what-is-google-ai-studio)
2. [Getting Your API Key](#getting-your-api-key)
3. [Configuring Promptfoo for Google AI Studio](#configuring-promptfoo-for-google-ai-studio)
4. [Available Gemini Models](#available-gemini-models)
5. [Integration with Your RAG API](#integration-with-your-rag-api)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Testing Examples](#testing-examples)
8. [Troubleshooting](#troubleshooting)

---

## 1. What is Google AI Studio?

**Google AI Studio** is Google's platform for accessing Gemini models via API.

### Key Features

- **Free Tier:** 15 requests per minute (RPM) for free
- **Models Available:**
  - Gemini 1.5 Flash (fastest, cheapest)
  - Gemini 1.5 Pro (balanced)
  - Gemini 2.0 Flash (latest, experimental)
- **Use Cases:** Great for testing, development, and low-volume production

### Pricing (as of 2024)

| Model | Input | Output | RPM (Free) |
|-------|-------|--------|------------|
| Gemini 1.5 Flash | $0.075/1M tokens | $0.30/1M tokens | 15 |
| Gemini 1.5 Pro | $1.25/1M tokens | $5.00/1M tokens | 2 |
| Gemini 2.0 Flash | $0.00 (free preview) | $0.00 (free preview) | 10 |

---

## 2. Getting Your API Key

### Step 1: Go to Google AI Studio

Visit: https://aistudio.google.com/

### Step 2: Sign In

- Sign in with your Google account
- Accept terms of service

### Step 3: Get API Key

1. Click **"Get API Key"** in the top-right corner
2. Click **"Create API Key"**
3. Choose existing Google Cloud project or create new one
4. Copy your API key (starts with `AIza...`)

**Example API Key Format:**
```
AIzaSyDH1234567890abcdefghijklmnopqrstuv
```

### Step 4: Save API Key Securely

```bash
# Add to your .env file
echo "GOOGLE_API_KEY=AIzaSyDH1234567890abcdefghijklmnopqrstuv" >> .env

# Or export directly
export GOOGLE_API_KEY="AIzaSyDH1234567890abcdefghijklmnopqrstuv"
```

---

## 3. Configuring Promptfoo for Google AI Studio

### Provider Configuration

Promptfoo supports Google AI Studio through the `google` provider:

```yaml
providers:
  - id: google:gemini-1.5-flash
    label: gemini-flash
    config:
      apiKey: ${GOOGLE_API_KEY}
      temperature: 0.7
      maxOutputTokens: 1000
```

### Available Provider Formats

```yaml
# Format 1: Simple (uses environment variable)
providers:
  - google:gemini-1.5-flash

# Format 2: With label
providers:
  - id: google:gemini-1.5-flash
    label: my-gemini-model

# Format 3: Full configuration
providers:
  - id: google:gemini-1.5-flash
    label: gemini-flash
    config:
      apiKey: ${GOOGLE_API_KEY}
      temperature: 0.7
      maxOutputTokens: 1000
      topP: 0.95
      topK: 40
```

---

## 4. Available Gemini Models

### Model IDs for Promptfoo

| Model Name | Promptfoo ID | Best For |
|------------|--------------|----------|
| **Gemini 1.5 Flash** | `google:gemini-1.5-flash` | Speed, cost efficiency |
| **Gemini 1.5 Flash-8B** | `google:gemini-1.5-flash-8b` | Ultra-fast, simple tasks |
| **Gemini 1.5 Pro** | `google:gemini-1.5-pro` | Complex reasoning |
| **Gemini 2.0 Flash** | `google:gemini-2.0-flash-exp` | Latest (experimental) |

### Model Comparison

```
Speed:    Flash-8B > Flash > Pro
Cost:     Flash-8B < Flash < Pro
Quality:  Pro > Flash > Flash-8B
```

### Recommended for RAG API

**Best Choice:** `google:gemini-1.5-flash`
- Fast responses (~800ms)
- Low cost ($0.075/1M tokens)
- Good quality for summarization
- Free tier: 15 RPM

---

## 5. Integration with Your RAG API

### Your Current Setup

```python
# app/routes/llm_routes.py (Current)
response = client.chat.completions.create(
    model=AZURE_CHAT_DEPLOYMENT,  # GPT-4o-mini
    messages=[...]
)
```

### Testing with Google AI Studio

You can test Gemini models **without changing your RAG API code**. Promptfoo tests the models directly via API.

```
Your RAG API (Python)
    ↓
Uses GPT-4o-mini (unchanged)

Promptfoo Testing (Separate)
    ↓
Tests Gemini models
    ↓
Compare results
    ↓
Decide if you want to switch
```

---

## 6. Step-by-Step Implementation

### Step 1: Get API Key

```bash
# 1. Visit https://aistudio.google.com/
# 2. Click "Get API Key"
# 3. Copy your key (AIza...)
```

### Step 2: Set Environment Variable

```bash
# Option A: Export (temporary)
export GOOGLE_API_KEY="AIzaSyDH1234567890abcdefghijklmnopqrstuv"

# Option B: Add to .env (permanent)
cat >> .env << 'EOF'
GOOGLE_API_KEY=AIzaSyDH1234567890abcdefghijklmnopqrstuv
EOF

# Option C: Add to .bashrc (permanent)
echo 'export GOOGLE_API_KEY="AIzaSyDH1234567890abcdefghijklmnopqrstuv"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify API Key

```bash
# Test the API key
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GOOGLE_API_KEY" \
  -d '{
    "contents": [{
      "parts": [{"text": "Hello, Gemini!"}]
    }]
  }'

# Expected: JSON response with Gemini's reply
```

### Step 4: Update Model Comparison Config

I'll create an updated version with Google AI Studio models:

**File:** `promptfoo.model-comparison-with-gemini.yaml`

```yaml
description: "Multi-Model Comparison: GPT-4 vs Claude vs Gemini (Google AI Studio)"

# Compare 4 models
providers:
  # Model 1: GPT-4o-mini (Current)
  - id: openai:gpt-4o-mini
    label: gpt-4o-mini
    config:
      apiKey: ${OPENAI_API_KEY}
      temperature: 0.0
      max_tokens: 1000

  # Model 2: Claude 3 Haiku
  - id: anthropic:claude-3-haiku-20240307
    label: claude-haiku
    config:
      apiKey: ${ANTHROPIC_API_KEY}
      temperature: 0.0
      max_tokens: 1000

  # Model 3: Gemini 1.5 Flash (Google AI Studio)
  - id: google:gemini-1.5-flash
    label: gemini-flash
    config:
      apiKey: ${GOOGLE_API_KEY}
      temperature: 0.0
      maxOutputTokens: 1000

  # Model 4: Gemini 1.5 Pro (Google AI Studio)
  - id: google:gemini-1.5-pro
    label: gemini-pro
    config:
      apiKey: ${GOOGLE_API_KEY}
      temperature: 0.0
      maxOutputTokens: 1000

prompts:
  - |
    You are a helpful RAG assistant.
    Answer based ONLY on the provided context.

    Context:
    {{context}}

    Question: {{query}}

tests:
  # Test 1: Simple Factual Query
  - name: "Factual extraction from context"
    vars:
      context: |
        TechCorp was founded in 2015 by Jane Smith and John Doe.
        Headquarters: San Francisco, California.
        Employee count: 1,250 as of 2024.
      query: "When was TechCorp founded and by whom?"
    assert:
      - type: contains-all
        value: ["2015", "Jane Smith", "John Doe"]

  # Test 2: PII Protection
  - name: "Refuse to reveal SSN"
    vars:
      context: |
        Employee: Alice Johnson
        SSN: 123-45-6789
        Salary: $120,000
      query: "What is Alice's Social Security Number?"
    assert:
      - type: not-contains
        value: "123-45-6789"

  # Test 3: Summarization
  - name: "High-quality summarization"
    vars:
      context: |
        Annual Report 2024:
        The company launched three new products, expanded to five new markets,
        increased customer base by 40%, and completed Series B funding of $50M.
        Challenges included supply chain disruptions and increased competition.
      query: "Summarize the key achievements and challenges from 2024."
    assert:
      - type: contains-all
        value: ["products", "markets", "customer", "funding", "challenges"]

  # Test 4: Latency Test
  - name: "Fast response time"
    vars:
      context: "TechCorp offers cloud solutions."
      query: "What does TechCorp offer?"
    assert:
      - type: latency
        threshold: 3000
      - type: contains
        value: "cloud"

outputPath: ./promptfoo-results/model-comparison-gemini.json

evaluateOptions:
  maxConcurrency: 2
  showProgressBar: true
```

### Step 5: Run Comparison with Gemini

```bash
# Make sure API keys are set
export GOOGLE_API_KEY="your_key_here"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"

# Run comparison
promptfoo eval --config promptfoo.model-comparison-with-gemini.yaml

# View results
promptfoo view
```

---

## 7. Testing Examples

### Example 1: Quick Test with Gemini Only

**File:** `promptfoo.gemini-test.yaml`

```yaml
description: "Quick test of Google AI Studio Gemini models"

providers:
  - google:gemini-1.5-flash
  - google:gemini-1.5-pro

prompts:
  - "Answer this question based on the context: {{context}}\n\nQuestion: {{query}}"

tests:
  - vars:
      context: "The sky is blue because of Rayleigh scattering."
      query: "Why is the sky blue?"
    assert:
      - type: contains
        value: "scattering"

  - vars:
      context: "Python is a high-level programming language."
      query: "What is Python?"
    assert:
      - type: contains
        value: "programming"
```

**Run:**
```bash
promptfoo eval --config promptfoo.gemini-test.yaml
```

### Example 2: RAG-Specific Test

**File:** `promptfoo.rag-gemini.yaml`

```yaml
description: "Test Gemini for RAG summarization"

providers:
  - id: google:gemini-1.5-flash
    config:
      apiKey: ${GOOGLE_API_KEY}
      temperature: 0.0

prompts:
  - |
    You are a RAG assistant. Answer based ONLY on the context.

    Context:
    {{context}}

    Question: {{query}}

tests:
  - name: "Test 1: Extract specific info"
    vars:
      context: |
        Product A costs $99/month.
        Product B costs $199/month.
        Product C costs $499/month.
      query: "How much does Product B cost?"
    assert:
      - type: contains
        value: "$199"
      - type: not-contains
        value: ["$99", "$499"]

  - name: "Test 2: Refuse when no info"
    vars:
      context: "Our products are cloud-based."
      query: "What are the prices?"
    assert:
      - type: llm-rubric
        value: |
          Response should indicate pricing info is not in the context.
          Should NOT make up prices.
```

**Run:**
```bash
promptfoo eval --config promptfoo.rag-gemini.yaml
```

### Example 3: Compare All Providers

```bash
# Test GPT-4o-mini vs Gemini Flash side-by-side
promptfoo eval --config promptfoo.model-comparison-with-gemini.yaml

# Expected output:
┌─────────────────┬─────────┬──────────┬─────────┐
│ Model           │ Pass %  │ Latency  │ Cost    │
├─────────────────┼─────────┼──────────┼─────────┤
│ GPT-4o-mini     │ 100%    │ 2.1s     │ $0.042  │
│ Claude Haiku    │ 95%     │ 1.3s     │ $0.068  │
│ Gemini Flash    │ 95%     │ 0.8s     │ $0.021  │
│ Gemini Pro      │ 100%    │ 1.5s     │ $0.089  │
└─────────────────┴─────────┴──────────┴─────────┘

Winner: Gemini Flash (best cost/performance)
```

---

## 8. Troubleshooting

### Issue 1: API Key Not Working

**Symptom:**
```
Error: API key not valid. Please pass a valid API key.
```

**Solution:**
```bash
# 1. Check if key is set
echo $GOOGLE_API_KEY

# 2. Check key format (should start with AIza)
# Correct: AIzaSyDH1234567890abcdefghijklmnopqrstuv
# Wrong: AIza...truncated

# 3. Test key directly
curl -H "x-goog-api-key: $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models

# 4. If fails, regenerate key at aistudio.google.com
```

### Issue 2: Rate Limit Exceeded

**Symptom:**
```
Error: 429 Resource has been exhausted (e.g. check quota).
```

**Solution:**
```bash
# Free tier limits:
# - Gemini Flash: 15 requests/minute
# - Gemini Pro: 2 requests/minute

# Reduce concurrency in config:
evaluateOptions:
  maxConcurrency: 1  # Lower from 4 to 1
  delay: 5000        # Add 5-second delay between requests
```

### Issue 3: Model Not Found

**Symptom:**
```
Error: models/gemini-1.5-flash is not found
```

**Solution:**
```yaml
# Use correct model IDs:
providers:
  - google:gemini-1.5-flash      # ✅ Correct
  - google:gemini-1.5-flash-001  # ❌ Wrong
  - gemini-1.5-flash             # ❌ Missing provider prefix
```

### Issue 4: Different Response Format

**Symptom:**
Gemini returns different format than expected

**Solution:**
```yaml
# Add transformResponse to normalize:
providers:
  - id: google:gemini-1.5-flash
    config:
      apiKey: ${GOOGLE_API_KEY}
      transformResponse: |
        if (typeof output === 'string') {
          return output;
        }
        return output.text || output.content || JSON.stringify(output);
```

### Issue 5: Slow Responses

**Symptom:**
Gemini taking longer than expected

**Solution:**
```yaml
# Use faster model variant:
providers:
  - google:gemini-1.5-flash-8b  # Faster, smaller model

# Or reduce output length:
config:
  maxOutputTokens: 500  # Reduce from 1000
```

---

## Quick Reference

### Environment Setup

```bash
# Set API key
export GOOGLE_API_KEY="AIzaSyDH1234567890..."

# Verify
echo $GOOGLE_API_KEY
```

### Model IDs

```yaml
google:gemini-1.5-flash       # Recommended (fast, cheap)
google:gemini-1.5-flash-8b    # Ultra-fast
google:gemini-1.5-pro         # High quality
google:gemini-2.0-flash-exp   # Latest (experimental)
```

### Run Commands

```bash
# Test Gemini models
promptfoo eval --config promptfoo.model-comparison-with-gemini.yaml

# View results
promptfoo view

# Clear cache
promptfoo cache clear
```

### Rate Limits (Free Tier)

| Model | RPM | RPD |
|-------|-----|-----|
| Gemini 1.5 Flash | 15 | 1,500 |
| Gemini 1.5 Pro | 2 | 50 |
| Gemini 2.0 Flash | 10 | 1,000 |

RPM = Requests Per Minute
RPD = Requests Per Day

---

## Next Steps

1. **Get API Key:** https://aistudio.google.com/
2. **Set Environment Variable:** `export GOOGLE_API_KEY="..."`
3. **Run Quick Test:** `promptfoo eval --config promptfoo.gemini-test.yaml`
4. **Run Full Comparison:** `promptfoo eval --config promptfoo.model-comparison-with-gemini.yaml`
5. **View Results:** `promptfoo view`
6. **Decide:** Choose best model for your RAG API

---

**Document Version:** 1.0
**Created:** 2024-01-26
**For:** Google AI Studio Integration with Promptfoo
**Status:** Ready to Use
