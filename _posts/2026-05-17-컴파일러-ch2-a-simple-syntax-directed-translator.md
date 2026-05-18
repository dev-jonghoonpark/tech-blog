---
layout: post
title: "Compilers (Dragon Book) Ch.2 A Simple Syntax-Directed Translator 정리 - 1"
description: "Dragon Book 2장을 읽고 정리한다. 이번 글에서는 2.1 Introduction과 2.2 Syntax Definition(문맥 자유 문법, 유도, 파스 트리, 모호성, 결합성, 우선순위)을 다룬다."
categories: ["스터디"]
tags: [컴파일러, Dragon Book, 파싱, CFG, 스터디]
date: 2026-05-17 18:00:00 +0900
toc: true
mermaid: true
---

## 들어가며

[이전 글](/2026/05/11/컴파일러-ch1-introduction)에서 Dragon Book 1장을 정리했다. 이번 글에서는 2장 "A Simple Syntax-Directed Translator" 중 2.1 Introduction과 2.2 Syntax Definition을 정리한다.

2장은 컴파일러 front end를 실제로 만들어보는 장이다. 중위(infix) 수식을 후위(postfix) 표기로 변환하는 간단한 번역기에서 출발하여, 문장 수준의 코드를 3-주소 코드로 변환하는 데까지 확장한다. 이 과정에서 문법 정의, 구문 지시 번역, 파싱, 어휘 분석, 심볼 테이블, 중간 코드 생성이라는 front end의 핵심 주제를 하나씩 소개한다. 이번 글에서는 먼저 문맥 자유 문법(CFG)을 이용한 구문 정의까지 다루고, 나머지는 이어지는 글에서 정리한다.

---

## 2.1 Introduction

컴파일러의 **분석(analysis)** 단계는 소스 프로그램을 구성 요소로 분해하고 **중간 표현(intermediate code)**을 생성한다. **합성(synthesis)** 단계는 이 중간 표현으로부터 타겟 프로그램을 만든다.

분석은 언어의 "구문(syntax)"을 중심으로 조직된다. 프로그래밍 언어의 **구문(syntax)**은 프로그램의 올바른 형태를 기술하고, **의미(semantics)**는 프로그램이 실행될 때 무엇을 하는지를 정의한다. 구문을 명세하기 위해 **문맥 자유 문법(context-free grammar, CFG)** 또는 **BNF(Backus-Naur Form)**라는 널리 쓰이는 표기법을 사용한다(2.2절). 문법을 기반으로 번역을 안내하는 기법이 **구문 지시 번역(syntax-directed translation)**이다(2.3절). 그리고 **파싱(parsing)** 또는 구문 분석은 2.4절에서 소개한다.

2장에서 다루는 컴파일러 front end 모델은 다음과 같다.

<pre class="mermaid">
flowchart LR
    A[source\nprogram] --> B[Lexical\nAnalyzer]
    B -- tokens --> C[Parser]
    C -- syntax\ntree --> D[Intermediate\nCode Generator]
    D --> E[three-address\ncode]
    B & C & D <--> F[Symbol\nTable]
</pre>

**어휘 분석기(lexical analyzer)**는 식별자처럼 여러 문자로 이루어진 구문을 처리할 수 있게 해준다. 예를 들어 `count + 1`에서 식별자 `count`는 하나의 단위인 **토큰(token)**으로 취급된다. 어휘 분석기(2.6절)는 숫자, 식별자, 공백 등을 인식하여 파서에게 토큰을 전달한다.

중간 표현에는 두 가지 주요 형태가 있다.

- **추상 구문 트리(abstract syntax tree)**: 소스 프로그램의 계층적 구문 구조를 트리로 표현한다. 파서가 구문 트리를 생성하고, 이를 3-주소 코드로 추가 번역한다.
- **3-주소 코드(three-address code)**: `x = y op z` 형태의 명령어 시퀀스. 명령어당 최대 하나의 연산자만 가진다. 이항 연산자 **op**의 피연산자 주소 y, z와 결과 주소 x에서 이름이 유래했다.

예를 들어 `do i = i+1; while(a[i] < v);`의 두 가지 중간 표현은 다음과 같다.

구문 트리:

```
    do-while
    /      \
  body      >
   |       / \
 assign  [ ]   v
  / \   / \
 i   + a   i
    / \
   i   1
```

3-주소 코드:

```
1: i = i + 1
2: t1 = a [ i ]
3: if t1 < v goto 1
```

2장의 나머지는 이 front end 모델을 따라 순서대로 진행한다. 먼저 파서를 다루고(2.4~2.5절), 중위 수식을 후위 표기로 변환하는 간단한 번역기를 완성한 뒤, 어휘 분석기(2.6절), 심볼 테이블(2.7절), 중간 코드 생성(2.8절)으로 확장해 나간다

---

## 2.2 Syntax Definition

### 2.2.1 Definition of Grammars

**문맥 자유 문법(context-free grammar)**은 네 가지 구성 요소를 가진다.

여기서 **심볼(symbol)**이란 문법을 구성하는 기본 단위를 말한다. 심볼은 터미널과 논터미널로 나뉜다.

1. **터미널(terminal)** 집합: 토큰이라고도 한다. 더 이상 다른 것으로 대체되지 않는, 최종 결과에 실제로 나타나는 심볼이다. 예를 들어 `+`, `-`, `0`~`9` 같은 것들이 터미널이다. 파스 트리에서 리프 노드, 즉 끝(terminus) 지점에 위치하기 때문에 터미널이라는 이름이 붙었다.
2. **논터미널(nonterminal)** 집합: "구문 변수"라고도 한다. 터미널들의 조합 패턴에 이름을 붙인 것으로, 실제 코드에 직접 나타나지 않고 문법 규칙을 설명하기 위해 존재한다. 예를 들어 `list`, `digit` 같은 것들이 논터미널이다. 파스 트리에서 내부 노드에 위치하며, 프로덕션에 의해 계속 확장되므로 아직 끝이 아니라는(non-terminal) 의미이다.
3. **프로덕션(production)** 집합: "이 논터미널은 이렇게 구성된다"는 규칙이다. 각 프로덕션은 head(논터미널), 화살표, body(터미널/논터미널의 시퀀스)로 구성된다. 예를 들어 `list → list + digit`은 "list는 list 뒤에 +와 digit이 오는 것"이라는 규칙이다.
4. **시작 심볼(start symbol)**: 문법의 출발점이 되는 논터미널. 논터미널 중 하나를 지정한다.

예를 들어 "덧셈·뺄셈 기호로 이어진 숫자 나열"를 나타내는 문법은 다음과 같다.

```
list → list + digit
list → list - digit
list → digit
digit → 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
```

논터미널 *list*를 head로 가지는 세 프로덕션의 body는 다음과 같이 하나로 묶을 수 있다.

```
list → list + digit | list - digit | digit
```

여기서 터미널은 `+ - 0 1 2 3 4 5 6 7 8 9`이고, 논터미널은 *list*와 *digit*이며, *list*가 시작 심볼이다.

### 2.2.2 Derivations

문법은 시작 심볼에서 출발하여, 논터미널을 해당 프로덕션의 body로 반복 대체함으로써 문자열을 **유도(derive)**한다. 시작 심볼에서 유도할 수 있는 모든 터미널 문자열의 집합이 문법이 정의하는 **언어(language)**이다.

예를 들어 `9-5+2`가 *list*인 것을 다음과 같이 유도할 수 있다.

1. `9`는 *digit*이므로 *list*이다 (프로덕션 `list → digit`)
2. `9-5`는 *list*이다 (`list → list - digit`, 9는 _list_, 5는 _digit_)
3. `9-5+2`는 *list*이다 (`list → list + digit`, 9-5는 _list_, 2는 _digit_)

어떤 논터미널이 프로덕션의 head일 때, 그 프로덕션은 해당 논터미널에 **대한(for)** 프로덕션이라고 한다. 터미널 문자열(string of terminals)은 0개 이상의 터미널로 이루어진 시퀀스이며, 터미널이 0개인 문자열을 **빈 문자열(empty string)**이라 하고 ε(엡실론)으로 표기한다. 예를 들어 프로덕션 `A → ε`은 A가 아무 터미널도 생성하지 않고 비어 있을 수 있다는 의미이다.

### 2.2.3 Parse Trees

**파스 트리(parse tree)**는 문법의 시작 심볼이 문자열을 어떻게 유도하는지 그림으로 보여준다.

파스 트리의 성질:

1. 루트는 시작 심볼로 레이블링된다
2. 각 리프는 터미널 또는 ε으로 레이블링된다
3. 각 내부 노드는 논터미널로 레이블링된다
4. 내부 노드가 A이고 자식이 X₁, X₂, ..., Xₙ이면 `A → X₁X₂...Xₙ`이 프로덕션이다

리프를 왼쪽에서 오른쪽으로 읽으면 트리의 **yield**가 된다. 즉, yield는 파스 트리가 최종적으로 생성하는 문자열을 의미한다. 이것이 시작 심볼에서 유도된 문자열이다.

`9-5+2`의 파스 트리:

<pre class="mermaid">
graph TD
    L1[list] --- L2[list]
    L1 --- i1[ ]:::hide
    L1 --- D1[digit]
    L2 --- L3[list]
    L2 --- i2[ ]:::hide
    L2 --- D2[digit]
    L3 --- D3[digit]

    D3 --- V9["9"]
    i2 --- i3[ ]:::hide
    i3 --- VM["-"]
    D2 --- i4[ ]:::hide
    i4 --- V5["5"]
    i1 --- i5[ ]:::hide
    i5 --- i6[ ]:::hide
    i6 --- VP["+"]
    D1 --- i7[ ]:::hide
    i7 --- i8[ ]:::hide
    i8 --- V2["2"]

    classDef hide fill:none,stroke:none,color:transparent
</pre>

### 2.2.4 Ambiguity

하나의 터미널 문자열에 대해 두 개 이상의 파스 트리가 존재할 수 있는 문법을 **모호한(ambiguous)** 문법이라고 한다.

예를 들어 *digit*과 *list*를 하나의 논터미널 *string*으로 합치면:

```
string → string + string | string - string | 0 | 1 | ... | 9
```

이 문법에서 `9-5+2`는 `(9-5)+2`와 `9-(5+2)` 두 가지로 해석될 수 있다. 후자는 값이 2가 되어 기대와 다르다. 앞서 *list*와 *digit*을 분리한 문법에서는 이 문제가 발생하지 않는다.

### 2.2.5 Associativity of Operators

관례상 `9+5+2`는 `(9+5)+2`와 같고, `9-5-2`는 `(9-5)-2`와 같다. 이처럼 왼쪽부터 묶이는 연산자를 **좌결합(left-associative)**이라고 한다.

좌결합 연산자의 문법은 왼쪽으로 재귀한다:

```
list → list + digit | list - digit | digit
```

반면 대입 연산자 `=`처럼 **우결합(right-associative)** 연산자의 문법은 오른쪽으로 재귀한다:

```
right → letter = right | letter
letter → a | b | ... | z
```

`9-5-2`의 파스 트리는 왼쪽 아래로 자라고, `a=b=c`의 파스 트리는 오른쪽 아래로 자란다.

### 2.2.6 Precedence of Operators

`9+5*2`에서 `*`가 `+`보다 **높은 우선순위(higher precedence)**를 가지므로 `9+(5*2)`로 해석된다.

우선순위 수준마다 별도의 논터미널을 두어 문법으로 표현한다.

| 결합성 | 연산자 |
| ------ | ------ |
| 좌결합 | + -    |
| 좌결합 | \* /   |

```
factor → digit | ( expr )
term   → term * factor | term / factor | factor
expr   → expr + term | expr - term | term
```

이 문법에서:

- *factor*는 연산자 없이 그 자체로 하나의 값을 나타내는 기본 단위(숫자 또는 괄호 식)
- *term*은 높은 우선순위 연산자(`*`, `/`)만 포함할 수 있는 단위
- *expr*은 모든 연산자를 포함할 수 있는 단위

일반적으로 n개의 우선순위 수준이 있으면 n+1개의 논터미널이 필요하다.
