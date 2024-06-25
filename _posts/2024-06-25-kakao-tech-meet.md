---
layout: post
title: "[Review] Kakao 에서는 스팸을 어떻게 처리하는가 - 제6회 Kakao Tech Meet"
categories: [스터디-AI, 행사]
tags:
  [
    Kakao,
    카카오,
    AI,
    Gen AI,
    Generative AI,
    인공지능,
    생성형 AI,
    LLM,
    스팸,
    Spam,
    Transformer,
    GPT,
  ]
date: 2024-06-25 19:00:00 +0900
toc: true
---

지난 6월에 있었던 Kakao Tech Meet에 참여하였습니다.

참여해서 들은 내용을 정리해보았습니다. (개인적으로 추가한 내용도 함께 있습니다.)

[제6회 Kakao Tech Meet에 초대합니다!](https://tech.kakao.com/posts/619)

![poster](/assets/images/2024-06-25-kakao-tech-meet/poster.png)

# 사진 정리

![x-banner](/assets/images/2024-06-25-kakao-tech-meet/image1.jpeg)

![welcome-gift](/assets/images/2024-06-25-kakao-tech-meet/image2.jpeg)

![panel-talk](/assets/images/2024-06-25-kakao-tech-meet/panel-talk.jpeg)

# 내용 정리

## 1. 카카오의 스팸 메일 대응 전략: 문자열 변형 CASE STUDY

이 섹션의 경우 정적인 분석 방법에 대해서 주로 이야기 하였다.

## 2. 성인 이미지 세계에서 살아남는 법 Part 2

Part 1 은 2019년 `if kakao` 에서 발표

- [part1 영상 다시보기](https://mk.kakaocdn.net/dn/if-kakao/conf2019/conf_video_2019/2_105_01_m1.mp4)
- [part1 PDF](/assets/images/2024-06-25-kakao-tech-meet/성인이미지%20세계에서%20살아남는%20방법%20part01.pdf)

어떻게 적은 리소스로 효율적으로 이미지 모니터링을 할 것인가.

### 기존에 가지고 있던 문제들

- 학습 지표와 실제 지표의 차이
  - 일부만 라벨링
  - Overfitting
  - 적합한 모델인가?
- 과도한 서버 비용
  - 확장이 어려운 구조
- 주기적인 모델 갱신 프로세스 이슈
  - 지표 간의 괴리감으로 인해 롤백하는 경우 발생
  - 정책적 이슈

### 효율적인 모델 찾기

- EfficientNet 도입 시도

  - [https://arxiv.org/abs/1905.11946](https://arxiv.org/abs/1905.11946)
  - 응답 속도 아직은 아쉽 → 병목 해결 시도
    - 이미지 다운로드 횟수 줄이기 : head 검사
    - 이미지 전처리
      - 리사이즈 : [pillow](https://github.com/python-pillow/Pillow) 사용

- Vision Transformer 도입 시도

  - [https://arxiv.org/abs/2010.11929](https://arxiv.org/abs/2010.11929)

  - CNN(Convolutional Neural Network) 보다는 좋지만 아쉽

- Swin

  - [https://arxiv.org/abs/2103.14030](https://arxiv.org/abs/2103.14030)
  - 특징이 잘 학습됨 (Robust한 결과를 얻음)

### transformers 라이브러리

hugging face 가 생긴 후로 데이터에만 집중하면 되서 효율성이 올라감.

### 병목 해결

- 배치로 처리
- CPU 기반은 Async stream
- 캐시등을 활용한 횟수 줄이기

### 정성평가

- 반드시 통과되야 하는 체크 리스트 생성

### 라벨링 전략

라벨링 데이터를 어떻게 선별할 것인가가 중요

적은 리소스로 효율적인 라벨링을 하기 위해 **active learning** 사용

- active learning

  - 어떤 데이터에 라벨링이 필요한지를 기계가 판단하여 사람에게 라벨링을 부탁하면 더 적은 라벨링 공수를 들이면서 좋은 모델을 학습할 수 있지 않을까?

    - [액티브 러닝이란 무엇인가](https://littlefoxdiary.tistory.com/52)

- query by committee (QBC)

  - 여러 모델이 투표하여 결정하는 전략
  - 효과가 제일 좋았지만 프로세스 복잡 + 리소스가 많이 필요함

- Loss를 이용한 대상 선정

  - 현재 테스트 중인 방법
  - 손실값이 클수록 아직 불확실한 데이터 아닐까 라는 가설로 진행

### 노이즈 라벨과 함께 살아가기

- 크로스 체크

  - 어떻게 기계적으로 할까?

    - QBC

    - K-FLOD

      - [K-FOLD Cross Validation (교차 검증) 정의 및 설명](https://nonmeyet.tistory.com/entry/KFold-Cross-Validation%EA%B5%90%EC%B0%A8%EA%B2%80%EC%A6%9D-%EC%A0%95%EC%9D%98-%EB%B0%8F-%EC%84%A4%EB%AA%85)

    - 가중치 부여

  - 여전히 복잡

- 학습하면서 레이블을 같이 할수는 없을까?

- Co-teaching

  - [https://arxiv.org/abs/1804.06872](https://arxiv.org/abs/1804.06872)

  - 로스가 낮은 데이터를 크로스로 전달
  - 효과는 좋았으나 오래걸림
  - 학습 로직도 복잡함.

### 재밌는 시도

- LLM

  - Image to Text를 통해 스팸 검사 시도
    - 키워드를 이용해 재검토 대상 추출
    - 워드 임베딩, 성인 이미지와 유사하면 검사
  - image to image
    - stable diffusion 을 통한 이미지 증식 시도
    - 자동화는 불가했음.
  - LoRa vs Full Fine Tuning
    - 스팸은 후자가 좋은 듯. 아직까진
  - 주기적인 학습 그리고 배포
    - 요즘은 하이퍼파리미터 튜닝 보다는 데이터 자체에 더 집중하는 중.

### 향후 계획

- CLIP을 활용한 다양한 시도
- 다양하게 고민중인 라벨링 전략
- 노이즈 레이블 찾기
- image to text fine tuning

## 3. 스팸 콘텐츠 대응을 위한 카카오의 대규모 언어 모델(LLM) 도입 사례

도배 콘텐츠 / 장문의 콘텐츠

목표 : 분류 결과와 분류 사유를 운영자에게 제공

### Transformer와 LLM

BERT와 GPT는 Transformer를 기반으로 만들어진 LLM들이다.

BERT는 트랜스포머의 인코더를, GPT는 트랜스포머의 디코더를 분리해 각각 독자적인 모델로 발전해나감.

### 프롬프트

- 역할 지시
- 시스템 명령

#### 프롬프트 예시

> 너는 스팸 분류 전문가야 : 역할
> 다음 문자을 보고 스팸이니 분류해 : 지시
> 참고 내용 추가

참고 내용이 길어지면?
LLM에 사전 정보가 있으면?

기존의 LLM 모델을 바로 사용하기 어려움
전용 LLM을 만들어야 했음.

### 데이터 수집 방법

스팸 도메인의 LLM 데이터를 생성하자.

LLM 데이터의 기본 구조

1. 역할 부여, 지시
2. 분류할 콘텐츠
3. LLM의 응답

#### 분류 사유는 어덯게 만들지?

- 라벨 기반의 문장 : {label} 입니다.
- 라벨과 키워드를 활용한 문장 : {keyword}는 {label} 입니다.
  - 할루시네이션 이 있음.
- 라벨과 키워드와 리즌을 활용한 문장 : {keyword}는 {reason}으로 {label} 입니다.
- 키워드 중심이 아닌, 문장의 목적을 설명하는 문장 : {Label}을 기반하는 목적을 설명하는 문장.

라벨러(사람)의 도움을 통한 LLM 데이터 수집 (자연스러운 형태로 데이터를 얻어야 함.)

### 뷸균형 데이터 문제와 해결 방법

- 다양한 어휘 사용
  - 오버피팅 방지
- 명령 데이터 활용

### 클래스 불균형 문제와 해결 노하우

- 데이터 증강
  - 스팸과 정상 데이터의 비율을 상세 라벨 별로 맞추는 것이 필요
- 언더샘플링
  - ...
