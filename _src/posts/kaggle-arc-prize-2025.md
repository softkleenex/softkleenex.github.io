---
title: "ARC Prize 2025 추상 추론"
subtitle: "로컬 98% 픽셀 매치도 pass@2에서는 0점이 되는 평가 구조"
date: 2025-11-17
category: "Kaggle"
description: "rule-based DSL과 program search로 ARC에 도전해 public 1.67점. 로컬 97-98% 픽셀 매치가 왜 0점이 되는지, DSL 탐색이 어디서 막히는지를 정리했다."
repo: "kaggle-arc-prize-2025"
date_basis: "저장소 생성일"
---

이 프로젝트는 Kaggle `ARC Prize 2025` 대회 기록이다. ARC는 작은 grid 입출력 예시 몇 개를 보고, 새로운 input grid에 같은 추상 규칙을 적용해 output grid를 맞히는 문제다. 겉으로는 색깔 있는 작은 배열 문제처럼 보이지만, 실제로는 few-shot abstraction, object-centric reasoning, program synthesis가 섞인 어려운 벤치마크다.

최종 public leaderboard 기록은 `1.67`점, 약 top 45%였다. README에는 1위 `27.64`점과의 차이도 남아 있다. 이 숫자는 높지 않지만, 이 프로젝트에서 남은 핵심은 점수보다 실패의 모양이다. 로컬에서는 일부 task가 `97-98%` pixel match까지 갔지만, ARC의 pass@2 평가는 정답 grid와 완전히 같아야 점수를 준다. 1-3%의 픽셀 차이가 0점과 만점의 차이가 됐다.

## 빠르게 만든 것

초기 목표는 Kaggle code competition 제출 루프를 빨리 닫는 것이었다. JSON을 직접 업로드하는 대회가 아니라 notebook output을 제출해야 했기 때문에, kernel metadata, offline execution, submission.json 형식 검증까지 먼저 맞췄다.

그 뒤 solver는 하루 안에 빠르게 커졌다.

| 버전   | 방향                  | 메모                                                    |
| ------ | --------------------- | ------------------------------------------------------- |
| V1     | baseline transforms   | rotate, flip, transpose, scale, tile                    |
| V2-V3  | color/pattern/object  | color mapping, symmetry, crop, padding                  |
| V4     | multi-step transforms | border, quadrant, row/column rules                      |
| V5     | broader ensemble      | 50+ transforms, scoring and fallback                    |
| V8-V10 | hybrid/DSL/search     | DSL program search, transform search, learning fallback |

V10은 세 단계 pipeline에 가까웠다. 먼저 DSL primitive 조합을 찾고, 안 되면 50개 이상의 custom transform을 검증하고, 마지막에는 size ratio, color mapping, repeating pattern 같은 rule을 학습하려 했다.

## 왜 어려웠나

ARC의 함정은 "대충 맞음"이 점수로 이어지지 않는다는 것이다. 로컬 평가 문서에는 모든 V2-V5가 exact accuracy `0.00%`였지만, partial match는 `97-98%`까지 나오는 케이스가 있었다. 사람이 보면 방향은 맞아 보이지만, 평가 시스템은 한 칸이라도 틀리면 그 task를 틀린 것으로 본다.

실패 패턴도 반복됐다.

| 실패 유형        | 비율/예시 | 의미                                 |
| ---------------- | --------- | ------------------------------------ |
| Size mismatch    | 약 30%    | 출력 grid 크기 규칙을 제대로 못 배움 |
| Pattern wrong    | 약 50%    | 크기는 맞아도 논리/객체 규칙이 틀림  |
| Color wrong      | 약 15%    | 색상 매핑이나 색상 의미 해석 실패    |
| Completely wrong | 소수      | 정의한 primitive 밖의 문제           |

처음에는 변환 함수를 늘리면 점수가 오를 것처럼 느껴졌다. 하지만 ARC에서는 primitive 개수보다 "이 task에서 어떤 개념을 보고 있는가"가 더 중요했다. 같은 색상 변경도 단순 remap인지, object role인지, count 결과인지에 따라 전혀 다른 규칙이 된다.

## DSL의 한계

rule-based DSL은 필요한 출발점이었다. 작은 grid에서 rotate, flip, crop, recolor 같은 연산을 program으로 표현하면, train examples에 맞는 후보를 탐색할 수 있다. 문제는 search depth가 조금만 깊어져도 조합 수가 폭발한다는 점이다.

더 근본적인 한계도 있었다.

1. predefined primitive 안에 없는 개념은 찾을 수 없다.
2. object, containment, symmetry, counting을 모두 grid-level numpy operation으로만 표현하기 어렵다.
3. train example 2-4개에 딱 맞는 program이 test input에서도 맞는다는 보장이 없다.
4. pixel-level partial score가 좋아도 pass@2 task score는 0이 될 수 있다.

그래서 이 프로젝트는 "DSL을 만들면 ARC가 풀린다"보다 "DSL만으로는 어디까지 막히는지"를 확인한 쪽에 가깝다.

## 다음에 다시 한다면

다시 ARC를 한다면 transform catalog를 더 늘리는 것보다 representation을 먼저 바꿀 것이다.

1. grid를 connected components와 object graph로 변환한다.
2. 색상을 단순 숫자가 아니라 background, marker, object id 같은 role로 추론한다.
3. candidate program마다 exact match뿐 아니라 실패 유형 taxonomy를 남긴다.
4. open-weight LLM이나 vision-language model로 primitive proposal을 만들되, 실행/검증은 symbolic하게 둔다.
5. test-time training이나 task-specific search를 쓰더라도 Kaggle 12시간 제한 안에서 budgeted search를 설계한다.

ARC는 "많이 시도하면 언젠가 맞는다"가 잘 통하지 않는 문제였다. 오히려 작은 task 하나를 제대로 이해하는 능력이 중요했다. 이 점이 매력적이면서도 답답했다. 컴퓨터는 98%를 맞혔다고 말하지만, ARC는 "그럼 나머지 2%는 왜 틀렸는데?"라고 묻는다.

## 기록 포인트

- 빠른 제출 루프와 code competition 운영은 repo의 `docs/evaluation_reports/FINAL_SUMMARY.md`에 남아 있습니다.
- 실패 유형 분석은 `docs/evaluation_reports/EVALUATION_INSIGHTS.md`에서 확인할 수 있습니다.
- 이 페이지는 ARC score 자체보다 pixel-perfect reasoning, DSL search 한계, object-centric representation 필요성을 중심으로 정리합니다.
