import httpx
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from packages.common.settings import settings

class SpotifyClient:
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.access_token = None
        
    async def get_access_token(self) -> str:
        """Get Spotify access token"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Spotify credentials not configured")
            
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                headers={"Authorization": f"Basic {auth_base64}"},
                data={"grant_type": "client_credentials"}
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            return self.access_token
    
    async def search_new_releases(self, market: str = "JP", limit: int = 50) -> List[Dict]:
        """Search for new releases in specified market"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.spotify.com/v1/browse/new-releases",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"market": market, "limit": limit}
            )
            response.raise_for_status()
            return response.json()["albums"]["items"]
    
    async def get_artist_info(self, artist_id: str) -> Dict:
        """Get detailed artist information"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.spotify.com/v1/artists/{artist_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_related_artists(self, artist_id: str) -> List[Dict]:
        """Get related artists"""
        if not self.access_token:
            await self.get_access_token()
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.spotify.com/v1/artists/{artist_id}/related-artists",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 404:
                print(f"関連アーティストが見つかりません（アーティストID: {artist_id}）")
                return []
            response.raise_for_status()
            return response.json()["artists"]
    
    async def get_filtered_related_artists(self, artist_id: str, min_popularity: int = 2, max_popularity: int = 24) -> List[Dict]:
        """Get related artists filtered by popularity range"""
        related_artists = await self.get_related_artists(artist_id)
        return [artist for artist in related_artists if min_popularity <= artist.get("popularity", 0) <= max_popularity]
    
    async def search_similar_artists_by_genre(self, artist_id: str, limit: int = 20) -> List[Dict]:
        """Search similar artists by genre when related artists are not available"""
        if not self.access_token:
            await self.get_access_token()
            
        # Get original artist info
        artist_info = await self.get_artist_info(artist_id)
        genres = artist_info.get("genres", [])
        
        if not genres:
            return []
            
        # Search by first genre
        search_query = f"genre:{genres[0]}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"q": search_query, "type": "artist", "limit": limit}
            )
            if response.status_code == 200:
                artists = response.json().get("artists", {}).get("items", [])
                # Exclude the original artist
                return [a for a in artists if a["id"] != artist_id]
            return []

async def sync_yesterday_releases() -> List[Dict]:
    """日本のアルバム情報を取得し、指定条件のアーティストを返す"""
    client = SpotifyClient()
    all_releases = []
    
    # japanese indieアーティストを特定する検索クエリ（2025年6月7日テスト）
    search_queries = [
        "japanese indie year:2025",
        "math rock year:2025",
        "shoegaze year:2025", 
        "midwest emo year:2025",
        "underground japan year:2025"
    ]
    
    async with httpx.AsyncClient() as http_client:
        for query in search_queries:
            print(f"検索クエリ: {query}")
            response = await http_client.get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {await client.get_access_token()}"},
                params={"q": query, "type": "album", "market": "JP", "limit": 20}
            )
            
            if response.status_code != 200:
                print(f"エラー: {response.status_code}")
                continue
                
            albums = response.json().get("albums", {}).get("items", [])
            print(f"取得アルバム数: {len(albums)}")
            
            for album in albums:
                release_date_str = album.get("release_date", "")
                
                # 2025年6月のフィルタリング
                if release_date_str and not release_date_str.startswith("2025-06"):
                    continue
                    
                print(f"アルバム: {album['name']} ({release_date_str})")
                    
                for artist in album.get("artists", []):
                    try:
                        artist_info = await client.get_artist_info(artist["id"])
                        artist_popularity = artist_info.get("popularity", 100)
                        print(f"  アーティスト: {artist_info['name']} (人気度: {artist_popularity})")
                        
                        if not (2 <= artist_popularity <= 24):
                            print("    アーティスト人気度範囲外")
                            continue
                        
                        artist_genres = [g.lower() for g in artist_info.get("genres", [])]
                        print(f"    ジャンル: {artist_genres}")
                        
                        # japanese indieのみ
                        has_japanese_indie = "japanese indie" in artist_genres
                        
                        if not has_japanese_indie:
                            print("japanese indieジャンルではない")
                            continue
                            
                        print(f"✓ japanese indieジャンル合致")
                            
                        print("    ✓ 条件合致!")
                        print(f"    アーティストID: {artist_info['id']}")
                        all_releases.append({
                            "release": album,
                            "artist": artist_info,
                            "artist_id": artist_info['id'],
                            "genre": "japanese indie"
                        })
                    except Exception as e:
                        print(f"    エラー: {e}")
                        continue
    
    return all_releases