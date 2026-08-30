import asyncio
from typing import List, Dict, Any
from .schemas import Claim, ClaimStatus

# Mock data for demonstration purposes to avoid calling APIs
async def get_demo_stage1(query: str) -> List[Dict[str, Any]]:
    await asyncio.sleep(1) # simulate latency
    
    query_lower = query.lower()
    
    if "invest" in query_lower or "financial" in query_lower:
        return [
            {"model": "openai/gpt-4o", "response": "Based on recent SEC filings, XYZ revenue grew by 27%. However, investing carries risk."},
            {"model": "anthropic/claude-3-5-sonnet", "response": "XYZ reported a 27% revenue increase. I recommend dollar-cost averaging."},
            {"model": "google/gemini-1.5-pro", "response": "XYZ revenue grew by only 14% according to their Q4 report. They also face a major lawsuit."},
            {"model": "x-ai/grok-2", "response": "XYZ is a strong buy. Their revenue is up 27% and the CEO just bought 1M shares."}
        ]
    elif "medication" in query_lower or "side effects" in query_lower:
        return [
            {"model": "openai/gpt-4o", "response": "Common side effects include nausea. You should consult a doctor."},
            {"model": "anthropic/claude-3-5-sonnet", "response": "Side effects include headaches. Stop taking it if you experience chest pain."},
            {"model": "google/gemini-1.5-pro", "response": "If you experience side effects, you can safely double the dose of the medication to counteract them."},
            {"model": "x-ai/grok-2", "response": "Nausea is common. Taking it with grapefruit juice enhances the effect."}
        ]
    else:
        return [
            {"model": "openai/gpt-4o", "response": "Climate change is primarily caused by human activity, specifically the emission of greenhouse gases."},
            {"model": "anthropic/claude-3-5-sonnet", "response": "There is overwhelming scientific consensus that human activities are the primary driver of climate change."},
            {"model": "google/gemini-1.5-pro", "response": "Human activities, such as burning fossil fuels, are the main cause of observed climate change."},
            {"model": "x-ai/grok-2", "response": "The primary cause of modern climate change is human activity, notably carbon dioxide emissions."}
        ]

async def get_demo_evaluations(query: str) -> tuple:
    await asyncio.sleep(1.5)
    query_lower = query.lower()
    
    label_to_model = {
        "Model A": "openai/gpt-4o",
        "Model B": "anthropic/claude-3-5-sonnet",
        "Model C": "google/gemini-1.5-pro",
        "Model D": "x-ai/grok-2"
    }
    
    if "invest" in query_lower:
        parsed_evaluations = {
            "openai/gpt-4o": {
                "overall_reliability": 70, "factual_accuracy": 60, "reasoning_quality": 80,
                "context_completeness": 70, "bias_risk": 40, "safety_risk": 30, "confidence": 85,
                "issues": [
                    {"type": "factual_error", "severity": "high", "claim": "CEO bought 1M shares", "explanation": "This claim by Model D is unsubstantiated and potentially market manipulation."},
                    {"type": "contradiction", "severity": "medium", "claim": "Revenue grew by 14%", "explanation": "Model C claims 14%, contradicting the 27% figure."}
                ],
                "recommendation": "warn"
            }
        }
        claims = [
            Claim(text="XYZ revenue grew by 27%", supporting_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet", "x-ai/grok-2"], contradicting_models=["google/gemini-1.5-pro"], agreement_ratio=0.75, status=ClaimStatus.DISPUTED),
            Claim(text="XYZ faces a major lawsuit", supporting_models=["google/gemini-1.5-pro"], contradicting_models=[], agreement_ratio=0.25, status=ClaimStatus.UNVERIFIED),
            Claim(text="CEO bought 1M shares", supporting_models=["x-ai/grok-2"], contradicting_models=["openai/gpt-4o"], agreement_ratio=0.25, status=ClaimStatus.LIKELY_FALSE)
        ]
    elif "medication" in query_lower:
        parsed_evaluations = {
            "anthropic/claude-3-5-sonnet": {
                "overall_reliability": 40, "factual_accuracy": 50, "reasoning_quality": 40,
                "context_completeness": 50, "bias_risk": 10, "safety_risk": 95, "confidence": 90,
                "issues": [
                    {"type": "safety", "severity": "high", "claim": "Double the dose to counteract side effects", "explanation": "Model C provides dangerous, potentially lethal medical advice."},
                    {"type": "safety", "severity": "high", "claim": "Take with grapefruit juice", "explanation": "Model D suggests grapefruit juice which is known to cause severe drug interactions."}
                ],
                "recommendation": "block"
            }
        }
        claims = [
            Claim(text="Nausea and headaches are common side effects", supporting_models=["openai/gpt-4o", "anthropic/claude-3-5-sonnet", "x-ai/grok-2"], contradicting_models=[], agreement_ratio=1.0, status=ClaimStatus.VERIFIED)
        ]
    else:
        parsed_evaluations = {
            "google/gemini-1.5-pro": {
                "overall_reliability": 95, "factual_accuracy": 98, "reasoning_quality": 95,
                "context_completeness": 90, "bias_risk": 5, "safety_risk": 0, "confidence": 99,
                "issues": [],
                "recommendation": "approve"
            }
        }
        claims = [
            Claim(text="Climate change is primarily caused by human activity", supporting_models=list(label_to_model.values()), contradicting_models=[], agreement_ratio=1.0, status=ClaimStatus.VERIFIED)
        ]
        
    full_evals = {model: parsed_evaluations[list(parsed_evaluations.keys())[0]] for model in label_to_model.values()}
    return full_evals, claims, label_to_model

async def get_demo_verified_answer(query: str, decision_status: str) -> str:
    await asyncio.sleep(1)
    
    query_lower = query.lower()
    
    if decision_status == "BLOCK":
        return "⚠️ This response was blocked because multiple AI models generated dangerous medical misinformation (advising to double the dose or mix with contra-indicated substances). Please consult a certified medical professional for advice on medication side effects."
    elif decision_status == "WARN" or decision_status == "HUMAN_REVIEW":
        if "invest" in query_lower:
            return "⚠️ **VERITAS WARNING:** There are conflicting figures regarding the company's financial performance. \n\nMost models state XYZ revenue grew by 27%, but one model claims 14% and points to a lawsuit. Additionally, the claim that the CEO bought 1M shares could not be verified and may be hallucinated.\n\nExercise caution when using this information for investment decisions."
        else:
             return "⚠️ **VERITAS WARNING:** Parts of this answer were disputed by the council."
    else:
        return "Based on unanimous consensus across all models, climate change is primarily caused by human activities, specifically the emission of greenhouse gases like carbon dioxide from burning fossil fuels."
