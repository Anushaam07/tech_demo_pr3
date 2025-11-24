# app/routes/llm_routes.py
import time
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import vector_store, get_chat_client, AZURE_CHAT_DEPLOYMENT

router = APIRouter()
logger = logging.getLogger(__name__)


class QueryWithSummaryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    file_id: Optional[str] = Field(None, description="Filter by specific file ID")
    entity_id: str = Field(..., description="Entity/user ID for access control")
    k: int = Field(4, ge=1, le=50, description="Number of chunks to retrieve")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt (optional)")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(500, ge=50, le=2000, description="Maximum tokens in response")


class ChunkMetadata(BaseModel):
    content: str
    file_id: Optional[str] = None
    page: Optional[int] = None


class QueryWithSummaryResponse(BaseModel):
    query: str
    summary: str
    retrieved_chunks: List[ChunkMetadata]
    metadata: dict


@router.post("/query_with_summary", response_model=QueryWithSummaryResponse)
async def query_with_summary(request: QueryWithSummaryRequest):
    """
    RAG endpoint with LLM summarization.
    
    Steps:
    1. Retrieve relevant document chunks using vector search
    2. Build context from retrieved chunks
    3. Call GPT-4o-mini to generate a grounded summary
    4. Return summary + retrieved chunks for verification
    """
    start_time = time.time()
    
    # Get Azure OpenAI client
    client = get_chat_client()
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="Azure Chat OpenAI not configured. Set AZURE_CHAT_API_KEY and AZURE_CHAT_ENDPOINT in .env"
        )
    
    try:
        # Step 1: Retrieve documents from vector store
        retrieval_start = time.time()
        
        # Build filter for user_id (entity_id) and optional file_id
        filter_dict = {"user_id": request.entity_id}
        if request.file_id:
            filter_dict["file_id"] = request.file_id
        
        # Perform similarity search
        chunks = await vector_store.asimilarity_search(
            query=request.query,
            k=request.k,
            filter=filter_dict
        )
        
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        if not chunks:
            return QueryWithSummaryResponse(
                query=request.query,
                summary="I couldn't find any relevant information in the knowledge base to answer your question.",
                retrieved_chunks=[],
                metadata={
                    "model": AZURE_CHAT_DEPLOYMENT,
                    "retrieval_latency_ms": retrieval_time,
                    "llm_latency_ms": 0,
                    "total_latency_ms": (time.time() - start_time) * 1000,
                    "chunks_retrieved": 0,
                    "tokens_used": 0,
                    "cost_usd": 0.0
                }
            )
        
        # Step 2: Build context from chunks
        context_parts = []
        chunk_metadata_list = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Chunk {i}]\n{chunk.page_content}")
            chunk_metadata_list.append(ChunkMetadata(
                content=chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content,
                file_id=chunk.metadata.get("file_id"),
                page=chunk.metadata.get("page")
            ))
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Prepare system prompt
        system_prompt = request.system_prompt or """You are a helpful RAG (Retrieval-Augmented Generation) assistant. 
Your job is to answer questions based ONLY on the provided context from the knowledge base.

Rules:
1. Answer based solely on the context provided - do not use external knowledge
2. If the context doesn't contain relevant information, clearly state that you don't have that information
3. Be concise but complete
4. If you're uncertain, acknowledge it
5. Do not hallucinate or make up information
6. You may reference specific chunks (e.g., "According to Chunk 2...")"""
        
        # Step 4: Call GPT-4o-mini
        llm_start = time.time()
        
        response = client.chat.completions.create(
            model=AZURE_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context from knowledge base:\n\n{context}\n\nQuestion: {request.query}\n\nAnswer:"}
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        llm_time = (time.time() - llm_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # Extract summary
        summary = response.choices[0].message.content
        
        # Calculate cost (GPT-4o-mini pricing: $0.150/1M input, $0.600/1M output)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        cost_usd = (input_tokens * 0.150 / 1_000_000) + (output_tokens * 0.600 / 1_000_000)
        
        # Step 5: Return structured response
        return QueryWithSummaryResponse(
            query=request.query,
            summary=summary,
            retrieved_chunks=chunk_metadata_list,
            metadata={
                "model": AZURE_CHAT_DEPLOYMENT,
                "retrieval_latency_ms": round(retrieval_time, 2),
                "llm_latency_ms": round(llm_time, 2),
                "total_latency_ms": round(total_time, 2),
                "chunks_retrieved": len(chunks),
                "tokens_prompt": input_tokens,
                "tokens_completion": output_tokens,
                "tokens_total": total_tokens,
                "cost_usd": round(cost_usd, 6),
                "temperature": request.temperature,
                "max_tokens": request.max_tokens
            }
        )
        
    except Exception as e:
        logger.error(f"Error in query_with_summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
