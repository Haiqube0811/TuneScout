# 開発ツール

Spotify API調査用の開発ツールです。

## spotify_artist_analyzer.py

指定したアーティストの詳細情報をCSVファイルに出力します。

### 使用方法

```bash
# 基本的な使用
cd TuneScout
uv run python dev_tools/spotify_artist_analyzer.py

# カスタムアーティストIDで実行
python -c "
import asyncio
from dev_tools.spotify_artist_analyzer import SpotifyArtistAnalyzer

async def custom_analysis():
    analyzer = SpotifyArtistAnalyzer()
    artist_ids = ['YOUR_ARTIST_ID_1', 'YOUR_ARTIST_ID_2']
    await analyzer.analyze_artists_to_csv(artist_ids, 'custom_output.csv')

asyncio.run(custom_analysis())
"
```

### 出力項目

**基本情報**
- id: Spotify アーティストID
- name: アーティスト名
- type: タイプ (artist)
- uri: Spotify URI
- href: Spotify API URL

**人気度・フォロワー**
- popularity: 人気度 (0-100)
- popularity_tier: 人気度ティア (Very High/High/Medium/Low/Very Low)
- followers: フォロワー数
- follower_tier: フォロワーティア (Mega/Major/Popular/Rising/Emerging/Niche)

**ジャンル分析**
- genres: ジャンル (カンマ区切り)
- genres_count: ジャンル数
- has_japanese_genre: 日本関連ジャンルの有無 (True/False)
- genre_categories: ジャンルカテゴリ分類

**画像・URL**
- external_urls_spotify: Spotify URL
- images_count: 画像数
- image_large_url: 大サイズ画像URL
- image_large_height: 大サイズ画像高さ
- image_large_width: 大サイズ画像幅
- image_medium_url: 中サイズ画像URL
- image_small_url: 小サイズ画像URL