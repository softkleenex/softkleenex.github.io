---
title: "Toss CTR 예측 대회 회고"
subtitle: "익명 광고 로그에서 AUC 0.0025를 올리는 일"
date: 2025-10-13
category: "DACON"
description: "토스 광고 클릭률 예측 대회 기록. 1,070만 행 로그와 1.91% 클릭률 위에서 피처 엔지니어링과 rank calibration으로 AUC를 0.3409에서 0.3434까지 밀어올렸다."
repo: "dacon-toss-ctr-prediction"
date_basis: "저장소 생성일"
---

이 프로젝트는 DACON `Toss NEXT 2025 ML Challenge - 광고 클릭률(CTR) 예측` 기록이다. 토스 앱 안에서 광고가 노출됐을 때 사용자가 클릭할 확률을 예측하는 binary classification 문제였다.

최종 private leaderboard 기록은 `0.3434805649` AUC였고, 1위 점수 `0.35179`와의 차이는 `-0.00831`이었다. 데이터는 train `10.7M` rows, test `1.5M` rows 규모였고, click rate는 약 `1.91%`로 매우 낮았다. 이 대회는 화려한 딥러닝보다 익명화된 광고 로그에서 조금이라도 신호를 더 보존하는 tabular engineering 싸움에 가까웠다.

## 왜 어려웠나

CTR 문제는 겉으로는 간단하다. 클릭하면 1, 클릭하지 않으면 0이다. 하지만 실제로는 대부분의 row가 non-click이고, 피처명은 익명화되어 있으며, train/test distribution을 직접 이해하기 어렵다. `history_b_21`, `feat_b_3`, `feat_c_8` 같은 이름만 보고 도메인을 알 수 없으니, 의미를 "확정"하기보다 패턴을 조심스럽게 가정해야 했다.

이때 중요한 건 이름이 아니라 관계였다.

- `history_*` 계열은 과거 반응이나 노출 이력에 가까운 강한 신호로 보였다.
- `feat_*` 계열은 행동/컨텍스트 신호처럼 작동했다.
- `inventory_id`, `hour`, `age_group`은 광고 지면, 시간, 사용자 세그먼트의 기본축이었다.
- 단일 피처보다 `history_a_1 x history_b_21`, `feat_b_3 / feat_c_8` 같은 조합에서 추가 신호가 나왔다.

## 성능이 오른 흐름

기록상 개선은 작지만 일관됐다.

| 단계             | AUC      | 변화      | 핵심                             |
| ---------------- | -------- | --------- | -------------------------------- |
| Baseline         | `0.3409` | -         | 22개 기본 피처, LightGBM         |
| Basic FE         | `0.3417` | `+0.0008` | 상호작용 피처 6개 추가           |
| Advanced FE      | `0.3425` | `+0.0008` | 통계/시간/다항식 포함 42+ 피처   |
| Ensemble         | `0.3432` | `+0.0007` | 5-fold x 5-seed LightGBM + XGB   |
| Rank Calibration | `0.3434` | `+0.0002` | rank-based linear transformation |

최종 모델은 LightGBM 25개, XGBoost 1-2개, weighted ensemble, 그리고 `0.248 + 0.504 x rank` 형태의 rank calibration을 사용했다. CTR처럼 raw probability가 낮게 몰리는 문제에서는 확률의 절대값보다 ordering을 안정적으로 보존하는 것이 중요했다.

## Feature Engineering

성능을 가장 많이 올린 부분은 모델 교체가 아니라 feature engineering이었다.

| 그룹        | 예시                                      | 역할                       |
| ----------- | ----------------------------------------- | -------------------------- |
| Interaction | `history_a_1 x history_b_21`              | 과거 행동 신호의 조합 효과 |
| Ratio       | `feat_b_3 / (feat_c_8 + eps)`             | 상대적 강도                |
| Statistics  | mean, std, skew, kurtosis, IQR, MAD       | 이력 피처 묶음의 분포 요약 |
| Time        | sin/cos by 24, 12, 8, 6 hour periods      | 시간의 주기성 보존         |
| Polynomial  | square, cube, sqrt, log1p for top signals | 비선형 click response 포착 |

중요도 상위에는 `history_b_21`, `history_a_1`, `feat_b_3`, `feat_c_8`, `inventory_id`, `hour`가 반복해서 등장했다. 익명화된 데이터에서도 "광고/사용자/시간/이력"이라는 CTR의 기본 구조는 꽤 강하게 남아 있었다.

## 실패한 시도

이 대회는 작은 개선이 쌓이는 만큼, 작은 실수도 크게 벌어졌다.

1. 93개 피처까지 늘렸을 때는 오히려 점수가 크게 떨어졌다. 의미 없는 조합이 늘면서 일반화가 무너졌다.
2. aggressive calibration은 ordering을 살리기보다 예측 분포를 왜곡했다.
3. 100개 이상 모델을 섞는 mega ensemble은 계산 비용만 키우고 품질 낮은 모델까지 끌고 들어왔다.
4. 10M+ row 전체를 무심코 메모리에 올리면 OOM이 반복됐다. dtype downcast, chunking, 명시적 `gc.collect()`가 필요했다.

가장 좋은 교훈은 "tabular competition에서 피처 수는 실력이 아니라 부채가 될 수 있다"는 점이었다. 42개 근처에서 멈춘 것이 성능과 안정성의 균형이었다.

## 남은 감각

이 프로젝트에서 재미있었던 건 점수의 단위가 작다는 점이다. `+0.0025` AUC는 겉보기에는 미세하지만, 830팀 규모의 CTR 대회에서는 며칠치 실험과 운영 판단이 들어간 결과였다. 특히 click rate가 `1.91%`인 환경에서는 잘못된 sampling, calibration, memory handling 하나가 바로 score collapse로 이어졌다.

다시 한다면 모델을 더 크게 만들기 전에 다음을 먼저 더 엄격히 할 것이다.

1. feature group별 ablation table을 자동 생성한다.
2. calibration 전후의 rank correlation과 probability histogram을 저장한다.
3. high-cardinality categorical 처리와 target encoding risk를 별도 audit한다.
4. memory profile을 실험 로그에 함께 남긴다.
5. 제출 파일마다 local metric, public score, calibration formula를 한 줄로 맞춘다.

CTR 예측은 결국 사람의 클릭을 맞히는 문제지만, 대회에서는 "작은 신호를 얼마나 덜 망가뜨리고 끝까지 가져가느냐"의 문제로 바뀐다. 이 프로젝트는 그 감각을 배운 기록이다.

## 기록 포인트

- 상세 제출 이력은 repo의 `docs/SUBMISSION_RECORD.md`에서 확인할 수 있습니다.
- feature engineering 근거는 `docs/FEATURES.md`, 실험 결과는 `docs/RESULTS.md`에 남아 있습니다.
- 이 페이지는 LightGBM/XGBoost ensemble보다 익명 로그 해석, calibration, 실패한 과최적화를 중심으로 정리합니다.
