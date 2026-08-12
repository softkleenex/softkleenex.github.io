---
title: "DACON 대회 시작 템플릿"
subtitle: "성능을 내기 전에 성능을 믿을 수 있게 만드는 운영 템플릿"
date: 2026-05-06
category: "기록"
description: "DACON과 Kaggle 대회를 30분 안에 시작하기 위한 운영 템플릿 기록. 검증 우선 원칙, 제출 로그, 데이터 사전, Kaggle 오프로드를 표준화한 이유를 정리했다."
repo: "dacon-base"
date_basis: "저장소 생성일"
---

`dacon-base`는 특정 대회 회고가 아니라, 여러 DACON과 Kaggle 대회를 반복하면서 생긴 운영 템플릿이다. 처음에는 매 대회마다 폴더 구조, 제출 로그, 데이터 사전, Kaggle 업로드 스크립트, README 링크를 다시 만들었다. 그 반복이 생각보다 시간을 많이 먹었고, 더 위험한 문제는 제출 직전의 기록 누락이었다.

그래서 이 저장소는 “대회 시작 30분 안에 최소한의 질서가 있는 상태를 만들자”는 목적으로 만들었다. 모델 성능을 직접 올리는 코드는 아니지만, 검증 점수와 리더보드 점수를 섞어 보지 않게 하고, 어떤 submission file이 어떤 실험에서 나왔는지 남기고, heavy run을 Kaggle notebook으로 넘기는 흐름을 표준화한다. ETRI 대회처럼 제출 파일, 로그 CSV, 노트북 기록이 맞물려야 하는 작업에서 특히 이런 템플릿의 필요성이 커졌다.

## 왜 만들었나

대회 막판에는 사람도 에이전트도 급해진다. 좋은 feature인지, public LB에만 맞춘 도박인지, 제출 파일 이름과 로그 행이 맞는지 확인하지 못한 채 넘어가기 쉽다. `dacon-base`는 그 지점을 줄이기 위한 바닥 공사에 가깝다.

- `docs/MASTER_PLAN.md`로 validation-first 원칙과 작업 단계를 고정한다.
- `docs/DATA_DICTIONARY.md`로 feature 의미와 EDA 발견을 공유 메모리로 남긴다.
- `docs/SUBMISSION_HISTORY.md`와 `submissions/submission_log.csv`로 local CV, public LB, 제출 여부를 분리한다.
- `src/`, `scripts/`, `configs/`, `notebooks/`를 기본 구조로 나눠 재사용 가능한 코드를 흩어지지 않게 한다.
- Kaggle dataset과 notebook push/pull 흐름을 Makefile에 묶어 local과 cloud 실행을 오갈 수 있게 한다.

## 운영 철학

이 템플릿의 중심은 “성능을 낸다”보다 “성능을 믿을 수 있게 만든다”에 있다. Public leaderboard가 빠른 feedback을 주더라도, 그 점수가 local CV와 어긋날 때는 기록이 없으면 다음 판단이 흐려진다. 특히 여러 후보를 cascade나 ensemble로 찍어낼 때는 파일명, 노트북, 결과 CSV, 로그 한 행이 서로 맞아야 한다.

또 하나의 목적은 에이전트 협업이다. 긴 대회 작업에서는 한 세션의 기억만으로 끝까지 가기 어렵다. 그래서 data dictionary, submission history, master plan 같은 문서를 agent-human shared memory로 쓰도록 했다. 다음 세션이 들어와도 “어떤 실험이 왜 실패했는지”를 README보다 구체적으로 읽고 이어갈 수 있게 하는 구조다.

## 아쉬운 점

현재 저장소는 아직 실제 대회 하나의 완성된 성과물이 아니라 템플릿 성격이 강하다. 일부 문서는 placeholder가 남아 있고, 소스 레포도 구조 개편 중인 상태다. 그래서 이 페이지도 대회 성적 회고가 아니라, 앞으로의 DACON/Kaggle 작업을 더 빨리 시작하고 더 덜 잃어버리기 위한 운영 노트로 남긴다.

다음 개선 방향은 명확하다. 대회별 README와 블로그 URL 자동 삽입, 제출 로그 스키마 검증, secret scan, Kaggle metadata 생성, docs audit를 기본 명령으로 묶으면 템플릿의 가치가 더 커진다. 모델링 실험의 속도만 올리는 것이 아니라, 마지막 제출 직전의 실수를 줄이는 쪽으로 계속 다듬을 만하다.
