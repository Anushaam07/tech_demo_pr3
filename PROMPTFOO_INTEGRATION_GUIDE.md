# Integrating Promptfoo with Any Application

## 🎯 Short Answer: YES!

Promptfoo can be integrated with **ANY application** that uses LLMs or AI models, regardless of:
- Programming language (Python, Node.js, Java, Go, Rust, etc.)
- Framework (FastAPI, Express, Django, Flask, Spring Boot, etc.)
- Architecture (REST API, GraphQL, gRPC, WebSocket, etc.)
- Deployment (Docker, Kubernetes, serverless, on-premise, cloud)
- LLM provider (OpenAI, Anthropic, Azure, AWS, Google, open-source models)

---

## 🔧 What You Need to Integrate Promptfoo

Promptfoo only needs **ONE thing**: A way to send prompts and receive responses.

This can be:
1. ✅ **HTTP endpoint** (REST API, GraphQL)
2. ✅ **Python function** (direct function call)
3. ✅ **JavaScript/TypeScript function** (Node.js)
4. ✅ **Command-line script** (any language)
5. ✅ **WebSocket** (real-time connections)
6. ✅ **gRPC service** (microservices)
7. ✅ **Custom provider** (your own integration)

---

## 📊 Promptfoo Integration Architecture

```
┌─────────────────────────────────────────────────┐
│              YOUR APPLICATION                   │
│  (Any language, any framework, any architecture)│
├─────────────────────────────────────────────────┤
│                                                 │
│  Option 1: HTTP API                             │
│  ┌─────────────────┐                            │
│  │ POST /endpoint  │ ← Promptfoo sends HTTP     │
│  │ Body: {prompt}  │                            │
│  │ Returns: {text} │                            │
│  └─────────────────┘                            │
│                                                 │
│  Option 2: Python Function                      │
│  ┌─────────────────┐                            │
│  │ def my_llm():   │ ← Promptfoo calls function │
│  │   return output │                            │
│  └─────────────────┘                            │
│                                                 │
│  Option 3: CLI Script                           │
│  ┌─────────────────┐                            │
│  │ ./run.sh prompt │ ← Promptfoo executes       │
│  │ echo response   │                            │
│  └─────────────────┘                            │
│                                                 │
└─────────────────────────────────────────────────┘
                    ↑
                    │
         ┌──────────┴──────────┐
         │   PROMPTFOO          │
         │ (Red Team Testing)   │
         └─────────────────────┘
```

---

## 🚀 Integration Examples for Different Applications

### 1. **Node.js/Express API**

#### Your Express API:
```javascript
// server.js
const express = require('express');
const app = express();

app.post('/api/chat', async (req, res) => {
  const { message } = req.body;

  // Your LLM logic
  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [{ role: "user", content: message }]
  });

  res.json({ reply: response.choices[0].message.content });
});

app.listen(3000);
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: http
    config:
      url: http://localhost:3000/api/chat
      method: POST
      headers:
        Content-Type: application/json
      body:
        message: "{{prompt}}"
      transformResponse: "json.reply"  # Extract reply field

redteam:
  plugins:
    - prompt-injection
    - jailbreak
    - harmful:hate
  strategies:
    - jailbreak
    - prompt-injection
```

**Run**:
```bash
npx promptfoo redteam run --config promptfoo.yaml
```

---

### 2. **Django API (Python)**

#### Your Django View:
```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        # Your LLM logic
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )

        return JsonResponse({
            'answer': response.choices[0].message.content
        })
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: django-api
    config:
      url: http://localhost:8000/api/chat
      method: POST
      headers:
        Content-Type: application/json
      body:
        message: "{{prompt}}"
      transformResponse: "json.answer"

redteam:
  plugins:
    - prompt-extraction
    - contracts
    - pii:session
```

**Run**:
```bash
npx promptfoo redteam run
```

---

### 3. **Spring Boot (Java)**

#### Your Spring Boot Controller:
```java
// ChatController.java
@RestController
@RequestMapping("/api")
public class ChatController {

    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        String userMessage = request.getMessage();

        // Your LLM logic
        String llmResponse = openAiService.complete(userMessage);

        return ResponseEntity.ok(new ChatResponse(llmResponse));
    }
}
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: spring-boot
    config:
      url: http://localhost:8080/api/chat
      method: POST
      headers:
        Content-Type: application/json
        Authorization: Bearer YOUR_TOKEN
      body:
        message: "{{prompt}}"
      transformResponse: "json.response"

redteam:
  plugins:
    - harmful:hate
    - prompt-injection
```

---

### 4. **Flask Chatbot (Python)**

#### Your Flask App:
```python
# app.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('query')

    # Your chatbot logic
    bot_response = chatbot.get_response(user_input)

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(port=5000)
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: flask-chatbot
    config:
      url: http://localhost:5000/chat
      method: POST
      body:
        query: "{{prompt}}"
      transformResponse: "json.response"

redteam:
  plugins:
    - jailbreak
    - harmful:hate
    - prompt-extraction
```

---

### 5. **Custom Python Function (No HTTP)**

If your application doesn't have an HTTP API, you can test Python functions directly:

#### Your Python Module:
```python
# my_llm.py
def summarize_text(prompt: str) -> str:
    """Your custom LLM function"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
```

#### Promptfoo Provider:
```javascript
// promptfoo-provider.js
module.exports = async (prompt, context) => {
  const { PythonShell } = require('python-shell');

  const options = {
    mode: 'text',
    pythonPath: 'python3',
    scriptPath: './',
    args: [prompt]
  };

  return new Promise((resolve, reject) => {
    PythonShell.run('my_llm.py', options, (err, results) => {
      if (err) reject(err);
      resolve({ output: results[0] });
    });
  });
};
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - file://promptfoo-provider.js

redteam:
  plugins:
    - harmful:hate
    - prompt-injection
```

---

### 6. **LangChain Application**

#### Your LangChain App:
```python
# langchain_app.py
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI

vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever()
)

def query(question: str) -> str:
    return qa_chain.run(question)
```

#### Expose as HTTP endpoint:
```python
# api.py
from flask import Flask, request, jsonify
from langchain_app import query

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_endpoint():
    data = request.json
    result = query(data['question'])
    return jsonify({'answer': result})

app.run(port=8000)
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: langchain-rag
    config:
      url: http://localhost:8000/query
      method: POST
      body:
        question: "{{prompt}}"
      transformResponse: "json.answer"

redteam:
  plugins:
    - rag-document-exfiltration
    - rag-poisoning
    - prompt-injection
```

---

### 7. **GraphQL API**

#### Your GraphQL Schema:
```graphql
type Query {
  chat(message: String!): ChatResponse
}

type ChatResponse {
  reply: String!
}
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: graphql-api
    config:
      url: http://localhost:4000/graphql
      method: POST
      headers:
        Content-Type: application/json
      body:
        query: |
          query($message: String!) {
            chat(message: $message) {
              reply
            }
          }
        variables:
          message: "{{prompt}}"
      transformResponse: "json.data.chat.reply"

redteam:
  plugins:
    - harmful:hate
    - prompt-injection
```

---

### 8. **AWS Lambda (Serverless)**

#### Your Lambda Function:
```python
# lambda_function.py
import json
import openai

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_message = body.get('message')

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_message}]
    )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': response.choices[0].message.content
        })
    }
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: aws-lambda
    config:
      url: https://abc123.execute-api.us-east-1.amazonaws.com/prod/chat
      method: POST
      headers:
        x-api-key: YOUR_API_KEY
      body:
        message: "{{prompt}}"
      transformResponse: "JSON.parse(json.body).response"

redteam:
  plugins:
    - prompt-injection
    - harmful:hate
```

---

### 9. **Go/Gin API**

#### Your Gin API:
```go
// main.go
package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.POST("/chat", func(c *gin.Context) {
        var req struct {
            Message string `json:"message"`
        }
        c.BindJSON(&req)

        // Your LLM logic
        response := callOpenAI(req.Message)

        c.JSON(200, gin.H{
            "reply": response,
        })
    })

    r.Run(":8080")
}
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: go-gin
    config:
      url: http://localhost:8080/chat
      method: POST
      body:
        message: "{{prompt}}"
      transformResponse: "json.reply"

redteam:
  plugins:
    - jailbreak
    - harmful:hate
```

---

### 10. **Rust/Actix-Web API**

#### Your Actix API:
```rust
// main.rs
use actix_web::{post, web, App, HttpResponse, HttpServer};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct ChatRequest {
    message: String,
}

#[derive(Serialize)]
struct ChatResponse {
    reply: String,
}

#[post("/chat")]
async fn chat(req: web::Json<ChatRequest>) -> HttpResponse {
    // Your LLM logic
    let response = call_llm(&req.message).await;

    HttpResponse::Ok().json(ChatResponse {
        reply: response,
    })
}
```

#### Promptfoo Config:
```yaml
# promptfoo.yaml
targets:
  - id: rust-actix
    config:
      url: http://localhost:8080/chat
      method: POST
      body:
        message: "{{prompt}}"
      transformResponse: "json.reply"

redteam:
  plugins:
    - harmful:hate
    - prompt-injection
```

---

## 🎯 Real-World Application Examples

### **1. Customer Support Chatbot**
```yaml
# Test your support chatbot for safety
targets:
  - url: https://support.yourcompany.com/api/chat

redteam:
  plugins:
    - harmful:hate  # Ensure bot doesn't respond to abuse
    - pii:session   # Don't leak customer data
    - contracts     # Don't make unauthorized commitments
```

### **2. Code Generation Tool (GitHub Copilot-like)**
```yaml
# Test your code assistant
targets:
  - url: https://api.yourcodegen.com/complete

redteam:
  plugins:
    - harmful:harmful-code  # Don't generate malware
    - prompt-injection      # Resist malicious prompts
    - prompt-extraction     # Don't reveal system prompts
```

### **3. Healthcare Assistant**
```yaml
# Test medical advice bot
targets:
  - url: https://health.yourapp.com/api/consult

redteam:
  plugins:
    - harmful:medical-advice  # Don't give dangerous advice
    - pii:hipaa                # Protect patient data
    - hallucination            # Don't fabricate medical info
```

### **4. Financial Advisor Bot**
```yaml
# Test investment advice bot
targets:
  - url: https://finance.yourapp.com/api/advice

redteam:
  plugins:
    - harmful:financial-advice  # Don't give risky advice
    - pii:financial             # Protect account numbers
    - contracts                 # Don't make unauthorized promises
```

### **5. Educational Tutor**
```yaml
# Test learning assistant
targets:
  - url: https://learn.yourapp.com/api/tutor

redteam:
  plugins:
    - harmful:hate           # No inappropriate content
    - jailbreak              # Stay in tutor role
    - prompt-extraction      # Don't reveal answers
```

---

## 🔑 Key Integration Patterns

### **Pattern 1: HTTP/REST (Most Common)**
```yaml
targets:
  - id: http
    config:
      url: YOUR_ENDPOINT
      method: POST
      headers:
        Content-Type: application/json
        Authorization: Bearer TOKEN
      body:
        prompt: "{{prompt}}"
      transformResponse: "json.field.path"
```

### **Pattern 2: Custom Provider (Any Language)**
```javascript
// provider.js
module.exports = async (prompt, context) => {
  // Call your application however you want
  // - HTTP request
  // - Execute subprocess
  // - Import Python module
  // - gRPC call
  // - Database query

  return {
    output: "your response",
    metadata: { /* optional */ }
  };
};
```

### **Pattern 3: Command Line**
```yaml
targets:
  - id: exec
    config:
      command: "./your-script.sh {{prompt}}"
```

---

## 📋 Checklist: Can Promptfoo Test My App?

✅ **YES** if your app:
- [ ] Has an HTTP endpoint that accepts text input
- [ ] Has a Python/JavaScript function that can be called
- [ ] Can be invoked via command line
- [ ] Returns text/JSON responses
- [ ] Uses any LLM (OpenAI, Anthropic, Azure, open-source, etc.)

❌ **NO** (but workarounds exist) if:
- [ ] App requires complex GUI interactions → Create API wrapper
- [ ] App uses proprietary protocol → Write custom provider
- [ ] App is closed-source with no API → Can't test directly

---

## 🚀 Quick Start: Integrate with Your App

### **Step 1: Identify Your Interface**
- Do you have an HTTP API? → Use HTTP target
- Do you have a Python function? → Use Python provider
- Do you have a CLI? → Use exec target

### **Step 2: Create Config**
```yaml
# promptfoo.yaml
targets:
  - id: my-app
    config:
      url: http://localhost:YOUR_PORT/YOUR_ENDPOINT
      method: POST
      body:
        your_field: "{{prompt}}"
      transformResponse: "json.your_response_field"

redteam:
  plugins:
    - prompt-injection
    - jailbreak
    - harmful:hate
  strategies:
    - jailbreak
    - prompt-injection
```

### **Step 3: Test**
```bash
# Generate attacks
npx promptfoo redteam generate

# Run tests
npx promptfoo redteam run

# View results
npx promptfoo view
```

---

## 🎯 What Promptfoo Tests (Universal)

Regardless of your tech stack, Promptfoo tests:

| Category | What It Tests |
|----------|---------------|
| **Jailbreaking** | Can users bypass safety rules? |
| **Prompt Injection** | Can malicious prompts override instructions? |
| **Data Exfiltration** | Can users steal other users' data? |
| **PII Leakage** | Does app leak sensitive information? |
| **Harmful Content** | Does LLM generate toxic/dangerous content? |
| **Hallucination** | Does LLM make up information? |
| **Contracts** | Does LLM make unauthorized commitments? |
| **OWASP LLM Top 10** | All major LLM vulnerabilities |

---

## 📚 Additional Resources

### **Promptfoo Documentation**
- Official Docs: https://www.promptfoo.dev/docs/
- Red Team Guide: https://www.promptfoo.dev/docs/red-team/
- Custom Providers: https://www.promptfoo.dev/docs/providers/custom/

### **Example Integrations**
- Your RAG API (FastAPI): `promptfoo.redteam-llm.yaml`
- HTTP targets: https://www.promptfoo.dev/docs/providers/http/
- Python providers: https://www.promptfoo.dev/docs/providers/python/

---

## ✅ Summary

### **Can you integrate Promptfoo with ANY application?**

**YES!** As long as your application:
1. Uses an LLM or AI model
2. Can be accessed via HTTP, Python function, or CLI
3. Returns text responses

### **What do you need?**

Just create a `promptfoo.yaml` config pointing to your app:
```yaml
targets:
  - url: YOUR_APP_ENDPOINT

redteam:
  plugins: [YOUR_SECURITY_CONCERNS]
```

### **What can you test?**

- ✅ Any LLM-powered application
- ✅ Any programming language
- ✅ Any framework
- ✅ Any architecture (monolith, microservices, serverless)
- ✅ Any deployment (local, cloud, on-premise)

**Bottom Line**: If your app uses LLMs and has a way to send/receive text, you can use Promptfoo to test it! 🚀

---

**Generated**: 2025-11-25
**Promptfoo Version**: Compatible with any version
**Your Current Setup**: FastAPI + PostgreSQL + Azure OpenAI (working example)
