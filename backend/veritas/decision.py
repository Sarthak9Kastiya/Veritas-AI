from typing import List, Dict, Any, Tuple
from .schemas import Decision, ModelReview, Claim

def determine_decision(reliability: int, risk: int, reviews: List[ModelReview], claims: List[Claim]) -> Tuple[str, List[str]]:
    reasoning = []
    
    # Check for critical safety issues
    critical_safety = False
    for r in reviews:
        for issue in r.issues:
            if issue.type == "safety" and issue.severity == "high":
                critical_safety = True
                
    if critical_safety:
        reasoning.append("Critical safety issue detected by reviewers.")
        return "BLOCK", reasoning
        
    if risk >= 70 or (risk >= 40 and reliability < 50):
        if risk >= 70:
            reasoning.append("High risk score indicates potentially dangerous or severely biased content.")
        if reliability < 50:
            reasoning.append("Low reliability score combined with moderate risk requires human oversight.")
        return "HUMAN_REVIEW", reasoning
        
    # Count disputed claims
    disputed_claims = sum(1 for c in claims if c.status == "DISPUTED")
    
    if reliability < 70 or disputed_claims > 0 or risk >= 30:
        if reliability < 70:
            reasoning.append("Moderate reliability score suggests some factual or reasoning weaknesses.")
        if disputed_claims > 0:
            reasoning.append(f"{disputed_claims} claim(s) were disputed among models.")
        if risk >= 30:
            reasoning.append("Elevated risk score warrants a warning.")
        return "WARN", reasoning
        
    reasoning.append("High reliability and low risk. No major contradictions found.")
    return "APPROVE", reasoning
