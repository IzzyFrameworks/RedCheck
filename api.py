from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, LogEntry
from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime

app = FastAPI(title="RedCheck Enterprise API", version="0.5.0")

class LogIngestRequest(BaseModel):
    trace_id: str = "unknown"
    status: str = "UNKNOWN"
    risk_usd: float = 0.0
    raw_payload: Dict[str, Any] = {}

def make_json_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    return obj

@app.post("/v1/ingest")
def ingest_llm_log(payload: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        clean_payload = make_json_serializable(payload)
        
        db_entry = LogEntry(
            trace_id=str(clean_payload.get("trace_id", "unknown")),
            status=str(clean_payload.get("status", "SUCCESS")),
            risk_usd=float(clean_payload.get("risk_usd", 0.0)),
            raw_payload=clean_payload
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return {"status": "success", "id": db_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
