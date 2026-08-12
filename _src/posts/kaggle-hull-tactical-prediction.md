---
title: "Hull Tactical 시장 예측"
subtitle: "public 과적합 함정은 피했지만 live regime shift에는 졌다"
date: 2026-06-30
category: "Kaggle"
description: "Sharpe 17+ public 점수를 함정으로 보고 보수적으로 갔다. 2026년 1-6월 live 평가에서 3.898부터 -0.379까지, static model의 한계를 확인했다."
repo: "kaggle-hull-tactical-prediction"
date_basis: "본문 명시(2026-01~06 live 평가)"
---

이 프로젝트는 Kaggle `Hull Tactical Market Prediction` 대회에서 만든 quant 모델과 live evaluation 실패 분석을 정리한 기록이다. 대회 목표는 S&P 500 excess return을 예측하고, modified Sharpe ratio 관점에서 안정적인 전략을 만드는 것이었다.

처음부터 이 대회는 일반적인 tabular competition과 조금 달랐다. public leaderboard가 높다고 끝나는 문제가 아니었다. 2026년 1월부터 6월까지 미래 시장 데이터를 live로 평가하는 구조였고, 결국 모델이 과거에 맞춘 점수보다 미래 regime을 버틸 수 있는지가 중요했다.

결론부터 쓰면, 이 모델은 public leaderboard의 과적합 함정은 피했지만 live market regime shift에는 졌다. 그래서 이 글은 성공담이라기보다, 꽤 쓸모 있는 실패 분석이다.

## 무엇을 잘 피했나

training phase의 public leaderboard에는 Sharpe `17.0+` 같은 비현실적인 점수가 보였다. 이건 좋은 신호라기보다 함정에 가까웠다. market prediction에서 그렇게 높은 public 점수가 쉽게 나온다면, 보통은 feature leakage, public test distribution overfitting, 또는 미래 데이터 구조를 외운 모델을 의심해야 한다.

그래서 전략은 일부러 보수적으로 갔다.

- walk-forward validation을 사용해 시간 순서를 지켰다.
- SHAP 기반으로 180개 이상의 feature를 약 40개 robust feature로 줄였다.
- LightGBM과 XGBoost를 매우 얕게 만들었다.
- public score를 극대화하기보다 live out-of-sample 생존을 목표로 했다.

이 선택은 초반에는 맞았다. public leaderboard의 과도한 점수를 따라가지 않은 덕분에, live evaluation 초반에는 꽤 좋은 성과가 나왔다.

| 시기       | Live OOS Sharpe | 해석                                          |
| ---------- | --------------: | --------------------------------------------- |
| 2026년 1월 |           3.898 | 안정적인 trend regime에서 보수 모델이 잘 작동 |
| 2026년 2월 |           1.584 | 변동성이 커지며 경고 신호 발생                |
| 2026년 3월 |          -0.379 | whipsaw market에서 구조적 실패                |
| 2026년 4월 |           0.721 | 손실은 멈췄지만 경쟁력은 회복하지 못함        |

여기까지 보면 "그래도 positive Sharpe로 살아남았다"고 말할 수도 있다. 하지만 포트폴리오 회고로는 그 정도 포장이 별로 의미가 없다. 이 모델은 leaderboard에서 경쟁력을 잃었고, 그 이유를 분석하는 쪽이 더 가치 있었다.

## 무엇이 문제였나

핵심 문제는 모델이 너무 static했다는 점이다.

모델은 낮은 변동성의 과거 구간에서 안정적으로 보이는 feature와 shallow tree를 사용했다. EWMA 같은 과거 기반 feature도 당시에는 합리적으로 보였다. 하지만 2026년 3월에 시장 변동성이 올라가고 whipsaw가 생기자, 이 feature들은 너무 느리게 반응했다. 결과적으로 모델은 변화한 regime을 감지하지 못하고, 뒤늦은 신호로 top을 사고 bottom을 파는 쪽에 가까워졌다.

이건 단순한 hyperparameter 실패가 아니었다. frozen submission 구조에서 dynamic risk throttling이나 regime detection이 없었다는 설계상의 한계였다. 모델이 "방향 예측"에 집중했고, "지금은 예측을 줄여야 하는 시장인가"를 충분히 다루지 못했다.

## 검증에서 배운 점

repo에는 `v24` 계열 validation 결과가 남아 있다. walk-forward validation에서는 `70`개 window를 사용했고, `v24_sharpe`는 약 `8.30`, optimized 기준은 약 `8.54`로 기록되어 있다. validation만 보면 꽤 그럴듯했다.

하지만 live phase는 validation보다 더 냉정했다. 시계열 문제에서 검증은 leakage를 줄이는 최소 조건이지, 미래 regime 적응을 보장하지 않는다. 특히 금융 데이터에서는 과거 window를 아무리 조심스럽게 나눠도, 앞으로 올 volatility spike나 liquidity 변화, macro event를 그대로 재현할 수 없다.

이 대회에서 배운 검증의 한계는 분명했다.

- public leaderboard overfitting을 피하는 것은 필요조건이다.
- walk-forward validation은 look-ahead bias를 줄여주지만 regime shift를 막아주지는 않는다.
- adversarial validation은 distribution shift 경고를 줄 수 있지만, trading risk policy를 대신하지 않는다.
- static ensemble은 live market에서 오래 버티기 어렵다.

## 다음에 다시 한다면

다음에 비슷한 financial ML 대회를 한다면 모델보다 risk layer를 더 먼저 설계할 것 같다.

1. prediction model과 exposure sizing을 분리한다.
2. volatility regime detector를 별도 모듈로 둔다.
3. live evaluation 중에는 drawdown과 volatility spike를 기준으로 throttle rule을 준비한다.
4. public leaderboard score보다 live stability report를 더 크게 본다.
5. post-mortem plot과 decision log를 처음부터 남긴다.

이 프로젝트는 점수만 보면 아쉬운 결과다. 하지만 "public trap을 의심하고 보수적으로 갔다"는 판단은 맞았고, "static model만으로 live market을 버티기 어렵다"는 교훈도 선명하게 남았다. 포트폴리오 관점에서는 이 실패가 오히려 좋은 재료다. 성공한 모델보다, 깨진 모델을 어디까지 설명할 수 있는지가 더 오래 남을 때가 있다.

## 더 읽을거리

- 상세 구현과 코드 스니펫은 repo README에서 확인할 수 있다.
- 이 글은 public leaderboard 회피, live regime shift, risk management 교훈을 중심으로 요약했다.
- 특히 walk-forward validation이 leakage를 줄여도 frozen live submission의 regime shift 대응까지 보장하지는 않는다는 점을 실패 사례로 남겼다.
