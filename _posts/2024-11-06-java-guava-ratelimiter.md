---
layout: post
title: "[Java] 초당 api 호출 횟수 제한 처리 - Guava RateLimiter"
categories: [개발, 스터디-자바]
tags: [java, guava, rate, rate limit, api, api call, RateLimiter, token bucket]
date: 2024-11-06 15:30:00 +0900
toc: true
---

종종 API 명세를 보다보면, API에 대한 초당 호출 횟수가 제한되어 있는 경우가 있다. (QPS, queries per second)
그 반면, 클라이언트 쪽에서는 매우 많은 수의 데이터를 해당 API로 처리할 수 있기를 기대한다.

그러면 어떻게 API의 초당 호출 횟수를 넘어서지 않는 선에서 적절히 api 를 호출할 수 있을까?

이 글에서는 Guava 라이브러리의 **RateLimiter** 를 사용하는 방법을 소개한다.

## Guava 라이브러리

Guava 메인 페이지([https://guava.dev/](https://guava.dev/))에서는 Guava 라이브러리를 다음과 같이 소개하고 있다.

> Guava is a set of core Java libraries from Google that includes new collection types (such as multimap and multiset), immutable collections, a graph library, and utilities for concurrency, I/O, hashing, primitives, strings, and more! It is widely used on most Java projects within Google, and widely used by many other companies as well.

Guava는 구글이 작성한 자바 라이브러리이며 다양한 기능들을 제공하고 있다. 구글을 포함한 다양한 회사에서 사용중이다.

아마 java 개발자라면 나도 모르게 포함되어 있는 경우도 많을 것 같다. (특히, google 관련 라이브러리를 추가하였을 경우)

## RateLimiter

오늘 다를 RateLimiter 는 초당 허용량에 따라 api 호출 횟수를 제한하도록 돕는 클래스이다. 클래스에 대한 구체적인 설명은 documentation 을 참고하면 좋을 것 같다.

class documentation : [https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/util/concurrent/RateLimiter.html](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/util/concurrent/RateLimiter.html)

### api

모든 메소드를 설명하지는 않고 핵심이라고 생각되는 기본 create와 acquire 메소드에 대해서만 정리하여 보았다.

| Modifier and Type  | Method                           | Description                                       |
| ------------------ | -------------------------------- | ------------------------------------------------- |
| static RateLimiter | create​(double permitsPerSecond) | 입력받은 “초당 허용량"을 가진 RateLimiter 를 생성 |
| double             | acquire()                        | 1회 허가 요청 후 요청이 승인될 때까지 대기한다.   |

### 사용 예시

실제적으로 어떻게 사용할 수 있는지 예시를 통해서 알아보자.

아래는 초당 2회 api 를 호출하도록 한 테스트 코드이다. (예제이기 떄문에 그냥 `print` 메소드를 사용하였다.)

```java
RateLimiter rateLimiter = RateLimiter.create(2);

for (int i = 0; i < Integer.MAX_VALUE; i++) {
  rateLimiter.acquire();
  System.out.println(i);
}
```

RateLimiter 가 없었다면 반복문 안에서 매우 빠르게 순차적으로 숫자들이 출력되었겠지만, RateLimiter로 인해 초당 2회까지의 출력문이 출력되는 것을 확인할 수 있다.

이제 초당 허용량과 `print` 부분을 내가 원하는 api 호출로 변경하면 된다.

### Beta

참고로 RateLimiter는 Beta annotation 이 붙어있다. 이로 인해 IDE에서 warning을 출력해준다.

기능적으로 덜 구현되었다는 것일까?

[documentation](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/annotations/Beta.html) 에서는 다음과 같이 설명하고 있다.

> Signifies that a public API (public class, method or field) is subject to incompatible changes, or even removal, in a future release. An API bearing this annotation is exempt from any compatibility guarantees made by its containing library. Note that the presence of this annotation implies nothing about the quality or performance of the API in question, only the fact that it is not "API-frozen."

정리하면 Beta 는 기능 완성도와는 무관하며, API가 변경될 가능성이 있는 경우에 지정된다고 한다. 따라서 사용해도 기능적으로는 문제가 되지는 않는다.

다만, 앞서 이야기 한 대로 API가 변경될 수 있기 때문에 Guava 의 버전을 변경할 때는 유의를 해야하겠다. (RateLimiter의 경우에는 꽤 오랜 기간동안 Beta 을 유지하고 있는 것으로 보인다.)

## 참고

- 이와 유사한 주제로 과거 시스템 디자인 스터디를 진행하며 API 호출 제한에 대한 정리글을 작성했었다.
  - [API 제한 설정하기 - 처리율 제한 장치의 설계](https://jonghoonpark.com/2023/05/17/%EC%B2%98%EB%A6%AC%EC%9C%A8-%EC%A0%9C%ED%95%9C-%EC%9E%A5%EC%B9%98-%EC%84%A4%EA%B3%84)
  - Guava 의 RateLimiter 의 경우에는 **토큰 버킷 알고리즘** 이다.
