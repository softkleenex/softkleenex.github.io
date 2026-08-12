---
title: "해운물류 센서 이상탐지 회고"
subtitle: "익명 센서 52개로 21개 비정상 작동 유형을 가른다"
date: 2025-10-02
category: "DACON"
description: "익명화된 해양 장비 센서 데이터로 21개 클래스를 분류한 대회에서 946팀 중 236위. 피처를 149개까지 늘린 실험과 hard class 대응이 늦었던 반성을 남겼다."
repo: "dacon-shipping-anomaly-detection"
date_basis: "저장소 생성일"
---

해양 장비 센서 데이터에서 정상과 비정상 작동 유형을 구분하는 DACON 대회였다. 입력은 `X_01`부터 `X_52`까지 익명화된 52개 센서 신호였고, 목표는 21개 class를 맞히는 다중분류였다. 평가지표는 Macro-F1이라서 평균적으로 맞히는 것보다, 어려운 class를 방치하지 않는 것이 중요했다.

이 대회에서 가장 어려웠던 점은 도메인 해석이 거의 막혀 있었다는 것이다. 센서 이름이 무엇을 의미하는지 모르는 상태에서 분산, 상관, class별 평균 차이, 클러스터 거리 같은 통계적 단서로만 비정상 작동 패턴을 찾아야 했다. 최종 private 결과는 `0.75515`, 236등 / 946팀, 상위 24.9%였다. 1위 `0.88997`과의 격차가 있어서 만족스러운 상위권 성과는 아니었지만, 블랙박스 센서 데이터에서 feature engineering과 ensemble 운영의 한계를 꽤 선명하게 배운 프로젝트였다.

## 접근

초기 분석에서는 class 개수는 균형에 가까웠지만, class별 난이도는 전혀 균형이 아니었다. 빠른 LightGBM benchmark 기준으로 일부 class는 F1이 0.90을 넘었지만, class `9`, `0`, `15`, `19`, `3`은 크게 무너졌다. 이 때문에 단순 accuracy 관점보다 “Macro-F1에서 발목 잡는 class가 무엇인지”를 먼저 보는 방향으로 실험을 잡았다.

feature engineering은 52개 원본 센서를 149개 후보 feature로 확장하는 방식이었다. class 평균 차이가 큰 `X_19`, `X_37`, `X_40`, `X_11`, `X_28`을 중심으로 interaction을 만들고, row-level mean/std/skew/kurtosis, quantile, IQR, positive/negative count, PCA component, KMeans cluster label과 거리 feature를 추가했다. 상관이 높은 pair는 일부 제거해서 feature 수 증가가 그대로 noise가 되지 않도록 했다.

모델은 LightGBM, XGBoost, CatBoost를 soft voting으로 묶었다. GPU를 적극적으로 쓰려고 했지만, 실제 운영에서는 CatBoost GPU가 약 11.8GB를 요청하다가 8GB VRAM 환경에서 OOM으로 죽었다. 결국 LightGBM과 XGBoost는 GPU를 쓰고, CatBoost는 CPU로 돌리는 하이브리드 구성이 더 현실적이었다.

## 무엇이 통했고, 무엇이 막혔나

통한 것은 블랙박스 feature라도 통계적 구조가 있다는 점이었다. 저분산 feature 29개, 고상관 pair, class별 판별력이 큰 feature를 찾고, 그 주변에서 interaction과 clustering feature를 만들자 baseline보다 더 넓은 탐색이 가능해졌다. 센서 의미를 몰라도 row-level 통계와 거리 feature는 어느 정도의 domain substitute 역할을 했다.

막힌 것은 “feature를 더 많이 만들면 계속 좋아질 것”이라는 기대였다. 52개에서 149개로 늘리는 과정은 유용했지만, 어느 순간부터 noise와 차원의 저주가 같이 들어왔다. 특히 Macro-F1에서는 쉬운 class의 점수를 조금 올리는 것보다, 어려운 class의 오분류 구조를 직접 건드리는 쪽이 더 중요했다. 단순 class balance는 충분하지 않았다. 데이터 수가 균등해도 class boundary 난이도는 균등하지 않았다.

가장 아쉬운 점은 hard class 전용 전략이 늦었다는 것이다. class `9`, `0`, `15`, `19`, `3`처럼 낮은 F1을 보이는 class에 대해 one-vs-rest 분석, confusion pair별 보정, class-specific sampling, pseudo-label filtering을 더 빨리 했어야 했다. 전체 feature engineering과 ensemble을 넓게 밀기보다, Macro-F1을 실제로 깎는 class를 좁게 파고드는 시간이 더 필요했다.

## 회고

이 프로젝트는 “도메인 지식 없이도 어느 정도는 갈 수 있지만, 끝까지는 어렵다”는 쪽에 가까웠다. 센서 이름이 숨겨져 있어도 통계적 패턴과 ensemble로 상위 24.9%까지는 만들 수 있었다. 하지만 상금권이나 최상위권을 노리려면 익명 feature를 feature로만 보지 않고, class boundary와 오류 유형을 더 적극적으로 역추적해야 했다.

그래도 좋은 훈련이었다. local benchmark, feature importance, class-wise F1, GPU 리소스 문제, 제출 파일 운영이 한 번에 엮인 대회였고, 이후 ETRI 같은 더 큰 작업에서 “feature 의미를 기록하고, 로그와 제출 파일을 맞추고, hard segment를 따로 봐야 한다”는 습관으로 이어졌다.
