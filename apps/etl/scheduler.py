import asyncio
import schedule
import time
from datetime import datetime
from typing import List, Dict

from apps.etl.sources.spotify import sync_yesterday_releases
from apps.etl.pipeline import save_releases_to_db
from packages.common.settings import settings

async def daily_artist_sync():
    """毎日実行される前日リリースアーティスト同期タスク"""
    print(f"[{datetime.now()}] 前日リリースアーティストの同期を開始...")
    
    try:
        releases = await sync_yesterday_releases()
        print(f"取得したリリース数: {len(releases)}")
        
        # データベースに保存
        if releases:
            await save_releases_to_db(releases)
        
        print(f"[{datetime.now()}] 同期完了")
        return releases
        
    except Exception as e:
        print(f"[{datetime.now()}] エラーが発生しました: {e}")
        return []

def run_daily_sync():
    """スケジューラーから呼び出される同期関数"""
    asyncio.run(daily_artist_sync())

def start_scheduler():
    """スケジューラーを開始（毎日午前9時に実行）"""
    schedule.every().day.at("09:00").do(run_daily_sync)
    
    print("スケジューラーを開始しました（毎日09:00に実行）")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    start_scheduler()