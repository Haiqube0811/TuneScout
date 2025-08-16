from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os

from packages.common.db import get_db, UserProfile
from packages.common.auth import get_current_user
from packages.common.settings import settings

router = APIRouter()

# テンプレート設定
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
template_dir = os.path.join(base_dir, "templates")
templates = Jinja2Templates(directory=template_dir)

@router.get("/", response_class=HTMLResponse)
async def auth_page(request: Request):
    return templates.TemplateResponse("auth_simple.html", {
        "request": request,
        "supabase_url": settings.supabase_url,
        "supabase_key": settings.supabase_key
    })

@router.post("/register")
async def deprecated_register():
    raise HTTPException(status_code=404, detail="Use Supabase Auth UI at /auth instead")

@router.post("/login")
async def deprecated_login():
    raise HTTPException(status_code=404, detail="Use Supabase Auth UI at /auth instead")

@router.get("/me")
async def get_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.id == current_user.id).first()
    if not profile:
        # Create profile if doesn't exist
        try:
            profile = UserProfile(
                id=current_user.id,
                email=current_user.email
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error saving new user: {str(e)}")
    return profile

@router.post("/create-profile")
async def create_user_profile(request: Request, db: Session = Depends(get_db)):
    """Supabase認証後にプロフィールを作成"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        email = data.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=400, detail="Missing user_id or email")
        
        # 既存プロフィールチェック
        existing = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if existing:
            return {"status": "profile already exists"}
        
        # 新規プロフィール作成
        profile = UserProfile(
            id=user_id,
            email=email
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return {"status": "profile created", "profile_id": str(profile.id)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")