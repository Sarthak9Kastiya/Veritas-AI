from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class Severity(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class IssueType(str, Enum):
    factual_error = "factual_error"
    contradiction = "contradiction"
    missing_context = "missing_context"
    bias = "bias"
    safety = "safety"
    unsupported_claim = "unsupported_claim"

class Recommendation(str, Enum):
    approve = "approve"
    warn = "warn"
    block = "block"
    human_review = "human_review"

class Issue(BaseModel):
    type: str
    severity: str
    claim: str
    explanation: str

class ModelReview(BaseModel):
    overall_reliability: int = Field(..., ge=0, le=100)
    factual_accuracy: int = Field(..., ge=0, le=100)
    reasoning_quality: int = Field(..., ge=0, le=100)
    context_completeness: int = Field(..., ge=0, le=100)
    bias_risk: int = Field(..., ge=0, le=100)
    safety_risk: int = Field(..., ge=0, le=100)
    confidence: int = Field(..., ge=0, le=100)
    issues: List[Issue] = []
    recommendation: Recommendation

class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    LIKELY_TRUE = "LIKELY_TRUE"
    DISPUTED = "DISPUTED"
    UNVERIFIED = "UNVERIFIED"
    LIKELY_FALSE = "LIKELY_FALSE"

class Claim(BaseModel):
    text: str
    supporting_models: List[str]
    contradicting_models: List[str]
    agreement_ratio: float
    status: ClaimStatus

class RiskCategory(str, Enum):
    PERFORMANCE = "PERFORMANCE"
    RESPONSIBILITY = "RESPONSIBILITY"
    CONTEXT = "CONTEXT"
    COST = "COST"

class Decision(BaseModel):
    status: str  # "APPROVE", "WARN", "BLOCK", "HUMAN_REVIEW"
    reliability_score: int
    risk_score: int
    reasoning: List[str]
    verified_answer: str

class VerificationSummary(BaseModel):
    query: str
    responses: List[Dict[str, Any]]
    model_evaluations: Dict[str, Dict[str, Any]]
    claims: List[Claim]
    decision: Decision
    cost_metrics: Dict[str, Any]
