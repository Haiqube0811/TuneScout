from typing import List, Dict
from supabase import create_client, Client
from packages.common.settings import settings

async def save_releases_to_db(releases: List[Dict]) -> None:
    """前日のリリースをSupabaseに保存"""
    supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
    
    artists_dict = {}  # 重複防止用
    albums_dict = {}   # 重複防止用
    
    for release_data in releases:
        release = release_data["release"]
        artist_info = release_data["artist"]
        
        # アーティストデータ準備（重複防止）
        if artist_info["id"] not in artists_dict:
            artists_dict[artist_info["id"]] = {
                "id": artist_info["id"],
                "name": artist_info["name"],
                "popularity": artist_info.get("popularity", 0),
                "genres": artist_info.get("genres", []),
                "followers": artist_info.get("followers", {}).get("total", 0),
                "spotify_url": artist_info.get("external_urls", {}).get("spotify", "")
            }
        
        # 日付処理
        release_date = release.get("release_date")
        if release_date:
            if len(release_date) == 4:
                release_date = f"{release_date}-01-01"
            elif len(release_date) == 7:
                release_date = f"{release_date}-01"
        
        # アルバムデータ準備（重複防止）
        if release["id"] not in albums_dict:
            albums_dict[release["id"]] = {
                "id": release["id"],
                "name": release["name"],
                "artist_id": artist_info["id"],
                "release_date": release_date,
                "total_tracks": release.get("total_tracks", 0),
                "spotify_url": release.get("external_urls", {}).get("spotify", ""),
                "image_url": release.get("images", [{}])[0].get("url", "") if release.get("images") else ""
            }
    
    # 重複を除去したリストを作成
    artists_to_insert = list(artists_dict.values())
    albums_to_insert = list(albums_dict.values())
    
    # Supabaseにupsert
    if artists_to_insert:
        supabase.table("artists").upsert(artists_to_insert, on_conflict="id").execute()
    
    if albums_to_insert:
        supabase.table("albums").upsert(albums_to_insert, on_conflict="id").execute()
    
    print(f"Supabaseにアーティスト{len(artists_to_insert)}件、アルバム{len(albums_to_insert)}件を保存しました")