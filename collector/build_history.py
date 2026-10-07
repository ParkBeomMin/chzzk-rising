#!/usr/bin/env python3
"""채널별 시청자 히스토리 집계.

data/snapshot_*.json들을 읽어 채널별 시계열 데이터를 만든다.
출력: data/channel_history.json
  { channelId: {name, image, points: [[ts_epoch, viewers], ...]} }

- 최근 48시간 이내 스냅샷만 사용
- 피크 시청자 기준 상위 500 채널만 포함 (파일 크기 관리)
"""
import json
import time
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
WINDOW_SEC = 48 * 3600
TOP_N = 500


def parse_ts(s):
    # "2026-10-07T09:24:57.427729+09:00" → epoch
    from datetime import datetime
    try:
        return int(datetime.fromisoformat(s).timestamp())
    except Exception:
        return 0


def main():
    now = time.time()
    snaps = sorted(DATA.glob("snapshot_*.json"))
    hist = defaultdict(list)  # channelId → [(ts, viewers)]
    meta = {}  # channelId → {name, image}
    peak = defaultdict(int)

    for sp in snaps:
        try:
            d = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            continue
        ts = parse_ts(d.get("collectedAt", ""))
        if not ts or now - ts > WINDOW_SEC:
            continue
        for l in d.get("lives", []):
            cid = l.get("channelId")
            if not cid:
                continue
            v = l.get("viewers", 0)
            hist[cid].append((ts, v))
            peak[cid] = max(peak[cid], v)
            if cid not in meta:
                meta[cid] = {"name": l.get("channelName", "?"), "image": l.get("channelImage", "")}

    # 상위 채널만
    top = sorted(peak, key=peak.get, reverse=True)[:TOP_N]
    out = {}
    for cid in top:
        pts = sorted(hist[cid])
        # 같은 ts 중복 제거
        seen = set()
        clean = []
        for ts, v in pts:
            if ts not in seen:
                seen.add(ts)
                clean.append([ts, v])
        out[cid] = {"name": meta[cid]["name"], "image": meta[cid]["image"], "points": clean}

    path = DATA / "channel_history.json"
    path.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"채널 히스토리: {len(out)}개 채널 → {path.name} ({path.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    main()
