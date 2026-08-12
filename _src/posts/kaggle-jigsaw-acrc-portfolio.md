---
title: "Jigsaw ACRC 룰 위반 분류"
subtitle: "LoRA가 crash 없이 조용히 망가질 때 원인을 좁히는 법"
date: 2025-10-25
category: "Kaggle"
description: "LoRA adapter를 붙였더니 에러 없이 모든 예측이 0.0. prompt와 데이터 불균형을 차례로 지우고 4B/1.5B base mismatch를 찾아낸 silent failure 추적기."
repo: "kaggle-jigsaw-acrc-portfolio"
date_basis: "저장소 생성일"
---

이 프로젝트는 Kaggle `Jigsaw Agile Community Rules Classification` 대회 기록이다. Reddit 댓글과 subreddit rule, positive/negative example이 주어졌을 때 해당 댓글이 rule을 위반하는지 예측하는 few-shot binary classification 문제였다.

최종 결과는 2,444팀 중 1,121등, score `0.904 ROC-AUC`였다. 순위 자체는 화려하지 않다. 하지만 이 프로젝트는 포트폴리오에서 다른 의미가 있다. public LoRA adapter를 붙였을 때 모델이 에러 없이 로드되지만 모든 예측을 `0.0`으로 내뱉는 silent failure를 가설 기반으로 좁혀간 기록이기 때문이다.

## 문제 상황

baseline은 단순했다. 댓글 본문, rule, positive example 2개, negative example 2개를 `[SEP]`로 이어붙이고, TF-IDF + LightGBM으로 학습했다. 이 baseline은 mean CV AUC `0.614642` 정도였고, 안정적인 출발점 역할을 했다.

이후 Qwen 2.5 기반 LoRA adapter를 붙여 instruction-tuned generation으로 rule violation probability를 뽑아보려 했다. 여기서 이상한 일이 생겼다. 모델 로딩은 실패하지 않았다. parsing도 개선하면 잘 됐다. 그런데 출력이 전부 `0.0`이었다.

처음에는 prompt 문제처럼 보였다. 하지만 structured prompt로 바꾸고, chat template을 적용하고, parsing success rate를 `100%`까지 올려도 결과는 그대로였다. 즉 문제는 "답을 못 읽는 것"이 아니라, 모델이 정상적으로 숫자를 내지만 그 숫자가 전부 같은 degenerate output이라는 점이었다.

## 디버깅 흐름

| 가설                | 확인                                         | 결론                                        |
| ------------------- | -------------------------------------------- | ------------------------------------------- |
| Prompt mismatch     | ultra-structured prompt와 chat template 적용 | parsing은 좋아졌지만 all `0.0` 유지         |
| Data imbalance      | train target 분포 확인                       | violation 50.8%, non-violation 49.2%로 균형 |
| Base model mismatch | adapter config와 inference base 비교         | adapter는 4B 계열, inference는 1.5B 계열    |

결국 원인은 LoRA adapter와 base model의 mismatch였다. adapter는 다른 크기의 Qwen model에 맞춰 학습됐고, inference kernel에서는 `Qwen2.5-1.5B-Instruct`에 붙였다. 더 무서운 점은 이 과정이 명시적으로 crash하지 않았다는 것이다. `PEFT`가 로딩 과정에서 큰 에러를 내지 않으니 겉보기에는 정상처럼 보였지만, 실제 출력은 전부 무너졌다.

이건 production ML에서 자주 보는 종류의 문제다. config가 있고, weight가 로드되고, inference가 돌아가면 성공처럼 보인다. 하지만 output distribution을 보지 않으면 시스템은 조용히 잘못된 값을 계속 낼 수 있다.

## 배운 것

이 프로젝트에서 제일 큰 교훈은 "모델이 실행되는 것"과 "모델이 의미 있는 예측을 하는 것"은 다르다는 점이다.

LLM/LoRA inference에서는 다음 검사가 필요하다.

1. adapter config의 base model 이름과 inference base model을 비교한다.
2. output distribution sanity check를 항상 한다.
3. 작은 sample에서 class별 response 다양성을 본다.
4. parsing success와 prediction quality를 분리해서 기록한다.
5. 외부 adapter를 쓸 때는 compatibility를 CI 수준에서 검사한다.

이 대회에서는 DeBERTa/SetFit 계열 접근으로 최종 `0.904 ROC-AUC`까지 갔지만, 더 오래 남은 건 LoRA 실패 분석이었다. 좋은 포트폴리오 기록은 항상 최고 점수만 보여줄 필요는 없다. 조용히 망가지는 시스템을 어떻게 추적했는지 보여주는 것도 실전 ML 역량에 가깝다.

## 더 읽을거리

- 상세 실패 분석은 repo의 `docs/FAILURE_ANALYSIS.md`에서 확인할 수 있다.
- 이 글은 LoRA compatibility, degenerate output, production ML debugging 교훈을 중심으로 요약했다.
- 특히 adapter/base model mismatch가 crash 없이 all-zero prediction으로 이어질 수 있다는 점을 output sanity check 사례로 남겼다.
