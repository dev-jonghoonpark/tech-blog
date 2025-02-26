---
layout: "post"
title: "기초가 탄탄한 자바 개발자가 되기 위해 알아야할 테스트 대역 (Test Double)"
description: "자바 개발자를 위한 테스트 대역(Test Double)에 대한 글에서는 TDD 스타일로 코드 작성 시 의존성과 하위 시스템\
  으로부터 격리하는 방법을 설명합니다. 테스트 대역의 네 가지 종류인 더미, 스텁, 페이크, 목 객체에 대해 각각의 정의와 사용 예제를 제공하며\
  , 각 객체의 장점과 단점도 논의합니다. 특히, 목 객체의 경우 행동 검증을 통해 테스트의 신뢰성을 높일 수 있지만, 과도한 사용은 오히려 테스\
  트를 깨지기 쉽게 만들 수 있음을 경고합니다. 이 글은 자바 개발자가 테스트를 효과적으로 수행하기 위한 기초 지식을 제공합니다."
categories:
- "스터디-테스트"
tags:
- "테스트"
- "테스팅"
- "테스트 대역"
- "Test Double"
- "dummy"
- "stub"
- "fake"
- "mock"
- "더미"
- "스텁"
- "페이크"
- "목"
- "mocking"
date: "2023-12-05 04:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-12-02-test-double-for-well-grounded-java-developer.jpg"
---

원문 : Well Grounded Java Developer - ch13 testing fundamentals

- [기초가 탄탄한 자바 개발자가 되기 위해 알아야할 테스트 기초](/2023/11/27/testing-fundamentals)
- [기초가 탄탄한 자바 개발자가 되기 위해 알아야할 테스트 주도 개발](/2023/12/01/test-driven-development)

에서 이어지는 글입니다.

이 블로그에서는 이미 다양한 글을 통해 테스트 대역에 대해서 다뤘습니다. 함께 참고하면 좋을 것 같습니다.

- [목은 스텁이 아닙니다 (마틴 파울러 - Mocks Aren't Stubs 번역)](/2023/10/26/mocks-arent-stubs)
- [테스트 대역 (목 과 스텁)](/2023/05/11/테스트-대역-목-과-스텁)
- [테스트 더블과 모의 객체](/2023/09/27/테스트-더블과-모의-객체)

---

## 13.4 테스트 대역

TDD 스타일로 코드를 작성하다보면, (보통 서드 파티의) 종속성이나 하위 시스템을 참조해야 하는 상황이 생기곤 합니다. 일반적으로 이러한 상황이 발생되면 실제로 거치는 코드에 대한 부분에 대해서만 테스트할 수 있도록 테스트 코드가 해당 의존성으로부터 격리되기를 기대합니다.
동시에 우리는 언제나 테스트가 가능한 빠르게 완료될 수 있기를 기대합니다. 통합 테스트가 아닌 단위 테스트라면 더더욱 말이죠. 데이터베이스와 같은 서드 파티 종속성이나 하위 시스템들은 호출하는데 많은 시간이 걸립니다. 시간이 많이 걸린다는 것은 TDD의 빠른 피드백이라는 이점을 잃은 것입니다. 테스트 대역을 사용하면 이러한 문제를 해결할 수 있습니다.

이번 글에서는 테스트 대역을 이용하여 효과적으로 의존성과 하위 시스템으로부터 격리시키는 방법에 대해서 배웁니다. 예제와 함께 4가지 종류의 테스트 대역(더미, 스텁, 페이크, 목)에 대해서 알아봅니다. 또한 테스트 대역의 장점과 동시에 그로 인해 발생할 수 있는 문제들에 대해서도 살펴봅니다.

Gerard Meszaros는 xUnit Test Patterns 에서 테스트 대역에 대해 다음과 같이 설명하였습니다.
"테스트 대역은 실제 객체 대신 테스트 목적으로 사용되는 모든 종류의 가짜 객체입니다.”

Meszaros는 네 가지 종류의 테스트 더블에 대해서 정의하였습니다.

| 종류         | 설명                                                                                                           |
| ------------ | -------------------------------------------------------------------------------------------------------------- |
| 더미(dummy)  | 전달은 되지만 사용되지 않는 객체. 일반적으로 메소드의 파라미터 목록을 만족시키기 위해 사용                     |
| 스텁(stub)   | 준비된 응답 값을 항상 동일하게 전달하기 위한 객체. 더미의 상태를 일부 가질 수 있음.                            |
| 페이크(fake) | 실제 구현을 대체할 수 있는 실제로 동작하는 구현 (production 용으로 사용할 수 있는 정도의 품질이나 구성은 아님) |
| 목(mock)     | 예상과 준비된 응답값을 제공하는 객체.                                                                          |

각 유형에 대한 예제를 살펴보면 더 쉽게 이해할 수 있습니다.

### 13.4.1 더미(Dummy) 객체

더미 객체는 네 가지 유형 중 가장 사용하기 쉽습니다. 단지 매개변수 목록을 채우거나 사용되지 않지만 필수 필드 요구사항을 만족하기 위해 사용하는 객체라는 것을 기억하세요.

극장 티켓 시나리오로 다시 돌아가겠습니다.

> 극장 티켓 시나리오는 이전 글([기초가 탄탄한 자바 개발자가 되기 위해 알아야할 테스트 주도 개발](/2023/12/01/test-driven-development))에서 사용한 시나리오입니다.

하나의 키오스크에서 발생하는 수익에 대해서는 만족스럽지만, 극장의 소유자는 좀 더 큰 규모로 확장을 생각하고 있습니다. 이를 위해서는 더 나은 구조 설계(modeling)가 필요하며, 더 많은 요구 사항과 복잡성이 발생됩니다.

일부 티켓에 대해서10% 할인을 적용할 수 있도록 해달라는 요구사항이 생겼습니다. Ticket 클래스에 할인된 가격을 제공하는 메소드가 필요할 것 같습니다. getDiscountPrice() 라는 메소드에 대해 먼저 실패하는 테스트를 작성하는 것부터 해서 TDD 주기를 시작해봅시다.

먼저 두 가지 생성자가 필요할 것 같네요. 하나는 기존의 정가의 티켓을 위한 것이고, 다른 하나는 티켓의 액면가(표시 가격)를 다르게 설정할 수 있도록 하기 위한 것입니다.

Ticket 클래스는 아래의 2가지 인자를 가질 것입니다.

- 고객명 : String, 이번 테스트에서는 사용되지 않습니다.
- 정가 (normal price) : BigDecimal, 이번 테스트에서 사용됩니다.

getDiscountPrice 메소드에서 고객명이 필요하지는 않을 겁니다. 따라서 생성자에 더미 객체(아래 코드에서는 "Riley" 라는 문자열을 사용했습니다.)를 전달할 수 있습니다.

```java
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

public class TicketTest {

  private static String dummyName = "Riley";

  @Test
  public void tenPercentDiscount() {
    Ticket ticket = new Ticket(dummyName, new BigDecimal("10"));

    assertEquals(new BigDecimal("9.0"), ticket.getDiscountPrice());
  }
}
```

보시다시피, 더미 객체의 개념은 간단합니다.

개념을 더 명확하게 하기 위해 Ticket 클래스를 부분적으로 구현해보겠습니다.

```java
import java.math.BigDecimal;

public class Ticket {

  public static final int BASIC_TICKET_PRICE = 30;
  private static final BigDecimal DISCOUNT_RATE = new BigDecimal("0.9");

  private final BigDecimal price;
  private final String clientName;

  public Ticket(String clientName) {
    this.clientName = clientName;
    price = new BigDecimal(BASIC_TICKET_PRICE);
  }

  public Ticket(String clientName, BigDecimal price) {
    this.clientName = clientName;
    this.price = price;
  }

  public BigDecimal getPrice() {
    return price;
  }

  public BigDecimal getDiscountPrice() {
    return price.multiply(DISCOUNT_RATE);
  }
}
```

일부 개발자들은 더미 객체를 어렵게 생각하지만, 더미 객체는 매우 간단합니다. NullPointerException을 피하면서 코드가 실행될 수 있도록 사용하는 모든 객체를 의미합니다.

### 13.4.2 스텁(Stub) 객체

일반적으로 스텁 객체는 실제 구현을 매번 동일한 응답을 반환하는 객체로 대체하려고 할 때 사용합니다.

다시 극장 티켓 시나리오를 통해 어떻게 사용되는지 보겠습니다.

HttpPrice(Price 인터페이스의 구현체)가 새로 도입되었습니다.
이로인해 기존에 작성한 tenPercentDiscount 테스트가 실패하게 되었습니다.

이름에서 추측할 수 있듯 HttpPrice는 외부 웹사이트에 접속하여 언제든지 다른 값을 반환 할 수 있습니다. (실패할수도 있음)

처음에 테스트를 작성했을 때에는 10% 할인을 계산하는 단위 테스트 였습니다.
따라서 테스트의 목적이 오염되었으며 테스트가 실패하게 되었습니다.

> [참고] 다른 사이트에서 값을 받아오는 것은 이 테스트의 책임이 아닙니다. 별도의 통합 테스트를 만들어 HttpPrice 클래스와 타사의 가격을 받아오는 HttpPricingService 클래스에 대한 부분을 다뤄야 합니다.

테스트를 일관되고 안정적인 상태로 되돌리기 위해 HttpPrice 클래스를 스텁으로 대체하겠습니다.

우선 현재의 코드는 다음과 같습니다.

```java
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

public class TicketTest {
  private static String dummyName = "Riley";

  @Test
  public void tenPercentDiscount() {
    Price price = new HttpPrice();
    Ticket ticket = new Ticket(dummyName, price);

    assertEquals(new BigDecimal("9.0"), ticket.getDiscountPrice()); // 실패할 수 있음.
  }
}
```

```java
import java.math.BigDecimal;

public class Ticket {
  private final String clientName;
  private final Price priceSource;
  private final BigDecimal discountRate;

  private BigDecimal faceValue = null;

  public Ticket(String clientName,
                Price price,
                BigDecimal discountRate) {
    this.clientName = clientName;
    this.priceSource = price;
    this.discountRate = discountRate;
  }

  public BigDecimal getPrice() {
    if (faceValue == null) {
      faceValue = priceSource.getInitialPrice();
    return faceValue;
  }

  public BigDecimal getDiscountPrice() {
    return faceValue.multiply(discountRate);
  }
}
```

HttpPrice 클래스의 전체 구현을 제공하는 것은 이번 범위를 벗어나므로,여기서는 HttpPrice가 HttpPricingService의 메소드를 호출한다고 가정해보겠습니다.

```java
import java.math.BigDecimal;

public interface Price {
  BigDecimal getInitialPrice();
}
```

```java
public class HttpPrice implements Price {
  @Override
  public BigDecimal getInitialPrice() {
    return HttpPricingService.getInitialPrice();
  }
}
```

테스트 실패에 대한 원인 파악은 마쳤으니, 어떻게 테스트할지를 생각해보겠습니다.

우리의 목표는 Ticket 클래스의 getDiscountPrice() 메소드에서 곱셈이 예상대로 작동하는지 보여주는 것이였습니다. 이를 증명하는데 외부 웹사이트가 필요하지는 않습니다.

Price 인터페이스는 상황에 다라 달라지는 HttpPrice 인스턴스를 일관된 값으로 반환하는 StubPrice로 대체하는데 연결점을 제공합니다.

```java
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;

import static org.junit.jupiter.api.Assertions.*;

public class TicketTest {
  @Test
  public void tenPercentDiscount() {
    Price price = new StubPrice();
    Ticket ticket = new Ticket(price);
    assertEquals(new BigDecimal("9.0"), ticket.getDiscountPrice());
  }
}
```

StubPrice 클래스는 다음과 같이 초기 가격 10을 일관되게 반환하는 간단하고 작은 클래스입니다.

```java
import java.math.BigDecimal;

public class StubPrice implements Price {
  @Override
  public BigDecimal getInitialPrice() {
    return new BigDecimal("10");
  }
}
```

이제 다시 테스트가 안정적으로 통과됩니다. 다시 두려움 없이 나머지 구현 세부 사항을 리펙토링 할 수 있게 되었습니다.

스텁은 유용한 테스트 대역이지만, 때로는 스텁이 보다 더 실제에 가까운 작업을 수행하도록 해야할 필요가 있을 수 있습니다. 이럴 경우 페이크 객체를 사용하게 됩니다.

### 13.4.3 페이크(Fake) 객체

페이크 객체는 프로덕션 코드와 거의 동일한 작업을 수행하는 개선된 형태의 스텁으로 볼 수 있지만, 테스트 요구사항을 충족하기 위해 몇 가지 지름길(shortcuts, 편법)을 사용합니다.

페이크 객체는 실제 구현에 사용할 서드파티 종속성이나 하위 시스템과 매우 유사한 환경에서 코드를 실행하려는 경우에 유용합니다.

다시 티켓팅 어플리케이션을 예시로 알아보겠습니다.

티켓팅 어플리케이션의 데이터베이스 계층에서 아래와 같은 인터페이스를 제공해준다고 가정해보겠습니다.

```java
package com.wellgrounded;

public interface TicketDatabase {
    Ticket findById(int id);
    Ticket findByName(String name);
    int count();

    void insert(Ticket ticket);
    void delete(int id);
}
```

공연(show)을 관리하는 클래스는 이 데이터베이스 인터페이스를 사용합니다.

```java
package com.wellgrounded;

import java.math.BigDecimal;

public class Show {
  private TicketDatabase db;
  private int capacity;

  public Show(TicketDatabase db, int capacity) {
    this.db = db;
    this.capacity = capacity;
  }

  public void addTicket(String name, BigDecimal amount) {
    if (db.count() < capacity) {
      var ticket = new Ticket(name, amount);
      db.insert(ticket);
    } else {
      throw new RuntimeException("Oversold");
    }
  }
}
```

이러한 상황에서 데이터베이스의 인스턴스에 의존하지 않고 addTicket을 단위 테스트를 하고 싶을 수 있습니다. 이럴 때 페이크 객체를 사용합니다.

```java
package com.wellgrounded;

import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;

public class ShowTest {
  @Test
  public void plentyOfSpace() {
    var db = new FakeTicketDatabase();
    var show = new Show(db, 5);

    var name = "New One";
    show.addTicket(name, BigDecimal.ONE);

    var mine = db.findByName(name);
    assertEquals(name, mine.getName());
    assertEquals(BigDecimal.ONE, mine.getAmount());
  }
}
```

스텁을 통해서도 확인할 수 있겠지만, 그럴 경우에는 이 테스트에서 보이지 않는 함수들(count, insert)도 스텁화 해야하는 문제가 발생됩니다. 이는 테스트를 복잡하게 만들고 원래 목적에서 벗어나게 합니다.

또 다른 문제도 있습니다. 각 테스트는 count와 insert 호출 횟수 간의 관계가 일치하는지 확인해야 합니다.

또한 테스트의 검증문 에서 데이터가 저장되었음을 확인하기 위해 사용하는 findByName 호출 또한 스텁으로 처리해야 합니다. 이렇게 되면 굳이 검증문의 의미가 없어집니다. 구현이 올바르게 되었는지와 관계없이 테스트는 통과하게 되기 때문입니다. 스텁은 동작을 정확하게 검증할 수 있는 기능을 제공하지 못합니다.

페이크 객체는 실제로 동작하지만 단순화된 구현을 통해 대안을 제공합니다. 주어진 인터페이스에 따라 HashMap을 이용하여 간단한 Fake 객체를 만들어보겠습니다.

```java
package com.wellgrounded;

import java.util.HashMap;

class FakeTicketDatabase implements TicketDatabase {
  private HashMap<Integer, Ticket> tickets = new HashMap<>();

  private Integer nextId = 1;

  @Override
  public Ticket findByName(String name) {
    var found = tickets.values()
            .stream()
            .filter(ticket -> ticket.getName().equals(name))
            .findFirst();
    return found.orElse(null);
  }

  @Override
  public int count() {
    return tickets.size();
  }

  @Override
  public void insert(Ticket ticket) {
    tickets.put(nextId, ticket);
    nextId++;
  }

  // Remaining methods available in resources
}
```

페이크 객체는 강력한 인터페이스를 갖춘 프로젝트에서 사용될 때 좋은 솔루션이 될 수 있습니다. 모든 곳에서 적합하지는 않습니다. 만약 데이터베이스 인터페이스가 추가적으로 SQL 문을 전달할 수 있는 형태였다면 이는 페이크 객체의 범위를 벗어났을 것입니다.

구현이 너무 크거나 복잡해지지 않도록 주의하는게 좋습니다. 우리가 작성하는 모든 코드는 잠재적인 버그의 원인이 될 수 있기 때문입니다.

### 13.4.4 목(Mock) 객체

목 객체는 스텁과 관련이 있지만, 스텁은 일반적으로 보다 더 단순한 형태입니다. 예를들어 스텁은 항상 같은 값을 반환하도록 하기 위해 메서드를 가짜로 만듭니다. 이 방법은 상태 의존적인 동작을 하지는 못합니다.

예를들어, TDD를 따라 텍스트 분석 시스템을 작성한다고 해보겠습니다. 그리고 단위 테스트중 하나로 텍스트 분석 클래스로 이용하여 블로그에 "Java11" 이라는 문구의 발생 횟수를 계산하는 것을 작성하였습니다. 그러나 블로그 게시글은 서드 파티 리소스 이기 때문에, 계산 알고리즘과 상관없이 여러 가지 실패 시나리오가 발생할 수 있습니다. 다시 말해 테스트가 격리되지 못합니다. 또한 서드 파티 리소스 를 불러오는데 많은 시간이 걸릴 수 있습니다.

아래와 같은 실패 시나리오가 있을 수 있습니다.

- 방화벽으로 인해 인터넷을 통해 블로그 게시글에 도달하지 못할 수 있습니다.
- 게시글이 이동되었을 수 있습니다.
- 게시글이 편집되어 "Java11" 이라는 문구의 사용 횟수가 변경되었을 수 있습니다.

스텁을 사용하면 이 테스트를 작성하는것이 거의 불가능하며, 각 테스트 케이스에 대해 엄청나게 장황해집니다.

이럴 때 목 객체를 사용하면 좋습니다. 목 객체는 프로그래밍 가능한 스텁으로 생각해도 좋습니다. 목 객체를 사용하는 것은 매우 간단합니다. 목 객체를 준비하는 방법은 예상되는 호출 순서와 각 호출에 대해 어떻게 응답하면 될지에 대해서 알려주면 됩니다.

극장 티켓 시나리오를 통해 알아보겠습니다.

우리는 인기있는 목 라이브러리인 [Mockito](https://site.mockito.org)를 사용할 것입니다.

```java
import org.junit.jupiter.api.Test;
import java.math.BigDecimal;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class TicketTest {
  @Test
  public void tenPercentDiscount() {
    Price price = mock(Price.class);

    when(price.getInitialPrice())
      .thenReturn(new BigDecimal("10"));

    Ticket ticket = new Ticket(price, new BigDecimal("0.9"));
    assertEquals(new BigDecimal("9.0"), ticket.getDiscountPrice());

    verify(price).getInitialPrice();
  }
}
```

목 객체를 생성하려면 목 업(mock up)하려는 타입의 클래스 객체와 함께 mock() 정적 메소드를 호출하면 됩니다. 그런 다음 when() 메소드를 이용하여 행동을 "기록"할 메소드를 명시하고 thenReturn()을 호출하여 예상 결과를 지정함으로써 동작을 기록합니다. 마지막으로 모의 객체에서 예상했던 메서드를 호출했는지 확인합니다. 이를 통해 다른 방법을 통해 올바른 결과를 얻는 경우가 없도록 보장할 수 있습니다.

행동 검증이 스텁과 목 사이의 큰 차이점입니다. 스텁은 미리 준비된 값을 반환합니다. 목은 실제로 이루어진 행동에 대한 검증이 목적입니다. Mockito의 mock() 메서드를 이용해서 스텁을 만들수도 있긴 하지만, 테스트의 목적에 대해서 명확하게 이해하고 사용하는 것이 중요합니다.

일반 객체처럼 추가적인 작업 없이 목 객체를 Ticket 클래스의 생성자로 전달할 수 있습니다. 이 부분이 목 객체를 TDD를 위한 강력한 도구로 만듭니다. 일부 개발자들은 목을 이용해서 거의 모든 테스트를 수행하는 것을 선호하기도 합니다. 그러나 다른 강력한 도구들과 마찬가지로 목의 과도한 사용은 문제가 되기도 합니다.

### 13.4.5 Mocking의 문제점

테스트 대역의 가장 큰 어려움 중 하나는 결국 가짜이기 때문에, 테스트 대역을 사용했을 때의 동작이 실제 프로덕션 시스템과 다를 수 있다는 점입니다.
불행하게도, 문제가 될때까지 테스트를 통해 완전히 커버하였다는 생각에 빠져있을 수 있습니다.

일반적으로 이러한 차이는 다음과 같은 형태로 나타납니다.

- 반환된 payload의 차이 (특히 복잡하게 중첩된 객체의 경우)
- 테스트 데이터의 직렬화/역직렬화 차이
- 컬렉션 내 항목의 순서
- 에러 조건에 대한 응답 - 예외를 던지지 않거나 다른 예외 유형을 던지는 경우 등

이러한 상황에 대해서 포괄적인 해결책은 없지만, 일반적응로 테스트 수준을 통합 테스트의 레벨으로 올리면 발견되곤 합니다. 정리하자면, 각 테스트 세트에서 테스트하는 내용을 확실히 하여 단위테스트에서는 해당 부분의 로직에 집중하고, 통합테스트에서는 종속성간의 상호 작용을 다뤄야 합니다.

견고한(solid) 인터페이스 설계는 테스트 대역에도 도움이 됩니다. HTTP 호출에서 raw 콘텐츠 문자열을 반환하는 서비스 클래스 대신 특정 객체를 반환하도록 한다면 테스트 대역을 수정해야할 여지가 줄어듭니다.

클래스에서 발생하는 예외에 대한 정확한 하위 클래스(기본 예외 유형을 상속)를 사용하면 코드의 표현력이 좋아질 뿐 아니라 목을 사용하기 더 쉬워집니다.

목을 너무 남발하면, 테스트가 프로덕션 코드를 너무 밀접하게 모방하게 될 수 있습니다. 이렇게 될 경우 테스트 구성 중 정확한 예상 호출을 다시 명세하여 실제 코드의 미러링이 될 수 있습니다. 이러한 테스트는 매우 깨지기 쉽고, 코드가 변경될 때 관련이 없어 보이는 부분들까지 크게 수정해야 하는 경우가 발생되게 합니다.

목을 사용했을 때의 취약성은 개별 인수 레벨까지 확장됩니다. 목 프레임워크들은 전달되는 값에 대해 명시하는 것을 쉽게 만들지만, 테스트가 실제로 그 인수를 확인하는지를 고려해야 합니다. 더미 객체에서도 보앗듯이 특정 테스트 케이스에서는 주어진 값이 중요하지 않을 수 있습니다. 목 프레임워크는 "임의의 정수" 같은 문장을 효과적으로 허용하도록 하는 메커니즘을 제공합니다. 값이 중요하지 않다면 이러한 문장은 테스트가 관심을 두는 내용을 명확하게 하고 프로덕션 코드가 더 쉽게 발전할 수 있는 기회를 제공합니다. 테스트에 여유를 주세요 (구현에 너무 밀접하게 하지 말라는 뜻으로 보임 → 너무 밀접하면 쉽게 깨짐)

테스트 코드를 작성하면서 실행하기 위해 많은 양의 복잡한 설정이 필요한 경우에 대한 문제를 발견할 수 있습니다. 의존성 주입과 함께 목을 사용하면 쉽게 의존성을 구성할 수 있습니다. 테스트 설정이 코드 실행 및 결과 검증에 필요한 코드보다 길다면, 클래스가 지나치게 복잡하며 리팩터링이 필요하다는 힌트입니다.

테스트를 설정하면서 디미터의 법칙(객체는 직접 이웃하는 객체에 대한 지식만 가져야 한다.)을 위반하였는지 확인할 수 있습니다. 만약 테스트를 설정하는 중에 테스트에 필요한 객체와 상관없는 객체들을 다뤄야 한다면, 그 객체는 범위를 벗어난 객체일 수 있습니다.
