---
layout: "post"
title: "[Java] 다 쓴 객체 참조를 해제하라."
description: "Java에서 메모리 누수를 방지하기 위해 다 쓴 객체 참조를 해제하는 방법을 설명합니다. 스택 구현 예시를 통해 pop 메\
  서드에서 요소를 제거할 때 null 처리를 하지 않으면 메모리 누수가 발생할 수 있음을 보여줍니다. 참조를 직접 null 처리하는 것은 예외적인\
  \ 경우에만 필요하며, 일반적으로는 변수의 유효 범위를 벗어나게 하여 참조를 해제하는 것이 바람직합니다. 가비지 컬렉터가 비활성 영역의 데이터를\
  \ 인식하지 못하므로, 프로그래머가 직접 관리해야 할 필요가 있습니다."
categories:
- "스터디-자바"
tags:
- "자바"
- "java"
- "call by value"
- "reference"
- "pointer"
- "java 21"
date: "2024-04-07 05:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-04-07-eliminate-obsolete-object-references.jpg"
---

## 개요

지난 K-DEVCON 대전 스터디에서 한 회원분께서 이펙티브 자바 내용을 읽고 공유를 해주셨었다.

그 중 논란(??)이 있었던 부분에 대해서 이야기 해보려고 한다.

정리 해주셨던 부분중 해당 부분만 가져와보면

> 단 가비지컬렉션으로 참조가 해제되지 않을 수 있는 예외적인 경우가 있는데
>
> 1. 배열, 리스트, set, map 과 같은 개발자가 메모리를 직접 관리할 수 있는 경우.

이런 설명이 있었는데 이 부분이 다소 모호했던 부분이 있어서 무슨 내용이였는지 책을 통해서 확인을 해보았다. 그리고 책에 있는 예시와 함께 보니 내용이 이해가 되었다.

## 본문

책에는 다음과 같은 예시가 있다. (아래 코드는 메모리 누수가 발생된다.)

```java
public class Stack {
    private Object[] elements;
    private int size = 0;
    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    public Stack() {
        elements = new Object[DEFAULT_INITIAL_CAPACITY];
    }

    public void push(Object e) {
        ensureCapacity();
        elements[size++] = e;
    }

    public Object pop() {
        if (size == 0)
            throw new EmptyStackException();
        return elements[--size];
    }

    /**
      * Ensure space for at least one more element, roughly
      * doubling the capacity each time the array needs to grow.
      */
    private void ensureCapacity() {
      if (elements.length == size)
          elements = Arrays.copyOf(elements, 2 * size + 1);
    }
}
```

이 코드에서 메모리 누수가 어디서 발생될 수 있을까?

이 코드에서는 스택에서 pop시에 size 값을 변경하도록 처리하고 실제로 elements 에서 값을 제거하지는 않는다. 이로 인해 다시 사용하지 않는 element에 대한 참조를 계속 가지고 있게 된다.

따라서 이런 경우에는 해당 참조를 다 썼을 때 null 처리 (참조 해제)처리도 해줘야 한다.

다음과 같이 pop 함수를 수정하면 메모리 누수가 없는 Stack이 된다.

```java
public Object pop() {
    if (size == 0)
        throw new EmptyStackException();
    Object result = elements[--size];
    elements[size] = null; // Eliminate obsolete reference
    return result;
}
```

> obsolete : 더 이상 쓸모가 없는

그러면 모든 상황에서 null 처리를 해줘야 할까? 그것은 아니다. 프로그램을 필요 이상으로 지저분하게 만든다. 다 쓴 참조를 해제하는 가장 좋은 방법은 그 참조를 담은 변수를 유효 범위 (scope) 밖으로 밀어내는 것이다.

객체 참조를 직접적으로 null 처리하는 일은 예외적인 경우여야 한다.

이 예제에서는 Stack 클래스가 자기 메모리를 직접 관리하였기 때문이다. elements 배열의 비활성 영역(size 보다 큰 영역)에 데이터가 남아있을 수 있지만 가비지 컬렉터는 이 사실을 알 수 없다. 데이터가 여전히 참조되고 있기 때문이다. 따라서 프로그래머가 더 이상 사용되지 않을 경우 직접 null 처리해서 해당 객체를 더는 쓰지 않는다는 것을 알려줘야 한다.

책에서 나온 캐시, 리스터, 콜백의 경우도 마찬가지다. 사용이 완료되었으면 해제 해줘야한다.
