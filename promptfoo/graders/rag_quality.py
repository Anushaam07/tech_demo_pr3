#!/usr/bin/env python3
"""
Custom Promptfoo grader for RAG-specific quality metrics.
Evaluates response quality beyond simple string matching.
"""

import json
import sys
import os
import re
from typing import Dict, Any


def grade_response(output: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Grade RAG response quality on multiple dimensions.
    
    Returns:
        {
            "pass": bool,
            "score": float (0.0-1.0),
            "reason": str,
            "namedScores": {
                "relevance": float,
                "completeness": float,
                "conciseness": float,
                "factuality": float
            }
        }
    """
    test_vars = context.get("vars", {})
    prompt = context.get("prompt", "")
    
    # Initialize scores
    scores = {
        "relevance": 0.0,
        "completeness": 0.0,
        "conciseness": 0.0,
        "factuality": 0.0
    }
    
    # Check if output exists
    if not output or len(output.strip()) == 0:
        return {
            "pass": False,
            "score": 0.0,
            "reason": "Empty response",
            "namedScores": scores
        }
    
    # 1. Relevance: Does response address the query?
    query_keywords = set(re.findall(r'\w+', prompt.lower()))
    response_keywords = set(re.findall(r'\w+', output.lower()))
    keyword_overlap = len(query_keywords & response_keywords) / max(len(query_keywords), 1)
    scores["relevance"] = min(keyword_overlap * 2, 1.0)  # Scale up overlap
    
    # 2. Completeness: Sufficient detail?
    word_count = len(output.split())
    if word_count < 10:
        scores["completeness"] = 0.3
    elif word_count < 50:
        scores["completeness"] = 0.6
    elif word_count < 200:
        scores["completeness"] = 1.0
    else:
        scores["completeness"] = 0.8  # Too verbose
    
    # 3. Conciseness: Not too repetitive or verbose?
    unique_words = len(set(output.lower().split()))
    total_words = len(output.split())
    uniqueness_ratio = unique_words / max(total_words, 1)
    scores["conciseness"] = uniqueness_ratio
    
    # 4. Factuality: Check for hedging/uncertainty markers
    uncertainty_markers = [
        "i don't know", "i'm not sure", "i cannot", "no information",
        "unclear", "uncertain", "maybe", "possibly"
    ]
    has_uncertainty = any(marker in output.lower() for marker in uncertainty_markers)
    
    # Check for fabrication indicators (if query asks about non-existent data)
    fabrication_indicators = [
        "based on my knowledge", "as far as i know", "i believe",
        "the document states", "according to"
    ]
    has_fabrication_risk = any(ind in output.lower() for ind in fabrication_indicators)
    
    if has_uncertainty:
        scores["factuality"] = 1.0  # Good - admits uncertainty
    elif has_fabrication_risk and scores["relevance"] < 0.3:
        scores["factuality"] = 0.3  # Suspicious - cites sources when irrelevant
    else:
        scores["factuality"] = 0.7  # Neutral
    
    # Calculate overall score
    overall_score = sum(scores.values()) / len(scores)
    
    # Pass threshold: 0.6 or higher
    passes = overall_score >= 0.6
    
    # Generate reason
    weak_dimensions = [k for k, v in scores.items() if v < 0.5]
    if weak_dimensions:
        reason = f"Quality issues in: {', '.join(weak_dimensions)}"
    else:
        reason = "Response meets quality standards"
    
    return {
        "pass": passes,
        "score": round(overall_score, 2),
        "reason": reason,
        "namedScores": {k: round(v, 2) for k, v in scores.items()}
    }


def main():
    """Entry point for Promptfoo custom grader."""
    # Read input from stdin (Promptfoo passes JSON)
    input_data = json.load(sys.stdin)
    
    output = input_data.get("output", "")
    context = input_data.get("context", {})
    
    result = grade_response(output, context)
    
    # Write result to stdout
    print(json.dumps(result))


if __name__ == "__main__":
    main()
