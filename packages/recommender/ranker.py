from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict

from packages.common.db import Artist, Release
from packages.common.settings import settings

def get_recommendations(db: Session, limit: int = 10) -> List[Dict]:
    """Generate recommendations based on freshness and popularity"""
    
    # Get recent releases from artists with low popularity
    cutoff_date = datetime.utcnow() - timedelta(days=settings.RECO_FRESH_DAYS)
    
    query = db.query(Artist, Release).join(Release, Artist.id == Release.artist_id).filter(
        Artist.popularity <= settings.RECO_MAX_POPULARITY,
        Artist.popularity >= settings.RECO_MIN_POPULARITY,
        Release.release_date >= cutoff_date
    ).limit(limit)
    
    recommendations = []
    for artist, release in query:
        # Simple scoring: newer = higher score, lower popularity = higher score
        days_old = (datetime.utcnow() - release.release_date).days
        freshness_score = max(0, 1 - (days_old / settings.RECO_FRESH_DAYS))
        popularity_score = 1 - (artist.popularity / 100)
        
        total_score = (freshness_score * 0.6) + (popularity_score * 0.4)
        
        recommendations.append({
            "artist_name": artist.name,
            "release_title": release.title,
            "spotify_url": release.external_urls.get("spotify", "") if release.external_urls else "",
            "score": round(total_score, 3),
            "reason": f"Fresh release ({days_old} days old) from emerging artist"
        })
    
    return sorted(recommendations, key=lambda x: x["score"], reverse=True)