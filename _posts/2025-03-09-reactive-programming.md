---
layout: "post"
title: "[Spring] Reactive Programming (with reactor)"
description:
  "리액티브 프로그래밍은 비동기 프로그래밍 패러다임으로, 데이터 스트림과 변화의 전파를 다루며, Java에서는 RxJava와\
  \ Reactor를 통해 구현된다. 리액티브 프로그래밍은 동기식 처리와 달리 비동기식으로 작업을 수행하여 리소스 효율성과 응답성을 향상시키고,\
  \ Reactive Streams 인터페이스를 통해 데이터 흐름을 관리한다. Reactor는 Flux와 Mono를 제공하며, 다양한 오퍼레이션을\
  \ 통해 데이터 파이프라인을 구성할 수 있다. Spring에서는 Webflux와 R2DBC를 활용하여 리액티브 스택을 구현할 수 있으며, 이를\
  \ 통해 성능이 개선된 어플리케이션 개발이 가능하다."
categories:
  - "스터디-자바"
tags:
  - "Spring"
  - "Reactive Programming"
  - "Reactive"
  - "RxJava"
  - "ReactiveX"
  - "Reactive Streams"
  - "Reactor"
  - "async"
  - "asynchronous"
  - "operation"
  - "publisher"
  - "webflux"
  - "r2dbc"
date: "2025-03-09 03:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-03-09-reactive-programming.jpg"
---

# Reactive Programming

> 리액티브 프로그래밍은 **데이터 스트림 (데이터 흐름)** 과 **변화의 전파 (데이터가 흐르는 중 어떻게 변경되고, 또 그것이 어떻게 전파되는지)** 에 관련된 **비동기 프로그래밍 패러다임** 입니다. 즉 정적(예: 배열) 또는 동적(예: 이벤트 이미터) 데이터 스트림을 쉽게 표현할 수 있습니다.

위 문장은 리액티브 프로그래밍에 대한 요약이다. 말만 들으면 무슨 말인지 잘 이해가 되지 않을 것이다. 처음이면 당연하다. 차근차근 정리해보겠다.

## Declarative Programming (선언형 프로그래밍) 과의 비교

우리가 일반적으로 프로그래밍 하는 방식을 **선언형 프로그래밍** 이라고 한다.

선언형 프로그래밍에서는 작업을 순차적으로 진행한다. 각 작업은 한 번에 하나씩 그리고 이전 작업 다음에 실행 데이터는 모아서 처리되고 이전 작업이 데이터 처리를 끝낸 후에 다음 작업으로 넘어간다. 즉, **동기식** 이다. 동기는 작업 완료에 대한 응답을 기다리는 방식이다.

반면에 리액티브 프로그래밍은 비동기 방식이다. 작업 완료에 대한 응답을 기다리지 않아도 된다.

이는 다음과 같은 장점으로 연결된다.

- 리소스 사용의 효율성: 블로킹을 피하여 시스템 리소스를 더 효율적으로 사용할 수 있다.
- 응답성 향상: 다른 작업이 완료되기를 기다리지 않아도 되기 때문에 더 빠르게 응답해줄 수 있다.

## Java 에서의 Reactive Programming

반응형 프로그래밍은 .NET 생태계에서 Reactive Extensions(Rx, ReactiveX) 라이브러리가 만들어지면서 인지도가 올라가기 시작하였고, 그 영향으로 Java 에서 사용할 수 있는 RxJava가 구현되었다.

이후 JVM 에서 논블로킹 백프레셔(non-blocking backpressure)를 갖춘 비동기 데이터 스트림 처리에 대한 표준을 제공하는 것을 목표로 Reactive Streams 인터페이스가 만들어졌다. (데이터 스트림은 쉽게 말하자면 **데이터의 흐름** 을 의미한다.) 그리고 Reactive Streams 는 Flow 라는 이름으로 Java 9에 통합되었다.

현재는 Reactive Streams 를 기반으로 하는 다양한 프로젝트들이 있고, Spring 은 독자적으로 **Reactor** 라는 프로젝트를 만들어 관리하고 있다. (RxJava 도 Reactive Streams를 기반하도록 변경되었다.)

## Reactive Streams

Reactive Streams는 비차단 백 프레셔를 갖춤 비동기 데이터 스트림 처리라는 목표를 달성하는 데 필요한 최소한의 인터페이스, 메서드 및 프로토콜 세트를 찾기 위해 노력하였고, 그 결과 다음의 4개의 인터페이스로 정리되었다.

- Publisher(발행자)
- Subscriber(구독자)
- Subscription(구독)
- Processor(프로세서)

![Reactor3 intro](/assets/images/2025-03-09-reactive-programming/reactive-streams-diagram.png)

각각에 대해서 간단하게 설명하고 넘어가겠다.

### Publisher(발행자)

```java
public static interface Publisher<T> {
    public void subscribe(Subscriber<? super T> subscriber);
}
```

- subscribe() : 구독자(Subscriber) 가 구독(subscribe) 하는데 사용. 구독 하면 발행자로부터 이벤트를 수신.

### Subscriber(구독자)

```java
public static interface Subscriber<T> {
    public void onSubscribe(Subscription subscription);
    public void onNext(T item);
    public void onError(Throwable throwable);
    public void onComplete();
}
```

- onSubscribe() : 구독을 하면 Publisher와 연동된 Subscription 객체 인스턴스를 받음. 이 인스턴스(subscription)를 통해서 backpressure 를 관리.
- onNext() : 데이터를 처리할 때마다 호출
- onError() : 에러 발생 시 호출
- onComplete() : 처리가 종료되었을 경우 호출

**backpressure** 는 **처리 속도** 로 봐도 된다. 발행자(Publisher)와 구독자(Subscriber) 간의 데이터 흐름 속도를 동기화한다.

### Subscription(구독)

```java
public static interface Subscription {
    public void request(long n);
    public void cancel();
}
```

- request(): 처리량을 조정 (= backpressure)
- cancel(): 구독을 취소 (취소 후, 다시 데이터를 받으려면 다시 구독해야 한다.)

기본적으로는 요청된 대로 모두 처리하며, request의 파라미터를 통해 n 값을 조정하여 처리량을 조정할 수 있다.

### Processor(프로세서)

```java
public static interface Processor<T,R> extends Subscriber<T>, Publisher<R> {
}
```

Subscriber 와 Publisher 가 결합된 인터페이스이다. 중간에서 Subscriber 와 Publisher 를 둘 다 구현해야 할 경우 사용한다.

### 데이터 처리 파이프 라인

Publisher로 부터 시작, 0 개 또는 그 이상의 Processor를 통해 데이터를 끌어온 후, 최종 결과를 Subscriber 에게 전달한다.

### Reactive Programming 을 사용했을 때의 장점

일반적으로 Java 개발자는 블로킹 코드를 사용해 프로그램을 작성하게 된다.
이 방식은 성능 병목 현상이 발생하기 전까지는 크게 문제가 되지 않는다.

![single-thread-blocking](/assets/images/2025-03-09-reactive-programming/single-thread-blocking.png)

그럼 성능 병목 현상이 발생되면 어떻게 개선할 수 있을까?

병목이 발생되면 스레드를 추가해 병렬 처리를 시도할 수 있다. 그러나 병렬화는 만능 해결책이 아니다.
하드웨어의 성능을 활용하기 위해 필요하긴 하지만, 논리적으로 복잡하며 리소스 낭비에 취약하다. 게다가 경합과 동시성 문제가 쉽게 발생될 수 있다.

싱글 스레드만 사용했을 때와 마찬가지로 데이터베이스 요청이나 네트워크 호출 같은 I/O 작업으로 지연이 발생하면 데이터를 기다리며 유휴 상태에 빠져 리소스가 낭비될 수 있다.

![multi-thread-blocking](/assets/images/2025-03-09-reactive-programming/multi-thread-blocking.png)

**Reactive Programming** 은 이러한 문제를 해결하는데 도움을 줄 수 있다.

## Reactor

이제 본격적으로 Reactor 에 대해서 알아보도록 하겠다. Reactor는 앞서 말한대로 Reactive Streams의 구현체 중 하나이며, Spring은 Reactor를 적극적으로 활용하고 있다.

### Mono / Flux

Reactor 에서는 2가지의 Publisher 구현체를 제공한다.

- Flux : 0개 이상의 데이터 스트림 표현
- Mono : 0개 혹은 1개 의 데이터 스트림 표현

* Mono는 Flux 의 특수한 형태이다.

### 오퍼레이션 (operation)

Reactor 는 다양한 오퍼레이션을 제공하여 데이터 파이프라인을 구성할 수 있도록 돕는다.
오퍼레이션은 데이터 스트림에서 데이터를 생성, 변환, 필터링, 결합 또는 소비하기 위해 적용되는 연산자나 처리 단위를 의미한다.
Reactor 에서는 약 500개 이상의 오퍼레이션이 존재한다.

이 포스트에서는 Spring In Action 에서 소개해준 주요 오퍼레이션들을 위주로 살펴본다. 오퍼레이션을 **생성, 조합, 필터링, 변환, 로직, 기타** 로 나누어 설명해보도록 하겠다.

그 외에 더 알아보고 싶다면 < [Which operator do I need?](https://projectreactor.io/docs/core/release/reference/apdx-operatorChoice.html) > 문서를 참고 하면 좋을 것 같다.

### 마블 다이어그램 (marble diagrams?)

본격적으로 오퍼레이션들을 설명하기에 앞서 마블 다이어그램에 대해 간단하게 설명하고 넘어가도록 한다.

Reactor 에서는 오퍼레이션의 동작을 시각적으로 보여주기 위해 마블 다이어그램을 사용한다. (Reactor 뿐 아니라 다른 리액티브 프레임워크 도구들도 대부분 사용한다.)

아래 이미지는 Flux 와 Mono 를 통해 마블 다이어그램 템플릿을 통해 읽는 법을 설명한다.

![flux marble diagram](/assets/images/2025-03-09-reactive-programming/flux.png)

![mono marble diagram](/assets/images/2025-03-09-reactive-programming/mono.png)

더 자세한 내용은 < [How to read marble diagrams?](https://projectreactor.io/docs/core/release/reference/apdx-howtoReadMarbles.html) > 문서를 참고 하면 좋을 것 같다.

### 생성 오퍼레이션

- 객체로 부터 생성 : just
- 컬렉션으로부터 생성 : fromArray, fromIterable, fromStream
- 범위 생성 : range, interval
- 동적 생성 : create

#### 객체로 부터 생성

![operation just](/assets/images/2025-03-09-reactive-programming/operation-just.svg)

내보낼(emit) 요소들 (elements) 로 데이터 스트림을 생성한다.

```java
Flux<String> fruitFlux =
      Flux.just("Apple", "Orange", "Grape", "Banana", "Strawberry");
```

Flux는 앞에서 설명한 것과 같이 0개 이상의 데이터 스트림 표현한다.
만약 just 에 아무런 값도 넣지 않는다면 `Flux.empty()` 와 동일한 데이터 스트림이 생성된다.

#### 객체로 부터 생성

![operation from xxx](/assets/images/2025-03-09-reactive-programming/operation-from-xxx.png)

fromArray, fromIterable, fromStream 도 사용법이 크게 다르지는 않다.

````java
String[] fruits = new String[] {
    "Apple", "Orange", "Grape", "Banana", "Strawberry" };
Flux<String> fruitFlux = Flux.fromArray(fruits);

```java
List<String> fruitList =
    List.of("Apple", "Orange", "Grape", "Banana", "Strawberry");
Flux<String> fruitFlux = Flux.fromIterable(fruitList);
````

```java
Stream<String> fruitStream =
    Stream.of("Apple", "Orange", "Grape", "Banana", "Strawberry");
Flux<String> fruitFlux = Flux.fromStream(fruitStream);
```

#### 범위 생성

![operation range](/assets/images/2025-03-09-reactive-programming/operation-range.svg)

```java
Flux<Integer> intervalFlux = Flux.range(1, 5);
```

start 부터 count 개 만큼 1씩 증가시키면서 생성한다. (여기서는 1, 2, 3, 4, 5)

![operation interval](/assets/images/2025-03-09-reactive-programming/operation-interval.svg)

```java
Flux<Long> intervalFlux =
    Flux.interval(Duration.ofSeconds(1))
        .take(5);
```

참고로 take 는 첫 시작부터 N 개 까지의 요소만 가져오는 operation 이다. interval은 take 가 없으면 계속 요소를 publish 한다.
요소의 값은 0 부터 시작하며, interval 마다 1씩 증가한다.

#### 동적 생성

![operation create](/assets/images/2025-03-09-reactive-programming/operation-create.svg)

상황에 따라 동적으로 요소를 publish 하는데 사용된다. 아래의 예시와 같이 action listener 같은 것과 함께 사용할 수도 있다.

```java
Flux.<String>create(emitter -> {
    ActionListener al = e -> {
        emitter.next(textField.getText());
    };
    // without cleanup support:

    button.addActionListener(al);

    // with cleanup support:

    button.addActionListener(al);
    emitter.onDispose(() -> {
        button.removeListener(al);
    });
});
```

### 조합 오퍼레이션

- merge
- zip
- first

#### merge

![operation merge](/assets/images/2025-03-09-reactive-programming/operation-merge.svg)

2개 이상의 Flux를 합친다.

다음과 같이 사용할 수 있다.

```java
Flux<String> englishCharacters = Flux.just("a","b","c")
    .delayElements(Duration.ofMillis(500));

Flux<String> koreanCharacters = Flux.just("ㄱ","ㄴ","ㄷ")
    .delaySubscription(Duration.ofMillis(600))
    .delayElements(Duration.ofMillis(250));

Flux<String> mergedFlux = Flux.merge(englishCharacters, koreanCharacters);

StepVerifier.create(mergedFlux)
    .expectNext("a") // 500
    .expectNext("ㄱ") // 850
    .expectNext("b") // 1000
    .expectNext("ㄴ") // 1100
    .expectNext("ㄷ") // 1350
    .expectNext("c") // 1500
    .verifyComplete();
```

참고로 위 코드에서 추가적으로 사용된 operation은 다음과 같은 역할은 한다.

- delaySubscription : 구독을 지연 (최초 방출을 지연)
- delayElements : 각 Element 의 방출을 지연 (첫 element도 delay 되는 것에 주의)

또한 subscriber 마다 새로운 Iterator 가 생성됨에 주의하자.

#### zip

![operation zip](/assets/images/2025-03-09-reactive-programming/operation-zip.svg)

각 flux 에서 한 Element 씩 번갈아 가져와 새로운 Flux를 생성한다.
마블 다이어그램을 통해 알 수 있듯, 먼저 도착하더라도 tuple을 구성하지 못하면 emit 되지 못하고 대기하게 된다.

다음과 같이 사용할 수 있다.

```java
Flux<String> englishCharacters = Flux.just("a","b","c");
Flux<String> koreanCharacters = Flux.just("ㄱ","ㄴ","ㄷ");

Flux<Tuple2<String, String>> pairs = Flux.zip(englishCharacters, koreanCharacters);

StepVerifier.create(pairs)
    .expectNextMatches(pair -> pair.getT1().equals("a") && pair.getT2().equals("ㄱ"))
    .expectNextMatches(pair -> pair.getT1().equals("b") && pair.getT2().equals("ㄴ"))
    .expectNextMatches(pair -> pair.getT1().equals("c") && pair.getT2().equals("ㄷ"))
    .verifyComplete();
```

Tuple2 이라는 이름을 클래스를 다양한 곳에서 구현해놨기 때문에 import 시에 reactor 의 Tuple2 인지 잘 확인하자.

#### first

![operation first](/assets/images/2025-03-09-reactive-programming/operation-first.svg)

일반 first operation 은 deprecated 되었다. 그리고 두 가지 first 메소드로 세분화 되었다.

- firstWithValue : 첫 번째 값을 방출할 때까지 기다린다. (onNext)
- firstWithSignal: 첫 번째 신호 (onNext, onError, onComplete)가 발생할 때까지 기다린다.

### 필터링 오퍼레이션

- skip
- take
- filter
- distinct

#### skip

![operation skip](/assets/images/2025-03-09-reactive-programming/operation-skip.svg)

첫 n 개의 element를 건너뛴다.

#### take

![operation take](/assets/images/2025-03-09-reactive-programming/operation-take.svg)

첫 n 개의 element만 허용한다.

2번째 있는 boolean 인자는 limitRequest 인데 애초에 갯수를 제한해서 요청할지를 설정하는 옵션이라고 한다. 기본값은 true 이다.

#### filter

![operation filter](/assets/images/2025-03-09-reactive-programming/operation-filter.svg)

filter 의 조건에 맞는 element 만 허용한다.

#### distinct

![operation filter](/assets/images/2025-03-09-reactive-programming/operation-filter.svg)

데이터 스트림에서 중복되지 않는 element 만 허용한다. 중복의 기준은 `Object::hashcode` 메소드를 사용한다.

### 변환 오퍼레이션

- 매핑
  - map
  - flatMap
- 버퍼링
  - buffer
- 콜렉션
  - collectList
  - collectMap

#### map

![operation map](/assets/images/2025-03-09-reactive-programming/operation-map.svg)

element를 1:1 로 변환할 때 사용한다. (eg. 문자열에 대한 flux를 받아, 문자열의 길이에 대한 flux 로 변환)

#### flatMap

![operation flatmap](/assets/images/2025-03-09-reactive-programming/operation-flatmap.svg)

element를 1:n 으로 변환할 때 사용한다. (eg. 문자열에 대한 flux를 받아, 문자열을 각 문자로 나눠서, 문자 대한 flux 로 변환)

#### map 과 flatMap 의 차이

- **map**
  - `public final <V> Flux<V> map(java.util.function.Function<? super T,? extends V> mapper)`
  - 동기적으로 매핑 수행
  - 각 요소를 변환하여 반환
- **flatMap**
  - `public final <R> Flux<R> flatMap(java.util.function.Function<? super T,? extends Publisher<? extends R>> mapper)`
  - 비동기적으로 매핑 수행
  - 각 요소를 변환하고 그 결과를 평탄화하여 반환

#### buffer

![operation buffer](/assets/images/2025-03-09-reactive-programming/operation-buffer.svg)

개별 element를 buffer로 묶는다.

buffer operation의 입력값은 maxSize를 지정하는데 사용된다. 입력값은 0보다 커야 한다.
입력값을 넣지 않을 경우 하나의 버퍼로 구성된다.

#### 콜랙션

**collectList**

![operation collectList](/assets/images/2025-03-09-reactive-programming/operation-collectlist.svg)

개별 element를 list로 묶는다. 결과가 Mono 로 나온다.

**collectMap**

![operation collectMap](/assets/images/2025-03-09-reactive-programming/operation-collectmap.svg)

개별 element를 map으로 묶는다. 결과가 Mono 로 나온다.

입력 값으로는 keyExtractor Function을 넣어준다.

### 로직 오퍼레이션

- all
- any

#### all

![operation all](/assets/images/2025-03-09-reactive-programming/operation-all.svg)

모든 element가 조건을 만족할 경우 Mono true를 반환한다.

#### any

![operation any](/assets/images/2025-03-09-reactive-programming/operation-any.svg)

모든 element중 하나라도 조건을 만족할 경우 Mono true를 반환한다.

### 기타 오퍼레이션

- `log()` : operation 에 적용하면 데이터 스트림의 데이터를 로깅한다.

## Spring 에서 Reactive Programming 사용하기

리액티브 프로그래밍의 장점을 극대화하려면 완전한 e2e 리액티브 스택을 구현해야 한다. 기존의 의존성을 reactive 버전으로 교체하여 적용한다.

![e2e reactive stack](/assets/images/2025-03-09-reactive-programming/e2e-reactive-stack.png)

### Spring Webflux

`Spring MVC` 에 대한 Reactive 프로그래밍 대안이다. Controller 에서 Mono, Flux 를 반환하도록 처리하면 내부적으로 Reactive 하게 처리된다.

이벤트 루프 기법을 사용해서 더 적은 수의 스레드로 더 높은 처리량과 확장성을 달성하였다.

![webflux event loop](/assets/images/2025-03-09-reactive-programming/webflux-event-loop.png)

### Spring Data R2DBC

Spring Data R2DBC를 사용하면 기존의 Spring Data JPA 와 큰 차이 없이 개발할 수 있다.
ReactiveCrudRepository 라는 인터페이스를 상속하여 Data 레포지토리를 구현할 수 있다.

데이터베이스 드라이버도 일반적으로 사용되는 JDBC 가 아닌 **R2DBC (Reactive Relational Database Connectivity)** 를 사용해야한다.

### 사용 예시

최근에 개인적인 용도로 판결 데이터를 살펴볼 일이 있어서 reactor 를 이용하여 데이터를 저장하여 보았다.
아래 코드는 그 코드 중 일부이다.

```java
// 목록 조회
Flux<String> ids = judicialPrecedentExternalService.getList(0)
    .flatMapMany(response -> Flux.fromIterable(response.getData().getJudicialPrecedents())
            .map(ExternalListData::getJisCntntsSrno))
    .delayElements(Duration.ofSeconds(5)); // 5초 간격으로 방출

// 상세 페이지 조회
ids.take(1) // 테스트를 위해 1개만 받아오도록 처리
    .flatMap(judicialPrecedentExternalService::getDetail) // 상세 페이지 조회 API 호출
    .flatMap(response -> { // entity 로 매핑
        ExternalDetailData externalDetailData = response.getData().getJudicialPrecedent();
        return Mono.just(JudicialPrecedent.builder()
            .id(externalDetailData.getJisCntntsSrno())
            .type(externalDetailData.getJisCntntsKndCd())
            .fileId(externalDetailData.getJisFileSrno())
            .filepath(externalDetailData.getJisFilePathNm())
            .filename(externalDetailData.getJisFileNm())
            .updatedAt(externalDetailData.getLastChgDt())
            .createdAt(externalDetailData.getFrstInptDt())
            .content(externalDetailData.getOrgdocXmlCtt())
            .build());
    })
    .flatMap(judicialPrecedentService::save) // DB 저장
    .subscribe();
```

## 마무리

Reactive Programming 은 개념은 간단하다. 하지만 실제로 사용을 해보고자 하면 쉽지 않다. 많은 학습이 필요한 방식이다. 하지만 제대로 적용한다면, 더 좋은 성능을 낼 수 있는 어플리케이션을 만드는데 도움이 될 것이다. (무조건 쓰는게 좋다는 뜻은 아님.)

참고로 Reactive Programming 은 기존 방식(선언형 프로그래밍)에 비해 학습 해야할 것이 많아 진입 장벽이 있는 편이고, 디버깅과 에러 추적이 쉽지 않다. 모든 것에는 트레이드 오프가 따르는 것 같다.

## 기타

### 참고 자료

- Spring In Action
- Reactive Streams : [https://www.reactive-streams.org/](https://www.reactive-streams.org/)
- Reactor Core : [https://projectreactor.io/docs/core/release/reference/aboutDoc.html](https://projectreactor.io/docs/core/release/reference/aboutDoc.html)
- [Reactor3 intro By Simon Basle](https://files.speakerdeck.com/presentations/fa5195b61d9e4d7bb85c84fc53740b89/Reactor3ForSite.pdf)

### Operator 를 사용했는데 적용이 되지 않습니다.

Reactor Operator 는 decorator 방식으로 동작한다. 원래의 동작에 새로운 동작을 추가하여 새로운 인스턴스로 반환한다.
그래서 체이닝을 통해 호출하는 것을 권장하고 있다.

**잘못된 사용방법**

```java
Flux<String> flux = Flux.just("something", "chain");
flux.map(secret -> secret.replaceAll(".", "*"));
flux.subscribe(next -> System.out.println("Received: " + next));
```

이 방식은 map operation 이 적용되지 않고 생략 된다.

**제대로 된 사용방법**

```java
Flux<String> flux = Flux.just("something", "chain");
flux = flux.map(secret -> secret.replaceAll(".", "*"));
flux.subscribe(next -> System.out.println("Received: " + next));
```

이렇게 변경해주면 정상적으로 동작한다.

그리고 다시 한 번 chaining 을 사용하여 더 단순한 방식으로 수정해볼 수 있다.

```java
Flux.just("something", "chain")
    .map(secret -> secret.replaceAll(".", "*"))
    .subscribe(next -> System.out.println("Received: " + next));
```

참고: [I Used an Operator on my Flux but it Doesn’t Seem to Apply. What Gives?](https://projectreactor.io/docs/core/release/reference/faq.html#faq.chain)

### React.js 와 관련있는건가요?

스터디 발표 중 나왔던 질문이다. React.js 와는 크게 관련 없다.

본문에서 이야기 한 대로 Reactive Programming 은 프로그래밍 패터다임 중 하나이다.

React.js 는 UI 라이브러리이다. 컴포넌트의 상태가 변경되었을 때, 변경사항에 따라 UI 를 렌더링 한다. 선언형 프로그래밍 (declarative programming) 을 사용한다.

따라서 크게 관련있거나 하지는 않는다.
