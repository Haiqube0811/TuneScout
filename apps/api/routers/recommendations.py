from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from packages.common.db import get_db
from packages.recommender.ranker import get_recommendations

router = APIRouter()

class RecommendationItem(BaseModel):
    artist_name: str
    release_title: str
    spotify_url: str
    score: float
    reason: str

class RecommendationResponse(BaseModel):
    items: List[RecommendationItem]
    generated_at: str

@router.get("/today", response_model=RecommendationResponse)
async def get_today_recommendations(db: Session = Depends(get_db)):
    # Mock implementation for MVP
    recommendations = get_recommendations(db, limit=5)
    
    return RecommendationResponse(
        items=[
            RecommendationItem(
                artist_name=rec["artist_name"],
                release_title=rec["release_title"],
                spotify_url=rec["spotify_url"],
                score=rec["score"],
                reason=rec["reason"]
            ) for rec in recommendations
        ],
        generated_at="2024-01-01T00:00:00Z"
    )