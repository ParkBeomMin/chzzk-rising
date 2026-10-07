#!/usr/bin/env python3
"""스레드 일일 포스트 생성기.

rising.json을 읽어 "오늘의 치지직 라이징 TOP 5" 스레드 포스트 텍스트를 만든다.

사용법:
    python3 threads_post.py [rising.json 경로] [--site-url URL]
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "../frontend/data/rising.json"
    site_url = "https://chzzk.duckmu.com/"
    for i, a in enumerate(sys.argv):
        if a == "--site-url" and i + 1 < len(sys.argv):
            site_url = sys.argv[i + 1]

    d = json.loads(Path(path).read_text(encoding="utf-8"))
    ranking = d.get("ranking", [])[:5]
    if not ranking:
        print("라이징 데이터가 없습니다.")
        return

    today = datetime.now().strftime("%m/%d")
    lines = [f"🔥 오늘의 치지직 라이징 TOP 5 ({today})", ""]
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, r in enumerate(ranking):
        lines.append(
            f"{medals[i]} {r['channelName']} ({r['growthPct']}↑)"
        )
        lines.append(f"   {r['liveTitle'][:30]} | 👁 {r['viewers']:,}명 | {r['category']}")
    lines += [
        "",
        "시청자 수 급등 중인 방송만 모았어요 👀",
        f"전체 랭킹 보기: {site_url}",
        "",
        "#치지직 #스트리머 #라이징",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
