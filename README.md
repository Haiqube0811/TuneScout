# TuneScout - Music Discovery Recommendation System

音楽発掘レコメンドシステム。新人アーティストの発掘と日次レコメンド配信を行います。

## 特徴

- 🎵 Spotify APIを使用した新譜・新人アーティスト発掘
- 📧 日次メールレコメンド配信
- 🎯 人気度フィルタリング（マイナーアーティスト優先）
- 🌐 日本市場向け最適化
- 🔍 音楽メディア記事との連携

## 技術スタック

- **Backend**: FastAPI + SQLAlchemy + Supabase + pgvector
- **Frontend**: Jinja2 テンプレート
- **外部API**: Spotify Web API
- **メール**: SendGrid
- **認証**: Supabase Auth

## セットアップ

1. Supabaseプロジェクト作成:
   - [Supabase](https://supabase.com)でプロジェクト作成
   - Database > Extensions で `vector` を有効化

2. 環境変数設定:
```bash
cp .env.example .env
# .envファイルを編集してSupabase URLとキーを設定
```

3. 依存関係インストール:
```bash
uv sync
```

4. データベースマイグレーション:
```bash
uv run alembic upgrade head
```

5. 開発サーバー起動:
```bash
uv run uvicorn apps.api.main:app --reload
```

## API エンドポイント

- `GET /` - ホームページ
- `POST /auth/register` - ユーザー登録
- `POST /auth/login` - ログイン
- `POST /auth/logout` - ログアウト
- `GET /auth/me` - ユーザープロフィール
- `GET /recommendations/today` - 本日のレコメンド
- `GET /artists/{id}` - アーティスト詳細

## 開発

```bash
# 依存関係インストール
uv sync

# 開発サーバー起動
uv run uvicorn apps.api.main:app --reload

# マイグレーション作成
uv run alembic revision --autogenerate -m "description"

# マイグレーション実行
uv run alembic upgrade head
```

## Supabase設定

### 必要なExtensions
- `vector` - ベクトル検索用

### RLS (Row Level Security)
ユーザーデータのセキュリティのため、`user_profiles`テーブルにRLSを設定してください。