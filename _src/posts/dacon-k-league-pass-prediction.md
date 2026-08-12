---
title: "K리그 패스 좌표 예측 회고"
subtitle: "복잡한 모델보다 단단한 Zone baseline이 이겼다"
date: 2026-01-18
category: "DACON"
description: "K리그 패스 도착 좌표 예측 대회에서 1,782팀 중 121위, 상위 6.8%. delta 예측과 LOGO CV로 검증하며 Zone 6x6 baseline이 왜 더 강했는지 정리했다."
repo: "dacon-k-league-pass-prediction"
date_basis: "저장소 생성일"
---

이 프로젝트는 2024 시즌 K리그 경기 데이터를 바탕으로 episode의 마지막 패스 도착 좌표 `(x, y)`를 예측하는 DACON 대회 기록이다. 최종 private score는 `13.5100`, private rank는 1,782팀 중 121등, 상위 약 6.8%였다.

처음에는 축구 패스니까 복잡한 sequence model이나 많은 domain feature가 좋을 것 같았다. 하지만 실제로는 "새 경기에서도 무너지지 않는 단순한 공간 baseline"이 훨씬 중요했다. 이 대회는 모델 복잡도보다 OOD 일반화와 검증 방식이 더 크게 남은 프로젝트였다.

## 문제를 어떻게 바꿨나

대회 입력은 경기 내 패스 이벤트 sequence, 선수와 팀 정보, 시간 정보였고, 출력은 마지막 패스의 도착 좌표였다. 평가 지표는 Euclidean distance라 낮을수록 좋았다.

가장 먼저 한 중요한 선택은 절대 좌표를 직접 맞히는 대신, 시작점 대비 변화량인 `dx`, `dy`를 예측하는 것이었다. 축구에서 패스는 필드의 절대 위치도 중요하지만, 실제로는 현재 공 위치에서 어떤 방향과 거리로 전개되는지가 더 자연스럽다. delta prediction은 모델이 특정 좌표에 과하게 외우는 것을 줄이고, 패스 벡터의 물리적 의미를 더 잘 보게 했다.

## 점수에 도움이 된 것

| 접근                      | 효과                                       |
| ------------------------- | ------------------------------------------ |
| Delta prediction          | 도착 절대 좌표 대신 패스 벡터를 예측       |
| Iterative pseudo-labeling | public score 기준 약 `13.54 -> 13.43` 개선 |
| LOGO CV                   | 새 경기 OOD 일반화를 확인                  |
| Zone 6x6                  | 복잡한 모델보다 안정적인 공간 prior 제공   |

대회 후반에는 test 예측을 pseudo-label로 다시 학습에 넣는 iterative pseudo-labeling을 사용했다. public score 기준으로 `13.54` 근처에서 `13.43`까지 내려갔고, 최종 제출 계열의 핵심이 됐다.

하지만 더 중요한 교훈은 Zone 6x6였다. 경기장을 36개 구역으로 나누는 단순한 공간 모델이, 복잡한 LSTM이나 과한 feature engineering보다 더 안정적이었다. 특히 LOGO, 즉 Leave-One-Game-Out 검증에서 새 경기로 넘어갔을 때의 gap을 보는 것이 중요했다.

## 실패한 가설

가장 인상 깊었던 실패는 domain v2였다. "축구 도메인 지식을 더 넣고, 강한 정규화를 쓰면 OOD에 강해지지 않을까?"라는 가설이었다. 결과는 반대였다. 너무 적은 feature와 과도한 regularization으로 underfitting이 심해졌고, 핵심 공간 패턴을 제거하면서 CV가 `18.37` 수준까지 나빠졌다.

이때 배운 건 단순함과 빈약함은 다르다는 점이다. 단순한 모델은 좋을 수 있지만, 문제의 핵심 신호까지 없애면 그냥 못 맞히는 모델이 된다. 축구 패스 좌표 예측에서 field zone은 제거할 노이즈가 아니라 유지해야 할 구조였다.

## 회고

이 대회는 "복잡한 모델이 항상 이긴다"는 생각을 꽤 세게 꺾어줬다. sequence model은 그럴듯했고, 파생 feature도 많을수록 좋아 보였지만, 실제 새 경기에서는 오히려 쉽게 흔들렸다. 반대로 Zone 6x6처럼 단순한 공간 prior는 설명 가능하고, 검증에서도 안정적이었다.

다음에 비슷한 sports analytics 문제를 한다면 초반부터 이렇게 할 것 같다.

1. 절대 좌표와 delta target을 나눠서 비교한다.
2. LOGO CV를 기본 검증으로 둔다.
3. 복잡한 sequence model은 OOD gap을 통과한 뒤에만 채택한다.
4. 경기장 zone, 방향, 거리처럼 핵심 공간 prior는 끝까지 보존한다.
5. pseudo-labeling은 public feedback에 끌려가기 쉬우므로 제출 로그와 함께 관리한다.

이 프로젝트는 상위 6.8%라는 결과도 좋았지만, 그보다 "단순한 baseline이 왜 강한지"를 실제로 체감한 경험으로 남았다. AI 대회에서 멋진 모델보다 검증을 버티는 구조가 더 중요할 때가 있다는 걸 배웠다.

## 더 읽을거리

- 상세 제출 기록과 구현 구조는 repo README와 `analysis_results/`, `docs/`에 남겨 두었다.
- 이 글은 delta prediction, pseudo-labeling, LOGO CV, Zone 6x6 baseline의 교훈을 중심으로 요약했다.
- 특히 public score 개선보다 private/OOD 일반화를 더 믿을 수 있게 만든 검증 방식이 핵심 기록이다.
