from typing import List, Dict, Any, Tuple
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL, USE_DEMO_MODE
from .veritas import cross_model_verification, generate_verified_answer, calculate_reliability, calculate_risk, determine_decision, ModelReview
from .veritas.demo import get_demo_stage1, get_demo_evaluations, get_demo_verified_answer

async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    if USE_DEMO_MODE:
        return await get_demo_stage1(user_query)
        
    messages = [{"role": "user", "content": user_query}]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)
    
    stage1_results = []
    for model, response in responses.items():
        if response is not None:
            stage1_results.append({
                "model": model,
                "response": response.get('content', '')
            })
    return stage1_results

async def stage2_verify_responses(user_query: str, stage1_results: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Any], Dict[str, str]]:
    if USE_DEMO_MODE:
        return await get_demo_evaluations(user_query)
        
    return await cross_model_verification(user_query, stage1_results)

async def stage3_synthesize_verified_answer(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    decision_status: str,
    claims: List[Any],
    evaluations: Dict[str, Any]
) -> str:
    if USE_DEMO_MODE:
        return await get_demo_verified_answer(user_query, decision_status)
        
    # Extract high/medium severity issues to pass to the generator
    all_issues = []
    for eval_data in evaluations.values():
        all_issues.extend(eval_data.get('issues', []))
        
    # Deduplicate issues loosely by claim for the prompt
    unique_issues = {i['claim']: i for i in all_issues if i.get('severity') in ['high', 'medium']}.values()
    
    return await generate_verified_answer(user_query, stage1_results, decision_status, claims, list(unique_issues))

async def generate_conversation_title(user_query: str) -> str:
    messages = [{"role": "user", "content": f"Generate a very short title (3-5 words) for: {user_query}"}]
    response = await query_model("google/gemini-3.5-flash-lite", messages, timeout=10.0)
    if response:
        return response.get('content', 'New Verification').strip('"\'')[:50]
    return "New Verification"
