-- Supabase初期設定用SQL

-- vector extensionを有効化
CREATE EXTENSION IF NOT EXISTS vector;

-- user_profilesテーブルのRLS設定
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- ユーザーは自分のプロフィールのみアクセス可能
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 他のテーブルは認証済みユーザーが読み取り可能
ALTER TABLE artists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read artists" ON artists
    FOR SELECT USING (auth.role() = 'authenticated');

ALTER TABLE releases ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read releases" ON releases
    FOR SELECT USING (auth.role() = 'authenticated');

ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read articles" ON articles
    FOR SELECT USING (auth.role() = 'authenticated');

ALTER TABLE article_embeddings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Authenticated users can read embeddings" ON article_embeddings
    FOR SELECT USING (auth.role() = 'authenticated');