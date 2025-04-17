---
layout: "post"
title: "[Spring] Spring Data Redis 로 Redis Pub/Sub 구현하기"
description:
  "Redis PubSub는 발행자(Publisher)가 특정 채널에 메시지를 발행하면 구독자(Subscriber)들이 이를\
  \ 수신하는 구조로, Spring Data Redis를 활용하여 캐시 초기화를 효율적으로 관리할 수 있다. RabbitMQ와 비교할 때 메시지\
  \ 전송 보장과 지속성에서 차이가 있으며, Redis PubSub는 설정이 간단해 개발 환경에서 유용하다. 이 글에서는 Redis PubSub의\
  \ 구현 방법과 사용 사례를 소개한다."
categories:
  - "스터디-자바"
tags:
  - "Spring"
  - "Spring Data"
  - "Spring Data Redis"
  - "Redis"
  - "Redis Pubsub"
  - "PubSub"
  - "Publisher"
  - "Subscriber"
  - "Subscribe"
  - "cache"
  - "evict"
date: "2025-04-17 06:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-04-17-spring-data-redis-pubsub.jpg"
---

# Redis PubSub

[Redis PubSub](https://redis.io/docs/latest/develop/interact/pubsub/) 기능은 Redis 에서 [Publish-Subscribe pattern](https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern) 을 사용할 수 있도록 구현한 것이다.

Publish-Subscribe pattern은 발행자(Publisher)가 메시지를 특정 채널에 발행하면 해당 채널을 구독(Subscribe)하고 있는 수신자(Subscriber)들이 메시지를 받는 구조를 의미한다.

## Redis PubSub vs RabbitMQ

[RabbitMQ와 Redis PubSub의 차이점은 무엇인가요?](https://aws.amazon.com/ko/compare/the-difference-between-rabbitmq-and-redis/)

PubSub 구조로 유명한 다른 도구로는 RabbitMQ가 있다. 같은 PubSub 을 사용하지만 용도와 기능 면에서 차이가 있다.

내가 생각하기에 가장 중요한 차이는 메시지 전송 보장과 지속성에서의 차이 인 것 같다.

|                  | RabbitMQ                                       | Redis PubSub                                                         |
| ---------------- | ---------------------------------------------- | -------------------------------------------------------------------- |
| 메시지 전송 보장 | 소비자의 확인을 통해 메시지 전송 보장          | 별도의 보장을 하지 않으며, 구독자가 연결되어 있어야 메시지 수신 가능 |
| 지속성           | 영구 및 일시적 메시지 지원, 디스크에 저장 가능 | 기본적으로 지속성 없음                                               |

## Redis PubSub 을 사용하기로 결정한 이유

서비스 내에서 다양한 캐시를 사용하고 있는 중인데, 그 중 일부 캐시는 각 서버에서 인메모리로 관리하고 있다.
서버 어플리케이션은 k8s 위에서 여러개의 팟으로 관리되고 있다보니, 전체적으로 캐시를 초기화 하려면 각 서버 어플리케이션에 직접 포트포워딩을 하여 캐시 초기화 api 를 호출해주거나 해야하는 이슈가 있었다.

prod 환경에서는 그럴일이 크게 없겠지만, 개발 환경에서는 캐시를 초기화 해야할 일이 자주 발생되기도 한다.
이에 한쪽에서 캐시를 초기화를 호출하면 별도의 수동 작업 없이 각 pod 에서 캐시 초기화를 진행되도록 하고 싶었다.

이 시스템에는 이미 Redis 도, Rabbit MQ 도 구성되어 있다. 하지만, 데이터가 지속되어야 할 필요가 없었고, 수신을 검증할 필요도 없는 작업이라고 생각하였기 때문에 Redis PubSub로 빠르게 결정하고 진행하였다. 설정도 간단하게 가능한 것도 선택에 영향을 주었다.

기존의 architecture 는 다음과 같은 구조였다. 잘 변하지 않는 데이터라 그런지, 데이터 조회 후 cache 처리는 하는데 cache를 수정/삭제 하는 방법은 제공하고 있지 않았다. 그래서 캐시 초기화를 하려면 서버를 재실행 해야만 했다.

![prev architecture](/assets/images/2025-04-17-spring-data-redis-pubsub/prev-architecture-1.png)

그래서 evict 를 할 수 있도록 아래와 같이 개선을 해보기로 하였다.

![redis pubsub architecture](/assets/images/2025-04-17-spring-data-redis-pubsub/redis-pubsub-architecture.png)

## Spring Data Redis 로 Redis Pubsub 구현하기

[spring-data-redis - pub/sub](https://docs.spring.io/spring-data/redis/reference/redis/pubsub.html)

다음은 spring-data-redis 를 이용한 pub/sub 코드이다. pub/sub 을 위한 channel 명을 동일하게 설정해줘야 한다.

### Publisher

```java
@RequiredArgsConstructor
@Component
public class RedisPublisher {

  private static final String EVICT_CACHE_OF_SOMETHING = "evict-cache-of-something";

  private final StringRedisTemplate redisTemplate;

  public void publishEvictCacheOfSomething(int id) {
    redisTemplate.convertAndSend(EVICT_CACHE_OF_SOMETHING, String.format("{ \"id\": %d }", id));
  }
}
```

### Subscriber

#### RedisConfig.java

```java
@Bean
public MessageListenerAdapter messageListenerAdapter(RedisSubscriber redisSubscriber) {
    return new MessageListenerAdapter(redisSubscriber, "onMessage");
}

@Bean
public RedisMessageListenerContainer redisMessageListenerContainer(RedisConnectionFactory connectionFactory, MessageListenerAdapter listener) {
    RedisMessageListenerContainer container = new RedisMessageListenerContainer();
    container.setConnectionFactory(connectionFactory);
    container.addMessageListener(listener, PatternTopic.of("*"));
    return container;
}
```

공식 Document 에서는 Pattern 을 사용할 수도 있다고만 언급되어있는데, Pattern을 사용하려면 ChannelTopic이 아닌 PatternTopic 을 사용해야 한다. Document 에는 PatternTopic에 대한 언급이 없다. pattern 방식이 동작하지 않아 코드를 직접 확인해보고 알게되었다.

여기서는 모든 channel 의 데이터를 한 곳에서 받을 수 있도록 `*` 로 처리하였다.

#### RedisSubscriber.java

```java
@Component
public class RedisSubscriber implements MessageListener {

  private static final String EVICT_CACHE_PRODUCT_INFO = "evict-cache-product-info";
  private static final String EVICT_ALL_CACHE_PRODUCT_INFO = "evict-all-cache-product-info";

  @Override
  public void onMessage(Message message, byte[] bytes) {
    String channel = new String(message.getChannel());
    switch (channel) {
      case EVICT_CACHE_OF_SOMETHING:
        evictCacheOfSomeThing(new String(message.getBody()));
        break;
        // ...
      default:
        log.warn("Unknown channel: " + channel);
        break;
    }
  }

  public void evictCacheOfSomeThing(String message) {
    // evict cache
  }
}
```

## 마무리

말로만 들어왔던 Redis Pub/Sub 을 이용하여 직접 사용 사례를 구현해보았다. 들어왔던 대로 간단하게 설정 가능해서 필요할 경우에 빠르게 도입할 수 있겠다 생각이 들었다. 물론 장점만 있지는 않고 단점도 존재한다. 상황에 따라서 적절한 도구를 선택하여 활용하면 다양한 시스템 요구사항에 효과적으로 대응할 수 있을 것이다.

## 기타

- [RabbitMQ 와 Kafka 비교](https://jonghoonpark.com/2025/02/22/kafka-in-spring#rabbitmq-%EC%99%80-kafka-%EB%B9%84%EA%B5%90)
