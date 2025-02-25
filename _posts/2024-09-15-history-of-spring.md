---
layout: post
title: "[번역] Spring의 역사 (history of spring)"
description: Spring의 역사는 2002년 Rod Johnson의 J2EE 복잡성을 다룬 책 출판을 시작으로, 2003년 Spring Framework 오픈 소스 프로젝트가 시작되었고, 2004년 Spring Framework 1.0이 출시되었습니다. 이후 2008년 Spring Security 2.0, 2011년 Spring Data, 2014년 Spring Boot 1.0, Spring Batch 3.0, Spring Integration 4.0, 2015년 Spring Cloud 1.0, 2016년 Spring Cloud Task와 Stream, 2018년 Spring Cloud Skipper, 2021년 Spring Cloud Gateway for Kubernetes, 2022년 Spring Boot 3 및 Spring Framework 6가 출시되며 발전해왔습니다. 이 글에서는 Spring의 주요 역사적 사건들을 정리하고, Spring Cloud에 대한 추가 학습의 필요성을 언급합니다.
categories: [스터디-자바]
tags: [Spring, history, 스프링, 역사]
date: 2024-09-15 21:00:00 +0900
toc: true
---

Linkedin 을 보다가 재밌는 링크를 발견해서 정리해본다.

> 스프링의 역사를 게임처럼 알아볼 수 있는 사이트
> [https://springone.io/history-of-spring](https://springone.io/history-of-spring)
>
> ![og-history-of-spring](/assets/images/2024-09-15-history-of-spring/og-history-of-spring.png)

오픈소스면 한글판을 만들어보고 싶었는데 레포지토리가 따로 보이지 않는 것 같다.

## 번역

- 2002: Rod Johnson이 J2EE 복잡성을 다루는 책을 출판
- 2003: Rod Johnson, Juergen Hoeller, Yann Caroff가 **Spring Framework 오픈 소스 프로젝트를 시작**
- 2004: Spring Framework 1.0 출시
- 2008: Spring Security 2.0 출시, Acegi에서 이름 변경
- 2011: Spring Data가 Spring Data MongoDB, Spring Data Redis, Spring Data Neo4j, Spring Data GemFire로 NoSQL 워크로드를 처리
- 2014: Spring Boot 1.0 출시, 애플리케이션을 빠르게 개발할 수 있는 도구 제공
- 2014: Spring Batch 3.0 출시, Spring Boot 동적 부트스트래핑 제공
- 2014: Spring Integration 4.0 출시, XML 없이 통합 흐름을 구성 제공
- 2015: Spring Cloud 1.0 출시, 분산 시스템을 빠르게 개발할 수 있는 소프트웨어 도구 제공
- 2016: Spring Cloud Task 도입, 단기 실행(short-lived) 마이크로서비스 지원
- 2016: Spring Cloud Stream 1.0 출시, 이벤트 기반 마이크로서비스 활성화
- 2016: Spring Cloud Data Flow 1.0 출시, 데이터 마이크로서비스에 대한 오케스트레이션 서비스 제공
- 2016: Spring Cloud Data Flow for Kubernetes 1.0 출시, Kubernetes에서 장기 실행(스트리밍) 및 단기 실행(태스크/배치) 데이터 마이크로서비스에 대한 오케스트레이션 기능 지원
- 2018: Spring Cloud Skipper 1.0 출시, 여러 클라우드 플랫폼에서 애플리케이션 발견 및 생애 주기 관리 제공
- 2021: Spring Cloud Gateway for Kubernetes 출시, YAML 구성 객체를 Kubernetes 클러스터에 적용하여 API 게이트웨이 서비스의 배포를 자동화 지원
- 2022: Spring Boot 3 및 Spring Framework 6 출시, GraalVM을 통해 Kubernetes와 같은 환경에서 네이티브 컴파일된 애플리케이션이 더 효율적으로 실행될 수 있도록 지원

### 추가 설명

#### Rod Jonson

[Rod Johnson Wiki](<https://en.wikipedia.org/wiki/Rod_Johnson_(programmer)>)

"Expert One-on-One J2EE Design and Development" 라는 책을 작성했다고 한다.

#### long-lived microservice, short-lived microservice

참고 : [https://dataflow.spring.io/docs/concepts/architecture/#application-types](https://dataflow.spring.io/docs/concepts/architecture/#application-types)

##### 장기 실행 어플리케이션(long-lived application)

장기 실행 애플리케이션은 메시지 중심 애플리케이션이 속합니다. 데이터의 양이 정해져 있지 않습니다.

장기 실행 애플리케이션에는 두 가지 유형이 있습니다:

- 단일 입력 과 출력 메시지 기반 애플리케이션
- 여러 입력 과 출력 메시지 기반 애플리케이션

##### 단기 실행 어플리케이션(short-lived application)

단기 실행 어플리케이션은 유한한 데이터 집합을 처리한 후 어플리케이션을 종료합니다.

단기 실행 애플리케이션에는 두 가지 유형이 있습니다.

- Task : 코드를 수행하고 데이터 흐름 데이터베이스에 실행 상태를 기록합니다.
- Batch : 배치 처리를 수행합니다.

## 원문

- 2002: Rod Johnson publishes book addressing J2EE complexities
- 2003: Rod Johnson, Juergen Hoeller, and Yann Caroff start the Spring Framework open source project
- 2004: Spring Framework 1.0 is released
- 2008: Spring Security 2.0 is released, renaming it from Acegi
- 2011: Spring Data takes on NoSQL workloads with Spring Data MongoDB, Spring Data Redis, Spring Data Neo4j, and Spring Data GemFire
- 2014: Spring Boot 1.0 is released, introducing rapid application development
- 2014: Spring Batch 3.0 released, switching to Spring Boot's dynamic bootstrapping capabilities over archetypes
- 2014: Spring Integration 4.0 enables integration flows to be configured without XML
- 2015: Spring Cloud 1.0 is released, providing tools to quickly build software for distributed systems
- 2016: Spring Cloud Task is introduced, supporting short-lived microservices
- 2016: Spring Cloud Stream 1.0 is released, enabling event-driven microservices
- 2016: Spring Cloud Data Flow 1.0 is released, providing an orchestration service for data microservices
- 2016: Spring Cloud Data Flow for Kubernetes 1.0 orchestrates long-running (streaming) and short-lived (task/batch) data microservices on Kubernetes
- 2018: Spring Cloud Skipper 1.0 allows app discovery and lifecycle management on multiple cloud platforms
- 2021: Spring Cloud Gateway for Kubernetes automates the deployment of an API gateway service by applying YAML configuration objects to a Kubernetes cluster
- 2022: Spring Boot 3 and Spring Framework 6 enable natively compiled applications to run more efficiently in environments like Kubernetes via GraalVM

## 기타

정리하면서 느낀 것이 Spring Cloud에는 모르는 부분들이 많은 것 같다. 공부 해야할 게 끝이 없다.
