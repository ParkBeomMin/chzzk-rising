#!/usr/bin/env python3
"""라이징 랭킹 계산기.

두 스냅샷을 비교해 시청자 수 성장률 기준으로 랭킹을 만든다.

사용법:
    python3 rising.py <old_snapshot.json> <new_snapshot.json> [-o output.json]

성장률 = (new_viewers - old_viewers) / max(old_viewers, 1)
노이즈 제거를 위한 필터:
    - new_viewers >= 10 (너무 작은 방송 제외)
    - old_viewers >= 5 (0→N 폭등 노이즈 완화, 단 신규 급상은 별도 처리)
    - 같은 방송(liveId)이 양쪽에 있어야 함
"""
import json
import sys
from pathlib import Path

MIN_NEW_VIEWERS = 10
MIN_OLD_VIEWERS = 5


def load_snapshot(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {l["liveId"]: l for l in d["lives"]}, d.get("collectedAt", "")


def calc_rising(old_path, new_path):
    old, old_ts = load_snapshot(old_path)
    new, new_ts = load_snapshot(new_path)

    rising = []
    for live_id, cur in new.items():
        prev = old.get(live_id)
        if not prev:
            continue  # 신규 방송은 별도 트래킹 (MVP에서는 제외)
        ov, nv = prev["viewers"], cur["viewers"]
        if nv < MIN_NEW_VIEWERS or ov < MIN_OLD_VIEWERS:
            continue
        growth = (nv - ov) / max(ov, 1)
        if growth <= 0:
            continue
        rising.append({
            **cur,
            "prevViewers": ov,
            "growthRate": round(growth, 2),
            "growthPct": f"+{int(growth * 100)}%",
            "viewerGain": nv - ov,
        })

    # 성장률 순 정렬 (동률은 시청자 증가 수로)
    rising.sort(key=lambda x: (x["growthRate"], x["viewerGain"]), reverse=True)
    return {
        "oldCollectedAt": old_ts,
        "newCollectedAt": new_ts,
        "count": len(rising),
        "ranking": rising,
    }


def main():
    if len(sys.argv) < 3:
        print("사용법: python3 rising.py <old.json> <new.json> [-o output.json]")
        sys.exit(1)
    result = calc_rising(sys.argv[1], sys.argv[2])
    out = json.dumps(result, ensure_ascii=False, indent=1)
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        Path(sys.argv[idx + 1]).write_text(out, encoding="utf-8")
        print(f"저장: {sys.argv[idx+1]} ({result['count']}개)")
    else:
        print(out[:2000])


if __name__ == "__main__":
    main()
