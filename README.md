# Softkleenex Archive

AI 대회 회고와 생성형 디자인 제작기를 쓰는 블로그입니다.
점수만 적으면 다음에 쓸 수 없어서, 무엇을 검증했고 어디서 틀렸는지를 같이 남깁니다.

**[softkleenex.github.io](https://softkleenex.github.io/)** · [글 목록](https://softkleenex.github.io/posts/) · [소개](https://softkleenex.github.io/about/) · [RSS](https://softkleenex.github.io/feed.xml)

## 글 23편

### DACON — 국내 AI 경진대회 회고 (9편)

- [웹 미니게임 해커톤 회고](https://softkleenex.github.io/posts/dacon-webgamming/) — 2026-06-28
- [ETRI 휴먼 이해 대회 회고](https://softkleenex.github.io/posts/dacon-etri-human-understanding/) — 2026-06-26
- [모기 궤적 예측 대회 회고](https://softkleenex.github.io/posts/dacon-mosquito-trajectory-prediction/) — 2026-05-06
- [HAI 2025 딥페이크 탐지 회고](https://softkleenex.github.io/posts/dacon-hai-2025/) — 2026-01-28
- [K리그 패스 좌표 예측 회고](https://softkleenex.github.io/posts/dacon-k-league-pass-prediction/) — 2026-01-18
- [MAI 유전체 모델 대회 회고](https://softkleenex.github.io/posts/dacon-mai-glm-2025/) — 2025-11-28
- [Toss CTR 예측 대회 회고](https://softkleenex.github.io/posts/dacon-toss-ctr-prediction/) — 2025-10-13
- [해운물류 센서 이상탐지 회고](https://softkleenex.github.io/posts/dacon-shipping-anomaly-detection/) — 2025-10-02
- [자동차 뉴스 분류 프롬프트 대회 회고](https://softkleenex.github.io/posts/dacon-car-news-classification/) — 2025-09-23

### Kaggle — 해외 대회와 자동화 실험 (7편)

- [Hull Tactical 시장 예측](https://softkleenex.github.io/posts/kaggle-hull-tactical-prediction/) — 2026-06-30
- [Stanford RNA 3D 예측](https://softkleenex.github.io/posts/kaggle-stanford-rna-3d-folding-2/) — 2026-05-04
- [Deep Past 아카드어 번역](https://softkleenex.github.io/posts/kaggle-dpc-tate/) — 2026-05-04
- [MedGemma 임상 RAG 번역](https://softkleenex.github.io/posts/kaggle-medgemma-clinical-rag-pipeline/) — 2026-02-21
- [Kaggle S6E2 심장질환 예측](https://softkleenex.github.io/posts/kaggle-heart-disease-prediction/) — 2026-02-13
- [ARC Prize 2025 추상 추론](https://softkleenex.github.io/posts/kaggle-arc-prize-2025/) — 2025-11-17
- [Jigsaw ACRC 룰 위반 분류](https://softkleenex.github.io/posts/kaggle-jigsaw-acrc-portfolio/) — 2025-10-25

### 대회 — 주최사가 직접 여는 대회 회고 (4편)

- [AI_TOP_100 2026 온라인 예선 회고](https://softkleenex.github.io/posts/2026-ai-top-100-preliminary/) — 2026-11-04
- [국립국어원 AI말평 글쓰기 채점 능력 평가 회고](https://softkleenex.github.io/posts/korean-writing-assessment-2026/) — 2026-08-28
- [Global Quantum AI 회고](https://softkleenex.github.io/posts/2026-quantum-ai-competition/) — 2026-08-10
- [2026 NYPC 회고록](https://softkleenex.github.io/posts/2026-nypc-retrospective/) — 2026-07-20

### 공모전 — 기획과 디자인 출품작 (2편)

- [THE COLOR HOUSE 제작기](https://softkleenex.github.io/posts/2026-the-color-house/) — 2026-07-21
- [한화생명 공모전 LifeTwin AI](https://softkleenex.github.io/posts/hlftc/) — 2026-06-28

### 기록 — 운영 방식과 템플릿 (1편)

- [DACON 대회 시작 템플릿](https://softkleenex.github.io/posts/dacon-base/) — 2026-05-06

## 이 저장소

마크다운 frontmatter를 단일 진실원으로 삼는 정적 사이트 생성기입니다.
글 페이지, 홈, 목록, RSS, 사이트맵, 이 README까지 `build.py` 하나에서 생성합니다.

```
_src/posts/*.md        글 원문 (frontmatter + 본문)
_src/templates/*.html  Jinja2 템플릿
build.py               생성기
```

빌드: `./.venv/bin/python build.py`
