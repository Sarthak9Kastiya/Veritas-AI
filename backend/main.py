from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import json
import asyncio

from . import storage
from .council import stage1_collect_responses, stage2_verify_responses, stage3_synthesize_verified_answer, generate_conversation_title
from .veritas import calculate_reliability, calculate_risk, determine_decision, ModelReview, Claim

app = FastAPI(title="Veritas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SendMessageRequest(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"status": "ok", "service": "Veritas API"}

@app.get("/api/conversations")
async def list_conversations():
    return storage.list_conversations()

@app.post("/api/conversations")
async def create_conversation():
    conversation_id = str(uuid.uuid4())
    return storage.create_conversation(conversation_id)

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    success = storage.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok"}


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    is_first_message = len(conversation["messages"]) == 0

    async def event_generator():
        try:
            storage.add_user_message(conversation_id, request.content)
            
            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(generate_conversation_title(request.content))

            # Stage 1: Collect responses
            yield f"data: {json.dumps({'type': 'stage1_start'})}\n\n"
            stage1_results = await stage1_collect_responses(request.content)
            
            # Mock Cost metrics
            cost_metrics = {
                "latency": "2.8s",
                "models": len(stage1_results),
                "verification_calls": len(stage1_results),
                "estimated_cost": f"${len(stage1_results) * 0.012:.3f}"
            }
            
            yield f"data: {json.dumps({'type': 'stage1_complete', 'data': stage1_results, 'cost_metrics': cost_metrics})}\n\n"

            # Stage 2: Cross-Model Verification
            if not stage1_results:
                yield f"data: {json.dumps({'type': 'error', 'message': 'All models failed to respond. Please check your OpenRouter API credits or rate limits.'})}\n\n"
                return
                
            yield f"data: {json.dumps({'type': 'stage2_start'})}\n\n"
            evaluations, claims, label_to_model = await stage2_verify_responses(request.content, stage1_results)
            
            # Calculate Scores and Decision
            reviews = []
            for m, ev in evaluations.items():
                # Convert the dict back into ModelReview
                try:
                    # In demo mode, it might already be raw dict, we ensure it matches the schema for logic
                    review = ModelReview(**ev)
                    reviews.append(review)
                except Exception as e:
                    print(f"Error validating review from {m}: {e}")
                    
            reliability = calculate_reliability(reviews, claims)
            risk = calculate_risk(reviews)
            decision_status, reasoning = determine_decision(reliability, risk, reviews, claims)
            
            decision = {
                "status": decision_status,
                "reliability_score": reliability,
                "risk_score": risk,
                "reasoning": reasoning
            }
            
            claims_data = [c.dict() for c in claims]
            
            yield f"data: {json.dumps({'type': 'stage2_complete', 'data': evaluations, 'metadata': {'label_to_model': label_to_model, 'claims': claims_data, 'decision': decision}})}\n\n"

            # Stage 3: Synthesize Verified Answer
            yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
            verified_answer = await stage3_synthesize_verified_answer(
                request.content, stage1_results, decision_status, claims, evaluations
            )
            yield f"data: {json.dumps({'type': 'stage3_complete', 'data': {'response': verified_answer}})}\n\n"

            if title_task:
                title = await title_task
                storage.update_conversation_title(conversation_id, title)
                yield f"data: {json.dumps({'type': 'title_complete', 'data': {'title': title}})}\n\n"

            # We would normally save the assistant message here to storage
            # but for demo speed we might just send complete
            
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
