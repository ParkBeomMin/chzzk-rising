#!/usr/bin/env python3
"""채널별 시청자 히스토리 증분 집계.

data/latest.json(이번 스냅샷)을 읽어 data/channel_history.json에 추가한다.
출력: data/channel_history.json
  { channelId: {name, image, points: [[ts_epoch, viewers], ...]} }

- 48시간보다 오래된 포인트는 정리
- 피크 시청자 기준 상위 500 채널만 유지
- 스냅샷 파일은 git에 커밋하지 않음 (.gitignore)
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
WINDOW_SEC = 48 * 3600
TOP_N = 500


def parse_ts(s):
    try:
        return int(datetime.fromisoformat(s).timestamp())
    except Exception:
        return 0


def main():
    latest_path = DATA / "latest.json"
    hist_path = DATA / "channel_history.json"
    if not latest_path.exists():
        print("latest.json 없음, 종료")
        return

    d = json.loads(latest_path.read_text(encoding="utf-8"))
    ts = parse_ts(d.get("collectedAt", ""))
    if not ts:
        print("수집 시각 파싱 실패")
        return

    # 기존 히스토리 로드
    hist = {}
    if hist_path.exists():
        try:
            hist = json.loads(hist_path.read_text(encoding="utf-8"))
        except Exception:
            hist = {}

    cutoff = time.time() - WINDOW_SEC
    peak = {}

    # 이번 스냅샷 추가
    for l in d.get("lives", []):
        cid = l.get("channelId")
        if not cid:
            continue
        v = l.get("viewers", 0)
        e = hist.get(cid)
        if not e:
            e = {"name": l.get("channelName", "?"), "image": l.get("channelImage", ""), "points": []}
            hist[cid] = e
        else:
            # 이름/이미지 갱신
            if l.get("channelName"):
                e["name"] = l["channelName"]
            if l.get("channelImage"):
                e["image"] = l["channelImage"]
        pts = e["points"]
        # 같은 ts 중복 방지
        if not pts or pts[-1][0] != ts:
            pts.append([ts, v])

    # 오래된 포인트 정리 + 피크 계산
    for cid in list(hist.keys()):
        e = hist[cid]
        e["points"] = [p for p in e["points"] if p[0] >= cutoff]
        if not e["points"]:
            del hist[cid]
            continue
        peak[cid] = max(p[1] for p in e["points"])

    # 상위 500 채널만 유지
    if len(hist) > TOP_N:
        top = set(sorted(peak, key=peak.get, reverse=True)[:TOP_N])
        hist = {cid: e for cid, e in hist.items() if cid in top}

    hist_path.write_text(
        json.dumps(hist, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"채널 히스토리: {len(hist)}개 채널 → {hist_path.name} ({hist_path.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
