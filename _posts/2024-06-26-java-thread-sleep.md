---
layout: "post"
title: "[Java] Thread 클래스의 sleep() 은 어떤 Thread를 sleep 시키는가"
description: "Java의 Thread 클래스에서 sleep() 메소드는 현재 스레드를 일시정지시키는 static 메소드로, 특정 스레드를\
  \ 일시정지하려면 클래스를 통해 호출해야 합니다. 예를 들어, `th1.sleep(2000)`은 main 스레드를 일시정지시켜 `main end`가\
  \ 가장 마지막에 출력됩니다. 특정 스레드를 외부에서 일시정지하려면 공유 객체와 락을 사용해야 하며, deadlock에 주의해야 합니다."
categories:
- "스터디-자바"
- "개발"
tags:
- "java"
- "자바"
- "thread"
- "runnable"
- "sleep"
date: "2024-06-26 04:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-06-26-java-thread-sleep.jpg"
---

금주 스터디의 발표를 준비하면서 재밌는 부분을 발견하여서 정리해본다.

Java의 [Thread](https://docs.oracle.com/javase/8/docs/api/java/lang/Thread.html) 에는 sleep()이라는 메소드가 있다.

![sleep-method-in-thread-docs](/assets/images/2024-06-26-java-thread-sleep/sleep-method-in-thread-docs.png)

메소드 이름에서도 유추할 수 있듯 입력 값 만큼 스레드를 정지(sleep) 하는 메소드이다.

기존까지에는 거기까지 생각하고 있었다.

## Thread 클래스의 sleep() 은 어떤 Thread를 sleep 시키는가

만약 아래와 같은 코드가 있다고 해보자.

```java

Thread th1 = new Thread(() -> {
    // th1의 작업 내용
    System.out.println("th1 end");
});

Thread th2 = new Thread(() -> {
    // th2의 작업 내용
    System.out.println("th2 end");
});

th1.start();
th2.start();
try {
    th1.sleep(2000);
} catch (InterruptedException e) {
    // ...
}

System.out.println("main end");
```

이 코드를 동작시켰을 때 어떤 출력문이 가장 먼저 출력이 될까?

실행할 때의 상황에 따라 조금씩 차이는 있겠지만
일반적으로 생각하기에는 `main end -> th2 end -> th1 end` 일 것이라고 생각을 할 것 같다. (적어도 나는 그랬다. th1이 가장 마지막에 호출될 것이라고 기대했다.)
하지만 실제로 실행시켜 보면 `th1 end -> th2 end -> main end` 순으로 출력이 된다. (main end 가 마지막에 있다는 것이 포인트이다.)

이러한 결과가 나온 이유는 sleep이 **static 메소드** 이기 때문이다.

sleep은 현재의 thread를 일시정지 해주는 기능을 수행한다. 따라서 `th1.sleep(2000)` 는 th1 쓰레드가 아닌 main 쓰레드를 일시정지 한다. 따라서 `main end` 가 가장 마지막에 호출이 된다.

`th1.sleep(2000)` 은 `Thread.sleep(2000)` 과 동일하게 동작한다.

sleep 메소드를 호출할 때에는 변수를 통해서 메소드를 호출하는 것이 아닌 클래스를 통해서 호출하는 방식으로 작성해주는것이 좋다. 실제로 intellij 에서는 warning 을 띄워주고 있다.
![warning-in-intellij](/assets/images/2024-06-26-java-thread-sleep/warning-in-intellij.png)

## 번외

### 특정 스레드를 외부에서 sleep 처리하기

그러면 만약 진짜로 th1을 일시정지 해주고 싶었다면 어떻게 처리할 수 있을까? 가능은 할까?

우선 찾아본 결과 이는 자바에서 기본적으로 제공을 해주지는 않는다.

공유 객체와 락을 적절히 사용하면 처리할 수 있다. deadlock에 유의하여야 한다.

### sleep 코드 구현 살펴보기

```java
public static void sleep(long millis) throws InterruptedException {
    if (millis < 0) {
        throw new IllegalArgumentException("timeout value is negative");
    }

    long nanos = MILLISECONDS.toNanos(millis);
    ThreadSleepEvent event = beforeSleep(nanos);
    try {
        if (currentThread() instanceof VirtualThread vthread) {
            vthread.sleepNanos(nanos);
        } else {
            sleep0(nanos);
        }
    } finally {
        afterSleep(event);
    }
}
```
