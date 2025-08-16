-- 開発環境用：メール確認を無効化
-- Supabase Dashboard > Authentication > Settings で実行

-- 1. 既存ユーザーのメール確認済みに設定
UPDATE auth.users 
SET email_confirmed_at = NOW()
WHERE email_confirmed_at IS NULL;

-- 2. メール確認を無効化（Dashboard設定）
-- Authentication > Settings > Email Auth > Confirm email = OFF