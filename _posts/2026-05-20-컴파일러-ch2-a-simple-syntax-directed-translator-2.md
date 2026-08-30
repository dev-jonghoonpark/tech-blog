---
layout: post
title: "Compilers (Dragon Book) Ch.2 A Simple Syntax-Directed Translator 정리 - 2"
description: "Dragon Book 2장을 읽고 정리한다. 이번 글에서는 2.3 Syntax-Directed Translation부터 2.9 Summary까지(구문 지시 번역, 예측 파서, 단순 수식 번역기, 어휘 분석, 심볼 테이블, 중간 코드 생성)를 다룬다."
categories: ["스터디-컴파일러"]
tags: [컴파일러, Dragon Book, 파싱, CFG, 스터디]
date: 2026-05-20 18:00:00 +0900
toc: true
mermaid: true
---

## 들어가며

[이전 글](/2026/05/17/컴파일러-ch2-a-simple-syntax-directed-translator)에서 2장 "A Simple Syntax-Directed Translator" 중 2.1 Introduction과 2.2 Syntax Definition을 정리했다. 이번 글에서는 이어서 2.3 Syntax-Directed Translation부터 2.9 Summary of Chapter 2까지를 정리한다.

앞 글이 문맥 자유 문법으로 언어의 구문을 정의하는 데까지였다면, 이번 글은 그 문법 위에 실제로 번역기를 올리는 과정이다. 프로덕션에 시맨틱 액션을 붙여 번역을 정의하고(2.3), 재귀 하향 방식의 예측 파서를 만들고(2.4), 이 둘을 합쳐 중위(infix) 수식을 후위(postfix) 표기로 바꾸는 동작하는 번역기를 완성한다(2.5). 이어서 토큰을 만들어내는 어휘 분석기(2.6), 식별자 정보를 관리하는 심볼 테이블(2.7), front end의 최종 산출물인 3-주소 코드 생성(2.8)까지 다루면 2장이 목표로 한 front end 한 벌이 갖춰진다.

---

## 2.3 Syntax-Directed Translation

**구문 지시 번역(syntax-directed translation)**은 문법의 프로덕션에 규칙이나 프로그램 조각을 붙여서 수행한다. 두 가지 핵심 개념이 있다.

- **속성(attribute)**: 프로그래밍 구문에 연관된 양(quantity). 예: 식의 데이터 타입, 생성 코드의 명령어 수
- **번역 스킴(translation scheme)**: 프로덕션 body에 **시맨틱 액션(semantic action)**이라는 프로그램 조각을 삽입하는 기법

### 2.3.1 Postfix Notation

**후위 표기법(postfix notation)**은 연산자가 피연산자 뒤에 오는 표기법이다. 재귀적으로 정의하면:

1. 변수나 상수의 후위 표기는 자기 자신
2. `E₁ op E₂`의 후위 표기는 `E₁' E₂' op` (E₁', E₂'는 각각의 후위 표기)
3. `(E₁)`의 후위 표기는 E₁의 후위 표기와 같다

예시:

| 중위 표기 | 후위 표기 |
| --------- | --------- |
| `(9-5)+2` | `95-2+`   |
| `9-(5+2)` | `952+-`   |

후위 표기에는 괄호가 필요 없다. 연산자의 위치와 항수(arity)만으로 유일하게 해석할 수 있기 때문이다.

### 2.3.2 Synthesized Attributes

문법 심볼에 속성을 연관시키고, 프로덕션에 **시맨틱 규칙(semantic rule)**을 붙여서 속성 값을 계산한다. 이것이 **구문 지시 정의(syntax-directed definition)**다.

파스 트리 노드 N에서 속성 a의 값이 N의 자식 노드(와 N 자신)의 속성 값으로 결정되면, 그 속성을 **합성 속성(synthesized attribute)**이라 한다. 합성 속성은 트리의 **상향식(bottom-up)** 순회로 계산할 수 있다.

중위 → 후위 번역을 위한 구문 지시 정의:

| 프로덕션              | 시맨틱 규칙                       |
| --------------------- | --------------------------------- |
| `expr → expr₁ + term` | `expr.t = expr₁.t ‖ term.t ‖ '+'` |
| `expr → expr₁ - term` | `expr.t = expr₁.t ‖ term.t ‖ '-'` |
| `expr → term`         | `expr.t = term.t`                 |
| `term → 0`            | `term.t = '0'`                    |
| `term → 1`            | `term.t = '1'`                    |
| ...                   | ...                               |
| `term → 9`            | `term.t = '9'`                    |

여기서 `‖`는 문자열 연결 연산자이고, 속성 *t*는 각 논터미널이 생성하는 식의 후위 표기를 나타낸다.

### 2.3.3 Simple Syntax-Directed Definitions

위 정의에는 중요한 성질이 있다. head의 번역 문자열이 body에 나타나는 논터미널의 번역을 body와 같은 순서로 연결한 것이다(추가 문자열이 끼어들 수 있음). 이런 성질을 **단순(simple)** 구문 지시 정의라 한다.

단순 구문 지시 정의는 추가 문자열만 출력하면 되므로 구현이 간단하다.

### 2.3.4 Tree Traversals

**깊이 우선 순회(depth-first traversal)**는 루트에서 시작하여 자식을 재귀적으로 방문한다. 각 노드에서 액션을 수행하는 시점에 따라:

- **전위 순회(preorder traversal)**: 노드를 처음 방문할 때 액션 수행
- **후위 순회(postorder traversal)**: 노드를 마지막으로 떠날 때 액션 수행

```
procedure visit(node N) {
    for ( each child C of N, from left to right ) {
        visit(C);
    }
    evaluate semantic rules at node N;
}
```

합성 속성은 후위 순회(bottom-up)로 계산할 수 있다.

### 2.3.5 Translation Schemes

**번역 스킴(translation scheme)**은 프로덕션 body 안에 시맨틱 액션을 삽입하여, 실행 순서를 명시적으로 지정하는 방법이다.

```
expr → expr₁ + term  { print('+') }
expr → expr₁ - term  { print('-') }
expr → term
term → 0              { print('0') }
term → 1              { print('1') }
...
term → 9              { print('9') }
```

이 스킴에서 `9-5+2`를 후위 순회하면 `95-2+`가 출력된다. 핵심은 숫자는 만나는 즉시 출력하고, 연산자는 양쪽 피연산자를 모두 처리한 후에 출력한다는 것이다.

---

## 2.4 Parsing

**파싱(parsing)**은 터미널 문자열이 문법의 시작 심볼에서 어떻게 유도되는지 알아내는 문제다. 파싱 방법은 크게 두 가지로 나뉜다.

| 방법                  | 트리 구축 방향 | 특징                            |
| --------------------- | -------------- | ------------------------------- |
| **하향식(top-down)**  | 루트 → 리프    | 손으로 구축하기 쉬움            |
| **상향식(bottom-up)** | 리프 → 루트    | 더 넓은 문법 클래스를 처리 가능 |

### 2.4.1 Top-Down Parsing

하향식 파싱은 루트(시작 논터미널)에서 출발하여 반복적으로 다음을 수행한다.

1. 논터미널 A가 레이블인 노드 N에서, A의 프로덕션 중 하나를 선택하고 자식을 구성
2. 다음으로 확장할 노드를 찾는다 (보통 가장 왼쪽의 미확장 논터미널)

입력을 왼쪽에서 오른쪽으로 스캔하면서 현재 보고 있는 터미널을 **룩어헤드(lookahead)** 심볼이라 한다.

### 2.4.2 Predictive Parsing

**재귀 하강 파싱(recursive-descent parsing)**은 각 논터미널에 하나의 프로시저를 대응시키는 하향식 파싱 방법이다. 그중 룩어헤드 심볼만으로 프로덕션을 유일하게 결정할 수 있는 특별한 형태를 **예측 파싱(predictive parsing)**이라 한다.

예측 파서의 의사 코드:

```java
void stmt() {
    switch (lookahead) {
        case expr:
            match(expr); match(';'); break;
        case if:
            match(if); match('('); match(expr); match(')'); stmt();
            break;
        case for:
            match(for); match('(');
            optexpr(); match(';'); optexpr(); match(';'); optexpr();
            match(')'); stmt(); break;
        case other:
            match(other); break;
        default:
            report("syntax error");
    }
}
```

예측 파싱의 핵심은 **FIRST 집합**이다. 문자열 α에 대해 FIRST(α)는 α에서 유도할 수 있는 문자열의 첫 번째 터미널의 집합이다. 동일 논터미널의 두 프로덕션 body α, β에 대해 FIRST(α)와 FIRST(β)가 서로소(disjoint)이면 룩어헤드로 프로덕션을 유일하게 선택할 수 있다.

### 2.4.3 When to Use ε-Productions

논터미널에 ε-프로덕션과 다른 프로덕션이 있을 때, 룩어헤드 심볼이 다른 프로덕션의 FIRST 집합에 속하지 않으면 ε-프로덕션을 기본(default)으로 사용한다.

### 2.4.4 Designing a Predictive Parser

예측 파서를 설계하는 규칙:

1. 룩어헤드 심볼로 사용할 프로덕션을 결정한다. body α가 ε이 아닌 프로덕션은 룩어헤드가 FIRST(α)에 속할 때 사용하고, ε-프로덕션은 다른 어떤 프로덕션도 적용 불가능할 때 사용한다.
2. 선택한 프로덕션의 body를 왼쪽부터 "실행"한다. 논터미널은 해당 프로시저를 호출하고, 터미널은 룩어헤드와 매칭한다.

### 2.4.5 Left Recursion

재귀 하강 파서는 **좌재귀(left recursion)** 프로덕션에서 무한 루프에 빠진다. `expr → expr + term`에서 _expr_ 프로시저가 자기 자신을 먼저 호출하는데, 입력을 소비하지 않으므로 같은 호출이 무한 반복된다.

좌재귀를 제거하려면 `A → Aα | β`를 다음과 같이 변환한다.

```
A → βR
R → αR | ε
```

예를 들어:

```
expr → expr + term | expr - term | term
```

이것을 변환하면:

```
expr → term rest
rest → + term rest | - term rest | ε
```

변환 전 좌재귀는 왼쪽으로 자라는 트리를, 변환 후 우재귀는 오른쪽으로 자라는 트리를 만든다.

---

## 2.5 A Translator for Simple Expressions

앞의 세 절(구문 정의, 구문 지시 번역, 파싱)의 기법을 결합하여, 중위 수식을 후위 표기로 변환하는 Java 프로그램을 구성한다.

### 2.5.1 Abstract and Concrete Syntax

**추상 구문 트리(abstract syntax tree)**에서 내부 노드는 연산자, 자식은 피연산자다. 파스 트리와 비슷하지만, _term_, _factor_ 같은 "도우미" 논터미널이 생략된다.

`9-5+2`의 추상 구문 트리:

```
      +
     / \
    -    2
   / \
  9    5
```

파스 트리는 **구체 구문 트리(concrete syntax tree)**라고도 한다. 번역 스킴은 파스 트리가 구문 트리에 최대한 가까운 문법에 기반하는 것이 바람직하다.

### 2.5.2 Adapting the Translation Scheme

좌재귀 제거를 번역 스킴(시맨틱 액션 포함)에도 적용한다. 핵심은 시맨틱 액션을 터미널처럼 취급하여 함께 변환하는 것이다.

원래 스킴:

```
expr → expr₁ + term  { print('+') }
     | expr₁ - term  { print('-') }
     | term
```

좌재귀 제거 후:

```
expr → term rest
rest → + term { print('+') } rest
     | - term { print('-') } rest
     | ε
```

`{ print('+') }`의 위치가 *term*과 _rest_ 사이에 있다는 점이 중요하다. 만약 _rest_ 뒤로 옮기면 `9-5+2`가 `952+-`(= `9-(5+2)`의 후위 표기)로 잘못 번역된다.

### 2.5.3 Procedures for the Nonterminals

변환된 스킴을 구현하는 프로시저:

```java
void expr() {
    term(); rest();
}

void rest() {
    if (lookahead == '+') {
        match('+'); term(); print('+'); rest();
    } else if (lookahead == '-') {
        match('-'); term(); print('-'); rest();
    } else { } // ε, do nothing
}

void term() {
    if (lookahead is a digit) {
        t = lookahead; match(lookahead); print(t);
    } else report("syntax error");
}
```

### 2.5.4 Simplifying the Translator

두 가지 단순화를 적용한다.

1. **꼬리 재귀 제거**: *rest*의 재귀 호출이 마지막 문장이므로(꼬리 재귀) while 루프로 대체할 수 있다.
2. **프로시저 통합**: *rest*를 *expr*에 인라인한다.

### 2.5.5 The Complete Program

최종 Java 프로그램:

```java
import java.io.*;
class Parser {
    static int lookahead;

    public Parser() throws IOException {
        lookahead = System.in.read();
    }

    void expr() throws IOException {
        term();
        while(true) {
            if( lookahead == '+' ) {
                match('+'); term(); System.out.write('+');
            }
            else if( lookahead == '-' ) {
                match('-'); term(); System.out.write('-');
            }
            else return;
        }
    }

    void term() throws IOException {
        if( Character.isDigit((char)lookahead) ) {
            System.out.write((char)lookahead); match(lookahead);
        }
        else throw new Error("syntax error");
    }

    void match(int t) throws IOException {
        if( lookahead == t ) lookahead = System.in.read();
        else throw new Error("syntax error");
    }
}

public class Postfix {
    public static void main(String[] args) throws IOException {
        Parser parse = new Parser();
        parse.expr(); System.out.write('\n');
    }
}
```

이 프로그램은 `9-5+2`를 입력받아 `95-2+`를 출력한다.

---

## 2.6 Lexical Analysis

**어휘 분석기(lexical analyzer)**는 입력에서 문자를 읽어 **토큰(token)** 객체로 그룹화한다. 토큰은 터미널 심볼과 속성 값으로 구성된다. 단일 토큰을 구성하는 입력 문자 시퀀스를 **렉심(lexeme)**이라 한다.

### 2.6.1 Removal of White Space and Comments

대부분의 언어는 토큰 사이에 공백, 탭, 개행을 허용한다. 어휘 분석기에서 이를 제거하면 파서가 처리할 필요가 없다.

```
for ( ; ; peek = next input character ) {
    if ( peek is a blank or a tab ) do nothing;
    else if ( peek is a newline ) line = line + 1;
    else break;
}
```

### 2.6.2 Reading Ahead

어휘 분석기는 토큰을 결정하기 위해 한 문자를 **미리 읽기(read ahead)**해야 할 수 있다. 예를 들어 `>`를 보면 다음 문자가 `=`인지 확인해야 `>=`인지 `>`인지 구별할 수 있다.

변수 *peek*에 다음 입력 문자를 미리 읽어두고, `*` 같은 연산자는 미리 읽기 없이 바로 식별한다.

### 2.6.3 Constants

숫자 시퀀스를 만나면 정수 값으로 조합하여 **num** 토큰으로 반환한다.

```
if ( peek holds a digit ) {
    v = 0;
    do {
        v = v * 10 + integer value of digit peek;
        peek = next input character;
    } while ( peek holds a digit );
    return token ⟨num, v⟩;
}
```

예를 들어 `31 + 28 + 59`는 `⟨num, 31⟩ ⟨+⟩ ⟨num, 28⟩ ⟨+⟩ ⟨num, 59⟩`로 변환된다.

### 2.6.4 Recognizing Keywords and Identifiers

**키워드(keyword)**와 **식별자(identifier)**를 구별하기 위해 문자열 테이블을 사용한다.

- **예약어(reserved words)**: 테이블에 키워드를 미리 등록한다
- 문자열을 읽은 후 테이블에서 검색하여, 존재하면 키워드 토큰을, 없으면 **id** 토큰을 반환한다

```
if ( peek holds a letter ) {
    collect letters or digits into a buffer b;
    s = string formed from the characters in b;
    w = token returned by words.get(s);
    if ( w is not null ) return w;
    else {
        Enter the key-value pair (s, ⟨id, s⟩) into words
        return token ⟨id, s⟩;
    }
}
```

### 2.6.5 A Lexical Analyzer

토큰 클래스 계층:

| 클래스             | 필드          | 설명                         |
| ------------------ | ------------- | ---------------------------- |
| Token              | int tag       | 토큰 종류 (파싱 결정에 사용) |
| Num extends Token  | int value     | 정수 값                      |
| Word extends Token | String lexeme | 예약어 및 식별자의 렉심      |

`Tag` 클래스에서 `NUM = 256`, `ID = 257`, `TRUE = 258`, `FALSE = 259` 등 256 이상의 정수를 터미널 상수로 사용한다 (255 이하는 ASCII 문자 자체가 토큰).

Lexer 클래스는 `scan()` 함수에서 공백 건너뛰기, 숫자 처리, 키워드/식별자 처리, 단일 문자 토큰 처리를 순서대로 수행한다.

---

## 2.7 Symbol Tables

**심볼 테이블(symbol table)**은 식별자의 문자열(렉심), 타입, 저장 위치 등 정보를 보관하는 데이터 구조다.

### 2.7.1 Symbol Table Per Scope

블록이 중첩될 수 있으므로, 같은 이름의 식별자가 서로 다른 스코프에서 다른 의미를 가질 수 있다. **가장 가까운 중첩 규칙(most-closely nested rule)**에 따라, 이름 x의 사용은 x를 포함하는 가장 안쪽 블록의 선언을 참조한다.

이 규칙은 심볼 테이블을 **체이닝(chaining)**하여 구현한다. 중첩 블록의 테이블이 바깥 블록의 테이블을 가리킨다.

```
{ int x; char y; { bool y; x; y; } x; y; }
```

이 입력에서 안쪽 블록의 `y`는 `bool` 타입이고, 바깥 블록의 `y`는 `char` 타입이다.

### 2.7.2 The Use of Symbol Tables

`Env` 클래스로 체이닝된 심볼 테이블을 구현한다.

```java
public class Env {
    private Hashtable table;
    protected Env prev;

    public Env(Env p) {
        table = new Hashtable(); prev = p;
    }

    public void put(String s, Symbol sym) {
        table.put(s, sym);
    }

    public Symbol get(String s) {
        for( Env e = this; e != null; e = e.prev ) {
            Symbol found = (Symbol)(e.table.get(s));
            if( found != null ) return found;
        }
        return null;
    }
}
```

핵심 연산:

- **put**: 현재 테이블에 새 항목 추가
- **get**: 현재 테이블부터 체인을 따라 올라가며 식별자 검색

블록 진입 시 `top = new Env(top)`으로 새 테이블을 생성하고, 블록 탈출 시 `top = saved`로 이전 테이블을 복원한다. 테이블의 체인은 실질적으로 스택 구조를 형성한다.

---

## 2.8 Intermediate Code Generation

컴파일러 front end는 소스 프로그램의 **중간 표현(intermediate representation)**을 생성한다.

### 2.8.1 Two Kinds of Intermediate Representations

- **구문 트리(syntax tree)**: 계층적 구조. 노드가 프로그래밍 구문을 나타내고, 자식이 의미 있는 하위 구성 요소를 나타냄
- **3-주소 코드(three-address code)**: 평면적(flat) 구조. `x = y op z` 형태의 명령어 시퀀스

중간 표현을 생성하는 것 외에, front end는 소스 프로그램이 구문 및 의미 규칙을 따르는지 **정적 검사(static checking)**도 수행한다.

### 2.8.2 Construction of Syntax Trees

구문 트리에서 각 문장 구문에 대해 키워드를 연산자로 사용한다. 클래스 계층:

- `Node`: 기본 클래스
  - `Expr`: 모든 식의 기본 클래스 (Op, Rel, Num, Access 등)
  - `Stmt`: 모든 문장의 기본 클래스 (If, While, Do, Eval, Seq 등)

번역 스킴 예시 (if문):

```
stmt → if ( expr ) stmt₁    { stmt.n = new If(expr.n, stmt₁.n); }
```

문장 시퀀스는 `Seq` 노드로, 빈 문장은 `null`로 표현한다.

### 2.8.3 Static Checking

정적 검사에는 다음이 포함된다.

**L-value와 R-value**

대입의 좌변은 **l-value**(메모리 위치), 우변은 **r-value**(값)다. 식별자 `i`와 배열 접근 `a[2]`는 l-value를 가지지만, 상수 `2`는 r-value만 가진다.

**타입 검사(Type Checking)**

연산자에 피연산자의 타입이 맞는지 확인한다. 예를 들어 관계 연산자 `rel`의 두 피연산자는 같은 타입이어야 하고 결과는 boolean이다.

**강제 변환(Coercion)**

`2 * 3.14`에서 정수 `2`가 자동으로 부동소수점 `2.0`으로 변환된다.

**오버로딩(Overloading)**

Java의 `+` 연산자는 정수에는 덧셈, 문자열에는 연결 연산을 수행한다. 피연산자의 타입으로 의미가 결정된다.

### 2.8.4 Three-Address Code

구문 트리를 순회하면서 **3-주소 코드**를 생성한다. 3-주소 명령어의 형태:

| 형태               | 설명                   |
| ------------------ | ---------------------- |
| `x = y op z`       | 이항 연산              |
| `x [ y ] = z`      | 배열 원소에 저장       |
| `x = y [ z ]`      | 배열 원소 읽기         |
| `ifFalse x goto L` | x가 false이면 L로 점프 |
| `ifTrue x goto L`  | x가 true이면 L로 점프  |
| `goto L`           | 무조건 L로 점프        |
| `x = y`            | 값 복사                |

**문장의 번역**: 점프 명령어로 제어 흐름을 구현한다. if문의 경우:

```
  (expr을 x로 계산하는 코드)
  ifFalse x goto after
  (stmt₁의 코드)
after:
```

**수식의 번역**: 트리의 각 연산자 노드마다 하나의 3-주소 명령어를 생성한다. *lvalue*와 _rvalue_ 함수가 대입의 좌변/우변을 구별하여 처리한다.

예를 들어 `a[i] = 2*a[j-k]`는 다음과 같이 번역된다.

```
t3 = j - k
t2 = a [ t3 ]
t1 = 2 * t2
a [ i ] = t1
```

---

## 2.9 Summary of Chapter 2

2장에서 다룬 핵심 개념을 정리하면 다음과 같다.

- **문법(grammar)**: 프로그래밍 언어의 계층적 구조를 기술. 터미널, 논터미널, 프로덕션, 시작 심볼로 구성
- **속성(attribute)**: 프로그래밍 구문에 연관된 양. 합성 속성은 자식 노드의 속성 값으로 결정
- **어휘 분석기(lexical analyzer)**: 입력을 한 문자씩 읽어 토큰 스트림으로 변환
- **파싱(parsing)**: 터미널 문자열이 시작 심볼에서 어떻게 유도되는지 결정. 예측 파서는 각 논터미널에 프로시저를 대응시키며, 룩어헤드 하나로 프로덕션을 결정
- **구문 지시 번역(syntax-directed translation)**: 프로덕션에 규칙이나 액션을 부착. 구문 지시 정의는 속성 계산 규칙을, 번역 스킴은 시맨틱 액션의 실행 순서를 명시
- **중간 코드(intermediate code)**: 추상 구문 트리 또는 3-주소 코드. front end의 최종 산출물
- **심볼 테이블(symbol table)**: 식별자 정보를 보관. 선언 시 put, 사용 시 get으로 정보를 전달
