---
layout: "post"
title: "JDK-8368967: DivI/DivL 코드 중복 제거 리팩토링"
description: "OpenJDK C2 컴파일러의 DivINode/DivLNode에서 Identity/Ideal/Value 메서드의 코드 중복을 제거하는 리팩토링 작업을 정리한 글입니다. BasicType 파라미터를 활용한 통합 패턴과 C2 노드 최적화의 동작 원리를 설명합니다."
categories:
  - "오픈소스"
tags:
  - "JDK"
  - "OpenJDK"
  - "C2"
  - "JIT 컴파일러"
  - "리팩토링"
date: "2026-05-17 12:00:00"
toc: true
---

이 글은 OpenJDK 이슈 [JDK-8368967](https://bugs.openjdk.org/browse/JDK-8368967)에 대한 작업 내용을 정리한 것이다.

## 이슈 요약

DivINode과 DivLNode의 Identity/Ideal/Value 메서드가 거의 동일하고 타입(int/long)만 다르다. `AddNode::IdealIL()`이 `BasicType bt` 파라미터로 int/long 로직을 통합한 패턴을 따라, 나눗셈 노드에도 같은 리팩토링을 적용하는 것이 이 이슈의 목표다.

## 배경 지식

### C2 컴파일러와 노드 그래프

OpenJDK의 HotSpot JVM에는 C2라는 최적화 JIT 컴파일러가 있다. C2는 Java 바이트코드를 기계어로 변환할 때, 코드를 **노드(Node)로 구성된 그래프(Ideal Graph)**로 표현한다. 예를 들어 `a / b`라는 자바 코드는 `DivINode`(int 나눗셈) 또는 `DivLNode`(long 나눗셈) 노드로 표현된다.

### Identity / Ideal / Value 메서드

C2의 모든 노드는 다음 세 가지 최적화 메서드를 가진다:

- **Identity**: "이 노드를 다른 노드로 대체할 수 있는가?" — 예: `x / 1`은 그냥 `x`로 대체 가능
- **Ideal**: "이 노드를 더 효율적인 노드 구조로 변환할 수 있는가?" — 예: `x / 4`를 `x >> 2`(시프트)로 변환
- **Value**: "이 노드의 결과 값은 어떤 범위인가?" — JIT 컴파일러는 코드를 기계어로 변환하는 시점(컴파일 타임)에 런타임에 실제로 어떤 값이 들어올지 알 수 없다. 하지만 코드 흐름을 분석하면 가능한 값의 범위는 추적할 수 있다. Value는 입력들의 범위로부터 결과의 범위를 계산한다. 예를 들어 dividend가 0~100 사이, divisor가 2~5 사이라는 것을 알고 있다면, 결과의 최솟값은 `0 / 5 = 0`, 최댓값은 `100 / 2 = 50`이므로 결과는 0~50 범위라고 추론할 수 있다. 이 범위 정보가 있으면 이후 `if (result < 0)` 같은 분기가 나왔을 때 "항상 false"라는 것을 알고 분기 자체를 제거하는 등의 추가 최적화가 가능해진다.

### DivINode / DivLNode의 구조

```
in(0) = control input (div-by-zero 예외 처리를 위한 실행 순서 제어)
in(1) = dividend (피제수, 나눠지는 수)
in(2) = divisor (제수, 나누는 수)
```

나눗셈은 0으로 나누면 예외가 발생하므로, 다른 산술 노드(Add, Mul 등)와 달리 control input을 가진다. 이 control 연결이 있으면 컴파일러가 노드를 함부로 이동시키지 못한다.

### 클래스 계층

```
Node
 └─ DivModIntegerNode        ← 공통 부모 (control input 관리, pinning 등)
     ├─ DivINode             ← int 나눗셈
     ├─ DivLNode             ← long 나눗셈
     ├─ ModINode             ← int 나머지
     ├─ ModLNode             ← long 나머지
     ├─ UDivINode            ← unsigned int 나눗셈
     ├─ UDivLNode            ← unsigned long 나눗셈
     ├─ UModINode            ← unsigned int 나머지
     └─ UModLNode            ← unsigned long 나머지
```

### TypeInteger 계층

C2는 노드의 값 범위를 타입 시스템으로 추적한다:

```
Type
 └─ TypeInteger              ← int/long 공통 부모 (추상 클래스)
     ├─ TypeInt              ← int 범위 [_lo, _hi] (jint)
     └─ TypeLong             ← long 범위 [_lo, _hi] (jlong)
```

- `TypeInteger::zero(bt)` → bt가 T_INT이면 `TypeInt::ZERO`, T_LONG이면 `TypeLong::ZERO` 반환
- `TypeInteger::one(bt)` → 동일하게 1에 해당하는 타입 상수 반환
- `hi_as_long()` / `lo_as_long()` → virtual 메서드로, TypeInt이면 jint를 jlong으로 확장하여 반환

## 작업 내용

### 리팩토링 구조

`DivModIntegerNode`(부모 클래스)에 `IdentityIL`, `IdealIL`, `ValueIL` 메서드를 추가하고, `DivINode`/`DivLNode`은 각각 `T_INT`/`T_LONG`을 넘겨 위임하는 인라인 호출로 변경한다.

`TypeInteger`는 `TypeInt`과 `TypeLong`의 공통 부모 클래스다. `TypeInteger::zero(bt)`, `TypeInteger::one(bt)` 등 static 메서드가 bt에 따라 적절한 타입을 반환하고, `hi_as_long()`/`lo_as_long()`은 virtual 메서드라 서브클래스 구현이 호출된다. 이를 활용하면 int/long 로직을 하나로 통합할 수 있다.

```cpp
// divnode.hpp - DivINode (DivLNode도 동일 구조, T_LONG으로 위임)
class DivINode : public DivModIntegerNode {
  //...
  Node* Identity(PhaseGVN* phase) { return IdentityIL(phase, T_INT); }
  Node* Ideal(PhaseGVN* phase, bool can_reshape) { return IdealIL(phase, can_reshape, T_INT); }
  const Type* Value(PhaseGVN* phase) const { return ValueIL(phase, T_INT); }
  //...
};
```

클래스 자체는 그대로 존재하며, 중복 로직만 부모로 올린다.

## 통합된 메서드 상세

### IdentityIL

#### 하는 일

`x / 1 == x`이므로, divisor가 1이면 나눗셈 노드를 제거하고 dividend(피제수)를 그대로 반환한다.

#### 반환값의 의미

- `this`를 반환 → "대체할 노드 없음, 이 노드를 유지한다"
- `in(1)` (dividend)를 반환 → "이 나눗셈 노드를 dividend 노드로 대체하라"

즉, 그래프에서 `DivINode`이 사라지고 그 자리에 dividend가 직접 연결된다.

#### 코드

```cpp
Node* DivModIntegerNode::IdentityIL(PhaseGVN* phase, BasicType bt) {
  return (phase->type(in(2))->higher_equal(TypeInteger::one(bt))) ? in(1) : this;
}
```

- `phase->type(in(2))`: divisor(in(2))의 현재 타입(값 범위)을 가져온다
- `higher_equal(TypeInteger::one(bt))`: 그 타입이 "1"과 같거나 더 좁은 범위인지 체크한다. 실질적으로 "divisor가 항상 1인가?"를 확인하는 것이다

### IdealIL

#### 하는 일

나눗셈은 CPU에서 비용이 높은 연산이다 (보통 곱셈의 10~40배). IdealIL은 나눗셈을 더 빠른 곱셈이나 시프트 연산으로 변환하는 최적화를 수행한다. 모든 경우에 변환 가능한 것은 아니므로, 여러 조건을 순서대로 체크한다.

#### 반환값의 의미

- `nullptr` → "변환하지 않고 그대로 둔다" (이 노드는 나눗셈으로 남는다)
- `this` → "이 노드가 수정되었으니 다시 최적화를 시도하라" (예: control input을 제거한 경우)
- 새로운 노드 → "이 나눗셈 노드를 반환된 새 노드(곱셈/시프트 그래프)로 대체하라"

#### 처리 순서

```cpp
Node* DivModIntegerNode::IdealIL(PhaseGVN* phase, bool can_reshape, BasicType bt) {
```

**1단계: dead control 제거**

```cpp
  if (in(0) && remove_dead_region(phase, can_reshape))  return this;
```

나눗셈 노드의 control input(`in(0)`)이 이미 죽은 코드 영역(dead region)을 가리키고 있다면 정리한다. dead region이란 더 이상 실행되지 않는 코드 경로다. 예를 들어 이전 최적화에서 `if` 분기 하나가 제거되었다면, 그 분기 안의 코드는 dead region이 된다.

`this`를 반환하면 "노드가 변경되었으니 다시 처리하라"는 신호를 C2 프레임워크에 보내는 것이다.

**2단계: dead node 스킵**

```cpp
  if (in(0) && in(0)->is_top())  return nullptr;
```

control input의 타입이 Top이면 이 노드에 도달하는 실행 경로가 아예 없다는 뜻이다. C2에서 Top은 "이 값은 존재할 수 없다"를 의미한다.

예를 들어 다음 코드에서 `x / y`는 절대 실행되지 않으므로 해당 노드의 control은 Top이 된다:
```java
if (false) {
    return x / y;  // 도달 불가능 → control이 Top
}
```

이런 노드에 최적화를 시도해봤자 의미가 없으므로 `nullptr`을 반환하여 건너뛴다.

**3단계: Identity 스킵**

```cpp
  const Type *t = phase->type(in(2));
  if (t == TypeInteger::one(bt))   // Identity?
    return nullptr;                // Skip it
```

divisor가 정확히 1이면 `IdentityIL`에서 이미 이 노드를 dividend로 대체하도록 처리한다. Ideal에서 중복으로 처리할 필요가 없으므로 넘어간다.

**4단계: 타입 체크**

```cpp
  const TypeInteger *ti = t->isa_integer(bt);
  if (!ti) return nullptr;
```

divisor의 타입이 int/long이 아닌 경우 (예: 아직 타입 추론이 완료되지 않아 bottom 타입인 경우) 변환할 수 없다.

`isa_integer(bt)`는 "이 타입이 bt(T_INT 또는 T_LONG)에 해당하는 정수 타입이면 그것을 반환하고, 아니면 nullptr을 반환"하는 메서드다.

**5단계: control input 제거**

```cpp
  if (in(0) && (ti->hi_as_long() < 0 || ti->lo_as_long() > 0)) {
    set_req(0, nullptr);           // Yank control input
    return this;
  }
```

divisor의 값 범위가 0을 포함하지 않는다면 div-by-zero 예외가 절대 발생하지 않는다. 예를 들어:
- divisor 범위가 [3, 10] → 항상 양수, 0이 될 수 없음
- divisor 범위가 [-5, -1] → 항상 음수, 0이 될 수 없음

이 경우 예외 방지를 위한 control input이 불필요하므로 `set_req(0, nullptr)`로 제거한다.

control input은 일종의 "줄"이다. "이 나눗셈은 반드시 0 체크 이후에 실행해야 한다"라는 실행 순서 제약을 컴파일러에게 알려주는 역할을 한다. 이 줄이 있으면 컴파일러는 나눗셈 노드를 다른 위치로 옮길 수 없다. 하지만 divisor가 절대 0이 될 수 없다는 것이 증명되면 이 줄을 끊어도 안전하다. 줄이 끊어지면 컴파일러는 나눗셈을 CPU가 더 효율적으로 처리할 수 있는 위치로 자유롭게 재배치할 수 있다.

`ti->hi_as_long() < 0`은 "범위의 최댓값이 음수 = 모든 값이 음수", `ti->lo_as_long() > 0`은 "범위의 최솟값이 양수 = 모든 값이 양수"를 의미한다.

**6단계: 상수가 아니면 스킵**

```cpp
  if (!ti->is_con()) return nullptr;
```

`x / y`에서 y가 상수가 아닌 변수라면, 컴파일 타임에 어떤 값인지 알 수 없으므로 곱셈/시프트로 변환할 수 없다. 예를 들어 `x / 4`는 `x >> 2`로 변환 가능하지만, `x / y`는 y의 값을 모르므로 불가능하다.

`is_con()`은 `_lo == _hi`인지 확인한다. 범위의 최솟값과 최댓값이 같으면 가능한 값이 하나뿐이므로 상수다.

**7단계: 변환 불가 케이스 거부**

```cpp
  if (bt == T_INT) {
    jint i = ti->is_int()->get_con();
    if (i == 0 || i == min_jint) return nullptr;
    return transform_int_divide(phase, in(1), i);
  } else {
    jlong l = ti->is_long()->get_con();
    if (l == 0 || l == min_jlong) return nullptr;
    return transform_long_divide(phase, in(1), l);
  }
```

- **divisor == 0**: 항상 예외가 발생하므로 최적화 의미가 없다.
- **divisor == MIN_INT(-2147483648) 또는 MIN_LONG**: 2의 보수 체계에서 `-MIN_INT`는 오버플로로 다시 `MIN_INT`가 된다 (`-(-2147483648) == -2147483648`). 이 때문에 부호 처리가 깨져서 power-of-2 시프트 최적화가 적용되지 않는다.

**8단계: 변환 실행**

위 조건을 모두 통과하면 `transform_int_divide` 또는 `transform_long_divide`를 호출한다. 이 함수들은 나눗셈을 곱셈/시프트 연산의 그래프로 변환한다.

예를 들어 `x / 7`은 특정 magic number를 곱하고 시프트하는 형태로 변환되어, 비싼 나눗셈 명령어 대신 빠른 곱셈과 시프트로 같은 결과를 얻을 수 있다. 이 변환은 [Hacker's Delight](https://en.wikipedia.org/wiki/Hacker%27s_Delight)의 알고리즘을 기반으로 구현되어 있는데, 내부가 꽤 복잡하므로 관심이 있다면 `transform_int_divide`/`transform_long_divide` 함수를 직접 살펴보는 것을 추천한다.

### ValueIL

#### 하는 일

각 노드가 생성할 수 있는 값의 범위(Type)를 계산한다. 이 범위 정보는 다른 최적화에 활용된다. 예를 들어 결과가 항상 양수라는 것을 알면, 이후 `if (result < 0)` 같은 분기를 "항상 false"로 판단하여 제거할 수 있다.

#### 반환값의 의미

- `Type::TOP` → "이 노드는 유효한 값을 생성하지 않는다" (dead code이거나 항상 예외)
- `TypeInteger::one(bt)` → "결과가 항상 1이다" (상수 폴딩 가능)
- `TypeInt::make(lo, hi, widen)` / `TypeLong::make(lo, hi, widen)` → "결과는 [lo, hi] 범위"

#### 처리 순서

```cpp
const Type* DivModIntegerNode::ValueIL(PhaseGVN* phase, BasicType bt) const {
```

**1단계: TOP 전파**

```cpp
  const Type* t1 = phase->type(in(1));
  const Type* t2 = phase->type(in(2));
  if (t1 == Type::TOP || t2 == Type::TOP) {
    return Type::TOP;
  }
```

입력 중 하나라도 TOP(값이 존재할 수 없음)이면 결과도 TOP이다. 도달 불가능한 코드 경로에서의 값은 TOP이 되고, 이를 사용하는 연산도 전부 TOP으로 전파된다. 이렇게 전파된 TOP 노드들은 이후 dead code elimination 단계에서 그래프에서 제거된다.

**2단계: div-by-zero**

```cpp
  if (t2 == TypeInteger::zero(bt)) {
    return Type::TOP;
  }
```

divisor가 정확히 0이면 이 나눗셈은 항상 `ArithmeticException`을 던진다. 정상적인 결과 값이 존재하지 않으므로 TOP을 반환한다.

**3단계: x/x == 1**

```cpp
  if (in(1) == in(2)) {
    return TypeInteger::one(bt);
  }
```

dividend와 divisor가 동일한 노드이면 (같은 변수를 자기 자신으로 나누면) 결과는 항상 1이다. 0으로 나누는 경우는 어떡하냐고 생각할 수 있는데, C2는 div-by-zero 체크를 런타임에 별도로 생성하므로 여기서는 0이 아닌 경우만 고려한다.

**4단계: 범위 계산**

```cpp
  const TypeInteger* i1 = t1->is_integer(bt);
  const TypeInteger* i2 = t2->is_integer(bt);

  if (bt == T_INT) {
    return compute_signed_div_type<TypeInt>(i1->is_int(), i2->is_int());
  } else {
    return compute_signed_div_type<TypeLong>(i1->is_long(), i2->is_long());
  }
```

위 특수 케이스가 아니면 `compute_signed_div_type`을 호출하여 결과 범위를 수학적으로 계산한다. 기본 아이디어는 dividend 범위와 divisor 범위의 네 꼭짓점 조합에서 결과의 최솟값과 최댓값을 구하는 것이다:

```
dividend = [lo1, hi1], divisor = [lo2, hi2]
결과 범위 = [min(lo1/lo2, lo1/hi2, hi1/lo2, hi1/hi2),
            max(lo1/lo2, lo1/hi2, hi1/lo2, hi1/hi2)]
```

예: dividend=[6, 12], divisor=[2, 3]이면:
- 6/2=3, 6/3=2, 12/2=6, 12/3=4
- 결과 범위 = [2, 6]

실제 구현은 divisor가 0을 포함하는 경우(양수/음수 부분을 분리)나 MIN_INT/-1 오버플로 등의 특수 케이스도 처리한다.

## 정리

이번 리팩토링은 기능 변경 없이 코드 중복만 제거하는 작업이었다. `AddNode::IdealIL()` 패턴을 따라 `BasicType bt` 파라미터로 int/long 로직을 통합함으로써, 향후 나눗셈 관련 최적화를 추가할 때 한 곳만 수정하면 되는 구조가 되었다.

C2 컴파일러의 노드 최적화가 어떻게 동작하는지 이해하는 데도 좋은 작업이었다. Identity/Ideal/Value 각각의 역할과 반환값의 의미, control input의 존재 이유 등 C2의 핵심 개념들을 깊이 이해할 수 있었다.

이슈에서 언급된 것처럼 ModI/ModL, UDivI/UDivL, UModI/UModL에도 같은 패턴을 적용할 수 있어 보인다. 별도 패치로 이어서 진행해보고 싶다.
