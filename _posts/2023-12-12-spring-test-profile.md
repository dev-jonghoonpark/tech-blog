---
layout: post
title: Spring boot - 테스트용 프로파일 관리하기, CompletableFuture 목 처리 하기
description: Spring Boot에서 테스트용 프로파일 관리와 CompletableFuture 목 처리 방법을 다룹니다. `local` 프로파일을 기본으로 하여 `test` 프로파일의 설정을 덮어쓰는 방법을 설명하며, `application-test.yml` 파일을 생성하여 데이터 소스 정보를 설정합니다. 또한, 통합 테스트를 위한 별도의 작업을 등록하여 프로파일을 활성화하는 방법을 제시합니다. 마지막으로, CompletableFuture를 사용하여 결제 서비스의 Mock 처리를 통해 테스트를 진행하는 방법을 소개합니다.
categories: [개발, 스터디-테스트]
tags:
  [
    테스트,
    테스팅,
    통합 테스트,
    spring,
    spring boot,
    profile,
    mock,
    mockito,
    CompletableFuture,
  ]
date: 2023-12-12 01:00:00 +0900
---

## 테스트용 프로파일 관리하기

아침 daily 스크럼 후, 회사 devops 님께 최근 고민했던 내용(테스트 환경에서 데이터 초기화를 어떻게 진행할지)에 대해서 말씀드리고 잘못된 부분이나 개선할 부분은 없을지 의견을 구했다.

> 관련글
>
> - [Spring 기반 프로젝트에서 테스트컨테이너 (testcontainer) 사용해보기](/2023/12/07/testcontainer-with-spring)
> - [@SQLDelete 가 적용된 상태에서 테이블 초기화 하기](/2023/12/12/integration-test-with-database)

긍정적으로 반응해 주셨고 다만 overrideProps 부분만 프로파일 이나 환경변수 주입으로 처리 가능하게 되면 좋겠다고 하셨다.
그래서 프로파일로 처리하는 방법에 대해서 알아보았고 그에 대해서 정리한다.

---

지금 하고 있는 프로젝트에서는 `local` 이라는 프로파일을 기본적으로 사용한다.
내가 원했던 방향은 `local` 은 기본적으로 적용되되 `test` 프로파일에 있는 설정값들이 덮어쓰기 되었으면 좋겠다고 생각했다.

### application-test.yml 생성

`src/test/resources` 아래에 application-test.yml을 생성해주었다.

동일한 파일명이 있을 경우 `src/test/resources` 에 yml 파일을 넣어두면 테스트 시에 `src/main/resources` 의 파일들보다 우선적으로 사용된다.

별도의 프로파일명(`test`)을 사용하였기 때문에 겹칠 일은 없긴 하지만 궁금해서 찾아보았다.

```yaml
spring:
  datasource:
    url: jdbc:mysql://${DATASOURCE_HOST:localhost}:${DATASOURCE_PORT:3307}/${DATASOURCE_DBNAME:dbname}
```

yaml 파일은 간단하게 datasource 정보만 넣어두었다.

### 방법 1

먼저는 클래스에 ActiveProfiles를 붙이는 방법을 사용을 해보았다.

```java
@SpringBootTest
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@ActiveProfiles({"local", "test"})
public class CreateTest {
```

문제없이 적용은 잘 되었지만 걱정되었던 점은 만약 내가 (아니면 다른 팀원이) ActiveProfiles를 넣지 않아서 의도하지 않은 db가 초기화 되는 경우가 발생하면 어떻게 해야하는가에 대한 부분이였다.
환경변수로 값을 받은뒤 overrideProps 로 각 클래스마다 처리를 해주는 방법도 마찬가지로 이 부분을 깜박하고 넣어주지 않으면 문제가 될 수 있을 것이다.

그래서 최종적으로는 아래의 방법으로 변경하였다.

### 방법 2

```groovy
test {
    useJUnitPlatform()
    filter {
        includeTestsMatching('com.jonghoonpark.unit.*')
    }
}

tasks.register('integrationTest', Test) {
    doFirst {
        systemProperty 'spring.profiles.active', 'local, test'
    }
    useJUnitPlatform()
    filter {
        includeTestsMatching('com.jonghoonpark.integration.*')
    }
    group 'test'
    description 'run integration test'
}
```

해당 부분이 필요한 것은 통합테스트의 경우 뿐이다.
따라서 통합테스트를 위한 task를 따로 만들어서 doFirst 부분에 어떤 프로파일을 활성화를 지정할 수 있도록 처리하였다.

이렇게 되면 클래스 구현시 실수로 빠트리거나 하는 경우가 발생하지 않는다. 혹시나 integrationTest 가 아닌 test task로 실행한다 하더라도 filter에 걸려서 실행되지 않는다.

## CompletableFuture 목 처리 하기

회사 프로젝트에서 PG 서비스를 통해 결제를 진행하는 부분이 있다. 그리고 이 부분은 CompletableFuture를 통해서 값을 받아온다.

PG 서비스는 비관리 의존성이기 때문에 Mock으로 처리해도 좋을 것이다.

그래서 아래와 같이 처리했다.

```java
CompletableFuture<PaymentPayStatusDto> future = new CompletableFuture<>();
given(PaymentActionMock.pay(
        any(Integer.class), any(Integer.class), any(Integer.class), any(Integer.class), any(PaymentPayActionMetaDto.class)
)).willReturn(future);
future.complete(PaymentPayStatusDto.builder()
        .isPaymentSuccess(true)
        .build());
```

CompletableFuture는 외부에서 완료시킬 수 있는 구조이다. 따라서 외부에서 완료를 작성해주었다.

이렇게 해서 실제 로직 내에서 paymentSuccess 를 true로 반환해주므로 문제없이 테스트를 진행할 수 있었다.
