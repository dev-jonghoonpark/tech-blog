---
layout: "post"
title: "구글의 ai 관련 프로젝트들 알아보기 (vertex ai, gemini 등)"
description: "구글의 AI 프로젝트인 Vertex AI와 Gemini를 소개하며, Vertex AI는 머신러닝 플랫폼으로 Gemini를\
  \ 포함한 다양한 AI 모델을 훈련하고 관리하는 데 사용됩니다. Gemini는 대규모 언어 모델로, 여러 버전이 존재하며, PaLM은 이전의 대\
  표 LLM입니다. 또한, Spring AI는 구글 관련 다양한 AI 솔루션을 지원합니다."
categories:
- "스터디-AI"
tags:
- "langchain"
- "spring"
- "java"
- "gemini"
- "google"
- "vertex ai"
- "AI Studio"
- "palm"
- "gemma"
- "구글"
- "제미나이"
- "spring ai"
date: "2024-06-20 11:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-06-20-google-ai-products.jpg"
---

각 항목들이 무엇을 의미하는지 모르겠어서 찾아보고 간단하게 정리해본다.

## vertex ai 과 gemini 의 연관성

- Vertex AI는 Google Cloud Platform에서 제공하는 머신러닝 플랫폼
  - Google AI Studio 는 생성형 AI를 유저 친화적인 인터페이스로 제공
- Gemini는 Google AI에서 개발한 대규모 언어 모델
  - gemini 1.0
    - gemini-pro
    - gemini-pro-vision
    - gemini-ultra
  - gemini 1.5
    - gemini-pro
    - gemini-flash : 경량 모델, openai 로 치면 turbo 같은 개념인것 같음.
  - gemini nano : ondevice 용

Vertex AI는 Gemini를 포함한 다양한 AI 모델을 훈련, 배포, 관리하는 데 사용할 수 있다.

Gemini API 가 따로 있긴 한다. ([링크](https://ai.google.dev/gemini-api))
하지만 아직까지는 기본적으로 자바를 지원해주지는 않는다.

### 그 밖의 제품들

- PaLM 은 Gemini 출시 이전의 구글의 대표 LLM 이다.
  - Duet AI는 PaLM을 기반으로 한 AI 솔루션 (기업 대상)
  - Bard는 PaLM을 기반으로 한 AI 솔루션 (개인 대상)?
- Gemma 는 Google 에서 공개한 오픈 모델 이다. ([repository](https://github.com/google-deepmind/gemma)). Gemini의 경량화 모델이라 한다.

## spring ai 에서 google 관련하여 지원하는 항목

문서에 따르면 spring ai 에서는 구글 관련해서는 다음과 같은 항목들을 지원하고 있다.

![supported chat models](/assets/images/2024-06-20-google-ai-products/spring-ai-supported-chat-models.png)

![supported embeddings models](/assets/images/2024-06-20-google-ai-products/spring-ai-supported-embeddings-models.png)
