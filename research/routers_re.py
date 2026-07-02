from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from research import core_analysis

# Khởi tạo router chính thống
router = APIRouter(prefix="/research", tags=["AI Research"])

class ResearchPayload(BaseModel):
    coin: str
    klines: List[list]
    news: List[dict]
    investor_profile: Optional[Dict[str, Any]] = None
    macro_indicators: Optional[Dict[str, Any]] = {"fear_greed": 65, "btc_dominance": "54.2%"}

@router.post("/analyze")
async def analyze_market_data(payload: ResearchPayload):
    try:
        # Gọi an toàn qua module để tránh lỗi tuần hoàn import
        tech_result = core_analysis.calculate_technical_score(payload.klines)
        sentiment_result = core_analysis.calculate_sentiment_score(payload.news)
        
        risk_level = core_analysis.evaluate_risk_level(
            payload.coin, 
            tech_result["technical_score"], 
            sentiment_result["sentiment_score"]
        )
        
        portfolio_result = core_analysis.optimize_portfolio(
            payload.investor_profile, 
            payload.coin, 
            tech_result["technical_score"], 
            sentiment_result["sentiment_score"]
        )
        
        return {
            "coin": payload.coin.upper(),
            "technical_score": tech_result["technical_score"],
            "sentiment_score": sentiment_result["sentiment_score"],
            "risk_score": risk_level,
            "indicators": tech_result["indicators"],
            "macro": payload.macro_indicators,
            "chart_data": tech_result["chart_data"],
            "portfolio_allocation": portfolio_result["allocation_strategy"],
            "risk_management": portfolio_result["risk_management"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine internal glitch: {str(e)}")