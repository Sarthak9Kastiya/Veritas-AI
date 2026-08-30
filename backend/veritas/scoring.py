from typing import List, Dict, Any
from .schemas import ModelReview, Claim

def calculate_reliability(reviews: List[ModelReview], claims: List[Claim]) -> int:
    if not reviews:
        return 0
        
    avg_reliability = sum(r.overall_reliability for r in reviews) / len(reviews)
    avg_factual = sum(r.factual_accuracy for r in reviews) / len(reviews)
    avg_reasoning = sum(r.reasoning_quality for r in reviews) / len(reviews)
    avg_context = sum(r.context_completeness for r in reviews) / len(reviews)
    avg_confidence = sum(r.confidence for r in reviews) / len(reviews)
    
    # Base score is weighted average
    base_score = (
        avg_reliability * 0.3 +
        avg_factual * 0.3 +
        avg_reasoning * 0.2 +
        avg_context * 0.1 +
        avg_confidence * 0.1
    )
    
    # Penalize for disputed or likely false claims
    penalty = 0
    for claim in claims:
        if claim.status == "DISPUTED":
            penalty += 10
        elif claim.status == "LIKELY_FALSE":
            penalty += 20
            
    # Penalize for unresolved high severity issues
    for review in reviews:
        for issue in review.issues:
            if issue.severity == "high" and issue.type == "factual_error":
                penalty += 15
                
    final_score = max(0, min(100, int(base_score - penalty)))
    return final_score

def calculate_risk(reviews: List[ModelReview]) -> int:
    if not reviews:
        return 100
        
    avg_bias_risk = sum(r.bias_risk for r in reviews) / len(reviews)
    avg_safety_risk = sum(r.safety_risk for r in reviews) / len(reviews)
    
    base_risk = (avg_bias_risk * 0.4 + avg_safety_risk * 0.6)
    
    # Add flat risk for high severity issues
    extra_risk = 0
    for review in reviews:
        for issue in review.issues:
            if issue.severity == "high":
                if issue.type in ["safety", "bias"]:
                    extra_risk += 30
                else:
                    extra_risk += 15
                    
    final_risk = max(0, min(100, int(base_risk + extra_risk)))
    return final_risk
