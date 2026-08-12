---
title: "Kaggle S6E2 심장질환 예측"
subtitle: "1위와 0.00029 차이, 그리고 제출 파일 검증의 비용"
date: 2026-02-13
category: "Kaggle"
description: "CatBoost 앙상블과 pseudo-labeling으로 private AUC 0.95506, 1위와 0.00029 차이. 막판 제출 에러로 좋은 모델과 안전한 제출은 별개임을 배웠다."
repo: "kaggle-heart-disease-prediction"
date_basis: "저장소 생성일"
---

이 프로젝트는 Kaggle `Playground Series - Season 6, Episode 2` 심장 질환 예측 대회 기록이다. 목표는 tabular clinical feature를 바탕으로 `Heart Disease` 여부를 예측하는 binary classification이었고, 평가지표는 AUC-ROC였다.

최고 private score는 `0.95506`, 최고 public score는 `0.95349`였다. private 기준 1위 reference score `0.95535`와의 차이는 단 `0.00029`였다. 숫자만 보면 아주 좋은 결과지만, 이 프로젝트에서 더 오래 남은 건 "좋은 모델"과 "안전한 제출 파이프라인"은 별개의 문제라는 점이었다.

## 무엇이 먹혔나

핵심 모델은 `CatBoost`였다. 이 대회는 synthetic tabular data 성격이 강했고, 범주형 변수와 비선형 상호작용을 안정적으로 다루는 CatBoost가 강하게 작동했다. LightGBM, XGBoost, simple NN도 실험했지만, 최종 ensemble에서 CatBoost 비중이 약 `0.85`까지 올라간 것이 상징적이었다.

주요 접근은 세 가지였다.

| 축                  | 내용                                                          |
| ------------------- | ------------------------------------------------------------- |
| External data       | UCI Heart Disease 원본 920 rows를 통합해 synthetic noise 완화 |
| Feature engineering | `MaxHR_Age_Ratio`, `ST_MaxHR_Interaction`, target encoding    |
| Ensemble            | OOF AUC를 최대화하도록 SLSQP 기반 hill climbing weight 탐색   |

feature importance에서도 `Max HR`, `Cholesterol`, `Number of vessels fluro`, `MaxHR_Age_Ratio`, `ST depression` 같은 임상적으로 납득 가능한 feature가 위에 있었다. synthetic playground 데이터라고 해도, 도메인 감각이 완전히 사라지는 것은 아니었다.

## Pseudo-Labeling

pseudo-labeling은 test prediction confidence가 높은 샘플을 train에 다시 넣어 재학습하는 방식으로 사용했다. 기록상 threshold는 `0.98` 또는 `0.99` 계열이었다. 이 접근은 단일 모델 성능을 끌어올리는 데 도움이 됐다.

다만 pseudo-labeling은 늘 양날이다. test distribution에 적응할 수 있지만, 잘못된 high-confidence sample이 들어가면 모델의 자기 확신을 증폭한다. 이 프로젝트에서는 CatBoost dominant ensemble과 함께 썼을 때 효과가 있었지만, 후반부 round2에서는 제출 에러와 id/order 위험이 같이 커졌다.

## MLOps로 얻은 것

로컬에서 전부 돌리기보다 Kaggle CLI와 notebook runner를 사용해 원격 실행 파이프라인을 만들었다.

1. `src/` 아래에 model, preprocessing, ensemble 코드를 모듈화한다.
2. `notebooks/kaggle_runner/runner.py`를 Kaggle entrypoint로 둔다.
3. `kernel-metadata.json`과 `kaggle kernels push`로 cloud execution을 위임한다.
4. 결과물을 내려받아 local analysis와 submission 검증으로 이어간다.

이 흐름은 단순한 대회용 편의 기능이 아니었다. 실험이 많아질수록 notebook 안에 로직을 쌓는 방식은 금방 무너진다. repo 중심 구조와 cloud runner를 분리한 덕분에, 이후 다른 Kaggle tabular 작업에도 가져갈 수 있는 보일러플레이트가 생겼다.

## 뼈아픈 부분

가장 뼈아픈 실패는 막판 `SubmissionStatus.ERROR`였다. 기록상 `train_pseudo_round2.py`, `fix_submission.py` 계열 결과물이 Kaggle 시스템에서 에러를 냈고, 원인은 크게 두 가지로 추정됐다.

1. ensemble/post-processing 과정에서 확률값이 `[0, 1]` 범위를 미세하게 벗어났을 가능성
2. pseudo-labeling 후 test set을 다시 분리하면서 `id` order가 어긋났을 가능성

이건 모델링 문제가 아니라 운영 문제였다. AUC가 높아도 제출 파일이 깨지면 아무 의미가 없다. 다음부터는 submission 생성 직후 아래 검증이 pipeline 마지막에 강제로 들어가야 한다.

```python
assert submission["Heart Disease"].between(0, 1).all()
assert len(submission) == len(sample_submission)
assert submission["id"].equals(sample_submission["id"])
```

이 세 줄은 멋지진 않지만 제출권을 지켜준다. 대회 막판에는 이런 방어 코드가 모델 아이디어만큼 중요해진다.

## 배운 것

이 프로젝트는 좋은 성적과 좋은 반성을 동시에 남겼다.

- synthetic tabular에서는 CatBoost가 여전히 강력한 baseline이자 final model이 될 수 있다.
- pseudo-labeling은 효과가 있지만, id/order와 calibration 검증을 더 엄격히 해야 한다.
- hill climbing ensemble은 모델 수보다 OOF quality와 correlation 관리가 중요하다.
- private score가 1위에 가까워도 public rank와 운영 안정성은 별도 축이다.
- Kaggle CLI runner 구조는 반복 실험 속도를 크게 올린다.

가장 마음에 남는 문장은 이것이다. "0.00029 차이까지 모델을 끌어올릴 수 있어도, 제출 파일 검증 세 줄을 빼먹으면 그 노력은 쉽게 증발한다." 그래서 이 회고는 성적 자랑보다, 좋은 모델을 안전한 artifact로 끝내는 법에 더 가깝다.

## 기록 포인트

- 상세 회고는 repo의 `docs/retrospective_analysis.md`에 정리되어 있습니다.
- 포트폴리오 요약은 `docs/portfolio_summary.md`, feature importance는 `docs/feature_importance.csv`에서 확인할 수 있습니다.
- 이 페이지는 의료 예측 자체보다 synthetic tabular, CatBoost ensemble, Kaggle CLI MLOps, submission validation 교훈을 중심으로 정리합니다.
