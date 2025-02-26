---
layout: "post"
title: "Java constructor access modifier - reflection 이용하여 우회하기"
description: "Java의 default access modifier로 인해 OauthService 객체 생성 시 발생하는 접근 오류를 해\
  결하기 위해 reflection을 이용한 우회 방법을 설명합니다. 기본적으로 public 접근 제어자를 추가하는 대신, getDeclaredConstructor와\
  \ setAccessible 메서드를 활용하여 private 생성자에 접근하고 인스턴스를 생성하는 방법을 다룹니다."
categories:
- "개발"
tags:
- "java"
- "자바"
- "접근 제어자"
- "access modifier"
- "private"
- "public"
- "protected"
- "default"
date: "2024-02-19 13:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-02-19-reflect-default-access-modifier.jpg"
---

![thumbnail](/assets/images/2024-02-19-reflect-default-access-modifier/thumbnail.png)

간단하긴 하지만 기록을 위해 남겨둔다.

오늘 테스트를 구성하기위해 다음과 같이 서비스 객체를 생성해야 했다.

```java
OauthService oauthService = new OauthService(environment);
```

간단한 코드였지만 다음과 같은 에러가 발생되었다.

```
'OauthService(org.springframework.core.env.Environment)' is not public in 'com.example.service.oauth.OauthService'. Cannot be accessed from outside package
```

이유는 default access modifier로 작성되어 있었기 때문이다. OauthService 대략적인 코드는 다음과 같다.

```java
public class OauthService {
  private final String SECRET;

  OauthService(Environment environment) {
    SECRET = environment.getRequiredProperty("secret");
  }

  // ...
}
```

default access modifier는 같은 패키지가 아니라면 접근하지 못하도록 한다.

public을 추가해준다면 쉽게 해결할 수 있는 문제이긴 하나 기본적으로 테스트를 작성할때는 원본코드를 크게 건드리지 않으려 하는 편이기 때문에 reflect를 써서 다름과 같이 우회하였다.

```java
Class<?> clazz = OauthService.class;
Constructor<?> constructor = clazz.getDeclaredConstructor(Environment.class);
constructor.setAccessible(true);

OauthService oauthService = (OauthService) constructor.newInstance(environment);
```

getDeclaredConstructor 에서 어떤 Constructor를 사용할지를 정하게 된다. 이후 newInstance를 통해 변수를 전달해주면 된다.
