---
title: "MedGemma 임상 RAG 번역"
subtitle: "의료 VLM 출력을 환자가 읽을 수 있는 언어로 번역하기"
date: 2026-02-21
category: "Kaggle"
description: "방사선 리포트를 임상 리포트와 환자용 설명으로 나눠 내는 dual-agent RAG 파이프라인. 설명 난이도를 Grade 15.3에서 7.2로 낮추고 인증·경로 문제와 싸웠다."
repo: "kaggle-medgemma-clinical-rag-pipeline"
date_basis: "저장소 생성일"
---

이 프로젝트는 Kaggle `MedGemma Impact Challenge`에서 만든 의료 VLM + RAG 파이프라인 회고다. 목표는 방사선 리포트와 의료 이미지를 읽고, 임상적 판단을 돕는 구조화된 보고서와 환자가 이해하기 쉬운 설명을 함께 만드는 것이었다.

의료 도메인에서 AI를 쓴다는 건 단순히 모델을 붙이는 일이 아니었다. 임상 용어는 정확해야 하고, 환자용 설명은 불안을 키우지 않아야 하며, cloud notebook 환경에서는 인증, 파일 경로, multimodal token 처리 같은 엔지니어링 문제가 계속 튀어나왔다.

그래서 이 프로젝트의 핵심은 "MedGemma를 써봤다"가 아니라, 제한된 Kaggle 환경에서 VLM, RAG, agentic workflow를 끝까지 실행 가능한 파이프라인으로 묶었다는 점이다.

## 문제의식

방사선 리포트는 의료진에게는 정확한 문서지만, 환자에게는 너무 어렵다. 예를 들어 `periventricular white matter changes` 같은 표현은 임상적으로는 의미가 있지만, 환자 입장에서는 무엇이 위험하고 무엇을 해야 하는지 바로 이해하기 어렵다.

이 프로젝트에서는 두 단계 agent를 나눴다.

| Agent              | 역할                                                                 |
| ------------------ | -------------------------------------------------------------------- |
| Sentinel-Clinician | VLM이 scan/report를 읽고 RAG로 근거를 보강해 임상 triage report 생성 |
| Sentinel-Guide     | 임상 결과를 환자 친화적 설명으로 번역하고 다음 행동을 안내           |

중요한 건 환자용 설명이 의료 판단을 대체하지 않는다는 점이다. 이 파이프라인은 진단을 자동 확정하는 시스템이 아니라, 의료진과 환자 사이의 언어적 간극을 줄이는 보조 도구에 가깝다.

## 측정한 효과

repo README에는 Flesch-Kincaid Grade Level 기준으로 설명 난이도를 비교한 결과가 남아 있다.

| 출력                | Grade level | 해석                           |
| ------------------- | ----------: | ------------------------------ |
| Clinical baseline   |        15.3 | 대학원 수준에 가까운 의료 문체 |
| Patient translation |         7.2 | 일반인이 읽기 쉬운 수준        |

수치만 보면 약 `53%` 정도 언어 복잡도를 낮춘 셈이다. 물론 이 수치 하나로 임상 안전성을 증명할 수는 없다. 그래도 "환자에게 읽히는 설명"을 별도 목표로 측정했다는 점은 좋았다. 의료 AI 프로젝트에서는 모델 성능뿐 아니라 사용자가 실제로 이해할 수 있는지도 같이 봐야 한다.

## 제일 크게 막힌 것들

### 1. Kaggle secret과 401 Unauthorized

MedGemma 계열 모델은 gated model access가 필요했다. 라이선스를 수락했는데도 Kaggle notebook에서 `401 Unauthorized`가 반복됐다. 원인은 단순히 토큰이 틀린 게 아니라, Kaggle `UserSecretsClient`, notebook cell 실행 순서, `transformers` 모델 초기화 타이밍이 미묘하게 엇갈리는 문제였다.

해결은 "atomic execution"이었다. 여러 cell에 흩어진 초기화를 믿지 않고, token 주입, `HF_TOKEN`/`HUGGINGFACE_HUB_TOKEN` 설정, `huggingface_hub.login()`, 모델 로딩을 하나의 단단한 실행 흐름으로 묶었다. 예쁘지는 않지만, cloud notebook에서는 이런 방어적 설계가 훨씬 중요했다.

### 2. VLM image token mismatch

초기 multimodal prompt는 `Prompt contained 0 image tokens but received 1 images` 같은 에러로 깨졌다. 사람이 보기엔 `<image>` 문자열을 넣으면 될 것 같지만, VLM 입장에서는 내부 `image_token_id`와 processor 규약이 맞아야 한다.

결국 manual string prompt를 버리고 `processor.apply_chat_template()` 기반의 structured input으로 바꿨다. image와 text를 dictionary 구조로 넣어 processor가 pixel value와 text token을 함께 맞추게 하니 visual reasoning이 정상화됐다. 이 부분은 "모델을 아는 것"보다 "processor contract를 지키는 것"이 더 중요했던 지점이다.

### 3. RAG pathing trap

FAISS 기반 RAG engine은 Kaggle dataset mount 경로 때문에 자주 깨졌다. `/kaggle/input/...` 아래 경로가 세션마다 달라질 수 있는데, absolute path를 박아두면 바로 `FileNotFoundError`가 난다.

해결은 `os.walk` 기반 dynamic discovery였다. `/kaggle/input` 전체를 훑고, 파일명과 확장자 heuristic으로 필요한 MedQuAD 자료를 찾게 했다. 멋진 알고리즘은 아니지만, ephemeral cloud filesystem에서는 이런 resilience가 실제 완성도를 갈랐다.

## 회고

이 프로젝트에서 제일 크게 배운 건 RAG와 VLM은 모델 품질만으로 완성되지 않는다는 점이다. 인증, tokenization, pathing, notebook execution state 같은 작은 엔지니어링 문제가 하나라도 흔들리면 전체 pipeline이 바로 멈춘다.

또 하나는 의료 도메인의 출력 설계다. 임상 요약과 환자 설명을 하나의 답변에 섞으면 둘 다 애매해지기 쉽다. Sentinel-Clinician과 Sentinel-Guide를 나눈 것은 좋은 선택이었다. 하나는 정확한 clinical triage에 집중하고, 다른 하나는 쉬운 언어와 행동 안내에 집중할 수 있었다.

다음에 비슷한 프로젝트를 한다면 초반부터 세 가지를 더 강하게 가져갈 것 같다.

1. cloud notebook에서 인증과 모델 로딩을 atomic smoke test로 먼저 고정한다.
2. multimodal prompt는 처음부터 processor-native template만 사용한다.
3. RAG dataset path는 hardcoding하지 않고 discovery와 validation report를 기본으로 둔다.

이 프로젝트는 대회 점수표로만 설명하기 어려운 Impact Challenge였다. 하지만 포트폴리오 관점에서는 오히려 좋다. 모델을 붙이는 데서 끝나지 않고, 실제 cloud execution 제약 속에서 의료 AI pipeline을 끝까지 움직이게 만든 기록이기 때문이다.

## 더 읽을거리

- 상세 코드, demo video, 실행 구조는 repo README에서 확인할 수 있다.
- 이 글은 의료 VLM/RAG pipeline에서 겪은 cloud, tokenization, pathing 병목을 중심으로 요약했다.
- 특히 gated model access, processor-native multimodal prompt, Kaggle dataset discovery는 이후 의료 AI 실험에도 재사용할 만한 운영 패턴이다.
