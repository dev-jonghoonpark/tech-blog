---
layout: "post"
title: "Spring - 테스트 객체 준비 JSON으로 하기 (객체 초기화 부분 줄이기)"
description: "Spring 테스트 객체를 JSON으로 준비하는 방법을 소개합니다. 이 접근법은 객체 초기화 코드의 양을 줄여 테스트 가독\
  성을 향상시키고, JSON 파일을 통해 다른 개발자들과의 접근성을 높입니다. 유틸 클래스를 통해 JSON 파일을 읽고, Jackson 라이브러리\
  를 이용해 JSON 문자열을 객체로 변환하는 메소드를 구현하였으며, 중복 데이터 문제를 해결하기 위한 추가 메소드도 작성했습니다. 이로 인해 테\
  스트 코드의 불필요한 부분을 줄이고 본질에 집중할 수 있는 환경을 마련했습니다."
categories:
- "개발"
tags:
- "Spring"
- "Java"
- "json"
- "jackson"
- "스프링"
- "테스트"
- "unit test"
date: "2023-09-14 02:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-09-14-Spring-테스트-객체-준비-JSON으로-하기.jpg"
---

# 개요

![testing](/assets/images/2023-09-14-Spring-테스트-객체-준비-JSON으로-하기/image1.png)  
Image by mamewmy on Freepik

최근에 회사 신규 프로젝트의 BE 팀에서 테스트 코드를 작성하기 시작했다.

그래서 코드 리뷰할 때 나도 리뷰어로 넣어줄 수 있냐고 부탁드렸고, 허락해주셔서 코드를 구경하고 있다.

코드를 처음 봤을 때 아쉬웠던 점은 자바라는 언어가 장황한 편이라고는 하지만
객체를 초기화 하는데 너무 많은 코드가 사용되었고 (한 서비스 클래스를 테스트하는데 라인이 1000 줄이 넘어갔다. 줄이 길다고 꼭 나쁜건 아니겠지만 불필요한 부분이 많아보였다.), 이로 인해서 본질인 테스트의 가독성이 떨어진게 아닌가 라는 생각이 들었다. 어디서부터 봐야할지 다소 막막하였다.

일단 그래서 그 부분을 개선할 수 있는 방법이 없을까 싶어 찾아보던중에 아래의 글을 발견하였다.
**[# 테스트 코드 작성에 대한 나름의 고찰](https://cheese10yun.github.io/spring-about-test/)**
이 글을 작성하신 분은 최근에 [실무에서 적용하는 테스트 코드 작성 방법과 노하우](https://www.youtube.com/watch?v=XSkz0kO7J3w) 이라는 발표도 진행하셨던 분인데, 최근에 이 영상도 감사하게도 잘 보았다.

이 글에서 집중해서 본 파트는 **JSON 기반으로 테스트** 이라는 파트였다.

나도 E2E 테스트 코드를 할 때, 초기화 하는 부분이 테스트의 본질을 방해한다고 생각되어서 따로 json파일로 분리했었던 경험이 있기 때문에 좋은 방법이라고 생각이 들었다.
JSON 이라는 유형은 다른 개발자분들도 익숙한 형태이기 때문에 접근성 면에서도 좋다고 생각하였다.

# 유틸 클래스 만들기

이를 달성하기 위해서 유틸 클래스는 만들어 나갔다.

## 과정 1 : readJson 메소드 구현

먼저 블로그에 소개되어있는 json 파일을 읽어와서 string으로 변환해주는 readJSON 메소드를 만들었다. json 파일은 `/src/test/resources/`에 저장하였다.

```java
public static String readJSON(String filePath) throws IOException {
    ClassLoader classLoader = JsonUtil.class.getClassLoader();
    byte[] bytes = Files.readAllBytes(Path.of(Objects.requireNonNull(classLoader.getResource(filePath)).getPath()));
    return new String(bytes);
}
```

## 과정 2 : JSON String 을 객체로 파싱하기

그 이후에 Spring에서 기본적으로 제공되는 Jackson 라이브러리를 이용하여 JSON String을 특정 객체로 parse 해주는 메소드를 만들었다.

```java
public static <T> T readJSON(String filePath, Class<T> userClass) throws IOException {
    ClassLoader classLoader = JsonUtil.class.getClassLoader();
    return objectMapper.readValue(new File(Objects.requireNonNull(classLoader.getResource(filePath)).getFile()), userClass);
}
```

이를 통해서 매우 많은 코드 라인수를 줄일 수 있었다.

윗 부분이 json을 통한 초기화를 적용하기 전, 아랫 부분이 json을 통한 초기화를 적용한 후이다.
![코드 적용 예시](/assets/images/2023-09-14-Spring-테스트-객체-준비-JSON으로-하기/image2.png)

space에 대한 내용을 보고 싶으면 `/src/test/resources/` 에서 해당 json을 찾아보면 된다.

다만 이 과정에서 아래와 같은 에러가 나왔다.

```bash
Java 8 date/time type `java.time.LocalDateTime` not supported by default: add Module "com.fasterxml.jackson.datatype:jackson-datatype-jsr310"
```

에러 그대로 LocalDateTime을 사용하기 위해서는 모듈을 추가해 달라는 것인데
`build.gradle`에 `testImplementation "com.fasterxml.jackson.datatype:jackson-datatype-jsr310"`를 추가해주고 ObjectMapper 를 아래와 같이 수정해주면 해결된다.

```java
private static final ObjectMapper objectMapper = JsonMapper.builder()
        .addModule(new JavaTimeModule())
        .build();
```

## 과정3. 중복에 대한 고려하기

json으로 객체 정보를 관리하면 중복된 데이터가 발생될 수 있다.

예를 들어 자유게시판 에서도 작성된 user에 대한 데이터를 가지고 있을 수 있고
공지사항에서도 작성된 user에 대한 데이터를 가지고 있을 수 있다.

그러면 이러한 상황에서 article.json 에서도 user의 데이터를 직접 명시하고, notice.json 에서도 user의 데이터를 직접 명시해야 할까?
그렇게 된다면 user의 데이터가 수정되었을 때 너무 많은 곳에 영향을 미칠것 같다는 생각이 들었다.

그래서 아래와 같은 메소드를 추가로 작성하였다.

```java
public static <T> T readJSON(String filePath, Class<T> userClass, Pair<String, Object> setter) throws IOException {
    JsonNode jsonNode = objectMapper.readTree(readJSON(filePath));
    ObjectNode objectNode = (ObjectNode) jsonNode;
    objectNode.set(setter.getFirst(), objectMapper.valueToTree(setter.getSecond()));
    return objectMapper.treeToValue(objectNode, userClass);
}

public static <T> T readJSON(String filePath, Class<T> userClass, List<Pair<String, Object>> setterList) throws IOException {
    JsonNode jsonNode = objectMapper.readTree(readJSON(filePath));
    ObjectNode objectNode = (ObjectNode) jsonNode;
    for(var pair : setterList) {
        objectNode.set(pair.getFirst(), objectMapper.valueToTree(pair.getSecond()));
    }
    return objectMapper.treeToValue(objectNode, userClass);
}
```

이렇게 메소드를 추가하면 아래와 같은 형태로 사용이 가능해진다.

```java
user = JsonUtil.readJSON("user.json", User.class);
article = JsonUtil.readJSON("article.json", Article.class, Pair.of("user", user));
notice = JsonUtil.readJSON("notice.json", Branch.class, Pair.of("user", user));
```

json 파일을 바로 최종 객체로 parse 하는 것이 아니라 objectNode로 만든 뒤, 원하는 객체를 연결한 후 이후 최종객체로 parse 하도록 처리했다.

다만 여기서 주의해야 할 점은 article의 user 객체가 기본 user 객체와는 달라지게 된다는 것이다.
따라서 assert 할 때 어떤 user 객체를 가리키고 있는 것인지 주의해서 사용해야 한다.
user와 article.user와 notice.user 는 값은 서로 같을 수 있지만, 서로 다른 객체를 reference 하고 있다.

setter를 사용하지 않고 중간 객체를 거친 이유는 원본 코드에서 setter를 사용하지 않기 때문이였다.
테스트 코드를 작성하기 위해 원본 코드를 수정하는 것은 최대한 지양하고 싶었다.

# 마무리

일단은 이렇게 해서 불필요한 코드의 수를 줄이고 테스트 본연에 더 집중할 수 있지 않을까 기대하고 있다.

이 방법이 최선이라고 생각 하지는 않는다. 더 좋은 방식이 있을 것이다.
테스트는 개선해야할 부분에 대한 피드백을 줄 것이고, 그에 따라 코드를 개선해나가봐야겠다.
테스트 코드 작성에 대해 더 많이 공부해야겠다.
