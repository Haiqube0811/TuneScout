from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from uuid import UUID

from packages.common.db import get_db, Artist

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/{artist_id}", response_class=HTMLResponse)
async def get_artist_detail(artist_id: UUID, request: Request, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    return templates.TemplateResponse("artist_detail.html", {
        "request": request,
        "artist": artist
    })