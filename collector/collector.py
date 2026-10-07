#!/usr/bin/env python3
"""치지직 실시간 방송 데이터 수집기.

사용법:
    python3 collector.py              # 스냅샷 1회 수집 → data/snapshot_YYYYMMDD_HHMMSS.json
    python3 collector.py --latest     # 가장 최근 스냅샷을 data/latest.json으로 복사

GitHub Actions에서 주기적으로 실행하는 것을想定.
인증 불필요 (service API는 공개 엔드포인트).
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
API_URL = "https://api.chzzk.naver.com/service/v1/lives"
PAGE_SIZE = 50
MAX_PAGES = 40  # 최대 2000개
REQUEST_DELAY = 0.3
KST = timezone(timedelta(hours=9))


def fetch_page(size=PAGE_SIZE, cursor=None):
    url = f"{API_URL}?size={size}"
    if cursor:
        url += f"&concurrentUserCount={cursor['concurrentUserCount']}&liveId={cursor['liveId']}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect_all():
    """전체 라이브 목록 수집 (페이지네이션)."""
    lives = []
    cursor = None
    for _ in range(MAX_PAGES):
        try:
            d = fetch_page(cursor=cursor)
        except Exception as e:
            print(f"페이지 수집 실패: {e}", file=sys.stderr)
            break
        data = d["content"]["data"]
        if not data:
            break
        lives.extend(data)
        cursor = d["content"]["page"]["next"]
        if not cursor:
            break
        time.sleep(REQUEST_DELAY)
    return lives


def slim(live):
    """필요한 필드만 추출."""
    ch = live.get("channel", {})
    return {
        "liveId": live.get("liveId"),
        "liveTitle": live.get("liveTitle"),
        "viewers": live.get("concurrentUserCount", 0),
        "openDate": live.get("openDate"),
        "category": live.get("liveCategoryValue") or "기타",
        "categoryType": live.get("categoryType"),
        "tags": live.get("tags", [])[:5],
        "adult": live.get("adult", False),
        "thumbnail": (live.get("liveImageUrl") or "").replace("{type}", "480"),
        "channelId": ch.get("channelId"),
        "channelName": ch.get("channelName"),
        "channelImage": ch.get("channelImageUrl"),
        "verified": ch.get("verifiedMark", False),
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("수집 시작...", flush=True)
    lives = collect_all()
    print(f"수집 완료: {len(lives)}개 방송", flush=True)

    now = datetime.now(KST)
    ts = now.strftime("%Y%m%d_%H%M%S")
    snapshot = {
        "collectedAt": now.isoformat(),
        "count": len(lives),
        "lives": [slim(l) for l in lives],
    }
    path = DATA_DIR / f"snapshot_{ts}.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    # latest.json 갱신
    (DATA_DIR / "latest.json").write_text(
        json.dumps(snapshot, ensure_ascii=False), encoding="utf-8"
    )
    print(f"저장: {path.name} (+ latest.json)")


if __name__ == "__main__":
    main()
