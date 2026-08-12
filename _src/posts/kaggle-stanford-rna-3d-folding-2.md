---
title: "Stanford RNA 3D 예측"
subtitle: "LLM 자동화 루프가 과학 문제의 검증 벽에 부딪힌 기록"
date: 2026-05-04
category: "Kaggle"
description: "LLM agent 루프를 300회 이상 돌려 RNA 3D 구조를 예측해 0.41124점(905/1877). 반복 속도가 아니라 검증 층의 부재가 병목이었다는 기록."
repo: "kaggle-stanford-rna-3d-folding-2"
date_basis: "저장소 생성일"
---

이 프로젝트는 Kaggle `Stanford RNA 3D Folding 2` 대회 기록이다. RNA 염기서열이 주어졌을 때 3차원 좌표를 예측하는 문제였고, 점수는 예측 구조가 실제 구조와 얼마나 잘 맞는지를 반영했다.

최종 기록은 public 기준 top score `0.41124`, 1등 score `0.55488`, `1,877`팀 중 `905`등이었다. 순위만 보면 중간권이지만, 이 프로젝트의 핵심은 성적보다 실험 방식에 있다. LLM agent가 구조생물학 문서를 읽고, 물리 제약을 코드에 주입하고, Kaggle kernel을 빌드하고, 원격 로그를 읽어 다음 실험을 고르는 자동화 루프를 300회 이상 돌렸다.

## 자동화 루프

repo의 README는 이 프로젝트를 `Autonomous MLOps Pipeline`으로 설명한다. 역할은 대략 다섯 가지였다.

| 역할         | 담당                                                                |
| ------------ | ------------------------------------------------------------------- |
| Scout        | RNA A-form helix, groove width, C1' 거리 같은 도메인 제약 조사      |
| Coder        | PyTorch/NumPy inference script에 거리 제약과 fallback geometry 삽입 |
| Tester       | dummy validation과 syntax check로 로컬 실행 가능성 확인             |
| Orchestrator | Kaggle API로 notebook package, push, status polling 수행            |
| Reflector    | remote log와 leaderboard 결과를 읽고 다음 전략 문서 갱신            |

자동화가 잘한 부분도 분명했다. 예를 들어 A-form RNA에서 인접 C1' 거리 `5.95A`, minor groove width `13.5A`, helical rise `2.81A`, rotation `32.7도` 같은 제약을 찾아 fallback 구조 생성이나 post-processing에 반영하려 했다. 단순히 "코드만 쓰는 agent"가 아니라, 실험을 설계하고 실패 로그를 다음 입력으로 접는 형태에 가까웠다.

## 실제로 막힌 곳

가장 큰 병목은 과학 문제의 검증 난이도였다. 로컬 테스트는 syntax error, shape mismatch, 파일 경로 오류를 잡을 수 있다. 하지만 RNA 3D 구조가 물리적으로 그럴듯한지, local distance constraint가 전체 topology를 망가뜨리는지는 훨씬 늦게 드러났다.

대표적인 실패는 `local constraint` 과최적화였다. agent는 P(i)-P(j), O2'(i)-O2'(i+1), C1' paired residue 거리 같은 국소 제약을 계속 제안했다. 문제는 한 구간의 거리만 맞추는 편집이 전체 backbone을 비틀 수 있다는 점이었다. 겉으로는 더 생물학적인 숫자를 넣은 것처럼 보였지만, 실제로는 전역 구조를 더 나쁘게 만들 수 있었다.

두 번째 병목은 Kaggle 원격 환경이었다. 로그에는 `biotraj` 의존성 문제, platform wheel mismatch, `test_sequences.csv` 경로 문제, 긴 Protenix inference 시간 같은 이슈가 반복됐다. 특히 hidden test 환경에서는 `/kaggle/input`의 실제 디렉터리 구조가 로컬 가정과 다를 수 있어서, 이후에는 `Path('/kaggle/input').rglob()` 기반의 파일 탐색으로 바꾸는 식의 방어가 필요했다.

## 점수보다 남은 것

이 프로젝트의 결과는 1등권과 거리가 있었다. 하지만 포트폴리오 관점에서는 보여줄 수 있는 것이 많다.

1. agentic workflow를 실제 Kaggle API와 연결했다.
2. remote notebook execution, log polling, failure reflection을 자동화했다.
3. 과학 도메인 제약을 코드로 옮기는 실험을 반복했다.
4. 자동화가 강한 영역과 약한 영역을 분리해서 관찰했다.

가장 중요한 교훈은 "반복 속도"가 "좋은 탐색"을 보장하지 않는다는 점이다. 300회 이상 돌릴 수 있어도, 좋은 surrogate validation이 없으면 agent는 같은 종류의 실패를 조금씩 다르게 반복한다. 특히 3D 구조 예측처럼 global geometry가 중요한 문제에서는 로컬 실행 성공과 리더보드 점수 사이의 거리가 크다.

## 다음에 다시 한다면

다시 이 문제를 한다면 자동화 루프를 더 느리게 만들더라도 검증 층을 먼저 강화할 것이다.

1. distance constraint별 ablation을 작게 고정한다.
2. RMSD/TM-score 계열 local validation proxy를 별도 리포트로 남긴다.
3. 후보 구조를 3D viewer나 geometry summary로 사람이 빠르게 볼 수 있게 한다.
4. Kaggle 제출 전에는 path, dependency, runtime budget을 별도 preflight로 분리한다.
5. LLM에게 새 전략을 만들게 하기 전에 실패 유형 taxonomy를 먼저 업데이트한다.

이 대회는 "LLM이 알아서 과학 문제를 풀었다"는 성공담이라기보다, 자동화가 어디까지 빠르게 밀어붙일 수 있고 어디서 사람의 모델링 감각이 필요한지를 보여준 실험에 가깝다. 그래서 더 포트폴리오에 남길 만하다. 화려한 점수는 아니지만, 자동화 시스템을 실제 제약 많은 환경에 던졌을 때 무엇이 깨지는지 기록했기 때문이다.

## 기록 포인트

- 상세 시스템 설명은 repo의 `README.md`에서 확인할 수 있습니다.
- 실험 흔적은 `notebooks/logs_v*`, `docs/current_strategy.txt`, `docs/reflect_prompt.txt`에 남아 있습니다.
- 이 페이지는 RNA 3D 구조 예측 자체보다 agentic MLOps와 검증 병목을 중심으로 정리합니다.
