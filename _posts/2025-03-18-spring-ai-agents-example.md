---
layout: "post"
title: "[Spring AI] AI 에이전트 구현해보기 (AI Agents)"
description:
  "Spring AI를 활용하여 AI Agents의 기능을 구현하는 방법을 다루는 이 글에서는 Google Search API와\
  \ Google Places API를 이용해 실시간 정보를 검색하고, 복잡한 작업을 수행하는 예제를 제공합니다. 코드 예시를 통해 도구를 구현하\
  고, 사용자 입력에 따라 여러 도구를 순차적으로 호출하여 최종 결과를 도출하는 과정을 설명합니다. AI Agents의 특성을 이해하고 싶다면 Google\
  \ Agents Whitepapers를 참고하는 것을 추천합니다."
categories:
  - "스터디-자바"
tags:
  - "Spring"
  - "Spring AI"
  - "AI Agents"
  - "Agents"
  - "AI 에이전트"
  - "Example"
  - "Serp"
  - "Tool"
  - "Tool Calling"
  - "Langchain"
  - "LangGraph"
  - "Google Search"
  - "Google Search API"
  - "Google Place API"
  - "Google Agents Whitepapers"
date: "2025-03-17 15:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-03-18-spring-ai-agents-example.jpg"
---

# Agents 예제 구현해보기

이번 글에서는 Spring AI를 활용하여 AI 에이전트(AI Agents)를 구현해본다.

## AI Agents

AI Agents는 언어 모델(LLM)의 한계를 넘어 다양한 작업을 수행할 수 있도록 설계된 기술이다. 주어진 도구(Tool)를 활용해 실시간 정보에 접근하고, 현실 세계의 행동을 제안하며, 복잡한 작업을 계획하고 자율적으로 실행함으로써 LLM의 기능을 확장한다.

## Agents example in Google Agents Whitepapers

구글에서 발행한 [Google Agents Whitepapers](https://www.kaggle.com/whitepaper-agents) 에는 아래와 같은 Agents 예시가 있다.

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.tools import GooglePlacesTool

os.environ["SERPAPI_API_KEY"] = "XXXXX"
os.environ["GPLACES_API_KEY"] = "XXXXX"

@tool
def search(query: str):
    """Use the SerpAPI to run a Google Search."""
    search = SerpAPIWrapper()
    return search.run(query)

@tool
def places(query: str):
    """Use the Google Places API to run a Google Places Query."""
    places = GooglePlacesTool()
    return places.run(query)

model = ChatVertexAI(model="gemini-1.5-flash-001")
tools = [search, places]

query = "Who did the Texas Longhorns play in football last week? What is the address of the other team's stadium?"

agent = create_react_agent(model, tools)
input = {"messages": [("human", query)]}

for s in agent.stream(input, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()
```

해당 문서에서 제시한 실행 결과는 다음과 같다.

```
=============================== Human Message ================================
Who did the Texas Longhorns play in football last week? What is the address
of the other team's stadium?
================================= Ai Message =================================
Tool Calls: search
Args:
query: Texas Longhorns football schedule
================================ Tool Message ================================
Name: search
{...Results: "NCAA Division I Football, Georgia, Date..."}
================================= Ai Message =================================
The Texas Longhorns played the Georgia Bulldogs last week.
Tool Calls: places
Args:
query: Georgia Bulldogs stadium
================================ Tool Message ================================
Name: places
{...Sanford Stadium Address: 100 Sanford...}
================================= Ai Message =================================
The address of the Georgia Bulldogs stadium is 100 Sanford Dr, Athens, GA
30602, USA.
```

간단한 코드이지만 AI Agent 특성대로 도구들을 이용하여 model 외부의 데이터에 접근하고 있고, 내부 추론에 통해 목표 달성까지 진행된 것을 확인해볼 수 있다.

이 코드를 Spring AI 에서 구현해보자 생각이 들어 직접 구현해보았다.

## Spring AI 에서 구현해보기

### Tool 구현

Langchain 에서는 해당 API 들(SerpAPI, Place API)을 쉽게 가져다 쓸 수 있도록 사전 구현된 Tool 을 제공해주는 것으로 보이는데, Spring AI 에는 따로 없으므로 직접 Tool을 구현해보도록 한다.

예제 코드에 있는 SerpAPI 는 비공식적으로 Google Search API를 제공해주는 곳으로 보인다. (Google 은 검색 API를 제공해주지 않는것으로 알고 있다. 그래서 외부 API를 예제에 사용한 것으로 보인다.) 무료 플랜으로도 월 100회 까지는 사용가능한 것으로 보여 예제 그대로 구현해보기 위해 가입하여 Key를 받급받았다. java 라이브러리를 제공해주므로 [안내](https://serpapi.com/integrations/java) 에 따라 추가해주었다.

```java
class SearchTools {
    @Tool(description = "Use the SerpAPI to run a Google Search.", name = "google_search")
    String run(String query) {
        System.out.println(query);
        Map<String, String> parameter = new HashMap<>();

        parameter.put("q", query);
        parameter.put("hl", "en");
        parameter.put("gl", "us");
        parameter.put("google_domain", "google.com");
        parameter.put("api_key", SERP_API_KEY);

        GoogleSearch search = new GoogleSearch(parameter);

        try {
            return search.getJson().toString();
        } catch (SerpApiSearchException ex) {
            System.out.println("Exception:");
            System.out.println(ex.toString());
        }
        return null;
    }
}
```

Google Place API 도 키를 발급받아 주었다. Place API의 경우 [공식 Docs](https://developers.google.com/maps/documentation/places/web-service/text-search?hl=en) 를 보니 따로 라이브러리는 제공하지 않는것 같고 Rest API 형태로 제공해주는것 같아 해당 방식으로 진행해보기로 했다.

```java
WebClient webClient = WebClient.builder()
        .baseUrl("https://places.googleapis.com")
        .codecs(configurer -> configurer.defaultCodecs().jackson2JsonEncoder(new Jackson2JsonEncoder()))
        .build();

class PlaceTools {
    @Tool(description = "Use the Google Places API to run a Google Places Query.", name = "place_search")
    String run(String query) {
        Mono<String> response = webClient.post()
                .uri("/v1/places:searchText")
                .headers(httpHeaders -> {
                    httpHeaders.set("Content-Type", "application/json");
                    httpHeaders.set("X-Goog-Api-Key", PLACE_API_KEY);
                    httpHeaders.set("X-Goog-FieldMask", "places.displayName,places.formattedAddress,places.priceLevel");
                })
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(new PlaceSearchParam(query))
                .retrieve()
                .bodyToMono(String.class);
        return response.block();
    }
}

record PlaceSearchParam(String textQuery) {
}
```

현재 Spring AI 에서 Tool을 처리할 때, 다음과 같은 방식을 지원하지 않는다. (참고: ([Method Tool Limitations](https://docs.spring.io/spring-ai/reference/api/tools.html#_method_tool_limitations)))

- `Optional`
- Asynchronous types (e.g. `CompletableFuture`, `Future`)
- Reactive types (e.g. `Flow`, `Mono`, `Flux`)
- Functional types (e.g. `Function`, `Supplier`, `Consumer`).

그래서 webclient를 통해 받아온 결과값을 Mono 타입 으로 반환하는게 아니라 `block`을 통해 결과 값을 반환하도록 처리하였다.

그리고 예시에서는 나오지 않았지만, 실제로 예시를 만들다보니 한가지 Tool 이 더 필요하단 것을 알게되었다.
바로 현재의 DateTime을 조회하는 Tool 이다. 이 Tool이 없다면 model은 last week 를 계산하기 위한 기준을 알 수가 없다. (지금이 언제인지 알 수 있는 기능이 없다.) 기준이 없으면 이상한 날짜를 기준으로 계산을 진행하게 된다.
다음과 같이 구현하여 사용할 수 있도록 해주었다.

```java
class DateTimeTools {
    @Tool(description = "Get the current date and time in the user's timezone")
    String getCurrentDateTime() {
        return LocalDateTime.now().atZone(LocaleContextHolder.getTimeZone().toZoneId()).toString();
    }
}
```

### ChatClient 구성하기

위의 langgraph 기반 예시 코드에서는 `create_react_agent` 라는 함수를 통해 agent를 생성한다. 이 agent 는 아래와 같은 흐름으로 동작을 한다.

문서: [langgraph - create_react_agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)

![langgraph react agent graph](/assets/images/2025-03-18-spring-ai-agents-example/langgraph_react_agent_graph.png)

![langgraph react agent flow](/assets/images/2025-03-18-spring-ai-agents-example/langgraph_react_agent_flow.png)

한 번의 사용자 input에 대해서 여러 번 Tool 을 거쳐 최종 결과를 반환한다.

Spring AI는 chatClient에 tools를 지정하여 동일한 결과를 얻을 수 있다. 다음과 같이 하나의 요청에 대해 Tool들을 사용할 수 있도록 제공해주었다.

```java
ChatResponse chatResponse = chatClient
        .prompt()
        .user(query)
        .tools(new DateTimeTools(), new new SearchTools(), new PlaceTools())
        .call()
        .chatResponse();
```

시간 확인 → 검색 → 장소 조회 순으로 진행하게 된다.

### 실행 결과

실행 결과는 다음과 같았다. 로깅에서 내용을 추출하여 보기 좋게 정리하였다.

```
=============================== Human Message ================================
Who did the Texas Longhorns play in football last week? What is the address
of the other team's stadium?
================================= Ai Message =================================
Tool Calls: getCurrentDateTime
================================ Tool Message ================================
Name: getCurrentDateTime
2025-03-19T00:21:20.874474+09:00[Asia/Seoul]
================================= Ai Message =================================
Tool Calls: search
Args:
query: Texas Longhorns football schedule March 2025
================================ Tool Message ================================
Name: search
{... at Ohio State Buckeyes Ohio Stadium, Columbus, OH ...}
================================= Ai Message =================================
The Texas Longhorns played the Ohio State Buckeyes last week.
Tool Calls: places
Args:
query: Ohio State Buckeyes stadium address
================================ Tool Message ================================
Name: places
{...411 Woody Hayes Dr, Columbus, OH 43210, USA...}
================================= Ai Message =================================
Last week, the Texas Longhorns played against the Ohio State Buckeyes.
The address of Ohio Stadium, where the Ohio State Buckeyes play, is:
**411 Woody Hayes Dr, Columbus, OH 43210**.
```

### 실제 저 경기가 있었을까?

아쉽게도 그렇지는 않았다. google search api 에서 25년 8월 30일 에 있을 경기를 반환해주었다.
8월 30일 경기가 이번 시즌 첫 경기인 것으로 보인다.
지난주에는 경기가 없다보니 관련 정보를 반환해 준 것으로 보인다.

![texas_longhorns_schedule_2025](/assets/images/2025-03-18-spring-ai-agents-example/texas_longhorns_schedule_2025.png)

agent는 해당 경기를 지난주에 있던 경기처럼 소개를 해주었다. 반환받은 결과 내에서 최선을 다 해주었지만, 아쉬움이 남는 결과였다.

## 마무리

간단한 코드이지만, AI Agent 의 특성을 느껴볼 수 있는 예제라고 생각된다. AI Agents 에 관심이 있다면 [Google Agents Whitepapers](https://www.kaggle.com/whitepaper-agents) 를 읽어보는 것을 추천한다. 길어보일 수 있지만, 생각보다 금방 읽어볼 수 있다.
