#!/bin/bash

echo "🔒 RAG API Model Security Scan"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if promptfoo is installed
if ! command -v promptfoo &> /dev/null; then
    echo "${RED}❌ Promptfoo not found. Installing...${NC}"
    npm install -g promptfoo
fi

echo "📋 Scanning models used in RAG API..."
echo ""

# Function to scan a model
scan_model() {
    local model_path=$1
    local model_name=$2

    echo "─────────────────────────────────────────"
    echo "Scanning: $model_name"
    echo "Path: $model_path"
    echo ""

    if [ -f "$model_path" ] || [ -d "$model_path" ]; then
        promptfoo scan-model "$model_path"
        scan_result=$?

        if [ $scan_result -eq 0 ]; then
            echo "${GREEN}✅ $model_name: SAFE${NC}"
        else
            echo "${RED}❌ $model_name: VULNERABILITIES FOUND${NC}"
            return 1
        fi
    else
        echo "${YELLOW}⚠️  $model_name: NOT FOUND (skipping)${NC}"
    fi
    echo ""
}

# Track if any vulnerabilities found
vulnerabilities_found=0

# 1. Scan sentence-transformers embedding models
echo "1️⃣  Scanning Embedding Models"
echo "─────────────────────────────────────────"

# Check for all-MiniLM-L6-v2 (commonly used)
EMBEDDER_PATH="$HOME/.cache/torch/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2"
if [ -d "$EMBEDDER_PATH" ]; then
    # Scan all .bin files in the directory
    for model_file in "$EMBEDDER_PATH"/*.bin; do
        if [ -f "$model_file" ]; then
            scan_model "$model_file" "all-MiniLM-L6-v2 ($(basename $model_file))"
            if [ $? -ne 0 ]; then vulnerabilities_found=1; fi
        fi
    done

    # Scan .pt files if any
    for model_file in "$EMBEDDER_PATH"/*.pt; do
        if [ -f "$model_file" ]; then
            scan_model "$model_file" "all-MiniLM-L6-v2 ($(basename $model_file))"
            if [ $? -ne 0 ]; then vulnerabilities_found=1; fi
        fi
    done
else
    echo "${YELLOW}ℹ️  No local embedding models found (using cloud API)${NC}"
    echo ""
fi

# 2. Scan custom models directory
echo "2️⃣  Scanning Custom Models"
echo "─────────────────────────────────────────"

if [ -d "models" ]; then
    model_count=0
    for model_file in models/*.pkl models/*.pt models/*.h5 models/*.onnx; do
        if [ -f "$model_file" ]; then
            scan_model "$model_file" "Custom Model ($(basename $model_file))"
            if [ $? -ne 0 ]; then vulnerabilities_found=1; fi
            model_count=$((model_count + 1))
        fi
    done

    if [ $model_count -eq 0 ]; then
        echo "${YELLOW}ℹ️  No custom models found${NC}"
        echo ""
    fi
else
    echo "${YELLOW}ℹ️  No custom models directory${NC}"
    echo ""
fi

# 3. Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Model Security Scan Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $vulnerabilities_found -eq 0 ]; then
    echo "${GREEN}✅ All models passed security scan!${NC}"
    echo ""
    echo "Your RAG API models are safe to use."
    exit 0
else
    echo "${RED}❌ Vulnerabilities detected in one or more models!${NC}"
    echo ""
    echo "⚠️  DO NOT use models with critical vulnerabilities"
    echo "⚠️  Review scan output above for details"
    exit 1
fi
