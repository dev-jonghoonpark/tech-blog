---
layout: "post"
title: "Java 프로젝트에 OpenTelemetry JavaAgent 연동하기"
description:
  "OpenTelemetry JavaAgent를 활용하여 Spring 기반 애플리케이션에 모니터링과 트레이싱 기능을 손쉽게 추\
  가하는 방법을 소개합니다. 이 글에서는 OpenTelemetry의 개념, JavaAgent의 적용 방법, Grafana Tempo와의 연동, 그\
  리고 설정 시 발생할 수 있는 에러에 대한 해결책을 다룹니다. 이를 통해 시스템 성능을 실시간으로 모니터링하고 문제를 신속하게 진단할 수 있습니다"
categories:
  - "스터디-자바"
tags:
  - "Java"
  - "Spring"
  - "instrument"
  - "instrumentation"
  - "OpenTelemetry"
  - "Observability"
  - "javaagent"
  - "Traces"
  - "Logs"
  - "Metrics"
date: "2025-05-04 03:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-05-04-opentelemetry-javaagent.jpg"
---

# OpenTelemetry JavaAgent

## 개요

최근 스터디를 진행하면서, Spring 기반 프로젝트를 Grafana를 통해 모니터링 하는 방법에 대해서 알아보았다.

이 내용중 일부였던 OpenTelemetry JavaAgent 를 통해 instrumentation(인스트루먼테이션) 하는 방법에 대해서 정리해본다.

## 개념 설명

### Instrumentation (인스트루먼테이션, 계측)

instrumentation는 '계측'이라는 뜻을 가지고 있다. 컴퓨터 공학에서는 오류를 진단하거나 추적 정보를 쓰기 위해 제품의 성능 정도를 모니터하거나 측정하는 기능을 가리킨다. ([출처:위키](https://ko.wikipedia.org/wiki/%EC%9D%B8%EC%8A%A4%ED%8A%B8%EB%A3%A8%EB%A8%BC%ED%85%8C%EC%9D%B4%EC%85%98))

### Observability (옵저버빌리티, 관측가능성)

관측가능성은 시스템 또는 애플리케이션의 출력, 로그, 성능 메트릭을 통해 시스템 또는 애플리케이션의 상태를 모니터링, 측정, 파악하는 기능을 뜻한다. ([출처:redhat](https://www.redhat.com/ko/topics/devops/what-is-observability))

### Telemetry (텔레메트리, 원격 관측)

서버, 애플리케이션, 모니터링 장치 등 원격 소스에서 데이터를 수집, 전송 및 분석하는 프로세스 ([출처:elastic](https://www.elastic.co/what-is/telemetry-data))

### OpenTelemetry

[OpenTelemetry](https://opentelemetry.io/) 는 서비스와 소프트웨어에서 원격 측정 데이터를 생성하고 수집한 다음 다양한 분석 도구로 전달하는데 사용되는 도구이며, 이를 통해 효과적으로 Observability 를 제공해준다. 오픈 소스이며, 벤더 중립이라는 특징을 가지고 있다. 현재 기준, CNCF incubating project 중 하나이다.

### JavaAgent

Java 에서는 JVM에서 실행 중인 프로그램을 계측할 수 있는 서비스를 제공한다. 바이트코드 조작(Bytecode Manipulation)을 통해 애플리케이션의 런타임 동작을 제어하거나 모니터링할 수 있도록 되어있다. ([출처:오라클](https://docs.oracle.com/javase/10/docs/api/java/lang/instrument/package-summary.html))

## OpenTelemetry Instrumentation for Java

OpenTelemetry 에서 제공하는 instrumentation(계측)를 위한 javaagent 이다. Java 8 이상에서 사용 가능하며, 데이터를 다양한 형식으로 내보낼 수 있다(export). 코드 변경없이 Observability를 구현할 수 있다는 특징도 있다.

- 관련 링크
  - [repository](https://github.com/open-telemetry/opentelemetry-java-instrumentation)
  - [document](https://opentelemetry.io/docs/zero-code/java/agent/)

크게 3가지 기능(log 수집, trace 수집, metric 수집)을 제공한다. 대략적인 동작 방식은 다음과 같다.

![instrumentation overview chart](/assets/images/2025-05-04-opentelemetry-javaagent/instrumentation-overview-chart.svg)

<small>이미지 출처 : [feedbackInstrumentation and observability](https://cloud.google.com/stackdriver/docs/instrumentation/overview)</small>

### 적용 방법

먼저 [opentelemetry-javaagent.jar](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar) 를 다운받는다. ([repository 의 release 페이지](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases)에서도 다운로드 가능하다)

이후 적절한 위치로 이동 시킨 후 JVM startup arguments 에 `-javaagent:path/to/opentelemetry-javaagent.jar` 를 추가하여 함께 실행시킨다.

```sh
java -javaagent:path/to/opentelemetry-javaagent.jar -jar myapp.jar
```

### 추가 설정

추가적인 설정은 [sdk-configuration](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/) 문서를 참고하여 진행한다.

OpenTelemetry 는 다양한 Exporter 를 제공하는데, 기본 값은 `OTLP` 이다.

> 참고로 `OTEL` 는 OpenTelemetry 의 약자이고, `OTLP` 는 OpenTelemetry Protocol 의 약자이다. (OLTP 와는 관련 없다.)

본인의 환경에 따라 exporter 와 endpoint 를 지정해주면 된다.

## Grafana Tempo

Grafana Tempo는 분산 트레이스를 저장하기 위한 전용 저장소이다.
OpenTelemetry가 보낸 데이터를 저장하며, 최종적으로 Grafana에서 메트릭, 로그와 연계하여 트레이스를 조회하고 분석하는 데 사용된다.

설치 방법은 이 글에서 길게 다루지는 않는다. [Quick start for Tempo](https://grafana.com/docs/tempo/latest/getting-started/docker-example/) 문서를 참고하여 설치해볼 수 있다.

주의 해야할 점은 해당 방법에서 제공하는 docker compose 파일에서 k6-tracing 이미지는 데모를 위한 데이터들을 생성하는데 사용된다. 만약 본인의 프로젝트에 적용해보고 싶었다면, 해당 부분을 docker compose 에서 제거하는 것이 좋을 것이다.

## 결과

나의 경우에는 [petclinic](https://github.com/spring-projects/spring-petclinic) 이라는 샘플 프로젝트에 적용하여 테스트 해보았다.

API 엔드포인트를 호출하면 다음과 같이 instrument가 되는 것을 볼 수 있다.

![trace page example in grafana](/assets/images/2025-05-04-opentelemetry-javaagent/trace-page-example-in-grafana.png)

![trace detail page example in grafana](/assets/images/2025-05-04-opentelemetry-javaagent/trace-detail-page-example-in-grafana.png)

## 기타

### 연동시 에러 발생 (HttpExporter - Failed to export)

세팅을 해서 trace 가 정상적으로 동작하는것까지 확인을 하였는데, 어플리케이션에서 다음과 같은 워닝이 계속 발생되었다.

```
[OkHttp http://localhost:4318/...] WARN io.opentelemetry.exporter.internal.http.HttpExporter - Failed to export logs. Server responded with HTTP status code 404. Error message: Unable to parse response body, HTTP status message: Not Found
[OkHttp http://localhost:4318/...] WARN io.opentelemetry.exporter.internal.http.HttpExporter - Failed to export metrics. Server responded with HTTP status code 404. Error message: Unable to parse response body, HTTP status message: Not Found
```

logs 와 metrics 를 내보내는 데 실패하였다는 경고 로그였다. 기능에 큰 영향을 미친 것은 아니였으나, 이 경고 로그가 왜 계속 발생하는 것인지에 대해서 찾아보았다.

해당 내용과 직접적으로 관련이 없어보이지만 [이슈글](https://github.com/open-telemetry/opentelemetry-java-instrumentation/issues/11783) 하나를 발견하였고 내용을 정리해보자면 다음과 같다.

opentelemetry-javaagent 는 크게 3가지 기능(log 수집, trace 수집, metric 수집)을 제공한다.
그런데 `2.x` 버전부터는 log 수집과 metric 수집이 기본적으로 활성화 되도록 변경 된 것으로 보인다.

Grafana Tempo 는 Trace 에 대한 OTLP 만 제공한다. 따라서 나머지 기능들은 비활성화 해줘야 한다.

최종적으로 다음과 같이 실행문을 짜주면 된다.

```sh
java -javaagent:path/to/opentelemetry-javaagent.jar
-Dotel.logs.exporter=none
-Dotel.metrics.exporter=none
-jar myapp.jar
```

로그 수집은 Grafana Loki를 통해, 메트릭 수집은 actuator 와 prometheus를 통해 처리할 수 있다. (물론 다른 방법들로도 가능하다.)

Loki를 통해 로그 수집하는 방법은 이전에 글로 작성했었다.

- [spring boot 프로젝트에 loki 추가해서 로그 수집하기](https://jonghoonpark.com/2024/04/22/java-loki-grafana-with-spring-boot)

## 마무리

OpenTelemetry JavaAgent를 활용하면 Spring 기반 애플리케이션에 손쉽게 모니터링과 트레이싱 기능을 추가할 수 있으며, 이를 통해 시스템의 성능을 실시간으로 파악하고 문제를 빠르게 진단할 수 있다. 평소에 회사에서는 Datadog 를 쓰고 있는데, Grafana 로 직접 구현하려고 해보니, 왜 비싼 비용을 들어가면서도 Datadog 를 사용하는지 다시 한 번 느낄 수 있었다.
