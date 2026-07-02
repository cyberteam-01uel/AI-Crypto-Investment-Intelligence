from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/profiling", tags=["Profiling"])

class SurveyWebhookPayload(BaseModel):
    profile: Dict[str, Any]
    missing_fields: list
    confidence: float
    is_done: bool
    next_question: Optional[str] = None

@router.post("/update")
async def update_investor_profile(payload: SurveyWebhookPayload):
    """
    Endpoint tiếp nhận kết quả xử lý từ n8n sau khi phân tích câu trả lời của User.
    """
    try:
        return {
            "status": "success",
            "message": "Profile updated processed successfully",
            "data": payload.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))