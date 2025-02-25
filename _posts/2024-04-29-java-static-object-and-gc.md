---
layout: post
title: "[Java] Static Object는 GC 의 대상일까?"
description: Java 8부터 Static Object는 permanent generation(permgen)에서 Java Heap으로 이동하였고, 이로 인해 GC(garbage collector)의 대상이 될 수 있다. Static Object가 GC의 대상이 되는 경우는 참조가 없는 경우와 해당 Static Object를 포함하는 클래스 로더가 언로드된 경우로, 일반적으로 클래스 로더는 JVM 종료 시까지 살아있어 Static Object는 GC에 의해 정리되지 않는다. 따라서 Static Object가 GC에 의해 정리될 가능성은 낮지만, 메모리 누수를 방지하기 위해 주의가 필요하다.
categories: [스터디-자바, 개발]
tags:
  [
    자바,
    java,
    permgem,
    metaspace,
    static,
    jeps122,
    GC,
    garbage collector,
    heap,
    class loader,
  ]
date: 2024-04-29 11:50:00 +0900
toc: true
---

## 개요

Static Object의 경우에는 GC(garbage collector) 에 포함되지 않는다는 글이 인터넷 상에 많이 돌아다닌다. 그리고 permanent generation (permgen) 에 대한 언급이 함께 된다.

하지만 java 8 부터 permanent generation (permgen) 이라는 공간이 사라졌다. 그리고 Static Object는 Java Heap 으로 옮겨졌다.

그러면 java 8 부터는 어떻게 되었다는 걸까? 이에 대해 알아보았다.

## 본문

### permanent generation (permgen) 은 왜 사라졌을까?

우선 위 내용에 대해서 이야기 해보려 한다.

> Perm 영역은 보통 Class의 Meta 정보나 Method의 Meta 정보, Static 변수와 상수 정보들이 저장되는 공간으로 흔히 메타데이터 저장 영역이라고도 한다.

permgen 은 고정된 메모리 공간이다. 따라서 java 7 까지는 이 공간에 많은 데이터가 들어오게 되면 다음과 같은 에러가 발생되었다.

```
java.lang.OutOfMemoryError: PermGen space
```

java 8 부터는 이러한 에러를 막고자 permgen을 제거하였다.

그리고 클래스와 메소드의 메타 정보는 Native 영역의 Metaspace 영역으로 이동하였고, Static Object는 Java Heap 영역으로 이동하였다.

### Static Object는 Java Heap 영역으로 이동되었다.

그런데 여기서 조금 더 생각해 볼 부분은 Java Heap 에 있는 객체들은 GC의 영향을 받게 된다는 것이다.

그러면 다음과 같이 생각해 볼 수 있는걸까?

1. Static Object는 Java Heap 영역으로 옮겨졌다.
2. Java Heap은 GC의 대상이다.
3. 따라서, Static Object는 GC의 대상이다?

이에 대해 맞는지 확인해보았다.

### Static Object 가 GC 의 대상이 되는 경우

찾아보니 다음과 같은 경우에 Static Object 가 GC 의 대상이 된다고 한다.

- 참조가 없는 경우: 더 이상 어떤 객체도 Static Object를 참조하지 않는 경우
  - 의도적으로 참조변수에 null 을 대입한 경우이다.
- **클래스 로더가 언로드된 경우**: 해당 Static Object를 포함하는 클래스 로더가 더 이상 사용되지 않는 경우

1번의 경우에는 이해가 된다. 더 이상 사용할 수 없는거니깐. 그런데 2번의 경우가 알기 어려운 부분이다.

### 클래스 로더

일반적으로 개발자가 직접 클래스 로더와 클래스 로딩과 언로딩 에 대해서 신경쓰지 않아도 된다. 하지만 계속 알아보았다.

클래스 로더는 Java Runtime Environment의 일부이다. JVM이 클래스를 요청하면 클래스 로더는 클래스를 찾고 정규화된 클래스 이름을 사용하여 클래스 정의를 런타임에 로드한다.

#### 클래스 로더의 종류

클래스 로더는 다음과 같은 종류가 있다.

- **내장 클래스 로더 (Built-in Class Loader)**
  - **부트스트랩 클래스 로더 (Bootstrap Class Loader)** : JDK 내부 클래스를 로드
  - **확장 클래스 로더 (Extension Class Loader)** : JDK 확장 디렉토리를 로드
  - **어플리케이션 클래스 로더 (Application Class Loader)** : 애플리케이션 레벨 클래스를 로드
- **커스텀 클래스 로더 (Custom ClassLoader)** : 사용자 구현 클래스 로더

#### 클래스 로더가 언로드 되는 경우

내장 클래스 로더의 경우에는 일반적으로 jvm이 종료될 때 까지 살아있는다. 따라서 일반적인 경우에는 언로드 되지 않는다.

\* 커스텀 클래스 로더의 경우 사용자 구현에 따라 클래스 로더가 언로드 될 수 있긴 하다고 한다. (하지만 일반적인 경우는 아니다.)

## 정리

클래스 로더는 불러온 모든 Class Object를 참조하고 있는다. (Every Class object contains a reference to the ClassLoader that defined it.) 따라서 Class Object 의 Static Object 가 GC 에 의해 정리되지 않게 된다.

정리하자면 이론상으로 Static Object 는 GC에 의해서 처리 대상이 될 수 있지만, 현실적으로는 일부러 의도 하지 않는 이상 거의 힘들다고 할 수 있다.

따라서 Static Object가 GC에 의해 정리될지 걱정하지는 않아도 되겠다.

다만 GC에 의해 정리되지 않으므로 메모리 누수가 발생되지 않도록 주의해야 하겠다.

## 참고

- [JEP 122: Remove the Permanent Generation](https://openjdk.org/jeps/122)
- [JDK 8에서 Perm 영역은 왜 삭제됐을까](https://johngrib.github.io/wiki/java8-why-permgen-removed/#fnref:compare)
- [Are static fields open for garbage collection?](https://stackoverflow.com/questions/453023/are-static-fields-open-for-garbage-collection)
- [Class Loaders in Java](https://www.baeldung.com/java-classloaders)
- [ClassLoader - oracle docs](https://docs.oracle.com/javase/8/docs/api/java/lang/ClassLoader.html)

### 추가 정보

위의 클래스 로더의 분류는 java 8 기준이다.

java9 에서 [Jigsaw 프로젝트](https://openjdk.org/projects/jigsaw/)를 통한 모듈 시스템이 적용되면서 세부사항이 변경되었다.
클래스 로더 이름도 Extension Class Loader 는 Platform ClassLoader로, Application Class Loader은 System ClassLoader로 바뀌었다.
동작 방식은 거의 같다. 궁금하면 아래의 참조 링크를 보자.

- [[Java] JVM 클래스 로더 - java9 변경사항 포함](https://jerry92k.tistory.com/64)
