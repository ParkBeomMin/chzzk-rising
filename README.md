# 🧭 치지직 나침반

치지직에서 **지금 급상승 중인 스트리머**를 찾아주는 사이트.

## 컨셉

치지직 기본 랭킹은 시청자 수 순이라 대형 스트리머만 보인다.
나침반은 **성장률(모멘텀)** 기준으로 랭킹을 매겨, 묻혀 있던 라이징 스트리머를 발굴한다.

## 구조

```
chzzk-rising/
├── collector/
│   ├── collector.py      # 치지직 API로 실시간 방송 수집 → data/snapshot_*.json
│   ├── rising.py          # 두 스냅샷 비교 → 성장률 랭킹 → frontend/data/rising.json
│   └── threads_post.py   # 스레드 일일 포스트 텍스트 생성
├── frontend/
│   ├── index.html        # 랭킹 페이지 (정적)
│   └── data/
│       ├── latest.json   # 최신 방송 목록
│       └── rising.json   # 라이징 랭킹
├── data/                 # 원본 스냅샷 보관
└── .github/workflows/collect.yml  # 매시간 자동 수집
```

## 데이터

- 소스: 치지직 공개 Service API (`api.chzzk.naver.com/service/v1/lives`) — 인증 불필요
- 수집 주기: 1시간 (GitHub Actions)
- 라이징 계산: 이전 스냅샷 대비 시청자 수 성장률

## 수익 모델

- AdSense (frontend에 광고 슬롯 준비됨)
- 스레드 일일 포스트로 트래픽 유입 ("오늘의 라이징 TOP 5")

## 배포

GitHub Pages에 `frontend/` 내용을 배포.
