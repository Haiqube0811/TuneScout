#!/usr/bin/env python3
"""Spotify アーティスト分析ツール"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from apps.etl.sources.spotify import SpotifyClient

async def analyze_artist(artist_id: str):
    """指定したアーティストIDの詳細情報を分析"""
    print(f"=== アーティスト分析 (ID: {artist_id}) ===")
    
    client = SpotifyClient()
    
    try:
        artist_info = await client.get_artist_info(artist_id)
        
        print(f"名前: {artist_info.get('name', 'N/A')}")
        print(f"人気度: {artist_info.get('popularity', 0)}")
        print(f"フォロワー数: {artist_info.get('followers', {}).get('total', 0):,}")
        print(f"ジャンル: {artist_info.get('genres', [])}")
        print(f"Spotify URL: {artist_info.get('external_urls', {}).get('spotify', 'N/A')}")
        print(f"URI: {artist_info.get('uri', 'N/A')}")
        
        # 画像情報
        images = artist_info.get('images', [])
        print(f"画像数: {len(images)}")
        if images:
            print(f"メイン画像: {images[0]['url']} ({images[0]['width']}x{images[0]['height']})")
        
        # 人気度ティア
        popularity = artist_info.get('popularity', 0)
        if popularity >= 80:
            tier = "Very High (80+)"
        elif popularity >= 60:
            tier = "High (60-79)"
        elif popularity >= 40:
            tier = "Medium (40-59)"
        elif popularity >= 20:
            tier = "Low (20-39)"
        else:
            tier = "Very Low (0-19)"
        print(f"人気度ティア: {tier}")
        
        # TuneScout条件チェック
        print("\n--- TuneScout条件チェック ---")
        print(f"人気度2-24範囲: {'✓' if 2 <= popularity <= 24 else '✗'}")
        
        genres_lower = [g.lower() for g in artist_info.get('genres', [])]
        has_japanese_indie = "japanese indie" in genres_lower
        has_math_midwest = "math rock" in genres_lower and "midwest emo" in genres_lower
        
        print(f"japanese indie: {'✓' if has_japanese_indie else '✗'}")
        print(f"math rock + midwest emo: {'✓' if has_math_midwest else '✗'}")
        print(f"TuneScout対象: {'✓' if (2 <= popularity <= 24) and (has_japanese_indie or has_math_midwest) else '✗'}")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    # 指定されたアーティストIDを分析
    artist_id = "1htg5lwXpkH7DwmKnIW9JI"
    asyncio.run(analyze_artist(artist_id))