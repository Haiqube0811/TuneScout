import asyncio
from datetime import datetime
from typing import List, Dict, Any

import httpx

from packages.common.settings import settings
from apps.etl.sources.spotify import SpotifyClient


MIN_POPULARITY = 2
MAX_POPULARITY = 24


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


async def fetch_yesterday_artists() -> List[Dict[str, Any]]:
    """Fetch unique artists from yesterday's releases (market=JP),
    then return artist detail dicts filtered by popularity.
    """
    client = SpotifyClient()
    releases = await client.get_yesterday_releases(market=settings.market)

    artist_ids = []
    for rel in releases:
        for ar in rel.get("artists", []):
            if ar.get("id"):
                artist_ids.append(ar["id"])

    unique_ids = list(dict.fromkeys(artist_ids))  # preserve order, dedupe
    artists: List[Dict[str, Any]] = []
    for aid in unique_ids:
        info = await client.get_artist_info(aid)
        pop = info.get("popularity", 0)
        if isinstance(pop, int) and MIN_POPULARITY <= pop <= MAX_POPULARITY:
            artists.append(info)

    return artists


async def upsert_artists_to_supabase(artists: List[Dict[str, Any]]) -> int:
    if not artists:
        return 0

    url = f"{settings.supabase_url}/rest/v1/artists?on_conflict=id"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    payload = []
    for ar in artists:
        payload.append({
            "id": ar.get("id"),
            "name": ar.get("name"),
            "popularity": ar.get("popularity", 0),
            "genres": ar.get("genres", []) or [],
            "followers": (ar.get("followers") or {}).get("total", 0),
            "spotify_url": (ar.get("external_urls") or {}).get("spotify"),
            # updated_at は手動で更新しておく（スキーマは DEFAULT のみ）
            "updated_at": _now_iso(),
        })

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(url, headers=headers, json=payload)
        if res.status_code >= 300:
            raise RuntimeError(f"Supabase upsert failed: {res.status_code} {res.text}")

    return len(payload)


async def main() -> None:
    print("Sync target: artists (columns: id, name, popularity, genres, followers, spotify_url, timestamps)")
    artists = await fetch_yesterday_artists()
    print(f"Fetched artists filtered by popularity {MIN_POPULARITY}-{MAX_POPULARITY}: {len(artists)}")

    count = await upsert_artists_to_supabase(artists)
    print(f"Upserted to Supabase: {count} rows")


if __name__ == "__main__":
    asyncio.run(main())

