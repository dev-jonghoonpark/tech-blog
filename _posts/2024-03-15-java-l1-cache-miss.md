---
layout: "post"
title: "[자바 최적화] 캐시 미스 이해하기 (L1 Cache) + 코드 warm up 이해하기"
description: "자바 최적화에서 L1 캐시 미스와 코드 워밍업을 이해하는 방법을 다룹니다. L1 캐시 미스는 처리량이 많은 코드의 성능을\
  \ 저하시킬 수 있으며, 두 가지 메소드(touchEveryItem, touchEveryLine)의 실행 시간을 비교해보면 예상과 달리 큰 차이\
  가 없음을 보여줍니다. 이는 두 메소드가 동일한 캐시 읽기 횟수를 가지기 때문입니다. 또한, 코드 워밍업은 JIT 컴파일러가 관심 있는 코드를\
  \ 최적화하기 위해 반복 실행하는 과정을 의미합니다. 이를 통해 자바 애플리케이션의 성능을 향상시킬 수 있습니다."
categories:
- "스터디-자바"
tags:
- "자바"
- "하드웨어"
- "최적화"
- "CPU"
- "L1"
- "Cache"
- "Cache miss"
- "캐시"
- "캐시 미스"
- "java"
- "optimization"
- "hardware"
- "Well-Grounded Java Developer"
- "warm up"
date: "2024-03-15 14:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-03-15-java-l1-cache-miss.jpg"
---

최근에 자바 최적화를 읽고 있다.

**3장 하드웨어와 운영체제** 를 보면 L1 Cache 에 대한 부분이 나온다.
이 부분의 예시는 Well Grounded Java Developer에서도 동일하게 나오는데 더 자세하게 설명되었다고 생각해서 내용을 정리해보고자 한다.
(두 책의 저자가 같다.) (Well Grounded Java Developer 기준으로는 7.4.2 Understanding cache misses 부분이다.)

## 캐시 미스

처리량이 많은 코드에서 성능을 저하시키는 주요 요인 중 하나는 애플리케이션 코드 실행 중 발생되는 L1 캐시 miss 횟수이다.

아래 코드를 통해 알아보자.

```java
public class Caching {
    private final int ARR_SIZE = 2 * 1024 * 1024;
    private final int[] testData = new int[ARR_SIZE];

    private void touchEveryItem() {
        for (int i = 0; i < testData.length; i = i + 1) {
            testData[i] = testData[i] + 1;
        }
    }

    private void touchEveryLine() {
        for (int i = 0; i < testData.length; i = i + 16) {
            testData[i] = testData[i] + 1;
        }
    }

    private void run() {
        // Warms up the code
        for (int i = 0; i < 10_000; i = i + 1) {
            touchEveryLine();
            touchEveryItem();
        }

        System.out.println("Line     Item");
        for (int i = 0; i < 100; i = i + 1) {
            long t0 = System.nanoTime();
            touchEveryLine();
            long t1 = System.nanoTime();
            touchEveryItem();
            long t2 = System.nanoTime();
            long el1 = t1 - t0;
            long el2 = t2 - t1;
            System.out.println("Line: "+ el1 +" ns ; Item: "+ el2);
        }
    }

    public static void main(String[] args) {
        Caching c = new Caching();
        c.run();
    }
}
```

위 코드를 보았을 때 일반적으로 당연히 touchEveryItem 이 touchEveryLine 보다 훨씬 더 많은 시간이 소요될 것이라고 생각이 들 것이다.

하지만 실제로 실행을 해보면 생각외로 큰 차이는 없다.

```
Line: 487481 ns ; Item: 452421
Line: 425039 ns ; Item: 428397
Line: 415447 ns ; Item: 395332
Line: 372815 ns ; Item: 397519
Line: 366305 ns ; Item: 375376
Line: 332249 ns ; Item: 330512
...
```

![result](/assets/images/2024-03-15-java-l1-cache-miss/result.png)

### touchEvenyItem() 이 touchEveyLine() 보다 16배 더 오래걸리지 않는 이유는 무엇일까?

두 메소드가 동일한 cache read 횟수를 가지기 때문이다.

메인 메모리에서 cpu cache로 데이터를 가져올 때는 캐시 라인이라는 개념이 사용된다.
**캐시 라인** 은 캐시가 데이터를 메모리로부터 한 번에 가져오는 데이터의 단위 크기이다.
일반적으로 L1 **캐시 라인** 은 64 바이트이고, 자바에서 int는 4바이트 이다.
따라서 한 캐시 라인은 16개의 int를 가지게 된다.

데이터를 수정하는데는 얼마 걸리지 않는다.
그에 비해 메인 메모리에서 cpu cache로 데이터를 불러오는데에는 훨씬 많은 시간이 소요된다.

각 step 에서 16씩 증가하게 되면 순차적으로 읽었을 때와 cache read 트리거 시점이 같다.

- 1번째 항목에 접근할 때 : 1 ~ 16 번째 가져옴
- 17번째 항목에 접근할 때 : 17 ~ 32 번째 가져옴
- ...

그렇기 때문에 한개씩 데이터를 수정하나, 16개씩 건너뛰며 데이터를 수정하나,
같은 cache line read 횟수를 가지기 때문에 전체적인 시간에서는 큰 차이는 없는 것이다.

### 코드 wram up?

중간에 보면 `Warms up the code` 이라고 주석을 달아둔 부분이 있다.

이 부분에 대해서 자바 최적화에서는 예열시킨다는 표현으로 되어있다. 코드를 warm up 한다는게 무슨뜻일까?

이 과정에 대해서 well grounded java developer에서는 다음과 같이 설명한다.

> 정확한 결과를 얻기 위해서 우리는 코드를 warm up 해야 합니다. 이렇게 해서 JVM은 우리가 관심가지고 있는 부분을 컴파일 합니다. 이 부분은 JIT warmup 에 대해서 자세히 다룹니다.

자바는 컴파일 언어이면서 인터프리터 언어라고 이야기 한다. 일반적으로 많이 사용되지 않는 영역의 경우에는 인터프리터와 같은 형태로 동작하다가 최적화 포인트가 있을 것이다 판단되었을 경우 컴파일을 수행한다. 여기서는 실제 측정에 앞서 반복을 시켜줌으로 우리가 관심을 가지고 있는 부분을 컴파일 처리를 되도록 해준 것이다. 그리고 그것을 warm up 이라고 표현하였다.

> **JIT (Just-In-Time) 컴파일러** 는 런타임 시 바이트 코드를 원시 시스템 코드로 컴파일하여 Java™ 애플리케이션의 성능을 향상시키는 런타임 환경의 컴포넌트입니다. - [IBM 문서](https://www.ibm.com/docs/ko/sdk-java-technology/8?topic=reference-jit-compiler)
