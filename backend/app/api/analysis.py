import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.analysis import Analysis
from app.models.user import User

router = APIRouter()
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from app.engines.wellness_pipeline import WellnessPipeline
            _pipeline = WellnessPipeline()
        except Exception as e:
            print(f"Pipeline load error: {e}")
    return _pipeline


class AnalysisRequest(BaseModel):
    spotify_data: Optional[dict] = None
    youtube_data: Optional[dict] = None
    whatsapp_data: Optional[dict] = None


def get_current_user(token: str, db: Session) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/run")
async def run_analysis(
    token: str,
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    user = get_current_user(token, db)

    historical = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.analysis_date.desc())
        .limit(30)
        .all()
    )

    historical_scores = [
        {
            "date": a.analysis_date.strftime("%Y-%m-%d"),
            "score": a.overall_wellness_score,
        }
        for a in historical
        if a.overall_wellness_score
    ]

    pipeline = get_pipeline()
    if not pipeline:
        raise HTTPException(status_code=500, detail="ML pipeline unavailable")

    result = await pipeline.analyze(
        spotify_data=request.spotify_data,
        youtube_data=request.youtube_data,
        whatsapp_data=request.whatsapp_data,
        historical_scores=historical_scores,
    )

    analysis = Analysis(
        user_id=user.id,
        analysis_date=datetime.utcnow(),
        overall_wellness_score=result["overall_wellness_score"],
        linguistic_score=result["scores"]["linguistic"],
        consumption_score=result["scores"]["consumption"],
        behavioral_score=result["scores"]["behavioral"],
        risk_level=result["risk_level"],
        linguistic_details=json.dumps(result.get("linguistic_details")),
        consumption_details=json.dumps(result.get("consumption_details")),
        behavioral_details=json.dumps(result.get("behavioral_details")),
        predictions=json.dumps(result.get("predictions")),
        insights=json.dumps(result.get("explanation")),
    )
    db.add(analysis)
    db.commit()

    return result


@router.get("/history")
async def get_history(
    token: str,
    limit: int = 30,
    db: Session = Depends(get_db),
):
    user = get_current_user(token, db)
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.analysis_date.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "date": a.analysis_date.isoformat(),
            "overall_score": a.overall_wellness_score,
            "risk_level": a.risk_level,
            "linguistic_score": a.linguistic_score,
            "consumption_score": a.consumption_score,
            "behavioral_score": a.behavioral_score,
        }
        for a in analyses
    ]


@router.get("/latest")
async def get_latest_analysis(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    analysis = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id)
        .order_by(Analysis.analysis_date.desc())
        .first()
    )
    if not analysis:
        return None

    return {
        "id": str(analysis.id),
        "analysis_date": analysis.analysis_date.isoformat() if analysis.analysis_date else None,
        "overall_wellness_score": analysis.overall_wellness_score,
        "linguistic_score": analysis.linguistic_score,
        "consumption_score": analysis.consumption_score,
        "behavioral_score": analysis.behavioral_score,
        "risk_level": analysis.risk_level,
    }


@router.get("/")
async def analysis_root():
    pipeline = get_pipeline()
    return {
        "message": "MindWatch ML Analysis Engine",
        "status": "ready",
        "pipeline_loaded": pipeline is not None,
    }
