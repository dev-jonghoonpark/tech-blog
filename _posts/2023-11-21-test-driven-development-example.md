---
layout: post
title: 예시로 알아보는 테스트 주도 개발 (TDD) 사용법
description: 테스트 주도 개발(TDD)의 사용법을 예시를 통해 설명하며, 작은 단계로 작업을 나누고, 실패하는 테스트(빨간 막대)와 통과하는 코드(녹색 막대)를 작성하는 과정을 다룹니다. HTTP 쿼리 문자열을 파싱하는 자바 클래스를 만들며, 각 단계에서 생각하기, 테스트 작성, 코드 구현, 리팩토링을 반복합니다. 이 과정에서 쿼리 문자열의 이름과 값 쌍을 처리하고, 다양한 테스트 케이스를 통해 코드의 완성도를 높여가는 방법을 제시합니다. TDD의 핵심 원칙인 작은 단위로 작업하고 지속적으로 리팩토링하는 중요성을 강조합니다.
categories: [스터디-테스트]
tags: [
    테스트,
    테스트 주도 개발,
    Test-Driven Development,
    TDD,
    예제,
    Thinking
    Red Bar,
    Green Bar,
    Refactoring,
    리팩터링,
  ]
date: 2023-11-21 23:00:00 +0900
---

원문 : [Test-Driven Development](https://www.jamesshore.com/v2/books/aoad1/test_driven_development)  
James Shored의 Art of Agile Development의 TDD장

이 글은 [테스트 주도 개발 (TDD) 사용법](/2023/11/15/test-driven-development)에서 이어지는 글입니다.

---

TDD 에서는 작은 범위(increments)로 나눠서 작업을 진행합니다. 처음 보는 사람에게는 터무니 없이 작게 보일지 모르지만, 실수를 아주 쉽게 찾아낼 수 있고, 더 빠르게 작업하는데 도움이 됩니다.

> [Note]  
> TDD를 처음 접하는 프로그래머는 각 작은 범위가 얼마나 작은지 놀라는 경우가 많습니다. 초보자만 작은 단계로 작업하면 된다고 생각할 수도 있지만 제 경험은 반대입니다. TDD 경험이 많을수록 더 작은 단계를 밟고 더 빠르게 진행됩니다.

예시를 통해서 알아보겠습니다. 참고로 실제로 작업할 때에는 아래에 있는 단계들를을 몇 초 만에 완료합니다.

# 우리가 만들 것

HTTP 쿼리 문자열(Query String)을 파싱하는 자바 클래스를 만들어봅시다. TDD를 사용할 것입니다.

## 하나의 이름과 값 쌍

### 1 단계 : 생각하기

내가 무슨 기능을 만들어야 할지 생각해봅시다. 제 첫 생각은 "**이름과 값 쌍들**을 이름과 값으로 나누어서 HashMap에 보관하는 클래스를 만들어야겠다." 이였습니다. 아쉽게도 이 생각을 코드로 작성하려면 5줄 이상이 필요하므로 더 작은 부분을 생각해야 했습니다.

더 작은 부분을 만드는 가장 좋은 방법은 더 작은 케이스부터 시작하는 것입니다. "**하나의 이름과 값 쌍**에 대해서 이름과 값으로 나누어서 HashMap에 보관하는 클래스를 만들어야겠다" 를 목표를 잡으면, 5줄 이하로 작성하는 것이 가능할 것 같습니다.

### 2 단계: 빨간 막대 (Red Bar, 실패하는 테스트 작성하기)

이제 테스트를 작성해봅시다. 이 부분은 인터페이스를 설계하는 연습이기도 합니다.

처음에는 QueryStringParser라는 클래스를 호출하게 해볼까 생각 했는데, 바로 이렇게 작업하는 것은 아쉽게도 객체지향적이지는 않은것 같습니다. 그래서 일단 QueryString 라는 클래스부터 만들어야겠다 생각이 들었습니다.

> [Note]  
> 테스트를 어떻게 짤지 고민하는 것은 어떻게 코드를 설계할지에 대한 고민으로 이어집니다.

일단은 QueryString 클래스에 count() 메소드를 만들어 이름과 값 쌍의 개수를 반환하도록 하는 것부터 해보기로 결정했습니다. 일단 한 쌍만 고려하여 테스트를 구현해보겠습니다.

```java
public void testOneNameValuePair() {
    QueryString qs = new QueryString("name=value");
    assertEquals(1, qs.count());
}
```

그리고 QueryString 이라는 클래스와 count 메소드를 아무 것도 하지 않는 상태로 작성합니다.

```java
public class QueryString {
    public QueryString(String queryString) {}
    public int count() { return 0; }
}
```

이렇게 작성하고 테스트를 실행해보면 예상했던 대로 빨간 막대(실패)가 나옵니다.

### 3단계: 녹색 막대 (Green Bar, 테스트에 통과하는 코드 작성하기)

이 테스트를 통과하도록 하기 위해 정답을 하드코딩하겠습니다. 더 나은 솔루션을 프로그래밍할 수도 있지만 일단 코드가 어떻게 동작하게 할 지에 대해 정하지는 않았습니다.

```
public int count() { return 1; }
```

이렇게 하면 녹색 막대가 나옵니다.

> [Note]
> 어떻게 프로그래밍할지에 대한 아이디어가 있었지만 미리 정하지는 않았습니다. 일하면서 새로운 접근 방식을 발견할수도 있으니깐요.

### 4 단계: 리팩터링

사실 QueryString이라는 클래스 이름이 맘에 들지는 않았지만 일단 QueryString이라는 이름을 쓰기로 했고 그렇게 테스트 코드와 코드를 작성했습니다.

저는 "이름을 바꿔야겠다"고 색인 카드(index card)에 메모를 하였습니다. HttpQuery라는 이름이 더 좋아보이네요.

사이클을 진행하면서 어떻게 할지 결정해봅시다.

![index-card-1](/assets/images/2023-11-21-test-driven-development-example/index-card-1.gif)

### 5 단계: 반복

## 빈 문자열

`return 1` 로 하드코딩 한 부분을 제거하고 싶지만 아직 여러 쌍을 처리하고 싶지는 않습니다. 다음은 valueFor 메소드(key에 따른 value를 반환해주는 메소드)에 대한 부분을 작성하면 좋을 것 같은데 그 전에 여러 쌍을 다뤄야 하는 복잡함은 피하고 싶습니다. 그래서 복잡한 작업을 하기 전에 우선 일단 빈 문자열이 들어왔을 때에 대한 케이스를 먼저 다뤄야겠다 생각했습니다.

빨간 막대를 보여주는 새로운 테스트는 다음과 같습니다.

```java
public void testNoNameValuePairs() {
    QueryString qs = new QueryString("");
    assertEquals(0, qs.count());
}
```

테스트를 실행해보면 빨간 막대(테스트 실패 표시)와 함께 `Expected: <0> but was: <1>.` 이라는 결과도 나올텐데, 사실 당연합니다.

여기서 두 가지 생각이 들었는데, 첫째는 생성자의 인수로 null이 들어오는 것에 대한 테스트를 작성해야겠다는 부분과 테스트 코드에서 중복이 보이기 시작했다는 것입니다. 두 가지 모두 색인 카드에 추가하였습니다.

![index-card-2](/assets/images/2023-11-21-test-driven-development-example/index-card-2.gif)

이제 어떻게 테스트를 통과할지 생각해봅시다. 빈 문자열이 들어올 경우에 대한 처리를 추가해주면 되겠네요.

```java
public class QueryString {
    private String _query

    public QueryString(string queryString) {
        _query = queryString;
    }

    public int count() {
        if ("".equals(_query)) return 0;
        else return 1;
    }
}
```

다시 리팩터링 단계입니다. to-do 목록을 확인해봅니다. 테스트를 리팩터링해야하긴 하지만 아직 필요성일 덜 입증된 것 같습니다. 한번 더 필요한 것 같으면 리팩터링 해보겠습니다. ("Three strikes and you refactor" 라는 말도 있잖아요)

일단 사이클을 한 번 더 돌려봅시다.

## testNull()

다시 생각하기 단계입니다. to-do 목록을 보니 testNull이 들어가있네요. 쿼리 문자열이 null인 경우를 테스트해주면 됩니다. 이 부분을 추가해봅시다.

실패하는 테스트를 만들어봅시다(Red Bar). 이 테스트는 null이 인수로 들어왔을 때 내가 어떻게 처리하고 싶은지를 생각해보게 만듭니다. 나는 빠르게 실패하는 코드를 좋아하기 때문에 null 값이 들어오는 것을 부적합(illegal)으로 처리하겠습니다. null을 넣었을 경우 Exception을 발생시키면 되겠네요.

```java
public void testNull() {
    try {
        QueryString qs = new QueryString(null);
        fail("Should throw exception");
    }
    catch (NullPointerException e) {
        // expected
    }
}
```

코드를 만들어봅시다(Green Bar).

```java
public QueryString(String queryString) {
    if (queryString == null) throw new NullPointerException();

    _query = queryString;
}
```

리팩터링 단계입니다. 테스트를 리팩터링 하면 좋을 것 같은데 아직 테스트들간의 공통 부분이 충분하지 않습니다. 프로덕션 코드도 괜찮아보이고 내 색인 카드에는 중요한 내용은 없습니다. 이번에도 리팩터링은 하지 않습니다.

## valueFor()

![index-card-3](/assets/images/2023-11-21-test-driven-development-example/index-card-3.gif)

다시 생각하기 단계입니다. 쉬운 테스트(testNull)는 다 한 것 같네요. 이제 valueFor 메소드를 구현해보도록 하겠습니다. 이름을 주면 그에 대한 값을 주면 됩니다.

이 테스트에 대해 생각하다보니 이름이 QueryString에 없는 경우도 고려해야하겠다 생각이 들었습니다. 그래서 색인 카드에 추가하였습니다.

실패하는 테스트 작성하기 단계입니다. 테스트가 실패하도록 하기 위해 기존 테스트 끝에 새로운 검증문을 추가하였습니다.

```
public void testOneNameValuePair() {
    QueryString qs = new QueryString("name=value");
    assertEquals(1, qs.count());
    assertEquals("value", qs.valueFor("name"));
}
```

코드를 작성하는 단계입니다. 테스트를 어떻게 통과하게 할지 고민해봤을 때 split() 이면 될 것 같다는 생각이 들어서 그렇게 작성하였습니다.

```
public String valueFor(String name) {
    String[] nameAndValue = _query.split("=");
    return nameAndValue[1];
}
```

이 코드는 테스트를 통과하긴 합니다. 단 하나의 등호가 있다는 조건 하에서요. 등호가 여러개 있으면 어떻게 하죠? 아니면 등호가 없으면 어떻게 하죠? 해당 시나리오에 대한 부분을 to-do 에 추가하겠습니다.

리펙토링 단계입니다. 저는 QueryString이라는 이름을 계속 써도 괜찮겠다 라고 생각이 들었습니다. 하지만 qs라는 변수명보다는 query라는 변수명이 더 좋겠다 생각이 들어서 수정하겠습니다.

## 여러 쌍의 이름/값 처리하기

![index-card-4](/assets/images/2023-11-21-test-driven-development-example/index-card-4.gif)

다시 생각해봅시다. valueFor()의 에러가 발생하는 케이스를 처리해야 하기는 하지만. 일단 더 중요한 여러 쌍의 이름/값을 처리하는 테스트를 추가해보겠습니다.

실패하는 테스트 만들기 단계입니다. 저는 일반적으로 가변 개수의 항목을 다룰 때 0개일 경우, 1개일 경우, 3개인 경우에 대해서 테스트를 진행합니다. 이미 0, 1에 대해서는 테스트했기 때문에 3개일 경우를 테스트해보겠습니다.

```java
public void testMultipleNameValuePairs() {
    QueryString query = new QueryString("name1=value1&name2=value2&name3=value3");
    assertEquals("value1", query.valueFor("name1"));
    assertEquals("value2", query.valueFor("name2"));
    assertEquals("value3", query.valueFor("name3"));
}
```

여기서 핵심 메소드는 valueFor() 입니다. count에 대한 부분은 다음에 작성해보겠습니다.

코드를 작성해봅시다. 다시 한번 split()을 사용해보면 어떨까요?

```java
public String valueFor(String name) {
    String[] pairs = _query.split("&");
    for (String pair : pairs) {
        String[] nameAndValue = pair.split("=");
        if (nameAndValue[0].equals(name)) return nameAndValue[1];
    }
    throw new RuntimeException(name + " not found");
}
```

조금 hack 인 것 같지만 일단 테스트는 통과했습니다.

> [Note]  
> 완벽한 코드를 얻으려고 노력하기보다는 테스트에 통과하는 코드를 빠르게 작성하는 것이 좋습니다. 테스트 코드를 통해 제어 가능한 상태를 유지하면서 빠르게 hack 한 부분을 정리해나갈 수 있습니다.

리팩터링 단계입니다. valueFor()가 hack 하게 보였기 때문에 다시 살펴보았습니다. nameAndValue와 RuntimeException 쪽을 수정해야겠다는 생각이 드는데

일단 RuntimeException쪽이 더 안좋은 것 같아서 여기부터 고쳐보겠습니다. 자바 컨벤션은 이 부분을 Exception 처리하는 것보다는 null 처리를 하는 것입니다. 이미 to-do 리스트에는 이름이 없는 경우에 대해 테스트를 해야한다는 것을 적어둔 상태입니다. null을 반환하는 것이 더 올바른 동작이라 생각되기 때문에 수정하도록 하겠습니다.

또 테스트 로직이 3번 중복이 되었네요. 이제는 리팩터링을 해주는 것을 고려해볼까요? 테스트들의 중복된 부분을 QueryString 객체를 매번 재구성 한다는 것이였습니다. 하지만 QueryString의 생성자에 들어가는 매개변수는 다 다르기 때문에 당장은 테스트에 대한 리팩터링이 필요하지는 않을 것 같네요. 목록에서 해당 부분을 지우겠습니다.

사실, 코드는 생각보다 꽤 괜찮아 보입니다. 너무 엄격하게 본 것 같네요.

## 여러 쌍에 대한 count() 구현

![index-card-5](/assets/images/2023-11-21-test-driven-development-example/index-card-5.gif)

다시 생각해봅시다. &(ampersand)를 연달아서 여러번 사용했으면 어떻게 하죠? 이에 대한 테스트를 해야한다고 메모에 추가하겠습니다. 일단은 count 메소드를 여러 쌍이 입력으로 들어왔을 때에도 잘 동작하게 하고 싶었습니다.

실패하는 테스트를 만들어봅시다. 테스트에 count() 검증을 추가하였습니다.

```java
public void testMultipleNameValuePairs() {
    QueryString query = new QueryString("name1=value1&name2=value2&name3=value3");
    assertEquals(3, query.count());
    assertEquals("value1", query.valueFor("name1"));
    assertEquals("value2", query.valueFor("name2"));
    assertEquals("value3", query.valueFor("name3"));
}
```

코드를 작성해봅시다. valueFor()에서 작성했던 코드를 살짝 참고해서 수정하였습니다.

```java
public int count() {
    String[] pairs = _query.split("&");
    return pairs.length;
}
```

이렇게 작성하면 녹색바는 나오지만 바로 리팩터링을 하겠습니다. 이 코드는 빈 쿼리 문자열이 들어오면 바로 실패하게 됩니다. split은 분할할 문자를 찾을 수 없을 때 원래 문자열을 반환합니다.

따라서 이 문제를 해결하기 위해 보호 구문(Guard Clause)를 추가하겠습니다.

> **보호 구문**  
> 비정상적인 조건을 if에서 검사한 다음, 조건이 참이면(비정상이면) 한수에서 빠져나오게 함.  
> (리팩터링 2판, 10.3장, 360 페이지)

hack 하게 보이긴 하지만, 일단 테스트에 통과하고 개선해보는 것으로 해보겠습니다.

```java
public int count() {
    if ("".equals(_query)) return 0;
    String[] pairs = _query.split("&");
    return pairs.length;
}
```

리팩터링 시간입니다. 이번에는 확실히 리팩터링을 해야할 것 같네요.

count와 valueFor 사이에 함수 중복을 고쳐보겠습니다. 어떻게 처리할지 고민하다가 처음에 고려했었던 HashMap을 도입해보기로 했습니다. 일단은 valueFor 부터 수정해보겠습니다.

```java
public String valueFor(String name) {
    HashMap<String, String> map = new HashMap<String, String>();

    String[] pairs = _query.split("&");
    for (String pair : pairs) {
        String[] nameAndValue = pair.split("=");
        map.put(nameAndValue[0], nameAndValue[1]);
    }
    return map.get(name);
}
```

> [Note]  
> HashMap으로 리팩터링을 하면서 이름을 찾을 수 없을 때 발생할 수 있는 예외가 제거되었습니다. 하지만 그 것을 증명할 수 있는 테스트는 작성되지 않았기 때문에 해당 부분을 to-do 리스트에서 제거하지 않고 남겨두었습니다.

이 코드는 valueFor를 부를때마다 query string을 파싱합니다. 이 부분을 생성자로 옮기면 좋을 것 같습니다.

테스트를 해보면 testNoNameValuePairs 테스트가 실패할 것입니다. 이 부분도 이전과 같이 보호 조항을 추가하여 문제를 해결하도록 하겠습니다.

모든 리팩터링을 거치니 테스트와 프로덕션 코드 깔끔하고 보기 좋습니다.

```java
public class QueryStringTest extends TestCase {
    public void testOneNameValuePair() {
        QueryString query = new QueryString("name=value");
        assertEquals(1, query.count());
        assertEquals("value", query.valueFor("name"));
    }

    public void testMultipleNameValuePairs() {
        QueryString query = new QueryString("name1=value1&name2=value2&name3=value3");
        assertEquals(3, query.count());
        assertEquals("value1", query.valueFor("name1"));
        assertEquals("value2", query.valueFor("name2"));
        assertEquals("value3", query.valueFor("name3"));
    }

    public void testNoNameValuePairs() {
        QueryString query = new QueryString("");
        assertEquals(0, query.count());
    }

    public void testNull() {
        try {
            QueryString query = new QueryString(null);
            fail("Should throw exception");
        }
        catch (NullPointerException e) {
            // expected
        }
    }
}
```

```java
public class QueryString {
    private HashMap<String, String> _map = new HashMap<String, String>();

    public QueryString(String queryString) {
        if (queryString == null) throw new NullPointerException();
        parseQueryString(queryString);
    }

    public int count() {
        return _map.size();
    }

    public String valueFor(String name) {
        return _map.get(name);
    }

    private void parseQueryString(String query) {
        if ("".equals(query)) return;

        String[] pairs = query.split("&");
        for (String pair : pairs) {
            String[] nameAndValue = pair.split("=");
            _map.put(nameAndValue[0], nameAndValue[1]);
        }
    }
}
```

## 마무리

![index-card-6](/assets/images/2023-11-21-test-driven-development-example/index-card-6.gif)

아직 다 끝나지는 않았습니다. 더 구현해야할 부분들이 있습니다. 여러분들을 위해 남겨두겠습니다. 이제 남은 부분은 직접 구현해보시죠. 아주 작은 단계로 나누어 진행하고 매번 리팩터링을 해야한다는 것도 잊지 마시고요.

---

나머지 부분은 다음에 이어서 작성.
