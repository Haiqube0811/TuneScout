-- TuneScout用のSupabaseテーブル作成SQL
-- Supabase SQL Editorで実行してください

-- 既存テーブルを削除（データが失われます）
DROP TABLE IF EXISTS albums CASCADE;
DROP TABLE IF EXISTS artists CASCADE;

-- アーティストテーブル
CREATE TABLE artists (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    popularity INTEGER DEFAULT 0,
    genres JSONB DEFAULT '[]'::jsonb,
    followers INTEGER DEFAULT 0,
    spotify_url VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- アルバムテーブル
CREATE TABLE albums (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    artist_id VARCHAR REFERENCES artists(id),
    release_date DATE,
    total_tracks INTEGER DEFAULT 0,
    spotify_url VARCHAR,
    image_url VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_artists_popularity ON artists(popularity);
CREATE INDEX IF NOT EXISTS idx_artists_genres ON artists USING GIN(genres);
CREATE INDEX IF NOT EXISTS idx_albums_artist_id ON albums(artist_id);
CREATE INDEX IF NOT EXISTS idx_albums_release_date ON albums(release_date);

-- RLS (Row Level Security) 設定
ALTER TABLE artists ENABLE ROW LEVEL SECURITY;
ALTER TABLE albums ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能
CREATE POLICY "Artists are viewable by everyone" ON artists FOR SELECT USING (true);
CREATE POLICY "Albums are viewable by everyone" ON albums FOR SELECT USING (true);

-- サービスロールのみが書き込み可能
CREATE POLICY "Service role can insert artists" ON artists FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "Service role can update artists" ON artists FOR UPDATE USING (auth.role() = 'service_role');
CREATE POLICY "Service role can insert albums" ON albums FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "Service role can update albums" ON albums FOR UPDATE USING (auth.role() = 'service_role');