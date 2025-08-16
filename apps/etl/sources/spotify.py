import httpx
import base64
from datetime import datetime
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
    
    async def search_japanese_artists_by_genre(self, genre: str, limit: int = 50) -> List[Dict]:
        """Search for Japanese artists by specific genre"""
        if not self.access_token:
            await self.get_access_token()
            
        search_queries = [
            f"genre:{genre} market:JP",
            f"genre:j-{genre}", 
            f"genre:japanese-{genre}"
        ]
        
        all_albums = []
        async with httpx.AsyncClient() as client:
            for query in search_queries:
                if len(all_albums) >= limit:
                    break
                    
                response = await client.get(
                    "https://api.spotify.com/v1/search",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={
                        "q": f"{query} year:2024-2025",
                        "type": "album",
                        "market": "JP",
                        "limit": 20
                    }
                )
                if response.status_code == 200:
                    albums = response.json().get("albums", {}).get("items", [])
                    all_albums.extend(albums)
        
        return all_albums[:limit]
    
    async def search_albums_by_country(self, country: str, limit: int = 50) -> List[Dict]:
        """Search for albums by Japanese artists"""
        if not self.access_token:
            await self.get_access_token()
            
        all_albums = []
        async with httpx.AsyncClient() as client:
            # First try new releases in Japan market
            response = await client.get(
                "https://api.spotify.com/v1/browse/new-releases",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"market": "JP", "limit": limit}
            )
            if response.status_code == 200:
                jp_releases = response.json().get("albums", {}).get("items", [])
                
                # Filter for Japanese artists by checking artist info
                for album in jp_releases:
                    for artist in album.get("artists", []):
                        artist_info = await self.get_artist_info(artist["id"])
                        genres = ["japanese indie", "pop", "electronic", "indie", "metal"]
                        japanese_music = await sync_japanese_music_by_genres(genres)
                        # Check if artist has Japanese genres or matches popularity filter
                        popularity = artist_info.get("popularity", 100)
                        if (any("j-" in genre.lower() or "japan" in genre.lower() for genre in genres) or
                            (settings.reco_min_popularity <= popularity <= settings.reco_max_popularity)):
                            all_albums.append(album)
                            break
                    
                    if len(all_albums) >= limit:
                        break
            
            # If we need more results, search by genre
            if len(all_albums) < limit:
                search_queries = [
                    "genre:j-pop year:2024-2025",
                    "genre:japanese year:2024-2025",
                    "genre:jpop year:2024-2025",
                    "genre:j-rock year:2024-2025"
                ]
                
                for query in search_queries:
                    if len(all_albums) >= limit:
                        break
                        
                    response = await client.get(
                        "https://api.spotify.com/v1/search",
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        params={
                            "q": query,
                            "type": "album",
                            "market": "JP",
                            "limit": 10
                        }
                    )
                    if response.status_code == 200:
                        albums = response.json().get("albums", {}).get("items", [])
                        all_albums.extend(albums)
        
        return all_albums[:limit]

async def sync_japanese_music_by_genres(genres: List[str]) -> List[Dict]:
    """Sync Japanese artists across multiple genres"""
    client = SpotifyClient()
    all_releases = []
    
    for genre in genres:
        releases = await client.search_japanese_artists_by_genre(genre)
        
        for release in releases:
            for artist in release["artists"]:
                artist_info = await client.get_artist_info(artist["id"])
                if (settings.reco_min_popularity <= 
                    artist_info.get("popularity", 0) <= 
                    settings.reco_max_popularity):
                    all_releases.append({
                        "release": release,
                        "artist": artist_info,
                        "genre": genre
                    })
    
    return all_releases