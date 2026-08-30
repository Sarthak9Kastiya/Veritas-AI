import json
import asyncio
import re
from typing import List, Dict, Any, Tuple
from ..openrouter import query_models_parallel, query_model
from ..config import COUNCIL_MODELS, CHAIRMAN_MODEL
from .schemas import ModelReview, Claim, ClaimStatus, Issue

async def cross_model_verification(
    user_query: str, 
    stage1_results: List[Dict[str, Any]]
) -> Tuple[Dict[str, Dict[str, Any]], List[Claim], Dict[str, str]]:
    
    # Create anonymized labels for responses (Model A, Model B, etc.)
    labels = [chr(65 + i) for i in range(len(stage1_results))]
    label_to_model = {f"Model {label}": result['model'] for label, result in zip(labels, stage1_results)}
    
    responses_text = "\n\n".join([
        f"Model {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])
    
    verification_prompt = f"""You are Veritas, an independent AI verification system.
Evaluate the following AI responses to the user's question.

Question: {user_query}

Anonymized Responses:
{responses_text}

Task: Perform a deep verification of ALL responses. Do not just rank them. Identify factual errors, bias, missing context, and safety risks.

You MUST respond with ONLY a valid JSON object matching this schema. Do not include markdown code blocks or any other text outside the JSON.

{{
  "overall_reliability": (0-100),
  "factual_accuracy": (0-100),
  "reasoning_quality": (0-100),
  "context_completeness": (0-100),
  "bias_risk": (0-100),
  "safety_risk": (0-100),
  "confidence": (0-100),
  "issues": [
    {{
      "type": "factual_error|contradiction|missing_context|bias|safety|unsupported_claim",
      "severity": "high|medium|low",
      "claim": "The specific claim made in a response",
      "explanation": "Why this is an issue and which model(s) made it"
    }}
  ],
  "recommendation": "approve|warn|block|human_review",
  "extracted_claims": [
    "A factual claim made by one or more models (e.g., 'Company X revenue grew by 20%')",
    ...
  ]
}}
"""
    messages = [{"role": "user", "content": verification_prompt}]
    
    # Get evaluations from all council models in parallel
    evaluations = await query_models_parallel(COUNCIL_MODELS, messages)
    
    parsed_evaluations = {}
    all_extracted_claims = []
    
    for model, response in evaluations.items():
        if response is not None:
            content = response.get('content', '')
            # Try to parse JSON
            try:
                # Strip markdown if present
                content = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', content, flags=re.DOTALL).strip()
                data = json.loads(content)
                parsed_evaluations[model] = data
                all_extracted_claims.extend(data.get("extracted_claims", []))
            except json.JSONDecodeError:
                print(f"Failed to parse JSON from {model}")
                # Provide a fallback
                parsed_evaluations[model] = {
                    "overall_reliability": 50,
                    "factual_accuracy": 50,
                    "reasoning_quality": 50,
                    "context_completeness": 50,
                    "bias_risk": 50,
                    "safety_risk": 50,
                    "confidence": 50,
                    "issues": [{"type": "factual_error", "severity": "medium", "claim": "N/A", "explanation": "Failed to parse evaluation output"}],
                    "recommendation": "warn",
                    "extracted_claims": []
                }
                
    # Basic claim deduplication and voting logic (simplified for prototype)
    claims = []
    unique_claims = list(set([c for c in all_extracted_claims if len(c.split()) > 3][:5])) # Take up to 5 meaningful claims
    
    for claim_text in unique_claims:
        total_evaluators = len(parsed_evaluations)
        if total_evaluators == 0:
            continue
            
        # Check if this claim is targeted by any issues (factual_error or contradiction)
        claim_issues = []
        for eval_data in parsed_evaluations.values():
            for issue in eval_data.get('issues', []):
                # Simple heuristic: if the claim text overlaps significantly with the issue claim
                if claim_text.lower() in issue.get('claim', '').lower() or issue.get('claim', '').lower() in claim_text.lower():
                    claim_issues.append(issue)
                    
        has_high_sev = any(i['severity'] == 'high' for i in claim_issues)
        has_med_sev = any(i['severity'] == 'medium' for i in claim_issues)
        
        # If there are issues, it reduces the supporting models
        if has_high_sev:
            supporting = list(label_to_model.values())[:1]
        elif has_med_sev or len(claim_issues) > 0:
            supporting = list(label_to_model.values())[:max(1, total_evaluators - len(claim_issues))]
        else:
            supporting = list(label_to_model.values())
            
        contradicting = [m for m in label_to_model.values() if m not in supporting]
        
        agreement_ratio = len(supporting) / max(1, (len(supporting) + len(contradicting)))
        
        status = ClaimStatus.VERIFIED
        if agreement_ratio < 0.5:
            status = ClaimStatus.DISPUTED
        elif agreement_ratio < 0.8:
            status = ClaimStatus.LIKELY_TRUE
            
        claims.append(Claim(
            text=claim_text,
            supporting_models=supporting,
            contradicting_models=contradicting,
            agreement_ratio=agreement_ratio,
            status=status
        ))
        
    return parsed_evaluations, claims, label_to_model

async def generate_verified_answer(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    decision_status: str,
    claims: List[Claim],
    issues: List[Dict[str, Any]]
) -> str:
    
    stage1_text = "\n\n".join([f"Model: {r['model']}\nResponse: {r['response']}" for r in stage1_results])
    claims_text = "\n".join([f"- {c.text} (Status: {c.status.value})" for c in claims])
    issues_text = "\n".join([f"- {i['severity'].upper()}: {i['explanation']}" for i in issues])
    
    prompt = f"""You are Veritas, compiling the final VERIFIED response for the user.

Original Question: {user_query}

Original Model Responses:
{stage1_text}

Verification Status: {decision_status}
Claims Analysis:
{claims_text}
Identified Issues:
{issues_text}

Task: Write the final answer.
- If the decision is APPROVE, provide a clear, synthesized answer based on the models.
- If the decision is WARN, provide the answer but EXPLICITLY qualify unsupported or disputed claims inline. Add a warning disclaimer at the top.
- If the decision is BLOCK or HUMAN_REVIEW, provide a brief explanation of why the answer cannot be provided safely, and summarize the safe portions if any.
"""
    messages = [{"role": "user", "content": prompt}]
    response = await query_model(CHAIRMAN_MODEL, messages)
    
    if response:
        return response.get('content', '')
    return "The verification pipeline successfully analyzed the claims, but the final synthesis model failed to respond (likely due to OpenRouter API limits or insufficient credits). Please review the original model responses and Veritas Decision card."
