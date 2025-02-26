---
layout: "post"
title: "[Java] call by value"
description: "자바는 값을 복사하여 전달하는 call by value 방식을 사용하며, 객체를 전달할 때는 객체의 참조 값을 복사합니다\
  . 이로 인해 객체의 속성을 변경하려고 해도 원본 객체의 값은 변하지 않습니다. 예를 들어, `changeName` 메소드에서 새로운 객체를 생\
  성하면 원본 객체인 `me`는 영향을 받지 않지만, 객체의 속성을 직접 수정하면 값이 변경됩니다."
categories:
- "스터디-자바"
tags:
- "자바"
- "java"
- "call by value"
- "reference"
- "pointer"
- "java 21"
date: "2024-03-31 08:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-04-02-java-call-by-value.jpg"
---

## 개요

자바는 reference가 아닌 value를 복사하여 전달한다.

그럼 object의 경우에는 어떨까? object를 넘길경우 해당 object의 ref 값을 복사하여 전달한다.

다음과 같은 예시를 살펴보자.

```java
void main(String[] args) {
    Person me = new Person();
    me.name = "jonghoonpark";
    System.out.println(STR."my name: \{ me.name }");
    changeName(me, "noname");
    System.out.println(STR."my name: \{ me.name }");
}

class Person {
    String name;

    public Person() {
    }
}

public void changeName(Person person, String newName) {
    person = new Person();
    person.name = newName;
}
```

이 코드를 수행하면 어떻게 될까?

정답은 다음과 같다.

```
my name: jonghoonpark
my name: jonghoonpark
```

me 객체의 값이 바뀌지 않은 이유를 찾기위해 상태별로 구분해보면 다음과 같이 나눌 수 있다.

### 상태 1

`me` 변수에 `new Person()` 으로 생성된 객체를 할당한다.
![state 1](/assets/images/2024-04-02-java-call-by-value/state1.png)

### 상태 2

해당 object의 ref 값을 복사하여 메소드에 전달한다.
![state 2](/assets/images/2024-04-02-java-call-by-value/state2.png)

### 상태 3

처음의 `me` 를 수정하는게 아니라 `new Person()` 로 생성된 객체를 수정하게 된다.
![state 3](/assets/images/2024-04-02-java-call-by-value/state3.png)

만약 아래와 같이 작성했다면 일반적으로 기대하는대로 데이터가 변경이 될 것이다.

```java
void main(String[] args) {
    Person me = new Person();
    me.name = "jonghoonpark";
    System.out.println(STR."my name: \{ me.name }");
    changeName(me, "noname");
    System.out.println(STR."my name: \{ me.name }");
}

class Person {
    String name;

    public Person() {
    }
}

public void changeName(Person person, String newName) {
    person.name = newName;
}
```

```
my name: jonghoonpark
my name: noname
```

## 참고

- [call by value vs call by reference](https://perfectacle.github.io/2017/10/30/js-014-call-by-value-vs-call-by-reference/)
- [https://en.wikipedia.org/wiki/Evaluation_strategy](https://en.wikipedia.org/wiki/Evaluation_strategy)
