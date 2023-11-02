---
layout: post
title: 목은 스텁이 아닙니다 (마틴 파울러 - Mocks Aren't Stubs 번역)
categories: [스터디-아키텍처]
tags:
  [
    테스트,
    목,
    스텁,
    마틴 파울러,
    변역,
    모의,
    더블,
    페이크,
    더미,
    테스트 대역,
    모의 객체,
    마틴 파울러,
  ]
date: 2023-10-26 22:00:00 +0900
---

원문 : 마틴 파울러 - [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)

테스트 대역들에 대해서 찾아볼 때 많이 언급되는 글이라 언젠가 한 번 번역을 하면서 읽고 싶었던 글입니다.  
이 글에서는 반정도 번역하였으며 나머지 반은 또 기회가 되면 번역해보겠습니다.

---

**모의 객체** 는 실제 객체를 모방하는데 사용되는 객체를 뜻합니다. 대부분의 언어 환경에서 모의 객체를 쉽게 만들 수 있도록 하는 프레임워크가 있습니다.
모의 객체의 등장으로 다른 스타일로 테스트가 가능하게 되었습니다.

이 글에서는 어떻게 모의 객체가 동작하는지, 어떻게 동작을 검증하는지, 모의 객체를 활용하여 어떻게 테스트를 개발하는지에 대해서 설명합니다.

---

> (참고로 원문은 2007 년에 작성되었습니다.)

저는 몇 년 전 XP (Extreme Programming) 커뮤니티에서 "모의 객체" 라는 단어를 처음 듣게 되었습니다. 그 이후로 점점 더 많이 접하게 되었습니다. 모의 객체의 주요 개발자들이 여러 번 나와 동료였기 때문입니다. 그래서 XP의 영향을 받은 테스팅 문서들에서 자주 볼 수 있게 되었습니다.

종종 모의 객체에 대해서 제대로 설명되지 않은 것을 봅니다. 특히 테스트 환경의 일반적인 도우미인 스텁(stubs)과 혼동되게 설명하는 경우가 많습니다. 이러한 혼동을 이해합니다. 저도 처음에는 그랬었습니다. 그러나 모의 개발자들과 꾸준히 이야기를 나눈 결과 점점 이해할 수 있게 되었습니다.

둘 사이에는 두가지 차이가 있습니다.

테스트 결과를 검증하는 방법에서의 차이가 있습니다. 상태(state) 검증과 동작(behavior) 검증의 차이 입니다.

또한 테스팅과 디자인이 함께 작동하는 방식에 대한 완전히 다른 철학을 가지고 있습니다. 이 부분은 [TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)의 classical 스타일과 mockist 스타일로 나눠서 설명합니다.

## 일반적인 테스트(Regular Tests)

간단한 예를 통해 두 가지 스타일을 설명 해보겠습니다. (예시는 자바로 작성되어 있지만, 모든 객체 지향 언어에 유효합니다.)

창고(Warehouse) 객체에서 물건을 가져와 주문(Order) 객체에 담는 코드를 작성한다고 가정해보겠습니다.

주문은 단순하게 하나의 제품에 대한 수량만 정보로 가질 수 있습니다.
창고에는 다양한 제품의 재고가 보관되어 있습니다.

창고에 주문할 수 있는 충분한 양의 제품이 있다면 주문에 담아지고, 창고의 해당 제품 수량은 해당 양만큼 감소합니다.

그러나 창고에 충분한 제품이 없다면 주문에 담기지 않고, 창고에서는 아무 것도 일어나지 않습니다.

위 두가지 행동에 대한 테스트 코드를 작성해보면 다음과 같습니다. (일반적인 JUnit 테스트 입니다.)

```java
public class OrderStateTester extends TestCase {
  private static String TALISKER = "Talisker";
  private static String HIGHLAND_PARK = "Highland Park";
  private Warehouse warehouse = new WarehouseImpl();

  protected void setUp() throws Exception {
    warehouse.add(TALISKER, 50);
    warehouse.add(HIGHLAND_PARK, 25);
  }
  public void testOrderIsFilledIfEnoughInWarehouse() {
    Order order = new Order(TALISKER, 50);
    order.fill(warehouse);
    assertTrue(order.isFilled());
    assertEquals(0, warehouse.getInventory(TALISKER));
  }
  public void testOrderDoesNotRemoveIfNotEnough() {
    Order order = new Order(TALISKER, 51);
    order.fill(warehouse);
    assertFalse(order.isFilled());
    assertEquals(50, warehouse.getInventory(TALISKER));
  }
}
```

xUnit 테스트들은 일반으로 4단계 순서를 가집니다.

- setup (설정)
- exercise (실행)
- verify (검증)
- teardown (해체)

이 예제의 경우 설정 단계는 setup 메소드(창고 객체)와 테스트 메소드(주문 객체)에서 수행되었습니다.

실행 단계는 order.fill을 호출한 부분입니다. 이 단계는 우리가 테스트하고 싶은 것을 실행하는 단계입니다.

검증 단계는 실행 단계 다음에 나온 검증(assert)문이 있는 부분입니다. 실행된 메서드가 올바르게 수행되었는지 확인합니다.

해체 단계의 경우 이 예제에서는 가비지 컬렉터를 통해 암묵적으로 수행됩니다.

이 테스트에서 우리가 설정한 객체는 두 개 입니다. Order는 우리가 테스트할 클래스입니다. Warehouse는 테스트 할 대상은 아니지만 Order.fill을 작동하려면 필요합니다.

Order 객체가 여기서는 테스트하는 데 중점을 두고 있는 객체입니다.
테스트 지향적인 사람들은 이러한 것을 object-under-test 나 system-under-test 라고 부르는 것을 선호합니다. 여기서도 System Under Test, 줄여서 SUT 라고 부르겠습니다.

> 원문에는 Meszaros 에 대한 언급이 나오는데 "xUnit Test Patterns: Refactoring Test Code"라는 책을 쓰신 분이다. 저 책은 번역서가 나왔었지만 현재는 절판인 상태이다.

이 테스트에는 SUT(order)와 하나의 협력자(warehouse)가 사용되었습니다.
warehouse가 필요한 이유는 두가지 이유입니다. 하나는 Order의 fill메소드가 warehouse 객체를 필요로 하기 때문이고 두번째는 확인을 위해 필요합니다. (order의 fill메소드의 결과로 warehouse의 상태가 변경됨)
이 글을 읽다보면 SUT와 협력자 사이에 많은 차이가 있다는 것을 알게 될 것입니다.

이러한 스타일의 테스트는 상태 검증을 사용합니다. 다시 말해 메서드가 실행된 후 SUT와 협력자의 상태를 검사하여 실행된 메서드가 올바르게 작동했는지 여부를 결정합니다.

앞으로 살펴보겠지만, 모의 객체는 다른 접근 방식을 통해 검증을 합니다.

## 모의 객체를 이용한 테스트(Tests with Mock Objects)

이제 동일한 동작을 모의 객체를 통해 테스트 해보겠습니다.
이 코드에서는 모의 객체를 정의하기 위해 jMock라이브러리를 사용합니다. jMock은 Java 모의 라이브러리입니다. 다른 모의 객체 라이브러리도 있지만 이것은 기술의 창시자가 작성한 라이브러리이므로 시작하기에 좋은 라이브러리 입니다.

> [jmock-library](https://github.com/jmock-developers/jmock-library) 프로젝트에 들어가보니 컨트리뷰터에 Steve Freeman 와 Nat Pryce 가 보인다. 현재는 개발이 활발하지는 않는것 같다.

> [Mock roles, not objects](https://dl.acm.org/doi/10.1145/1028664.1028765) 이라는 논문을  
> Steve Freeman, Tim Mackinnon, Nat Pryce, Joe Walnes 이렇게 4명이서 작성한 것 같다.

```java
public class OrderInteractionTester extends MockObjectTestCase {
  private static String TALISKER = "Talisker";

  public void testFillingRemovesInventoryIfInStock() {
    //setup - data
    Order order = new Order(TALISKER, 50);
    Mock warehouseMock = new Mock(Warehouse.class);

    //setup - expectations
    warehouseMock.expects(once()).method("hasInventory")
      .with(eq(TALISKER),eq(50))
      .will(returnValue(true));
    warehouseMock.expects(once()).method("remove")
      .with(eq(TALISKER), eq(50))
      .after("hasInventory");

    //exercise
    order.fill((Warehouse) warehouseMock.proxy());

    //verify
    warehouseMock.verify();
    assertTrue(order.isFilled());
  }

  public void testFillingDoesNotRemoveIfNotEnoughInStock() {
    Order order = new Order(TALISKER, 51);
    Mock warehouse = mock(Warehouse.class);

    warehouse.expects(once()).method("hasInventory")
      .withAnyArguments()
      .will(returnValue(false));

    order.fill((Warehouse) warehouse.proxy());

    assertFalse(order.isFilled());
  }
}
```

Concentrate on testFillingRemovesInventoryIfInStock first, as I've taken a couple of shortcuts with the later test.

먼저 testFillingRemovesInventoryIfInStock 테스트를 확인해봅시다.

우선 설정 단계가 매우 다른것을 볼 수 있습니다. 설정 단계를 데이터 설정와 예상값 설정의 두가지 단계로 나눌 수 있습니다.

데이터 설정은 작업에 관심이 있는 객체를 설정합니다. 기존의 설정 단계와 유사합니다. 차이점은 생성되는 객체에 있습니다. SUT는 동일합니다. 그러나 협력자는 창고 객체가 아니라 모의 창고 객체 입니다.

예상값 설정은 모의 객체에 대한 예상값 을 설정합니다. 예상값은 SUT가 실행되었을 때 메소드가 어떤 값을 반환해야 하는지를 나타냅니다.

모든 예상치를 설정하고 나서 SUT를 실행합니다.

실행 후에는 두가지 검증을 수행합니다.
먼저는 이전과 마찬가지로 SUT에 대한 검증을 수행합니다. 그리고 모의 객체가 예상값에 따라 호출되었는지 검증을 수행합니다.

여기서 중요한 부분은 warehouse와 order의 상호작용을 어떻게 검증하였는지 입니다. 상태 검증을 통해서는

목은 동작을 검증합니다. order 객체가 warehouse 객체의 메소드를 올바르게 호출을 하였는지를 확인합니다. 우리는 모의 객체에게 예상을 설정하고 스스로 수행되었는지 검증하도록 합니다.

order 객체만 검증문을 통해서 검증합니다. 만약 메소드가 order의 상태를 바꾸지 않았다면 검증이 진행되지 않습니다.

> `warehouseMock.verify();` 에서 실패할 경우, order의 상태값이 바뀌지 않은 케이스 이기 때문에 여기서 테스트가 종료되고  
> `assertTrue(order.isFilled());` 가 수행되지 않는다는걸 이야기 하고 싶은 것으로 생각됨.

---

두번째 테스트 (testFillingDoesNotRemoveIfNotEnoughInStock) 에서는 몇 가지 다른것들이 있습니다.

첫번쨰 테스트와 달리 생성자 대신 mock 메서드를 사용하여 모의 객체를 만들었습니다. jMock 라이브러리의 편의 메서드를 사용하였습니다. 편의 메소드로 생성된 모의 객체는 테스트가 끝날 떄 자동으로 확인됩니다. 첫 번째 테스트에서도 이 작업을 수행할 수 있었지만 모의 테스트가 어떻게 작동하는지 보여주기 위해 검증을 더 명시적으로 보여주고 싶었습니다.

또 다른 점은 withAnyArguments를 사용하여 예상값 설정에 대한 제약 조건을 완화 하였습니다. 첫번쨰 테스트를 통해서 값이 제대로 전달되는지 확인을 하였기 때문에 두 번쨰 테스트에서는 해당 테스트 요소를 반복할 필요가 없기 때문입니다. 이렇게 하면 나중에 order 객체의 로직이 바뀌었을 때, 하나만 실패하기 때문에 테스트를 수정하는데 수고를 덜해도 됩니다.

사실 withAnyArguments 가 없어도 됩니다. 이것이 기본값이기 때문입니다.

> 이후에 나오는 EasyMock 에 대한 부분도 나오지만 이 글에서는 생략한다.

## The Difference Between Mocks and Stubs

처음 목이 소개되었을 때 많은 사람들은 스텁을 사용하는 일반적인 테스트 개념과 모의 객체를 쉽게 혼동했습니다. 그 때에 비하면 차이점을 잘 이해하고 있는 것 같습니다.

모의 객체를 사용하는 방식을 완전히 이해하려면 모의 객체와 다른 종류의 테스트 더블을 이해하는 것이 중요합니다.
('더블' 이라는 단어가 새롭다 해도 곧 설명할 것이니 걱정하지 마세요.)

이런 테스트를 할 때면 소프트웨어의 한 요소에만 집중하게 됩니다. 이것을 일반적으로 단위 테스트라고 합니다. 문제는 단일 유닛을 동작시키려면 종종 다른 유닛이 필요하다는 것입니다. 위의 예시에서는 warehouse가 필요했었습니다.

위의 두 가지 테스트 스타일에서 첫 번쨰 스타일은 실제 warehouse 객체를 사용하고 두 번째 스타일은 실제 warehouse 객체가 아닌 모의 warehouse 객체를 사용하였습니다.

모의 객체를 사용하는 것도 테스트에서 실제(real) 객체를 사용하지 않는 방법 중 하나이지만, 이와 같이 테스트에 사용되는 다른 형태의 가상(unreal) 객체들이 있습니다.

이 것들에 대해서 이야기 하려면 혼잡해집니다. 스텁(Stub), 모의(Mock), 가짜(Fake), 더미(Dummy) 등 다양한 용어가 나옵니다.
이 글에서는 Meszaros의 책에 나오는 어휘를 따릅니다.

Meszaros는 테스트 목적으로 실제 객체 대신 사용되는 모든 종류의 가상 대체에 대해 테스트 더블 이라는 용어를 사용합니다.

이 이름은 영화에 나오는 스턴트 더블(Stunt Double, 대역 으로 생각하면 됨) 개념에서 유래되었습니다. (이러한 단어를 쓴 이유 중 하나는 이미 널리 사용되는 이름을 사용하지 않기 위해서 였습니다.)

Meszaros는 5개의 더블에 대해서 정의하였습니다.

- **Dummy (더미)** 는 전달되지만 실제로는 사용되지 않습니다. 일반저긍로 매개변수 목록을 채우는 데 사용됩니다.
- **Fake (페이크)** 는 실제로 작동하는 구현이 있지만 실제 production 환경에서는 적합하지 않은 일종의 편법(shortcut)을 사용합니다. (메모리 데이터베이스가 종은 예시입니다.)
- **Stubs (스텁)** 테스트에 사용되는 호출에 대해 미리 준비된 답변을 제공합니다. 일반적으로 테스트를 위해 프로그래밍된 것 외에는 작동하지 않습니다.
- **Spies (스파이)** 호출 방식에 따라 정보를 기록하는 스텁입니다. 이러한 형태 중 하나는 전송된 메시지 수를 기록하는 이메일 서비스입니다.
- **Mocks (목)** 수신할 것으로 예상되는 호출의 사양을 형성하는 예상값으로 미리 프로그래밍된 객체입니다.

이러한 더블 중에서도 오직 목 만 동작 검증을 합니다. 다른 더블들은 상태 확인을 사용할 수 있으며, 일반적으로 사용합니다. 실행 단계에서는 다른 더블과 차이가 없으나, 준비 및 확인 단계에서는 다릅니다.

테스트 더블을 더 알아보려면 우리가 사용했던 예시를 확장해야 합니다. 테스트 더블은 일반적으로 실제 객체가 사용하기 불편한 경우에 사용합니다.
위의 예제에서 주문을 이행하지 못한 경우 이메일 메시지를 보내는 것 기능을 추가해봅시다. 우리는 테스트 중에 고객에게 실제 이메일 메시지를 보내기를 바라지 않습니다. 그래서 대신 우리는 제어하고 조작할 수 있는 이메일 시스템의 테스트 더블을 만듭니다.

여기서 우리는 mock과 stub의 차이점을 볼 수 있습니다. 먼저 이 메일을 보내는 동작에 대해 단순한 Stub을 만들어 테스트를 작성해보겠습니다.

```java
public interface MailService {
  public void send (Message msg);
}
public class MailServiceStub implements MailService {
  private List<Message> messages = new ArrayList<Message>();
  public void send (Message msg) {
    messages.add(msg);
  }
  public int numberSent() {
    return messages.size();
  }
}
```

그런 다음 아래와 같이 스텁에 대한 상태를 확인할 수 있습니다.

```java
public void testOrderSendsMailIfUnfilled() {
  Order order = new Order(TALISKER, 51);
  MailServiceStub mailer = new MailServiceStub();
  order.setMailer(mailer);
  order.fill(warehouse);
  assertEquals(1, mailer.numberSent());
}
```

메시지가 전송되었는지에 대한 부분만 간단하게 테스트 하였습니다. 누구에게 보냈는지 테스트하지는 않았지만 요점을 설명하는 데는 도움이 됩니다.

목을 사용하면 다른 모습의 테스트를 볼 수 있습니다.

```java
public void testOrderSendsMailIfUnfilled() {
  Order order = new Order(TALISKER, 51);
  Mock warehouse = mock(Warehouse.class);
  Mock mailer = mock(MailService.class);
  order.setMailer((MailService) mailer.proxy());

  mailer.expects(once()).method("send");
  warehouse.expects(once()).method("hasInventory")
    .withAnyArguments()
    .will(returnValue(false));

  order.fill((Warehouse) warehouse.proxy());
}
```

두 경우 모두 실제 메일 서비스 대신 테스트 더블을 사용하였습니다. 스텁은 상태 검증을 사용하는 반면, 모의 객체는 동작 검증을 사용한다는 차이점이 있습니다.

스텁에서 상태 확인을 사용하려면 스텁에서 확인에 도움이 되는 몇 가지 추가 메서드를 만들어야 합니다. 결과적으로 스텁은 MailService를 구현하지만 추가 테스트 메서드를 추가합니다.

모의 객체는 항상 동작 검증을 사용하며, 스텁은 양쪽 다 사용 가능합니다. Meszaros는 동작 검증에 사용하는 스텁을 '테스트 스파이'라고 합니다. 그 차이는 더블이 어떻게 실행되고 검증되는지에 대한 방식에 있으며, 이 부분은 스스로 알아볼 수 있도록 남겨두겠습니다.

---

이 글의 나머지 부분에서는 [테스트의 두 분파 (Classical and Mockist Testing)](/2023/10/31/테스트의-두-분파) 에 대해서 다룹니다.
