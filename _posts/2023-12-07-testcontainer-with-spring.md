---
layout: "post"
title: "Spring 기반 프로젝트에서 테스트컨테이너 (testcontainer) 사용해보기"
description: "Spring 기반 프로젝트에서 테스트컨테이너를 사용하여 데이터베이스 테스트를 설정하는 방법을 소개합니다. Gradle에 필\
  요한 의존성을 추가하고, MySQLContainer를 설정하여 로컬 MySQL DB와 포트 충돌을 피하며, application.yml을 구성하\
  여 테스트가 가능하도록 합니다. 또한, 테스트 실행 시 데이터 정리를 위해 로컬에서 별도의 데이터베이스를 사용하고, 각 테스트 케이스마다 초기화\
  하는 방식을 채택합니다."
categories:
- "스터디-테스트"
tags:
- "테스트"
- "테스팅"
- "test"
- "testing 스프링"
- "spring"
- "도커"
- "docker"
- "컨테이너"
- "container"
- "testcontainer"
- "테스트컨테이너"
- "데이터베이스 테스트"
- "데이터베이스 database"
- "db"
date: "2023-12-07 12:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-12-07-testcontainer-with-spring.jpg"
---

Well Grounded Java Developer 의 14장 에는 testcontainer 에 대한 이야기가 나온다.

읽으면서 좋아보인다는 생각이 들어서 직접 설정을 진행해보았다.

## 설정하기

설정할 것은 크게 없다. 공식 홈페이지에 있는 가이드를 참고해서 설정하면 된다.

[junit_5_quickstart](https://java.testcontainers.org/quickstart/junit_5_quickstart/)

우선 gradle에 testcontainer의 사용을 위해 필요한 의존성을 추가 해준다. mysql 모듈도 추가를 해주었다.

```Groovy
// junit의 경우 기본적으로 spring boot에 포함되어 있어서 나는 안 넣었다.
// testImplementation "org.junit.jupiter:junit-jupiter:5.8.1"

testImplementation "org.testcontainers:testcontainers:1.19.3"
testImplementation "org.testcontainers:junit-jupiter:1.19.3"
testImplementation "org.testcontainers:mysql:1.19.3"
```

그리고 이제 테스트 클래스 안에서 컨테이너를 설정해주면 된다.  
현재 회사에서 하고 있는 프로젝트는 8.0.33 버전을 사용중이기 때문에 그대로 적용하였으며, Local MYSQL DB 와 포트가 겹치지 않도록 하기 위해서 3307 포트로 변경해주었다.

그 외의 정보는 dev 환경과 동일하게 세팅을 해주었다.

```java
@Container
private static MySQLContainer mysqlContainer  = (MySQLContainer) new MySQLContainer("mysql:8.0.33")
            .withDatabaseName("dbname")
            .withUsername("username")
            .withPassword("password")
            .withEnv("MYSQL_TCP_PORT", "3307");
```

그러고 나서 테스트컨테이너 DB에 접근할 수 있도록 application.yml 을 적당히 구성해서 `src/test/resources/` 아래에 넣어주거나 테스트 클래스에 아래와 같이 넣어주면 된다.  
(port를 제외한 나머지 정보는 그대로 가져간다고 가정했기 때문에 url만 바꾸어주었다.)

```java
@DynamicPropertySource
public static void overrideProps(DynamicPropertyRegistry registry){
    registry.add("spring.datasource.url", mysqlContainer::getJdbcUrl);
}
```

이렇게 설정하면 이제 db가 testcontainer로 연결된 상태로 테스트가 가능해진다.

## 기타

공식 예제에 있는 코드를 사용했음에도 intellij 기준으로는 아래와 같은 워닝이 발생된다.

```
Raw use of parameterized class 'MySQLContainer'
```

그래서 코드를 아래와 같이 변경하면

```java
@Container
private static MySQLContainer<?> mysqlContainer = new MySQLContainer<>("mysql:8.0.33")
...
```

이번에는 이런 워닝이 발생한다.

```
MySQLContainer<SELF>' used without 'try'-with-resources statement
```

그래서 워닝 문구에 있는 대로 try-with-resources 방식으로 처리를 해보았지만 워닝은 계속 발생하였다.
인터넷에 찾아봐도 딱히 방법은 없었기에 명확한 해결책은 찾지는 못했다.

## 결론

세팅을 마치고 실행을 해보았다. DB를 띄우는데 꽤 시간이 소요되었다. (약 1분 정도 소요된 것 같다)

물론 깨끗한 상태로 DB를 띄울 수 있긴 하겠지만 시간이 이렇게 오래 걸리는데 이걸 쓰는게 맞나 라는 생각이 들었다.

블라디미르의 단위테스트 책에서도 컨테이너 관련된 이야기가 있었던 것이 어렴풋이 생각이 나서 정리한것을 확인해보았더니 <[데이터베이스 테스트](/2023/09/22/10장-데이터베이스-테스트)> 파트에서 다음과 같이 설명해두었다. (일부만 인용)

> 컨테이너를 사용해 테스트를 병렬 처리할 수도 있다. 그러나 이러한 방식은 실제로 유지 보수 부담이 너무 커지게 된다.
> 따라서 통합 테스트의 실행 시간을 최소화해야하는 경우가 아니라면 컨테이너를 사용하지 않는 것이 좋다.

그러면 컨테이너를 사용하지 않는다면 테스트 실행 간 데이터 정리는 어떻게 하면 좋을까.  
이 부분에 대해서는 아래와 같이 설명한다.

> **테스트 시작 시점에 데이터 정리하기**: 이 방법이 가장 좋다. 빠르게 작동하고 일관성이 없는 동작을 일으키지 않으며, 정리 단계를 실수로 건너뛰지 않는다.

그래서 최종적으로는 테스트용 디비를 로컬에서 하나 더 띄워서 3307를 사용하기로 하였다.  
대신 데이터는 위에서 이야기 한대로 각 테스트케이스마다 항상 초기화를 하도록 처리할 예정이다.

위 코드에서 db port만 3307을 바라볼 수 있도록 overrideProps 부분만 따와서 사용할 예정이다.

```java
@DynamicPropertySource
public static void overrideProps(DynamicPropertyRegistry registry){
    registry.add("spring.datasource.url", () -> "jdbc:mysql://localhost:3307/dbname");
}
```
