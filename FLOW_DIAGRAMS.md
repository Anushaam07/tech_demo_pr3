# 🔄 RAG API - Visual Flow Diagrams

This document contains visual flow diagrams in Mermaid format. You can view these in:
- GitHub (renders Mermaid automatically)
- VS Code (with Mermaid extension)
- Online: https://mermaid.live/

---

## 1. Document Upload & Embedding Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Loader as Document Loader
    participant Splitter as Text Splitter
    participant OpenAI as Azure OpenAI
    participant DB as PostgreSQL+pgvector

    User->>API: POST /embed (file, file_id, entity_id)
    API->>API: Save to /uploads/{user_id}/
    API->>Loader: Load document by type
    Loader->>Loader: PDFLoader/DOCXLoader/etc
    Loader-->>API: Return Document objects

    API->>Splitter: Split into chunks
    Note over Splitter: chunk_size=1500<br/>overlap=100
    Splitter-->>API: Return chunk array

    loop For each chunk
        API->>OpenAI: Generate embedding
        OpenAI-->>API: Return 1536-dim vector
    end

    API->>DB: INSERT embeddings + metadata
    Note over DB: Store: embedding, document,<br/>file_id, user_id, digest
    DB-->>API: Success

    API-->>User: 200 OK {status: true, file_id}
```

---

## 2. Query & Vector Search Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Auth as Middleware
    participant OpenAI as Azure OpenAI
    participant DB as PostgreSQL+pgvector

    User->>API: POST /query (query, file_id, entity_id, k)
    API->>Auth: Verify JWT (if enabled)
    Auth-->>API: User context

    API->>OpenAI: Generate query embedding
    OpenAI-->>API: Return 1536-dim vector

    API->>DB: Vector similarity search
    Note over DB: SELECT ... <br/>WHERE file_id = $1 AND user_id = $2<br/>ORDER BY embedding <=> $3<br/>LIMIT k
    DB-->>API: Top k chunks + scores

    API->>API: Authorization check
    alt User authorized
        API-->>User: 200 OK [chunks + scores]
    else Unauthorized
        API-->>User: 200 OK [] (empty)
    end
```

---

## 3. Query with LLM Summary Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant VectorDB as pgvector
    participant Embeddings as Azure OpenAI<br/>(Embeddings)
    participant LLM as Azure OpenAI<br/>(GPT-4o-mini)

    User->>API: POST /query_with_summary<br/>(query, file_id, system_prompt, temp, max_tokens)

    Note over API: Start retrieval timer
    API->>Embeddings: Generate query embedding
    Embeddings-->>API: Vector

    API->>VectorDB: Similarity search
    VectorDB-->>API: Top k chunks
    Note over API: Stop retrieval timer<br/>(retrieval_latency_ms)

    API->>API: Build context
    Note over API: System prompt +<br/>Retrieved chunks +<br/>User query

    Note over API: Start LLM timer
    API->>LLM: Generate summary
    Note over LLM: Model: gpt-4o-mini<br/>Temperature: 0.7<br/>Max tokens: 500
    LLM-->>API: Summary + token usage
    Note over API: Stop LLM timer<br/>(llm_latency_ms)

    API->>API: Calculate cost
    Note over API: tokens_total × price_per_token

    API-->>User: 200 OK<br/>{summary, chunks, metadata}
    Note over User: metadata includes:<br/>- tokens_total<br/>- cost_usd<br/>- retrieval_latency_ms<br/>- llm_latency_ms<br/>- total_latency_ms
```

---

## 4. Multi-Tenant Authorization Flow

```mermaid
flowchart TD
    Start([User sends request]) --> HasJWT{JWT token<br/>present?}

    HasJWT -->|Yes| ValidateJWT[Validate JWT signature]
    HasJWT -->|No| UseEntity[Use entity_id from request]

    ValidateJWT --> ExtractUser[Extract user_id from JWT]
    ExtractUser --> CheckEntity{entity_id<br/>provided?}

    CheckEntity -->|Yes| UseEntityID[user_authorized = entity_id]
    CheckEntity -->|No| UseJWTUser[user_authorized = jwt.user_id]

    UseEntity --> SetPublic[user_authorized = entity_id or 'public']

    UseEntityID --> QueryDB[Query vector DB]
    UseJWTUser --> QueryDB
    SetPublic --> QueryDB

    QueryDB --> GetResults[Retrieve documents]
    GetResults --> CheckOwnership{doc.user_id ==<br/>user_authorized?}

    CheckOwnership -->|Yes| ReturnDocs[Return documents]
    CheckOwnership -->|No| CheckFallback{entity_id used<br/>& JWT exists?}

    CheckFallback -->|Yes| TryJWTUser[Try with jwt.user_id]
    CheckFallback -->|No| LogWarning[Log unauthorized access]

    TryJWTUser --> CheckAgain{doc.user_id ==<br/>jwt.user_id?}
    CheckAgain -->|Yes| ReturnDocs
    CheckAgain -->|No| LogWarning

    LogWarning --> ReturnEmpty[Return empty array]
    ReturnDocs --> End([Response sent])
    ReturnEmpty --> End
```

---

## 5. Promptfoo Testing Architecture

```mermaid
flowchart TB
    subgraph Config["Configuration Layer"]
        YAML1[promptfoo.config.yaml<br/>Baseline Tests]
        YAML2[promptfoo.guardrails.yaml<br/>Quality Tests]
        YAML3[promptfoo.redteam.yaml<br/>Security Tests]
        YAML4[promptfoo.llm-quality.yaml<br/>LLM Tests]
    end

    subgraph TestGen["Test Generation"]
        Static[Static Tests<br/>from YAML]
        Dynamic[Dynamic Tests<br/>Red Team AI]
        Dataset[Dataset-Driven<br/>CSV/YAML]
    end

    subgraph Execution["Parallel Execution"]
        E1[Test 1]
        E2[Test 2]
        E3[Test N]
    end

    subgraph API["RAG API Endpoints"]
        Query[POST /query]
        Embed[POST /embed]
        Summary[POST /query_with_summary]
        Text[POST /text]
    end

    subgraph Assertions["Assertion Types"]
        JS[JavaScript<br/>Custom Logic]
        Contains[Contains/Not-Contains<br/>String Matching]
        LLMGrade[LLM-as-Judge<br/>Quality Scoring]
        Regex[Regex Patterns]
    end

    subgraph Results["Results & Reporting"]
        Console[Console Output]
        JSON[JSON Files]
        WebUI[Web Dashboard]
        Report[HTML Reports]
    end

    YAML1 --> TestGen
    YAML2 --> TestGen
    YAML3 --> TestGen
    YAML4 --> TestGen

    Static --> Execution
    Dynamic --> Execution
    Dataset --> Execution

    E1 --> API
    E2 --> API
    E3 --> API

    API --> Assertions

    Assertions --> Results

    Console -.Export.-> JSON
    JSON -.View.-> WebUI
    WebUI -.Generate.-> Report
```

---

## 6. Red Team Attack Flow

```mermaid
flowchart TD
    Start([Red Team Test Starts]) --> LoadConfig[Load promptfoo.redteam.yaml]
    LoadConfig --> GenAttacks[AI generates attack prompts]

    GenAttacks --> Attack1[Prompt Injection]
    GenAttacks --> Attack2[Document Exfiltration]
    GenAttacks --> Attack3[System Prompt Extraction]
    GenAttacks --> Attack4[SSRF Attempts]
    GenAttacks --> Attack5[Cross-Tenant Access]
    GenAttacks --> Attack6[PII Leakage]

    Attack1 --> SendAPI[Send to /query endpoint]
    Attack2 --> SendAPI
    Attack3 --> SendAPI
    Attack4 --> SendAPI
    Attack5 --> SendAPI
    Attack6 --> SendAPI

    SendAPI --> GetResponse[Get API Response]

    GetResponse --> Check1{Contains<br/>forbidden data?}
    GetResponse --> Check2{Leaked PII?}
    GetResponse --> Check3{System prompt<br/>revealed?}
    GetResponse --> Check4{Cross-tenant<br/>data?}

    Check1 -->|Yes| Fail1[❌ FAIL: Injection succeeded]
    Check1 -->|No| Pass1[✅ PASS: Blocked]

    Check2 -->|Yes| Fail2[❌ FAIL: PII leaked]
    Check2 -->|No| Pass2[✅ PASS: Protected]

    Check3 -->|Yes| Fail3[❌ FAIL: Prompt extracted]
    Check3 -->|No| Pass3[✅ PASS: Secure]

    Check4 -->|Yes| Fail4[❌ FAIL: Data leaked]
    Check4 -->|No| Pass4[✅ PASS: Isolated]

    Fail1 --> Aggregate[Aggregate Results]
    Fail2 --> Aggregate
    Fail3 --> Aggregate
    Fail4 --> Aggregate
    Pass1 --> Aggregate
    Pass2 --> Aggregate
    Pass3 --> Aggregate
    Pass4 --> Aggregate

    Aggregate --> CalcRate[Calculate Pass Rate]
    CalcRate --> GenReport[Generate Security Report]
    GenReport --> End([Display Results])

    style Fail1 fill:#ff6b6b
    style Fail2 fill:#ff6b6b
    style Fail3 fill:#ff6b6b
    style Fail4 fill:#ff6b6b
    style Pass1 fill:#51cf66
    style Pass2 fill:#51cf66
    style Pass3 fill:#51cf66
    style Pass4 fill:#51cf66
```

---

## 7. Complete System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        User1[LibreChat]
        User2[Promptfoo Tests]
        User3[Custom Apps]
        User4[curl/Postman]
    end

    subgraph FastAPI["FastAPI Application Layer"]
        Middleware[Middleware<br/>- JWT Auth<br/>- CORS<br/>- Logging]

        Routes[Routes Layer]
        DocRoutes[document_routes.py<br/>/embed, /query, /text]
        LLMRoutes[llm_routes.py<br/>/query_with_summary]
        DebugRoutes[pgvector_routes.py<br/>/db/* (debug only)]

        Services[Services Layer]
        VectorSvc[Vector Store Factory<br/>AsyncPgVector]
        DBSvc[Database Service<br/>Connection Pool]

        Utils[Utilities]
        DocLoader[Document Loader<br/>Multi-format support]
        Health[Health Check]
    end

    subgraph External["External Services"]
        AzureEmbed[Azure OpenAI<br/>text-embedding-3-small<br/>1536 dimensions]
        AzureLLM[Azure OpenAI<br/>GPT-4o-mini<br/>Summarization]
        PSQL[PostgreSQL 15+<br/>with pgvector extension]
    end

    subgraph Testing["Testing & Validation"]
        Promptfoo[Promptfoo Framework]
        Eval[Evaluation Tests<br/>Quality & Performance]
        Guard[Guardrails Tests<br/>PII, Toxicity, RBAC]
        RedTeam[Red Team Tests<br/>Security Scanning]
    end

    User1 --> Middleware
    User2 --> Middleware
    User3 --> Middleware
    User4 --> Middleware

    Middleware --> Routes
    Routes --> DocRoutes
    Routes --> LLMRoutes
    Routes --> DebugRoutes

    DocRoutes --> Services
    LLMRoutes --> Services

    Services --> VectorSvc
    Services --> DBSvc
    Services --> Utils

    VectorSvc --> PSQL
    DBSvc --> PSQL
    DocRoutes --> AzureEmbed
    LLMRoutes --> AzureEmbed
    LLMRoutes --> AzureLLM

    DocLoader --> DocRoutes
    Health --> DocRoutes

    Promptfoo --> Eval
    Promptfoo --> Guard
    Promptfoo --> RedTeam

    Eval --> DocRoutes
    Guard --> DocRoutes
    RedTeam --> DocRoutes
    RedTeam --> LLMRoutes

    style FastAPI fill:#e3f2fd
    style External fill:#fff3e0
    style Testing fill:#f3e5f5
    style Client fill:#e8f5e9
```

---

## 8. Data Flow: Upload to Query

```mermaid
stateDiagram-v2
    [*] --> Upload: User uploads document

    Upload --> Validate: POST /embed
    Validate --> LoadFile: File type detected

    LoadFile --> SplitText: Document loaded
    note right of SplitText: Chunk size: 1500 chars<br/>Overlap: 100 chars

    SplitText --> GenerateEmbeddings: Chunks created
    note right of GenerateEmbeddings: Azure OpenAI<br/>text-embedding-3-small

    GenerateEmbeddings --> StoreVectors: Embeddings generated
    note right of StoreVectors: PostgreSQL + pgvector<br/>Table: langchain_pg_embedding

    StoreVectors --> Indexed: Data stored with metadata

    Indexed --> Ready: System ready for queries

    Ready --> QueryReceived: User sends query

    QueryReceived --> QueryEmbed: POST /query
    note right of QueryEmbed: Convert query to vector

    QueryEmbed --> VectorSearch: Embedding generated
    note right of VectorSearch: Cosine similarity search<br/>Filter by file_id + user_id

    VectorSearch --> AuthCheck: Top k results retrieved

    AuthCheck --> ReturnResults: User authorized
    AuthCheck --> ReturnEmpty: Unauthorized

    ReturnResults --> [*]
    ReturnEmpty --> [*]
```

---

## 9. Promptfoo Test Execution Timeline

```mermaid
gantt
    title Promptfoo Test Execution Timeline
    dateFormat ss
    axisFormat %S

    section Quick Tests
    Baseline (3 tests)           :done, baseline, 00, 1s
    Multi-Endpoint (2 tests)     :done, multi, 01, 1s
    Dataset-Driven (4 tests)     :done, dataset, 02, 2s
    Performance (6 tests)        :done, perf, 04, 2s
    Guardrails (9 tests)         :done, guard, 06, 2s

    section LLM Tests
    LLM Quality (9 tests)        :active, llmq, 08, 10s
    Prompt Optimization (8 tests):active, prompt, 18, 15s

    section Security Tests
    Red Team RAG (35 tests)      :crit, red1, 33, 300s
    Red Team LLM (16 tests)      :crit, red2, 333, 165s

    section Comprehensive
    Full Red Team (400+ tests)   :milestone, red3, 498, 900s
```

---

## 10. Cost & Performance Tradeoffs

```mermaid
quadrantChart
    title RAG Configuration Tradeoffs
    x-axis Low Cost --> High Cost
    y-axis Low Quality --> High Quality
    quadrant-1 Premium
    quadrant-2 Sweet Spot
    quadrant-3 Basic
    quadrant-4 Inefficient

    k=2, no LLM: [0.2, 0.6]
    k=4, no LLM: [0.3, 0.75]
    k=8, no LLM: [0.5, 0.8]
    k=2, with LLM: [0.4, 0.7]
    k=4, with LLM: [0.6, 0.9]
    k=8, with LLM: [0.85, 0.95]
    k=4, conservative prompt: [0.5, 0.75]
    k=4, balanced prompt: [0.6, 0.85]
    k=4, detailed prompt: [0.7, 0.92]
```

---

## How to View These Diagrams

### Option 1: GitHub
- Push this file to GitHub
- View in browser (Mermaid renders automatically)

### Option 2: VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file
3. Press `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (Mac)

### Option 3: Online Viewer
1. Copy any diagram code block
2. Visit https://mermaid.live/
3. Paste and view

### Option 4: Export to Image
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i FLOW_DIAGRAMS.md -o diagrams.png
```

---

**Last Updated:** 2025-11-25
