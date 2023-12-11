---
layout: post
title: 통합테스트를 진행하면서 부딪힌 이슈들 (일부 항목만 Mock으로 처리하기, BeforeAll Non-static 에서 사용하기, @SQLDelete 가 적용된 상태에서 테이블 초기화 하기)
categories: [개발, 스터디-테스트]
tags:
  [
    테스트,
    테스팅,
    통합 테스트,
    Mock,
    비관리 의존성,
    BeforeAll,
    LifeCycle.PER_METHOD,
    LifeCycle.PER_CLASS,
    SQLDelete,
  ]
date: 2023-12-12 01:00:00 +0900
---

오늘은 회사에서 서비스 클래스를 테스트 하고자 하였다. 그 과정에서 부딪힌 이슈들에 대해서 정리해본다.

# 1. 일부 항목만 Mock으로 처리하기

테스트 대상인 서비스 클래스에는 많은 컴포넌트들이 물려있었고, 그 중에는 이벤트 디스패쳐 (실행 결과를 이메일, 알림톡, SMS 등으로 발송 하는 컴포넌트) 도 포함되어있었다.

테스트 코드를 작성할 때 가능하면 목을 사용하지 않으려 한다. 하지만 비관리 의존성은 예외이다.
비관리 의존성을 간단하게 이야기하면 `전체를 제어할 수 없는 프로세스 외부 의존성` 을 의미한다.

> 비관리 의존성에 대해서는 아래 글에 정리되어 있다.
>
> - [8장 통합 테스트를 하는 이유 (2) - 언제 목을 써야할까? + 예시](/2023/09/14/8장-통합-테스트를-하는-이유-2)
> - [8장 통합 테스트를 하는 이유 (3) - 언제 인터페이스를 써야할까? + 통합 테스트 작성 팁](/2023/09/15/8장-통합-테스트를-하는-이유-3)

이벤트 디스패처는 비관리 의존성 이다. 따라서 mocking을 해도 적절한 경우이다.

서비스에는 `@Autowired` 로 의존성 주입을 시켜주고 이벤트 디스패처는 `@MockBean` 으로 목 객체로 만들어주었다.

# 2. BeforeAll Non-static 에서 사용하기

[testcontainer를 직접 사용해보고 작성한 글](/2023/12/07/testcontainer-with-spring)에서 아래와 같은 내용을 언급하였다.

> **테스트 시작 시점에 데이터 정리하기**: 이 방법이 가장 좋다. 빠르게 작동하고 일관성이 없는 동작을 일으키지 않으며, 정리 단계를 실수로 건너뛰지 않는다.

이 내용을 실제 구현으로 옮기기위해 BeforeAll을 사용하려고 하였는데 문제는 BeforeAll은 기본적으로 static만 허용된다. 그래서 아래 글을 참고해서 non-static한 BeforeAll을 구현하였다.

- [@TestInstance Annotation in JUnit 5]https://www.baeldung.com/junit-testinstance-annotation
- [[JUnit] @BeforeAll, non-static으로 구현하기](https://velog.io/@joosing/JUnit-BeforeAll-non-static%EC%9C%BC%EB%A1%9C-%EA%B5%AC%ED%98%84%ED%95%98%EA%B8%B0)

TestInstance 어노테이션을 이용하여 아래와 같이 코드를 구성할 수 있다.

```java
@TestInstance(Lifecycle.PER_CLASS)
class TweetSerializerUnitTest {

    private String largeContent;

    @BeforeAll
    void setUpFixture() {
        // read the file
    }
}
```

# 3. @SQLDelete 가 적용된 상태에서 테이블 초기화 하기

SQLDelete이 적용되어 있으면 JPA를통해 Delete를 시도할 때 해당 어노테이션에 명시해둔 sql 문을 수행한다. 이를 통해 소프트 딜리트를 처리하였다.

하지만 나는 위에서 이야기 한 대로 **테스트 시작 시점에 데이터 정리하기** 를 하고 싶었기 때문에 어떻게든 데이터를 초기화 하고 싶었다.

그래서 발견한 것이 [How to ignore a @SQLDelete annotation in certain cases](https://stackoverflow.com/a/51893925) 이 글에 달린 답변이였다.

JPQL을 통해서 수행하면 삭제가 가능하다는 것을 보여주는 답변이였는데 실제로 해보니 소개해준 createQuery 로는 해결되지는 않았다. 다만 `em.createNativeQuery` 으로는 되었다.

```java
em.createNativeQuery("DELETE FROM user").executeUpdate();
```

위와같이 sql을 작성해서 수행하니 데이터가 잘 삭제 되었다.
하지만 이후 나온 문제가 auto increment 도 리셋이 되어야 완벽한 초기화가 된다는 것이였다.

```java
em.createNativeQuery("TRUNCATE payment_method").executeUpdate();
```

그래서 Delete를 Truncate로 변경해서 수행하였다.

마지막으로 아래와 같이 유틸화까지 진행하였다.

```java
public static void truncateTables(EntityManager em, String... tableNames) {
    if (tableNames.length == 0) {
        return;
    }

    em.getTransaction().begin();
    em.createNativeQuery("SET FOREIGN_KEY_CHECKS=0").executeUpdate();
    Arrays.stream(tableNames).forEach((tableName) -> em.createNativeQuery("TRUNCATE TABLE " + tableName).executeUpdate());
    em.createNativeQuery("SET FOREIGN_KEY_CHECKS=1").executeUpdate();
    em.getTransaction().commit();
    em.close();
}
```

`FOREIGN_KEY_CHECKS` 를 넣어준 이유는 외래키로 인한 꼬임이 없도록 하기 위해서 추가하였고

이렇게 작성한 코드를 BeforeAll 에서 사용해주었다. 필요에 따라서 BeforeEach에서 사용해도 된다.

```java
@BeforeAll
void setup() throws IOException {
    EntityManager em = emf.createEntityManager();
    DatabaseUtils.truncateTables(em, "table_a", "table_b", "table_c", ...);

    // ...
}
```

최대한 직접 손대는 것은 피하고 싶기 때문에 위와 같은 방식으로 직접 SQL을 작성하는 것은 데이터베이스 초기화에만 사용하였다.
나머지 부분들은 Repository를 이용해서 데이터를 구성하도록 처리하였다.
