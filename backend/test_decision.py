from backend.veritas.schemas import ModelReview, Claim, ClaimStatus, Issue, Recommendation
from backend.veritas.decision import determine_decision
from backend.veritas.scoring import calculate_reliability, calculate_risk

def test_critical_safety_block():
    review = ModelReview(
        overall_reliability=10, factual_accuracy=10, reasoning_quality=10,
        context_completeness=10, bias_risk=10, safety_risk=95, confidence=90,
        issues=[Issue(type="safety", severity="high", claim="xyz", explanation="abc")],
        recommendation=Recommendation.block
    )
    reliability = calculate_reliability([review], [])
    risk = calculate_risk([review])
    decision, reasoning = determine_decision(reliability, risk, [review], [])
    assert decision == "BLOCK"

def test_high_risk_low_reliability_human_review():
    review = ModelReview(
        overall_reliability=30, factual_accuracy=30, reasoning_quality=30,
        context_completeness=30, bias_risk=80, safety_risk=60, confidence=50,
        issues=[Issue(type="bias", severity="high", claim="xyz", explanation="abc")],
        recommendation=Recommendation.human_review
    )
    reliability = calculate_reliability([review], [])
    risk = calculate_risk([review])
    decision, reasoning = determine_decision(reliability, risk, [review], [])
    assert decision == "HUMAN_REVIEW"

def test_moderate_reliability_warn():
    review = ModelReview(
        overall_reliability=65, factual_accuracy=60, reasoning_quality=70,
        context_completeness=60, bias_risk=10, safety_risk=10, confidence=70,
        issues=[],
        recommendation=Recommendation.warn
    )
    reliability = calculate_reliability([review], [])
    risk = calculate_risk([review])
    decision, reasoning = determine_decision(reliability, risk, [review], [])
    assert decision == "WARN"
    
def test_disputed_claim_warn():
    review = ModelReview(
        overall_reliability=90, factual_accuracy=90, reasoning_quality=90,
        context_completeness=90, bias_risk=10, safety_risk=10, confidence=90,
        issues=[],
        recommendation=Recommendation.approve
    )
    claim = Claim(
        text="Disputed fact", supporting_models=["A"], contradicting_models=["B"],
        agreement_ratio=0.5, status=ClaimStatus.DISPUTED
    )
    reliability = calculate_reliability([review], [claim])
    risk = calculate_risk([review])
    decision, reasoning = determine_decision(reliability, risk, [review], [claim])
    assert decision == "WARN"

def test_approve():
    review = ModelReview(
        overall_reliability=95, factual_accuracy=95, reasoning_quality=95,
        context_completeness=95, bias_risk=5, safety_risk=0, confidence=95,
        issues=[],
        recommendation=Recommendation.approve
    )
    claim = Claim(
        text="Verified fact", supporting_models=["A", "B"], contradicting_models=[],
        agreement_ratio=1.0, status=ClaimStatus.VERIFIED
    )
    reliability = calculate_reliability([review], [claim])
    risk = calculate_risk([review])
    decision, reasoning = determine_decision(reliability, risk, [review], [claim])
    assert decision == "APPROVE"
