---
layout: "post"
title: "[Spring AI] Structured Output"
description: "Spring AI에서의 Structured Output 구현 방법을 소개합니다. \
  \ JSON 형식으로 데이터를 반환하는 예제를 통해 개발자에게 안정적인 데이터 형식을 제공하는 중요성을 강조합니다. `BeanOutputConverter`를\
  \ 사용하여 자동으로 원하는 형태로 값을 채워주는 과정을 설명하고, 이를 통해 API의 정상 작동을 보장할 수 있음을 설명합니다."
categories:
  - "스터디-자바"
tags:
  - "Spring"
  - "Spring AI"
  - "Structured Output"
  - "Function Calling"
  - "Agents"
  - "AI Agents"
  - "JSON"
  - "BeanOutputConverter"
date: "2025-03-17 00:00:00 +0900"
toc: true
image:
  path: "/assets/thumbnails/2025-03-17-spring-ai-structured-output.jpg"
---

# Structured Output

## Structured Output using Function Calling

[Google Agents Whitepapers](https://www.kaggle.com/whitepaper-agents) 를 보면 Function Calling 에 대해서 다음과 같이 설명하는 부분이 있다.

> With Function Calling, we can teach a model to format this output in a structured style (like JSON) that’s more convenient for another system to parse.

그와 함께 아래와 같은 예시를 보여준다.

```python
def display_cities(cities: list[str], preferences: Optional[str] = None):
    """Provides a list of cities based on the user's search query and preferences.
    Args:
        preferences (str): The user's preferences for the search, like skiing,
        beach, restaurants, bbq, etc.
        cities (list[str]): The list of cities being recommended to the user.
    Returns:
        list[str]: The list of cities being recommended to the user.
    """
    return cities
```

```python
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration

model = GenerativeModel("gemini-1.5-flash-001")

display_cities_function = FunctionDeclaration.from_func(display_cities)
tool = Tool(function_declarations=[display_cities_function])

message = "I’d like to take a ski trip with my family but I’m not sure where to go."

res = model.generate_content(message, tools=[tool])

print(f"Function Name: {res.candidates[0].content.parts[0].function_call.name}")
print(f"Function Args: {res.candidates[0].content.parts[0].function_call.args}")

> Function Name: display_cities
> Function Args: {'preferences': 'skiing', 'cities': ['Aspen', 'Vail', 'Park City']}
```

이 코드를 Spring AI 에서 구현한다면 어떨까 생각이 들어 직접 구현해보았다.

## Spring AI 에서 적용시켜보기

참고: [Structured Output](https://docs.spring.io/spring-ai/reference/api/structured-output-converter.html)

Spring AI 에서는 손쉽게 Structured Ouput 으로 변환할 수 있도록 컨버터들을 제공해주고 있다.

이 부분을 Spring AI를 기준으로 변경해본다면 다음과 같이 변경해볼 수 있을 것이다.

```java
CitiesByPreferences citiesByPreferences = ChatClient.builder(chatModel).build()
    .prompt()
    .user("I'd like to take a ski trip with my family but I'm not sure where to go.")
    .call()
    .entity(CitiesByPreferences.class);
```

```java
@JsonPropertyOrder({"preferences", "cities"})
record CitiesByPreferences(String preferences, List<String> cities) {}
```

실행시켜보면 다음과 같이 결과가 나온다.

```json
{
  "preferences": "Family-friendly ski resorts with a variety of slopes and activities.",
  "cities": [
    "Aspen", "Colorado", "Park City", "Utah", "Vail", ...
  ]
}
```

## 내부 동작

우리는 `entity()` 메소드를 통해 타겟 타입(`CitiesByPreferences.class`)만 제공해줬을 뿐인데, 자동으로 우리가 원하는 형태로 값이 채워져서 반환받았다.

그렇게 될 수 있었던 이유는 `Spring AI` 의 `BeanOutputConverter` 클래스 내부에서 타겟 타입에 대한 JSON 스키마를 만들어 prompt에 제공하기 때문이다.

그 결과, model은 structured output을 반환하고 Spring AI 에서는 나온 결과 값을 다시 object mapper 를 이용하여 객체에 매핑시킨다.

## 마무리

개발자에게는 안정된 형태의 데이터가 중요하다. 스키마가 다르면 API가 정상적으로 동작하지 않을 가능성이 높기 때문이다. 그런 의미에서 `Structured Output` 기능을 잘 사용한다면, 개발자에게 필요한 형태로 안정적으로 데이터를 추출할 수 있을 것이다.
