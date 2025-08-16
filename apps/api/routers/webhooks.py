from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
import json

from packages.common.db import get_db, UserProfile, SessionLocal

router = APIRouter()

@router.post("/supabase/auth")
async def handle_auth_webhook(request: Request):
    """Supabase認証Webhookハンドラー - 新規ユーザー登録時にプロフィール作成"""
    try:
        payload = await request.json()
        event_type = payload.get("type")
        
        if event_type == "user.created":
            user_data = payload.get("record", {})
            user_id = user_data.get("id")
            email = user_data.get("email")
            
            if user_id and email:
                db = SessionLocal()
                try:
                    # 既存プロフィールチェック
                    existing = db.query(UserProfile).filter(UserProfile.id == user_id).first()
                    if not existing:
                        profile = UserProfile(
                            id=user_id,
                            email=email
                        )
                        db.add(profile)
                        db.commit()
                        print(f"Created profile for user: {email}")
                finally:
                    db.close()
        
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")