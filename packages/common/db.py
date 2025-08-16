from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from supabase import create_client, Client

from .settings import settings

# Vector型の条件付きインポート
try:
    from pgvector.sqlalchemy import Vector
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

# Supabase client - 有効なURLの場合のみ初期化
supabase: Client = None
supabase_admin: Client = None

if settings.supabase_url and not settings.supabase_url.startswith('your_'):
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        supabase_admin = create_client(settings.supabase_url, settings.supabase_service_key)
    except Exception as e:
        print(f"Supabase初期化エラー: {e}")
        supabase = None
        supabase_admin = None

# SQLAlchemy for direct DB operations
def get_db_url():
    if settings.database_url and not settings.database_url.startswith('postgresql+psycopg://postgres:your_'):
        try:
            # PostgreSQL接続をテスト
            test_engine = create_engine(settings.database_url)
            test_engine.connect().close()
            return settings.database_url
        except Exception as e:
            print(f"PostgreSQL接続失敗、SQLiteを使用: {e}")
    # デフォルトのURL（テスト用）
    return "sqlite:///./test.db"

engine = create_engine(get_db_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    spotify_id = Column(String, unique=True)
    country = Column(String)
    genres = Column(JSON)
    popularity = Column(Integer)
    followers = Column(Integer)
    external_urls = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Release(Base):
    __tablename__ = "releases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    artist_id = Column(UUID(as_uuid=True), nullable=False)
    spotify_id = Column(String, unique=True)
    title = Column(String, nullable=False)
    release_date = Column(DateTime)
    total_tracks = Column(Integer)
    external_urls = Column(JSON)

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)
    url = Column(String, unique=True)
    title = Column(String, nullable=False)
    lang = Column(String, default="en")
    published_at = Column(DateTime)
    author = Column(String)
    raw_text = Column(Text)

class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    embedding = Column(Vector(settings.vector_dim) if VECTOR_AVAILABLE else Text)
    model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    preferences = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
