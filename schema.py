# schema.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"

class ExecutionData(BaseModel):
    model_name: str = Field(..., description="e.g., gpt-4o, llama-3-8b")
    latency_ms: int = Field(..., description="Total round-trip execution time in milliseconds")
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = Field(default=0.0, description="Calculated cost of the interaction")
    prompt_text: str
    response_text: str

class BusinessImpact(BaseModel):
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    category: str = Field(..., description="e.g., pricing_hallucination, policy_violation")
    risk_usd: float = Field(default=0.0, description="Estimated financial risk associated with this failure")

class EvaluationResult(BaseModel):
    status: StatusEnum
    lexical_coverage_percent: float
    reasons: List[str]
    business_impact: Optional[BusinessImpact] = None

class LLMLogPayload(BaseModel):
    trace_id: str = Field(..., description="Unique identifier for trace tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    project_id: str = Field(..., description="Project or client ID in the SaaS ecosystem")
    environment: str = Field(default="production")
    execution: ExecutionData
    evaluation: EvaluationResult
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Custom user metadata/tags")