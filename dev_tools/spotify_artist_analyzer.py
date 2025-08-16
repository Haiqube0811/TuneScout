import asyncio
import csv
import sys
from pathlib import Path
from typing import List, Dict

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from apps.etl.sources.spotify import SpotifyClient

class SpotifyArtistAnalyzer:
    def __init__(self):
        self.client = SpotifyClient()
    
    async def get_artist_data(self, artist_id: str) -> Dict:
        """指定したアーティストの詳細データを取得"""
        artist_info = await self.client.get_artist_info(artist_id)
        images = artist_info.get('images', [])
        
        return {
            'id': artist_info.get('id', ''),
            'name': artist_info.get('name', ''),
            'popularity': artist_info.get('popularity', 0),
            'followers': artist_info.get('followers', {}).get('total', 0),
            'genres': ', '.join(artist_info.get('genres', [])),
            'genres_count': len(artist_info.get('genres', [])),
            'external_urls_spotify': artist_info.get('external_urls', {}).get('spotify', ''),
            'images_count': len(images),
            'image_large_url': images[0]['url'] if images else '',
            'image_large_height': images[0]['height'] if images else 0,
            'image_large_width': images[0]['width'] if images else 0,
            'image_medium_url': images[1]['url'] if len(images) > 1 else '',
            'image_small_url': images[2]['url'] if len(images) > 2 else '',
            'type': artist_info.get('type', ''),
            'uri': artist_info.get('uri', ''),
            'href': artist_info.get('href', ''),
            'popularity_tier': self._get_popularity_tier(artist_info.get('popularity', 0)),
            'follower_tier': self._get_follower_tier(artist_info.get('followers', {}).get('total', 0)),
            'has_japanese_genre': self._has_japanese_genre(artist_info.get('genres', [])),
            'genre_categories': self._categorize_genres(artist_info.get('genres', []))
        }
    
    def _get_popularity_tier(self, popularity: int) -> str:
        """人気度をティア分けする"""
        if popularity >= 80: return 'Very High'
        elif popularity >= 60: return 'High'
        elif popularity >= 40: return 'Medium'
        elif popularity >= 20: return 'Low'
        else: return 'Very Low'
    
    def _get_follower_tier(self, followers: int) -> str:
        """フォロワー数をティア分けする"""
        if followers >= 10000000: return 'Mega (10M+)'
        elif followers >= 1000000: return 'Major (1M+)'
        elif followers >= 100000: return 'Popular (100K+)'
        elif followers >= 10000: return 'Rising (10K+)'
        elif followers >= 1000: return 'Emerging (1K+)'
        else: return 'Niche (<1K)'
    
    def _has_japanese_genre(self, genres: List[str]) -> bool:
        """日本関連のジャンルが含まれているかチェック"""
        japanese_keywords = ['j-', 'japan', 'jpop', 'jrock', 'visual kei', 'shibuya-kei']
        return any(keyword in genre.lower() for genre in genres for keyword in japanese_keywords)
    
    def _categorize_genres(self, genres: List[str]) -> str:
        """ジャンルをカテゴリ分けする"""
        categories = []
        genre_str = ' '.join(genres).lower()
        
        if any(word in genre_str for word in ['pop', 'jpop']): categories.append('Pop')
        if any(word in genre_str for word in ['rock', 'jrock', 'metal']): categories.append('Rock')
        if any(word in genre_str for word in ['electronic', 'edm', 'techno']): categories.append('Electronic')
        if any(word in genre_str for word in ['indie', 'alternative']): categories.append('Indie')
        if any(word in genre_str for word in ['hip hop', 'rap']): categories.append('Hip Hop')
        if any(word in genre_str for word in ['jazz', 'blues']): categories.append('Jazz/Blues')
        if any(word in genre_str for word in ['classical', 'orchestral']): categories.append('Classical')
        
        return ', '.join(categories) if categories else 'Other'
    
    async def analyze_artists_to_csv(self, artist_ids: List[str], output_file: str = 'artist_analysis.csv'):
        """複数のアーティストを分析してCSVに出力"""
        fieldnames = [
            'id', 'name', 'popularity', 'popularity_tier', 'followers', 'follower_tier',
            'genres', 'genres_count', 'has_japanese_genre', 'genre_categories',
            'external_urls_spotify', 'images_count', 'image_large_url', 'image_large_height', 'image_large_width',
            'image_medium_url', 'image_small_url', 'type', 'uri', 'href'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for artist_id in artist_ids:
                try:
                    artist_data = await self.get_artist_data(artist_id)
                    writer.writerow(artist_data)
                    print(f"✓ {artist_data['name']} - 人気度: {artist_data['popularity']}")
                except Exception as e:
                    print(f"✗ エラー (ID: {artist_id}): {e}")
        
        print(f"\n分析結果を {output_file} に保存しました")

async def main():
    """使用例"""
    analyzer = SpotifyArtistAnalyzer()
    
    # 分析したいアーティストのSpotify IDを指定
    artist_ids = [
        "1vs4LphTDQKsiFwVnDGFKf",  
        "2C2kOwLa4Zv5Y7MnKT3eJo",  
        "5oZhNJP1zUPqUW6RLwneNo",  
        "1htg5lwXpkH7DwmKnIW9JI", 
        "3PKV6Xh7jBI15NF76VX0hp",
        "40Jr8Cy8VYDrynncXqEzqG",
        "07sfpza24f0vZ3Scw4zzMG",
        "4a4eZ5B0QjXoHQ1Nat3Yez",
        "6wkRjQQHXHFvohWNjkPjm0",
        "44vCIlLzyYUo6UQ2s4huqu",

    ]
    
    await analyzer.analyze_artists_to_csv(artist_ids, 'dev_tools/spotify_artists.csv')

if __name__ == "__main__":
    asyncio.run(main())