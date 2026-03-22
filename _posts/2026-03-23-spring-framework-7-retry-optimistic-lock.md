---
layout: "post"
title: "Spring Framework 7의 Retry로 Optimistic Lock 충돌 해결하기"
description: "Spring Framework 7에서 core에 포함된 Retry 기능을 활용하여 JPA Optimistic Lock 충돌 시 자동 재시도하는 방법을 소개합니다. @Retryable, @EnableResilientMethods 사용법과 실제 적용 사례를 다룹니다."
categories:
  - "개발"
tags:
  - "Spring"
  - "Spring Framework 7"
  - "Retry"
  - "Optimistic Lock"
  - "JPA"
  - "동시성"
date: "2026-03-23 02:30:00 +0900"
toc: true
---

## 동시에 같은 게시글을 수정하면?

커뮤니티 서비스를 운영하다 보면 동시에 같은 데이터를 수정하는 상황이 발생할 수 있다. 게시글 내용을 동시에 수정하는 경우뿐만 아니라, 조회수나 좋아요 같은 메타데이터가 동시에 업데이트되는 경우에도 아무런 보호 장치가 없다면 먼저 저장한 변경이 나중 변경에 덮어씌워지는 **Lost Update** 문제가 발생한다.

**Optimistic Lock** 과 **Spring Framework 7의 내장 Retry** 기능을 조합하여 이 문제를 해결한 경험을 공유한다.

## 비관적 락 vs 낙관적 락

동시성 문제를 해결하는 대표적인 방법은 두 가지가 있다.

**비관적 락(Pessimistic Lock)**은 데이터를 읽을 때 락을 걸어 다른 트랜잭션의 접근을 차단한다. 안전하지만 동시 처리 성능이 떨어진다.

**낙관적 락(Optimistic Lock)**은 충돌이 드물다고 가정하고, 데이터를 수정할 때 버전을 비교하여 충돌을 감지한다. 충돌이 발생하면 예외를 던지고, 호출자가 재시도를 결정한다. 락을 걸지 않으므로 동시 처리 성능이 좋다.

비관적 락과 낙관적 락의 개념에 대해서는 [[MySQL] Optimistic Lock 과 Pessimistic Lock 이해하기 (컨셉)](https://jonghoonpark.com/2024/09/13/mysql-jpa-optimistic-lock-and-pessimistic-lock) 글에서 더 자세히 다루고 있다.

게시글 수정은 동시 충돌 빈도가 낮으므로 낙관적 락이 적합하다.

## Optimistic Lock 적용

### @Version 필드 추가

JPA에서 낙관적 락은 `@Version` 어노테이션으로 간단하게 적용할 수 있다. 엔티티에 버전 필드를 추가하면, JPA가 UPDATE 쿼리 실행 시 자동으로 버전을 비교하고 증가시킨다.

```java
@Entity
@Table(name = "posts")
@DynamicUpdate
@Getter
public class Post extends BaseEntity {
    // ... 기존 필드들

    @Version
    private Long version;
}
```

`@SQLDelete`를 사용하고 있다면 WHERE 조건에도 `version = ?` 을 추가해야 한다.

### version 컬럼 추가

Flyway 와 같은 DB 형상 관리 도구를 사용한다면 잊지말고 version 컬럼을 추가하는 마이그레이션 스크립트를 작성한다.

```sql
ALTER TABLE posts ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
```

이것만으로 낙관적 락 적용은 완료다. 이제 동시 수정이 발생하면 나중에 커밋하는 트랜잭션에서 `ObjectOptimisticLockingFailureException`이 발생한다.

하지만 예외만 던지면 사용자 경험이 좋지 않다. 충돌 시 자동으로 재시도하면 대부분의 경우 사용자가 충돌을 인지하지 못하고 정상적으로 수정할 수 있다.

## Spring Framework 7의 Retry 기능

### 기존 방식: spring-retry 라이브러리

Spring Framework 6 이하에서는 재시도 기능을 사용하려면 [spring-retry](https://github.com/spring-projects/spring-retry) 라이브러리를 별도로 추가해야 했다.

```gradle
implementation 'org.springframework.retry:spring-retry'
```

### Spring Framework 7: core에 통합

Spring Framework 7에서는 Retry 기능이 **core에 통합**되었다. 별도의 의존성 없이 `org.springframework.resilience.annotation` 패키지의 어노테이션을 바로 사용할 수 있다.

주요 변경점은 다음과 같다.

| 항목              | spring-retry (기존)                    | Spring Framework 7                          |
| ----------------- | -------------------------------------- | ------------------------------------------- |
| 의존성            | 별도 라이브러리 필요                   | core에 포함                                 |
| 활성화 어노테이션 | `@EnableRetry`                         | `@EnableResilientMethods`                   |
| 재시도 횟수 설정  | `maxAttempts` (최대 시도 횟수)         | `maxRetries` (최대 재시도 횟수)             |
| 패키지            | `org.springframework.retry.annotation` | `org.springframework.resilience.annotation` |

`maxAttempts`에서 `maxRetries`로 변경된 점에 주의해야 한다. `maxAttempts = 3`은 총 3번 시도(최초 1번 + 재시도 2번)이지만, `maxRetries = 3`은 최초 시도 후 최대 3번 재시도(총 4번 시도)를 의미한다.

참고 자료:

- [Spring Framework 공식 문서 - Resilience](https://docs.spring.io/spring-framework/reference/core/resilience.html)
- [Core Spring Resilience Features 블로그](https://spring.io/blog/2025/09/09/core-spring-resilience-features/)
- [Spring Framework 7.0 Release Notes](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-7.0-Release-Notes)

## @Retryable 적용

### @EnableResilientMethods 설정

먼저 `@EnableResilientMethods`를 설정 클래스에 추가한다.

```java
@Configuration
@EnableJpaAuditing
@EnableResilientMethods
public class JpaConfig {
}
```

### 트랜잭션 분리가 필요한 이유

`@Retryable`과 `@Transactional`을 같은 메서드에 적용하면 문제가 생긴다. 재시도가 트랜잭션 **내부**에서 일어나기 때문이다.

```java
// ❌ 이렇게 하면 안 됩니다 - 재시도가 롤백된 트랜잭션 안에서 일어남
@Retryable(includes = ObjectOptimisticLockingFailureException.class)
@Transactional
public PostResponse updatePost(...) { ... }
```

낙관적 락 예외가 발생한 시점에서 **트랜잭션은 이미 롤백 마킹된 상태** 다. 같은 트랜잭션 안에서 재시도해도 이미 더티(dirty) 상태이므로 의미가 없다. 재시도 시에는 **새로운 트랜잭션**에서 최신 데이터를 다시 읽어와야 한다.

따라서 `@Retryable`은 트랜잭션 바깥에, `@Transactional`은 실제 DB 작업을 수행하는 내부 메서드에 배치해야 한다. 이를 위해 서비스를 분리했다.

### 코드 적용

`PostService`에서 `@Retryable`을 적용하고, 실제 수정 로직은 `PostUpdateService`로 분리한다.

```java
@Service
@RequiredArgsConstructor
public class PostService {
    private final PostUpdateService postUpdateService;

    /**
     * 게시글 수정
     * 낙관적 락 충돌 시 최대 2회 재시도
     */
    // DB 충돌은 수십 ms 내에 해소되므로 짧은 대기(100ms ± 50ms)로 충분하다
    @Retryable(
        includes = ObjectOptimisticLockingFailureException.class,
        maxRetries = 2,
        delay = 100,
        jitter = 50
    )
    public PostResponse updatePost(final Long postId, final PostRequest request, final Long userId) {
        return postUpdateService.updatePostInternal(postId, request, userId);
    }
}
```

```java
@Service
@RequiredArgsConstructor
public class PostUpdateService {
    private final PostRepository postRepository;
    private final ChannelRepository channelRepository;
    private final UserRepository userRepository;
    private final XssSanitizer xssSanitizer;
    private final PermissionService permissionService;
    private final OgHtmlService ogHtmlService;

    @Transactional
    public PostResponse updatePostInternal(final Long postId, final PostRequest request, final Long userId) {
        // ...
    }
}
```

호출 흐름을 정리하면 다음과 같다.

1. `PostService.updatePost()` 호출 → `@Retryable` AOP 프록시 적용
2. `PostUpdateService.updatePostInternal()` 호출 → `@Transactional`로 새 트랜잭션 시작
3. 충돌 발생 시 `ObjectOptimisticLockingFailureException` → 트랜잭션 롤백
4. `@Retryable`이 예외를 캐치하고 100ms(±50ms) 후 재시도
5. 새로운 트랜잭션에서 최신 데이터를 읽어 다시 수정 시도

## @Retryable 주요 파라미터 정리

| 파라미터     | 설명                                     | 기본값 |
| ------------ | ---------------------------------------- | ------ |
| `includes`   | 재시도할 예외 클래스 목록                | -      |
| `excludes`   | 재시도하지 않을 예외 클래스 목록         | -      |
| `maxRetries` | 최대 재시도 횟수                         | 3      |
| `delay`      | 재시도 간 대기 시간 (ms)                 | 1000   |
| `jitter`     | 대기 시간에 추가되는 랜덤 지연 (ms)      | 0      |
| `multiplier` | 재시도마다 대기 시간에 곱해지는 배수     | 1.0    |
| `maxDelay`   | 최대 대기 시간 (ms)                      | -      |
| `predicate`  | 재시도 여부를 판단하는 Predicate 빈 이름 | -      |

## 정리

- **Optimistic Lock**은 `@Version` 필드 하나로 동시 수정 충돌을 감지할 수 있다.
- 충돌 시 **자동 재시도**를 적용하면 대부분의 경우 사용자에게 투명하게 처리된다.
- **Spring Framework 7**에서는 Retry가 core에 통합되어 별도 의존성 없이 `@Retryable`과 `@EnableResilientMethods`를 사용할 수 있다.
- `@Retryable`과 `@Transactional`은 반드시 **분리**해야 재시도 시 새로운 트랜잭션에서 최신 데이터를 읽을 수 있다.
