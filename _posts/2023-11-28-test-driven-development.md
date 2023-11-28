---
layout: post
title: 테스트 주도 개발 (TDD, Test-driven development)
categories: [스터디-테스트]
tags: [
    테스트,
    테스팅,
    테스트 주도 개발
    TDD,
    Test Driven Development,
    Red,
    Green,
    Refactor,
    리팩터링,
  ]
date: 2023-11-28 23:30:00 +0900
published: false
---

원문 : Well Grounded Java Developer - ch13 testing fundamentals

[테스트 기초 (testing fundamentals)](/2023/11/27/testing-fundamentals) 에서 이어지는 글입니다.

---

## 13.3 테스트 주도 개발

테스트 주도 개발은 꽤 오랫동안 소프트웨어 개발 산업의 일부로 존재해 왔습니다.

테스트 주도 개발의 기본 전제는 테스트를 구현하기 전에 작성하자는 것입니다. 이를 통해 테스트가 코드 설계에 영향을 미칩니다.

TDD는 일반적으로 다음과 같이 테스트를 먼저하는 접근 방식을 따릅니다. 먼저 구현하기 전에 실패하는 테스트를 만듭니다. 이후 구현하고 필요에 따라 리팩터링을 진행합니다.

예를들어, 두 문자열 객체("foo", "bar")를 연결하는 것을 구현한다고 해보겠습니다. "foobar" 라는 결과물이 나올 것을 예상하는 테스트를 먼저 작성합니다. 이 테스트는 구현을 옳게 하였는지 보장해줍니다.

많은 개발자들이 테스트를 작성합니다. 하지만 그 중에 많은 수가 테스트를 구현 이후에 작성해서 TDD의 주요 장점들을 놓칩니다.

TDD는 많이 퍼져 있는 개념이지만, 그럼에도 많은 개발자들이 왜 그렇게 까지 해야하는지에 대해 이해하지 못합니다.

TDD를 사용하는 사람들은 두려움과 불확실성을 제거하는 것이 가장 중요한 이유라고 믿습니다. Kent Beck의 테스트 주도 개발에는 이에 대해 훌륭하게 요약되어 있습니다.

- 두려움을 머뭇거리게 합니다.
- 두려움을 덜 소통하게 합니다.
- 두려움은 피드백 받는 것을 피하게 합니다.
- 두려움은 투덜거리게 합니다.

TDD는 두려움에서 벗어나게 하고, 기초가 탄탄한(well-grounded) 개발자로 하여금 더 자신감있고, 의사소통을 잘하며, 수용적이며, 행복하게 합니다.

TDD는 다음과 같은 상황(사고 방식)에서 벗어나도록 도와줍니다.

- 새 일을 시작할 때 "어디서 부터 시작해야할지 모르니깐 그냥 시작해볼께요"
- 기존 코드를 변경할 때 "기존 코드가 어떻게 동작하는지 모르겠어요, 그래서 바꾸기가 무서워요"

TDD는 아래와 같은 장점들을 제공합니다. (장점이 바로 나타나지는 않음, aren’t always immediately obvious)

- 깔끔한 코드 - 당신이 필요한 코드만 작성하면 됩니다.
- 더 나은 설계 - 그래서 Test-driven design 이라고도 부릅니다.
- 더 나은 인터페이스 - 테스트는 코드에 대한 클라이언트 역할로 초기에 잘못된 부분들을 드러냅니다.
- 더 유연함 - TDD는 인터페이스 사용을 장려합니다.
- 테스트를 통한 문서화 - 테스트를 작성해야만 하기 때문에 테스트에서 모든 것에 대한 사용 예시가 있습니다.
- 빠른 피드백 - production까지 가기 전에 버그를 발견할 수 있습니다.

이제 막 TDD를 시작해보려는 개발자는 TDD가 특별한 개발자만 쓰는 방식이라는 벽에 부딪히곤 합니다. 하지만 그렇지 않습니다. 앞으로 증명하겠지만 TDD는 모든 개발자를 위한 기술입니다.

### 13.3.1 TDD 요약

TDD는 단위 테스트 수준에서 가장 쉬우며 TDD에 익숙하지 않은 경우 시작하기 좋은 곳입니다. 여기서부터 시작하여 특히 단위 및 통합 테스트의 경계에서 TDD가 어떻게 작동하는지 보여드리겠습니다.

> [Note] 테스트가 아예 없거나, 거의 없는 기존 코드에서 작업하는 것은 어려운 작업이 될 수 있습니다. 모든 테스트를 소급 적용하는 것은 거의 불가능합니다. 대신, 앞으로 추가하는 새로운 기능에 대해서 테스트를 추가해나가면 됩니다. Michael Feathers의 레거시 코드 활용 전략(Working Effectively with Legacy Code)가 도움이 될 수 있습니다.

지금부터 red-green-refactor 방식을 사용하여 TDD에 대해 알아가보겠습니다. JUnit을 사용하며 극장의 티켓 판매에 대한 수익을 계산하기 위한 코드에 대한 테스트 코드를 작성할 것입니다.

만약 JUnit이 익숙하지 않다면 [사용자 가이드](https://junit.org/junit5/docs/current/user-guide/)를 참고하는 것을 권장합니다. 더 자세한 내용은 Cătălin Tudose의 [JUnit in Action](https://livebook.manning.com/book/junit-in-action-third-edition/chapter-1/)을 보십시오.

### 13.3.2 단일 사용 사례를 갖는 TDD 예제

실무에서 TDD에 대해 익숙하다면 이 과정을 건너뛰어도 좋습니다. 하지만 이 글을 통해 새로운 통찰력을 제공할 것입니다.

우리는 여러 곳의 극장에서 티켓을 판매하여 발생하는 수익을 계산하는 확실한 방법에 대해 코드를 작성해야 한다고 가정해봅시다.

초기 비지니스 규칙은 다음과 같이 간단합니다.

- 티켓의 기본 가격은 $30 입니다.
- 총 수익 = 판매된 티켓 수 \* 티켓 가격
- 극장의 좌석 = 100명

극장에는 현재 POS 소프트웨어가 없기 때문에 현재 사용자는 판매된 티켓 수를 자동으로 입력해야 합니다.

TDD를 접한적이 있다면 red-green-refactor 방식에 대해 익숙할 것입니다. 처음 접했거나, 약간의 복습이 필요한 사람을 위해 Kent Beck의 테스트 주도 개발에 있는 정의를 다시 살펴보겠습니다.

- Red : 작동하지 않는 작은 테스트를 작성합니다. (실패하는 테스트)
- Green : 가능한 빠르게 테스트를 통과하게 하세요 (테스트 통과)
- Refactor : 중복을 제거하세요 (통과한 코드 개선하기)

우리의 목표를 달성하기 위해 다음과 같은 의사코드(pseudocode)를 생각해봅시다.

```
estimateRevenue(int numberOfTicketsSold)
  if (numberOfTicketsSold is less than 0 OR greater than 100)
    Deal with error and exit
  else
    revenue = 30 * numberOfTicketsSold;
    return revenue;
endif
```

이에 대해 너무 깊게 생각하지 않는것이 중요합니다. 테스트가 설계와 구현을 주도할 것입니다.

### 실패하는 테스트 작성 (Red)

이 단계에서 해야하는 것은 실패하는 테스트로 부터 시작하는 것입니다. 아직 우리는 TicketRevenue 라는 클래스를 작성하지도 않았기 때문에 테스트가 컴파일 되지도 못한 상태입니다.

회계사와 논의를 마친 후 다음과 같은 작업이 필요하다는 것을 깨달았습니다.

우리는 5개의 테이스를 작성해야 합니다.

- 음수
- 0
- 1
- 2-100
- \> 100

> [Note] 테스트(특히 숫자와 관련된)를 작성할 때는 먼저 0/null 케이스, 1개 케이스, 많은(many) 케이스 를 고려하면 좋습니다. 그 이후로는 음수 또는 최대 한도를 초과하는 금액과 같은 케이스를 고려하면 좋습니다.

첫번째로 1개의 티켓에 대한 수익을 다루는 테스트를 작성하기로 하였습니다. 이를 JUnit 테스트로 작성해보면 아래와 같은 모습일 것입니다. (우리는 아직 테스트에 통과하는 완벽한 것을 작성하는 것이 아닙니다.)

```java
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

public class TicketRevenueTest {
  private TicketRevenue venueRevenue;

  @BeforeEach
  public void setUp() {
    venueRevenue = new TicketRevenue();
  }

  // One sold case
  @Test
  public void oneTicketSoldIsThirtyInRevenue() {
    var expectedRevenue = new BigDecimal("30");
    assertEquals(expectedRevenue, venueRevenue.estimateTotalRevenue(1));
  }
}
```

코드에서 볼 수 잇듯이 테스트에서는 티켓 한 장 판매하여 30원의 수익을 얻을 것을 기대하고 있습니다.

아직 `estimateTotalRevenue` 메소드를 포함한 `TicketRevenue` 클래스가 작성되지 않았기 때문에 이 테스트는 아직 컴파일 되지 않습니다. 우선 테스트 코드에 대한 컴파일을 없애기 위해 다음과 같이 무작위로 구현합니다.

```java
public class TicketRevenue {
  public BigDecimal estimateTotalRevenue(int i) {
    return BigDecimal.ZERO;
  }
}
```

일반적인 상황에서는 불변성이 선호되지만, 테스트 코드에서 venueRevenue는 변경 가능한 형태로 되어 있어서 이상하다고 느낄 수 있습니다. 이렇게 작성된 이유는 공유 필드를 통해 (곧 추가적으로 작성될) 다른 테스트 케이스들과의 공동 설정을 하기 위해서 입니다. 테스트에는 프로덕션 코드와 동일한 보호가 필요하지 않으며, 이렇게 작성하면 테스트 케이스들 간의 동일한 부분을 보여줘 명확성이 향상됩니다.

## 13.4 테스트 대역

### 13.4.1 Dummy 객체

### 13.4.2 Stub 객체

### 13.4.3 Fake 객체

### 13.4.4 Mock 객체

### 13.4.5 Mocking의 문제점

## 13.5 Junit 4에서 5로 migration 하기

## 요약
