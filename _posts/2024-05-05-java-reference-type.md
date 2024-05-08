---
layout: post
title: "[Java] 네가지 참조유형 (Hard, Soft, Weak, Panthom)"
categories: [스터디-자바, 개발]
tags:
  [
    java,
    자바,
    reference,
    참조,
    hard,
    string,
    soft,
    weak,
    panthom,
    reference queue,
  ]
date: 2024-05-05 01:00:00 +0900
toc: true
---

## 개요

요즘 자바 메모리 관련 자료들을 보고 있으면 Weak Reference 에 대한 언급이 자주 되었다. 그래서 관련된 내용들을 찾아보고 정리해보기로 하였다.
Weak Reference 의 경우 따로 그 동작 원리에 대해서 깊게 알아볼 예정이다.

## 본문

GC가 실제로 언제 객체를 회수할지는 GC 알고리즘에 따라 모두 다르므로, GC가 수행될 때마다 반드시 메모리까지 회수된다고 보장하지는 않는다.

### Hard Reference (Strong Reference)

Java로 프로그래밍할 때 일반적으로 사용된다. 대부분의 경우 사용되며, 적합하다. 자바에서는 일반적으로 가비지 컬렉터가 언제 언제 객체를 수집할지에 대해서 고려하지 않아도 된다.

선언한 변수는 직접적으로 null 로 참조를 무효화 하기 전까지는 가비지 컬렉터에 수집되지 않는다.

### Soft Reference

[oracle docs - soft reference](https://docs.oracle.com/javase/8/docs/api/java/lang/ref/SoftReference.html)

유용하지만 필수는 아닌 객체에 사용된다.

Soft Reference 를 사용한 경우 추가 메모리가 필요할 때까지 계속 존재한다.
JVM이 추가 메모리가 필요할 경우(OutOfMemoryError를 발생시켜야 하는 상황이 왔을 때)에 객체에 대한 참조를 지워 공간을 확보한다.
아래서 설명할 Weak Reference 객체보다는 일반적으로 수명이 더 길다.

따라서 가능한 한 오랫동안 객체를 메모리에 보관해야 하는 경우에 적합한 선택이라고 하며 메모리에 민감한 캐시를 구현하는 데 사용된다고 한다.

실제 코드는 다음과 같다.

```java
SoftReference<List<String>> listReference = new SoftReference<List<String>>(new ArrayList<String>());
List<String> list = listReference.get();
if (list == null) {
    // object was already cleared
}
listReference.clear();
```

get과 clear 메소드가 있다. get을 통해 객체를 가져왔을 때 정상적으로 객체가 반환되었는지 확인해야 한다.

clear를 하면 객체가 정리된다. (더 이상 get을 통해서 가져오지 못한다.)

enqueue 라는 메소드도 있는데 객체를 정리하면서 동시에 queue 에 추가한다.(Clears this reference object and adds it to the queue with which it is registered)

### enqueue

여기서 자바 공식 문서에서 이야기 하는 queue 가 뭘 의미하는것인지 한참 고민해야 했다.

이에 대한 답을 찾다보니 네이버 D2 블로그를 발견하여서 내용을 가져와 본다.

> SoftReference 객체나 WeakReference 객체가 참조하는 객체가 GC 대상이 되면 SoftReference 객체, WeakReference 객체 내의 참조는 null로 설정되고 SoftReference 객체, WeakReference 객체 자체는 ReferenceQueue에 enqueue된다. ReferenceQueue에 enqueue하는 작업은 GC에 의해 자동으로 수행된다. ReferenceQueue의 poll() 메서드나 remove() 메서드를 이용해 ReferenceQueue에 이들 reference object가 enqueue되었는지 확인하면 softly reachable 객체나 weakly reachable 객체가 GC되었는지를 파악할 수 있고, 이에 따라 관련된 리소스나 객체에 대한 후처리 작업을 할 수 있다. 어떤 객체가 더 이상 필요 없게 되었을 때 관련된 후처리를 해야 하는 애플리케이션에서 이 ReferenceQueue를 유용하게 사용할 수 있다.

공식문서에서 이야기 하는 queue 는 ReferenceQueue 임을 확인할 수 있었다.

사용하고 싶다면 아래와 같이 코드를 작성하면 된다.

```java
ReferenceQueue<List<String>> queue = new ReferenceQueue<>();
SoftReference<List<String>> listReference = new SoftReference<List<String>>(new ArrayList<String>(), queue);
```

만약 Reference Queue 를 별도로 설정하지 않는다면 내부적으로 Null 이라는 이름의 ReferenceQueue 를 기본값으로 사용하여 enqueue 의 결과를 항상 false를 반환하도록 처리되어 있다.

```java
private static class Null extends ReferenceQueue<Object> {
    public Null() { super(0); }

    @Override
    boolean enqueue(Reference<?> r) {
        return false;
    }
}
```

### Weak Reference

[oracle docs - weak reference](https://docs.oracle.com/javase/8/docs/api/java/lang/ref/WeakReference.html)

Soft Reference 와 비슷하지만 연결 강도가 더 약하다.

다음번 가비지 컬렉션이 진행될 때까지만 살아있는다.
가비지 컬렉션이 진행되면 메모리가 넉넉하더라도 모두 회수된다.

### Panthom Reference

[oracle docs - phantom reference](https://docs.oracle.com/javase/8/docs/api/java/lang/ref/PhantomReference.html)

PhatomReference는 항상 ReferenceQueue를 필요로 한다.

파이널라이즈(finalize) 이후에도 자동으로 메모리가 회수되지 않는다. 파이널라이즈 이후 작업을 애플리케이션이 수행하게 하고 메모리 회수는 지연시킨다.

객체에 대한 참조를 GC가 자동으로 null로 설정하지 않으므로, 후처리 작업 후에 사용자 코드에서 명시적으로 clear() 메서드를 실행하여 null로 설정해야 메모리 회수가 진행된다.

메모리 회수 전 반드시 정리해야 할 리소스가 있다면 사용할 수 있겠지만, 거의 사용되지 않는다고 한다.

### GC의 처리 순서

GC가 객체를 처리하는 순서는 항상 다음과 같다.

- soft references
- weak references
- 파이널라이즈
- phantom references
- 메모리 회수

\* finalize 메서드를 구현한 객체는 별도의 대기열에 등록된다. (내용을 찾아보다보니 finalize 메서드는 jdk 9 부터 deprecated 되었고, jdk 18 부터 완전히 제거된 모양이다. 관련해서는 [jeps-421](https://openjdk.org/jeps/421) 를 통해 확인할 수 있다.)

## 마무리

이 글을 통해서는 대략적인 reference type 들에 대한 대략적인 개념들에 대해서 알아 봤다.
다음 글에서는 Weak Reference를 이용한 WeakHashMap 에 대해서 알아보고자 한다.

### 참고

- JVM 밑바닥까지 파헤치기
- [Java Reference와 GC](https://d2.naver.com/helloworld/329631)
