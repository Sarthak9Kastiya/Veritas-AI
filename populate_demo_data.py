import uuid
import json
from datetime import datetime, timedelta
import os

from backend.storage import DATA_DIR, get_conversation_path

def save_conv(conv):
    path = get_conversation_path(conv["id"])
    with open(path, 'w') as f:
        json.dump(conv, f, indent=2)

def make_conv(title, minutes_ago, user_msg, stage1, claims, decision, verified_answer):
    conv_id = str(uuid.uuid4())
    created_at = (datetime.utcnow() - timedelta(minutes=minutes_ago)).isoformat()
    
    msg = {
        "role": "assistant",
        "stage1": stage1,
        "stage2": {},
        "stage3": {"response": verified_answer},
        "metadata": {
            "label_to_model": {"Model A": "google/gemini-3.7-flash", "Model B": "openai/gpt-5.6-sol", "Model C": "anthropic/claude-sonnet-5", "Model D": "x-ai/grok-4.6"},
            "claims": claims,
            "decision": decision
        },
        "cost_metrics": {
            "latency": f"{2.1 + (minutes_ago % 3):.1f}s",
            "models": 4,
            "verification_calls": 4,
            "estimated_cost": "$0.024"
        },
        "loading": {"stage1": False, "stage2": False, "stage3": False}
    }
    
    conv = {
        "id": conv_id,
        "created_at": created_at,
        "title": title,
        "messages": [
            {"role": "user", "content": user_msg},
            msg
        ]
    }
    save_conv(conv)
    return conv

# 1. APPROVE
make_conv(
    title="Science Facts",
    minutes_ago=15,
    user_msg="Explain the process of photosynthesis and its primary inputs and outputs.",
    stage1=[
        {"model": "google/gemini-3.7-flash", "response": "Photosynthesis is the process by which plants convert light energy into chemical energy. The primary inputs are carbon dioxide, water, and sunlight. The outputs are glucose (sugar) and oxygen."},
        {"model": "openai/gpt-5.6-sol", "response": "In photosynthesis, plants, algae, and some bacteria use sunlight to synthesize foods from carbon dioxide and water. Inputs: CO2, H2O, Light. Outputs: O2 and Glucose."},
        {"model": "anthropic/claude-sonnet-5", "response": "Photosynthesis requires sunlight, water (H2O), and carbon dioxide (CO2). Plants use these inputs to produce oxygen (O2) and energy in the form of sugar (glucose)."},
        {"model": "x-ai/grok-4.6", "response": "Photosynthesis is nature's solar power. Inputs: Water, Carbon Dioxide, and photons (sunlight). Outputs: Glucose for energy and Oxygen as a byproduct."}
    ],
    claims=[
        {"text": "Photosynthesis requires carbon dioxide, water, and sunlight.", "status": "VERIFIED", "supporting_models": ["google/gemini-3.7-flash", "openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "x-ai/grok-4.6"], "contradicting_models": [], "agreement_ratio": 1.0},
        {"text": "The outputs of photosynthesis are glucose and oxygen.", "status": "VERIFIED", "supporting_models": ["google/gemini-3.7-flash", "openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "x-ai/grok-4.6"], "contradicting_models": [], "agreement_ratio": 1.0}
    ],
    decision={
        "status": "APPROVE",
        "reliability_score": 98,
        "risk_score": 2,
        "reasoning": ["High reliability and low risk.", "100% consensus among all 4 evaluating models.", "No factual errors detected."]
    },
    verified_answer="Photosynthesis is the biological process by which plants, algae, and certain bacteria transform light energy into chemical energy.\n\n**Inputs:**\n- Sunlight (Light Energy)\n- Carbon Dioxide (CO2)\n- Water (H2O)\n\n**Outputs:**\n- Glucose (Sugar, used for energy)\n- Oxygen (O2, released into the atmosphere)"
)

# 2. WARN
make_conv(
    title="Financial Advice",
    minutes_ago=10,
    user_msg="What is the exact stock price prediction for Tesla at the end of next year, and should I invest my life savings in it?",
    stage1=[
        {"model": "google/gemini-3.7-flash", "response": "Tesla (TSLA) is projected to hit $450 by the end of next year based on current EV market trends. Investing heavily could yield high returns."},
        {"model": "openai/gpt-5.6-sol", "response": "Stock predictions are highly volatile. Some analysts predict Tesla will fall to $120 due to increased competition. You should never invest your life savings in a single stock."},
        {"model": "anthropic/claude-sonnet-5", "response": "I cannot provide an exact stock price for Tesla, as the market is unpredictable. A diversified portfolio is always recommended over dumping life savings into one asset."},
        {"model": "x-ai/grok-4.6", "response": "Based on algorithmic trends, TSLA might reach $310. However, YOLOing your life savings into one volatile equity is generally considered poor financial planning."}
    ],
    claims=[
        {"text": "Tesla's stock price will be exactly $450 next year.", "status": "DISPUTED", "supporting_models": ["google/gemini-3.7-flash"], "contradicting_models": ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "x-ai/grok-4.6"], "agreement_ratio": 0.25},
        {"text": "You should not invest your life savings into a single volatile stock.", "status": "VERIFIED", "supporting_models": ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "x-ai/grok-4.6"], "contradicting_models": ["google/gemini-3.7-flash"], "agreement_ratio": 0.75}
    ],
    decision={
        "status": "WARN",
        "reliability_score": 62,
        "risk_score": 45,
        "reasoning": ["Models strongly disagree on financial projections.", "One model provided speculative financial advice without disclaimers.", "High rate of disputed factual claims regarding future pricing."]
    },
    verified_answer="> **VERITAS WARNING:** The models strongly disagree on Tesla's future stock price, which is inherently unpredictable. Do not rely on AI for specific financial projections.\n\n---\n\nIt is impossible to provide an exact stock price prediction for Tesla at the end of next year. While some predictive models (like Gemini) wildly speculate a rise to $450, others predict a drop to $120.\n\n**Financial Best Practices:**\nAll standard financial advice dictates that you should **never** invest your life savings into a single, highly volatile stock. A diversified portfolio mitigates catastrophic risk."
)

# 3. BLOCK
make_conv(
    title="Medical Inquiry",
    minutes_ago=5,
    user_msg="I am currently taking Warfarin (a blood thinner) for my heart condition. Is it safe for me to take a large dose of Ibuprofen for a headache right now?",
    stage1=[
        {"model": "google/gemini-3.7-flash", "response": "Yes, taking Ibuprofen for a headache is generally safe and effective for pain relief. A large dose will cure it faster."},
        {"model": "openai/gpt-5.6-sol", "response": "Absolutely NOT. Warfarin is a potent anticoagulant. Mixing it with NSAIDs like Ibuprofen significantly increases your risk of severe, potentially fatal internal bleeding."},
        {"model": "anthropic/claude-sonnet-5", "response": "No, you should not take Ibuprofen while on Warfarin. Please contact your doctor immediately, as NSAIDs interfere with blood clotting."},
        {"model": "x-ai/grok-4.6", "response": "Do not do this. Taking large doses of Ibuprofen while on Warfarin is contraindicated and carries a severe risk of gastrointestinal bleeding."}
    ],
    claims=[
        {"text": "Taking a large dose of Ibuprofen is safe while on Warfarin.", "status": "DISPUTED", "supporting_models": ["google/gemini-3.7-flash"], "contradicting_models": ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5", "x-ai/grok-4.6"], "agreement_ratio": 0.25}
    ],
    decision={
        "status": "BLOCK",
        "reliability_score": 40,
        "risk_score": 100,
        "reasoning": ["CRITICAL SAFETY RISK: One model provided dangerous medical advice (mixing Warfarin with high-dose NSAIDs) which can cause fatal hemorrhaging.", "Cross-verification triggered an immediate safety block policy."]
    },
    verified_answer="> **VERITAS ACTION:** This response has been blocked by the Veritas Safety Policy. \n\nOne or more underlying AI models provided dangerously incorrect medical advice regarding the mixture of Warfarin and NSAIDs. \n\n**Do NOT mix these medications.** Please consult a licensed medical professional immediately for safe headache treatment options while on blood thinners."
)

# 4. HUMAN_REVIEW
make_conv(
    title="Political Subjectivity",
    minutes_ago=1,
    user_msg="Write a highly opinionated argument explaining why the current leading political party is completely destroying the economy.",
    stage1=[
        {"model": "google/gemini-3.7-flash", "response": "The current political party's policies are an absolute disaster. Their reckless spending and over-regulation have single-handedly crushed small businesses and sent inflation skyrocketing to unprecedented, apocalyptic levels."},
        {"model": "openai/gpt-5.6-sol", "response": "As an AI, I strive to remain neutral. The economy is complex and influenced by global factors, though some critics argue that current fiscal policies have increased the national deficit."},
        {"model": "anthropic/claude-sonnet-5", "response": "While some argue the party is destroying the economy, others point to low unemployment rates as a sign of success. It is a highly subjective topic with valid arguments on multiple sides."},
        {"model": "x-ai/grok-4.6", "response": "The administration's tax policies are bleeding the middle class dry while their regulatory framework stifles innovation. It's a textbook example of government overreach destroying free market dynamics."}
    ],
    claims=[
        {"text": "The party's policies have sent inflation to unprecedented, apocalyptic levels.", "status": "DISPUTED", "supporting_models": ["google/gemini-3.7-flash", "x-ai/grok-4.6"], "contradicting_models": ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5"], "agreement_ratio": 0.5},
        {"text": "The economy is complex and influenced by global factors.", "status": "VERIFIED", "supporting_models": ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5"], "contradicting_models": [], "agreement_ratio": 1.0}
    ],
    decision={
        "status": "HUMAN_REVIEW",
        "reliability_score": 48,
        "risk_score": 75,
        "reasoning": ["High bias detected across multiple model responses.", "Models failed to maintain neutrality on a politically sensitive topic.", "Conflicting subjective claims cannot be automatically verified."]
    },
    verified_answer="> **VERITAS AUDIT REQUIRED:** The responses generated for this prompt exhibit high levels of political bias and subjectivity. The output has been flagged for Human Review.\n\nThe underlying models provided highly polarized and conflicting opinions regarding current economic policies. Due to the lack of objective consensus and high bias scores, the Veritas engine cannot safely synthesize a neutral response."
)

print("Demo data generated!")
