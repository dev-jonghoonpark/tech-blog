---
layout: post
title: "[Java] call by value"
categories: [스터디-자바]
tags: [자바, java, call by value, reference, pointer, java 21]
date: 2024-03-31 17:00:00 +0900
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

me 객체의 값이 바뀌지 않은 이유는 다음과 같다.

![state 1](/assets/images/2024-04-02-java-call-by-value/state1.png)
![state 2](/assets/images/2024-04-02-java-call-by-value/state2.png)
![state 3](/assets/images/2024-04-02-java-call-by-value/state3.png)

만약 아래와 같이 작성했다면 우리가 기대한대로 데이터가 변경이 될 것이다.

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

- [https://en.wikipedia.org/wiki/Evaluation_strategy](https://en.wikipedia.org/wiki/Evaluation_strategy)
