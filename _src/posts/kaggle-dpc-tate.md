---
title: "Deep Past 아카드어 번역"
subtitle: "Akkadian 번역 모델보다 Kaggle 자동화가 더 어려웠다"
date: 2026-05-04
category: "Kaggle"
description: "ByT5와 MBR decoding, 사전 lookup으로 Akkadian을 영어로 번역해 33.8371점(954/2673). 정작 가장 오래 붙든 건 Kaggle 자동화의 실패 모드였다."
repo: "kaggle-dpc-tate"
date_basis: "본문 리더보드 CSV 파일명"
---

이 프로젝트는 Kaggle `Deep Past Initiative: Machine Translation` 대회 기록이다. 목표는 고대 Akkadian transliteration을 English로 번역하는 것이었다. 데이터는 언어학 자료, 사전, published texts, train/test CSV가 섞여 있었고, 일반적인 영어 중심 NLP와는 다른 전처리 감각이 필요했다.

최종 public leaderboard CSV 기준 기록은 score `33.8371`, rank `954 / 2,673`이었다. top 36% 정도의 중상위 기록이다. 상위권은 41점대까지 갔기 때문에 우승권은 아니었지만, byte-level model, MBR decoding, lexicon lookup, Kaggle 자동화 루프를 끝까지 붙들고 간 프로젝트였다.

## 왜 ByT5였나

Akkadian transliteration은 일반적인 영어 tokenization과 잘 맞지 않는다. 특수 문자, 긴 transliteration, 형태소적 변형, 고유명사, 신명/지명 표기가 섞인다. WordPiece나 BPE가 항상 나쁘다는 뜻은 아니지만, 이 대회에서는 character/byte 단위 처리가 더 안전한 출발점이었다.

그래서 중심 모델은 `ByT5` 계열이었다. 단어를 예쁘게 쪼개기보다 원문 문자열을 최대한 있는 그대로 보존하고, beam search로 여러 후보 번역을 만든 뒤 MBR로 가장 안전한 후보를 고르는 쪽으로 갔다.

## MBR과 Lexicon

가장 큰 축은 `Minimum Bayes Risk` decoding이었다. greedy output 하나를 믿지 않고, diverse beam search로 후보를 여러 개 만들고, 후보끼리 CHRF++/BLEU 유사도를 비교해 평균적으로 가장 덜 위험한 번역을 선택했다.

여기에 외부 지식도 섞었다.

| 장치                | 역할                                                              |
| ------------------- | ----------------------------------------------------------------- |
| Golden lookup       | train에 있던 `1,559`개 exact transliteration match를 우선 적용    |
| eBL lexicon         | `OA_Lexicon_eBL.csv`의 PN/GN/DN/name 정보를 후보 reranking에 반영 |
| Vectorized MBR      | PyTorch tensor 기반 후보 비교로 inference 병목 완화               |
| Diverse beam search | `num_beam_groups`, `diversity_penalty`로 후보 다양성 확보         |

흥미로운 점은 MBR이 항상 점수를 올리지는 않았다는 것이다. 기록에는 `33.8 -> 30.8 -> 33.6 -> 32.3`처럼 parameter가 조금만 흔들려도 점수가 출렁이는 흔적이 있다. 결국 안정적인 baseline을 버리지 않고, 실패 버전을 빠르게 되돌릴 수 있는 version control 감각이 중요했다.

## 진짜 난이도는 자동화였다

이 프로젝트에서 가장 오래 남은 것은 번역 모델보다 Kaggle 자동화의 실패 모드였다.

1. Kaggle P100 GPU의 `sm_60` 아키텍처가 최신 PyTorch/bfloat16/bitsandbytes 조합과 충돌했다.
2. `/kaggle/input` mount path가 바뀌면서 hardcoded path가 깨졌다.
3. local directory가 없으면 `transformers`가 이를 Hugging Face Hub ID로 오해해 `HFValidationError`를 냈다.
4. Kaggle API polling이 429 rate limit에 걸렸다.
5. 이전 kernel score를 새 score로 착각하는 "ghosting" 문제가 생겼다.

해결책도 점점 운영 시스템처럼 변했다.

- P100 감지 시 CPU fallback
- `os.walk('/kaggle/input')` 기반 model/config 탐색
- `local_files_only=True` 강제
- exponential backoff
- kernel description에 unique `SID-` timestamp 삽입 후 exact grep matching

모델링이 아니라 배관 같은 이야기지만, 대회 막판에는 이런 배관이 점수를 지킨다.

## 놓친 방향

회고를 보면, 너무 많은 에너지가 inference optimization과 자동 submission loop에 들어갔다. 반면 상위권과의 차이는 아마 data quality에서 더 크게 났을 가능성이 높다.

다시 한다면 다음을 먼저 할 것이다.

1. noisy PDF/academic text에서 깨끗한 parallel corpus를 더 공격적으로 추출한다.
2. English가 아닌 문서를 `langdetect`나 rule filter로 제거한다.
3. transliteration-English alignment quality를 사람이 빠르게 검수할 수 있는 report를 만든다.
4. MBR parameter sweep은 stable baseline을 기준으로 작게만 움직인다.
5. 자동화 loop는 score보다 artifact integrity를 먼저 검증하게 한다.

이 대회는 "고대어 번역 모델을 잘 만들었다"보다 "Kaggle의 닫힌 환경에서 자동화가 어떻게 자주 망가지는지"를 배운 프로젝트였다. 그래서 포트폴리오에서는 성능보다 운영 회고로 남기는 편이 더 정직하다.

## 기록 포인트

- 점수 근거는 repo의 `data/deep-past-initiative-machine-translation-publicleaderboard-2026-05-04T06:46:20.csv`에서 확인했습니다.
- 자동화 실패와 해결은 `docs/learnings.md`, `learnings.md`, `state.log`에 남아 있습니다.
- 이 페이지는 Akkadian 번역 품질보다 ByT5/MBR/lexicon과 Kaggle automation resilience를 중심으로 정리합니다.
