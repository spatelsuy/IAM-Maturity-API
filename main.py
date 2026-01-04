import os
import re
import requests
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import Response
import yaml

load_dotenv()

# -------------------------------------------------
# App Setup
# -------------------------------------------------

app = FastAPI(title="IAM General Context Assessment Agent (Groq)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Environment
# -------------------------------------------------

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("PROMPT_GROQ_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("PROMPT_GROQ_KEY not found in environment variables")

# -------------------------------------------------
# Request Model (YAML input as string)
# -------------------------------------------------

class AgentRequest(BaseModel):
    user_name: str
    general_question: str   # YAML string

# -------------------------------------------------
# SYSTEM CONTEXT (YAML → embedded as system prompt)
# -------------------------------------------------

SYSTEM_CONTEXT = """
You are an IAM General Context Assessment Agent specialized in the Banking industry.

Your task is to evaluate a General IAM governance question and determine
how the answer influences downstream IAM domain assessments.

Follow these instructions:
1. Interpret the user's selected maturity level conservatively.
2. Validate the selection against banking regulatory expectations.
3. Identify foundational governance capabilities established by this answer.
4. Produce structured GEN context signals for downstream domain evaluation.
5. Do NOT inflate maturity beyond what is explicitly supported.
6. Put the response in YAML format ONLY.

agent:
  name: IAM General Context Agent
  version: v1.0

context:
  maturity_model:
    levels:
      - level: 1
        definition: Ad-hoc, manual, inconsistent
      - level: 2
        definition: Partially implemented, limited consistency
      - level: 3
        definition: Defined, documented, repeatable
      - level: 4
        definition: Managed, integrated, measured
      - level: 5
        definition: Optimized, automated, continuously improved

  banking_principles:
    - Certifications must be authoritative, enforced, and auditable
    - Risk-based exception handling is mandatory for Level 4+
    - Manual or spreadsheet-based certifications cannot exceed Level 3
    - Evidence and integration determine confidence

RESPONSE FORMAT (YAML ONLY):

gen_context_update:
  governance_maturity_signal: ""
  certification_integration:
    authoritative_data_used: true|false
    role_alignment_enforced: true|false
  exception_handling:
    risk_assessed: true|false
    documented: true|false
  audit_readiness_level: ""

domain_influence:
  access_governance: ""
  monitoring_and_audit: ""

assessment_rationale:
  - ""

confidence_level: ""
"""

# -------------------------------------------------
# Groq Processing
# -------------------------------------------------

def process_with_groq(question_yaml: Dict[str, Any]) -> Dict[str, Any]:
    try:
        user_prompt = yaml.dump(
            {"general_question": question_yaml},
            sort_keys=False
        )

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_CONTEXT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.text}")

        data = response.json()
        raw_output = data["choices"][0]["message"]["content"]

        # Clean markdown if present
        cleaned = raw_output.replace("```yaml", "").replace("```", "").strip()

        # Parse YAML safely
        parsed_yaml = yaml.safe_load(cleaned)

        if not isinstance(parsed_yaml, dict):
            raise Exception("LLM response is not valid YAML")

        return parsed_yaml

    except Exception as e:
        return {
            "gen_context_update": {
                "governance_maturity_signal": "Unknown",
                "certification_integration": {
                    "authoritative_data_used": False,
                    "role_alignment_enforced": False
                },
                "exception_handling": {
                    "risk_assessed": False,
                    "documented": False
                },
                "audit_readiness_level": "Low"
            },
            "domain_influence": {
                "access_governance": "Unable to determine due to processing error",
                "monitoring_and_audit": "Unable to determine due to processing error"
            },
            "assessment_rationale": [f"Agent processing error: {str(e)}"],
            "confidence_level": "Low"
        }

# -------------------------------------------------
# API Endpoint
# -------------------------------------------------

@app.post("/assess")
def assess_question(request: AgentRequest):
    try:
        question_wrapper = yaml.safe_load(request.general_question)
        print("***question_wrapper***", question_wrapper)
        if "general_question" in question_wrapper:
            question_data = question_wrapper["general_question"]
        else:
            raise HTTPException(status_code=400, detail="Missing general_question key")

        assessment = process_with_groq(question_data)

        yaml_output = yaml.dump(
            assessment,
            sort_keys=False,
            default_flow_style=False
        )

        return Response(
            content=yaml_output,
            media_type="text/yaml"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "agent": "IAM General Context Agent (Groq)"
    }
