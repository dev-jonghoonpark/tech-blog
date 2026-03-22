---
layout: "post"
title: "Value Numbering (GVN, LVN)"
description: "컴파일러 최적화 기법인 Value Numbering을 소개합니다. GVN(Global Value Numbering)과 LVN(Local Value Numbering)의 원리, 동작 예시, 그리고 CSE와의 차이점을 다룹니다."
categories:
  - "개발"
tags:
  - "GVN"
  - "LVN"
  - "Value Numbering"
  - "SSA"
date: "2026-02-22 01:00:00"
toc: true
math: true
---

[Value numbering](https://en.wikipedia.org/wiki/Value_numbering) 은 프로그램 내의 두 계산 식이 서로 동일한지 판단하여, 중복된 계산을 제거함으로써 시맨틱(의미)을 유지한 채 프로그램을 최적화하는 기법입니다.

## GVN(Global Value Numbering)

GVN은 [SSA(정적 단일 할당)](/2026/02/22/ssa) 형태의 중간 표현(IR)을 기반으로 하는 컴파일러 최적화 기법입니다.

공통 부분식 제거(CSE)가 잡아내지 못하는 중복 코드를 제거하기도 하지만, 반대로 CSE만 할 수 있는 영역도 있어 현대 컴파일러에서는 두 기법을 함께 사용합니다.

GVN은 변수와 식에 **값 번호(Value Number)**를 부여합니다. 동일한 값을 가지는 변수와 식에는 같은 번호가 매겨집니다.

### 동작 예시

**변환 전:**

```plaintext
w := 3
x := 3
y := x + 4
z := w + 4
```

GVN은 $w$와 $x$에 같은 번호를, $y$와 $z$에 같은 번호를 부여합니다. 예를 들어 다음과 같은 값 번호 매핑이 만들어집니다.

$$\lbrace w \mapsto 1,\; x \mapsto 1,\; y \mapsto 2,\; z \mapsto 2 \rbrace$$

이 정보를 활용하면, 코드를 다음과 같이 안전하게 변환할 수 있습니다.

**변환 후:**

```plaintext
w := 3
x := w
y := w + 4
z := y
```

이후 코드에 따라 복사 전파(Copy Propagation)를 통해 $x$와 $z$에 대한 할당을 완전히 제거할 수도 있습니다.

### GVN vs CSE

GVN이 CSE보다 강력한 경우가 있는 이유는, CSE는 **철자가 완전히 똑같은 식(Lexically Identical)**을 찾는 반면 GVN은 **논리적으로 동일한 값**을 가지는지를 판단하기 때문입니다.

예를 들어 다음 코드를 보겠습니다.

```plaintext
a := c × d
e := c
f := e × d
```

복사 전파 없이는 CSE가 $f$의 중복 계산을 제거하지 못합니다. $a$는 $c \times d$이고 $f$는 $e \times d$로 문자열이 다르기 때문입니다. 하지만 GVN은 $e$와 $c$가 동일한 값임을 알고 있으므로, $f = e \times d = c \times d = a$라는 중복을 발견하고 제거할 수 있습니다.

## LVN(Local Value Numbering)

LVN은 단일 기본 블록(Basic Block) 내에서만 작동하는 최적화 기법입니다.

**작동 방식**: 각 연산에 고유 번호를 부여하고 이를 기록합니다. 이후 동일한 연산이 등장하면 새로 계산하지 않고 이전 결과를 재사용합니다.

예시:

```plaintext
a ← 4          (a는 #1)
b ← 5          (b는 #2)
c ← a + b      (c는 #1 + #2 = #3)
d ← 5          (d는 #2, b와 동일)
e ← a + d      (e는 #1 + #2 = #3)
```

여기서 $c$와 $e$는 같은 번호(#3)를 갖게 되므로, 이후 $e$를 참조하는 코드는 모두 $c$로 대체될 수 있습니다.

## 번외1: 왜 GVN은 SSA를 사용하는 것일까?

### SSA를 사용하지 않을 때의 문제

재바인딩(같은 변수에 두 번 이상 할당)이 가능한 IR이나 소스 언어에서는 GVN을 수행하기 위해 SSA 형태가 필요합니다. SSA 없이 $\lbrace\text{variable name} \mapsto \text{value number}\rbrace$ 매핑을 만들면, 변수 값이 재할당될 때 잘못된 매핑이 생길 수 있습니다.

오류 사례:

```plaintext
a ← 1          (#1)
b ← 2          (#2)
c ← a + b      (#3)
b ← 3          (b의 값이 변함!)
d ← a + b      (여전히 #3으로 잘못 판단할 위험)
```

위 코드에서 $c = a + b$는 $1 + 2 = 3$이지만, 이후 $b$가 $3$으로 재할당되었으므로 $d = a + b$는 $1 + 3 = 4$입니다. 그러나 값 번호만으로 판단하면 $c$와 $d$에 동일한 번호(#3)가 부여되어 잘못된 최적화가 이루어질 수 있습니다.

이런 문제를 방지하기 위해 각 변수에 한 번만 값을 할당하는 SSA 형태가 권장됩니다.

## 번외2: 피연산자의 순서만 바뀐 경우

단순한 구현으로는 피연산자의 순서만 바뀐 경우($a + b$ vs $b + a$)를 잡아내기 어렵습니다.

이를 해결하기 위해 **수학적 항등식**을 활용합니다.

**1. 교환법칙 적용**: $a + b$와 $b + a$에 같은 번호를 부여하거나, 피연산자를 정렬한 후 비교합니다.

**2. 수학적 최적화**: 컴파일러가 다음과 같은 항등식을 인식하여 동일한 값 번호를 부여할 수 있습니다.

- $b \leftarrow a + 0$ → $a$와 동일
- $c \leftarrow a \times 1$ → $a$와 동일
- $e \leftarrow \max(a, a)$ → $a$와 동일
