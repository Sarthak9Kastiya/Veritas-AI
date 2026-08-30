# Veritas AI: Verification & Trust Layer

**"Don't Trust AI. Verify It."**

Veritas is an enterprise-grade AI verification, control, and auditing layer designed to sit between foundation Large Language Models (LLMs) and end users. It acts as an independent auditor, running multiple foundation models in parallel to peer-review outputs, identify hallucinations, catch bias, and prevent dangerous advice before it reaches the user.

This project was built from scratch for the **Accenture Innovation Challenge 2026**.

---

## 🚀 The Core Problem

As enterprises deploy generative AI, they face critical risks:
1. **Hallucinations:** AI confidently presenting false or speculative information as fact.
2. **Safety & Liability Risks:** AI dispensing dangerous medical, financial, or legal advice that could lead to catastrophic corporate liability.
3. **Bias & Subjectivity:** Hidden biases creeping into sensitive decisions, violating corporate neutrality or regulatory laws (e.g., EU AI Act).
4. **Lack of Ground Truth:** Most enterprises do not have real-time, deterministic "ground truth" databases to check an LLM's generative output against.

Relying on a single AI model is a single point of failure. **Veritas solves this by treating AI verification as a consensus problem.** By routing queries through a multi-vendor "council" of AI models, Veritas forces models to cross-examine and fact-check each other in real-time, functioning as a highly scalable "AI-as-Judge" framework.

---

## 🧠 System Architecture

The Veritas verification pipeline operates in three distinct, deterministic stages, functioning as an inline middleware between the user and the final output:

### Stage 1: Parallel Generation
When a user submits a query, Veritas does not rely on one single model. The backend acts as a dynamic router, fanning out the request concurrently to a diverse panel of foundation models (e.g., Google Gemini, OpenAI GPT, Anthropic Claude, xAI Grok).
- **Latency Optimization:** These network requests are executed asynchronously in parallel to ensure the verification overhead is kept to an absolute minimum.
- **Diversity:** By querying models from entirely different corporate vendors and training architectures, Veritas avoids vendor-specific blind spots.

### Stage 2: Cross-Model Verification (AI-as-Judge)
Once the initial responses are collected, they are anonymized (e.g., "Model A", "Model B"). Veritas then feeds these responses back into the models, asking them to act as independent reviewers of each other. Each model outputs a strict, deterministic JSON schema evaluating the others on five core metrics:
- **Factual Accuracy** (0-100)
- **Reasoning Quality** (0-100)
- **Context Completeness** (0-100)
- **Bias Risk** (0-100)
- **Safety Risk** (0-100)

**Claim Extraction:** During this stage, models actively extract individual factual claims and map them to specific identified issues (`factual_error`, `contradiction`, `missing_context`, `bias`, `safety`). The Veritas backend mathematically aggregates these claims to calculate an **Agreement Ratio**, mathematically classifying each claim as `VERIFIED`, `LIKELY_TRUE`, or `DISPUTED`.

### Stage 3: Deterministic Policy Engine
Based on the JSON evaluations from Stage 2, the Veritas Policy Engine calculates an aggregate **Reliability Score (0-100)** and **Risk Score (0-100)**. It then routes the response through a strict, deterministic rules engine:

- 🟢 **APPROVE:** Triggered by high reliability, low risk, and strong consensus. The Chairman model synthesizes a clean, verified answer for the user.
- 🟡 **WARN:** Triggered by mediocre reliability or highly disputed claims. The Chairman model highlights the disagreements and provides explicit inline warnings, protecting the user from speculation.
- 🟠 **HUMAN REVIEW:** Triggered by extreme bias or subjectivity. The system requires a human corporate auditor to intervene, as the AI cannot guarantee neutrality.
- 🔴 **BLOCK:** Triggered if any model detects a high-severity safety risk. The system applies a massive penalty weight to the Risk Score and immediately refuses to output the dangerous advice.

---

## 🛠 Engineering Deep Dive

### The Backend (Python / FastAPI)
The backend is the engine of the Veritas Control Plane, designed for high throughput and structured data handling.
- **Framework:** Built on **FastAPI** running on **Uvicorn**, ensuring that the heavy network I/O of talking to 4-5 different APIs simultaneously does not block the main event loop.
- **Schema Enforcement:** Utilizes **Pydantic** to strictly enforce the complex JSON outputs generated during the Stage 2 Cross-Model Verification. If a model hallucinates its schema, the backend dynamically falls back to safe defaults to prevent pipeline collapse.
- **Model Orchestration:** Uses `httpx` to handle concurrent asynchronous networking to the OpenRouter API, which acts as a unified hub connecting to the various LLMs.
- **Server-Sent Events (SSE):** The backend streams its current execution state (`stage1_complete`, `stage2_complete`, `stage3_complete`) back to the frontend in real-time, delivering calculated payloads for latency, cost, and extracted claims as soon as they are mathematically resolved.

### The Frontend (React / Vite)
The frontend is built to resemble an Enterprise-Grade Control Plane for AI Governance Officers and end-users.
- **Framework:** **React 18** built with **Vite** for rapid hot-module replacement and optimized production builds.
- **State Management:** Dynamically parses incoming SSE streams to update the UI sequentially, preventing the user from waiting in the dark while the verification pipeline runs.
- **Visual Claim Analysis:** The UI dynamically renders custom status bars (`VERIFIED`, `DISPUTED`) based on the Agreement Ratios returned by the backend.
- **Cost & Latency Telemetry:** Includes a real-time metrics dashboard to give enterprise stakeholders full visibility into the API token cost and latency footprint of the inline verification layer.

---

## ⚙️ Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- An active [OpenRouter](https://openrouter.ai/) API Key

### 1. Clone the Repository
```bash
git clone https://github.com/Sarthak9Kastiya/Veritas-AI.git
cd Veritas-AI
```

### 2. Backend Environment Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install fastapi uvicorn httpx pydantic python-dotenv

# Set up your environment variables
cp .env.example .env
```
Edit the `.env` file and insert your OpenRouter API key.
```env
OPENROUTER_API_KEY="sk-or-v1-your-key-here"
USE_DEMO_MODE="false"
```

Start the backend server:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

### 3. Frontend Dashboard Setup

Open a new terminal window:
```bash
cd Veritas-AI/frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

Navigate to **`http://localhost:5173`** in your browser to access the Veritas Control Plane.

---

## ⚖️ License
MIT License.
