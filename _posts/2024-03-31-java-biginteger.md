---
layout: post
title: "BigInteger 의 내부는 어떤 식으로 동작할까?"
categories: [스터디-자바]
tags:
  [
    자바,
    java,
    임의 정밀도,
    arbitrary-precision,
    primitive,
    int,
    long,
    BigInteger,
  ]
date: 2024-03-31 17:00:00 +0900
---

## 개요

java의 int는 4byte의 크기를 가진다. long은 8byte의 크기를 가진다.

| 타입 | 메모리 크기 | 범위                                                                        |
| ---- | ----------- | --------------------------------------------------------------------------- |
| int  | 4byte       | -2^31 ~ (2^31 - 1) / -2,147,483,648 ~ 2,147,483,647                         |
| long | 8byte       | -2^63 ~ (2^63 - 1) / -9,223,372,036,854,775,808 ~ 9,223,372,036,854,775,807 |

그럼 그보다 큰 수는 어떻게 표현할까?

## 본문

자바에서는 이러한 사이즈 제한을 벗어나야 할 때 biginteger를 사용한다.

### 임의 정밀도 (arbitrary-precision)

biginteger 와 bigdecimal에 대한 정보를 찾아보면 임의 정밀도에 대한 내용이 나온다. 임의 정밀도에 대한 부분을 먼저 찾아보면 다음같은 설명을 찾아볼 수 있다. (출처 : wikipedia)

> In computer science, **arbitrary-precision** indicates that calculations are performed on numbers whose digits of precision are limited only by the available memory of the host system

쉽게 이야기 하면 메모리에 의한 제한이 아니라면 얼마든지 큰 자리수를 저장할 수 있는 방식이다.

자바에서는 이것을 어떤 방식으로 달성하였는지 클래스 내부를 살펴보자.

### biginteger

Immutable arbitrary-precision integers

big integer 는 불변 객체이다.

BigInteger 클래스는 다음과 같은 변수를 가지고 있다.

> 쉽게 이해할 수 있도록 PlusOne, PlusTwo 를 제외하고 설명한다. 이에 대해서는 하단에 추가적으로 정리한다.

bitCount, bitLength, lowestSetBit, firstNonzeroIntNum 의 경우 lazy하게 필요할때만 값이 할당된다.

- signum
  - 부호, 양수이면 1, 음수이면 -1, 0일경우 0 으로 설정한다.
- mag
  - mag는 int 배열이다.
  - 실제 값을 담기위해 사용한다.
- bitCount
  - 양수일 경우 : 1인 bit의 수
  - 음수일 경우 : 1인 bit의 수 + 뒤에서부터 첫 1이 나올때까지의 0의 갯수 (numberOfTrailingZeros) - 1
- bitLength
  - 양수일 경우 : bit 길이
  - 음수일 경우 : bit 길이 (값이 2의 n승 일 경우 - 1 처리한다.)
    - 예를들어 `-1 00000000000000000000000000000000(2)` 의 경우 bitLength 값이 33이 아닌 32가 된다.
- lowestSetBit : 뒤에서부터 첫 1이 나올때까지의 0의 갯수 (numberOfTrailingZeros)
- firstNonzeroIntNum : 뒤에서부터 몇번째 mag item 부터 값이 시작되는지 (1이 들어있는지)
  - 음수일때만 사용된다
  - 예를들어 `-1 00000000000000000000000000000000(2)` 의 경우 firstNonzeroIntNum 값이 1이 된다.

#### 64

![debug biginteger 64](/assets/images/2024-03-31-java-biginteger-bigdecimal/debug_biginteger_+64.png)

- signum = 1
- mag[0] = 1000000(64)
- bitCount = 1
- bitLength = 7
- lowestSetBit = 6
- firstNonzeroIntNum = 0 (양수이므로 사용되지 않기때문에 0이다.)

#### -64

![debug biginteger -64](/assets/images/2024-03-31-java-biginteger-bigdecimal/debug_biginteger_-64.png)

- signum = -1
- mag[0] = 1000000(64)
- bitCount = 6
  - 1의 갯수 : 1개
  - 뒤에서부터 첫 1이 나올때까지의 0의 갯수 : 6개
  - \> 1의 갯수 + 뒤에서부터 첫 1이 나올때까지의 0의 갯수 - 1 = 1 + 6 - 1 = 6
- bitLength = 6
  - 64는 `2의 n승`에 해당되므로 -1 처리한다.
- lowestSetBit = 6
- firstNonzeroIntNum = 0 (mag[0]에 값이 0이 아니기 때문에 0)

#### bitCount와 bitLength 의 차이

- bitCount : bit이 1로된 숫자의 갯수
- bitLength : 전체 bit의 수

#### 왜 PlusOne 과 PlusTwo 가 붙는걸까?

이 이유를 찾으려고 정말 많은 시간이 들었다. 해당 변경은 java 9 로 넘어가면서 진행되었다.

- [java 8 : BigInteger](https://github.com/AdoptOpenJDK/openjdk-jdk8u/blob/2544d2a351eca1a3d62276f969dd2d95e4a4d2b6/jdk/src/share/classes/java/math/BigInteger.java)
- [java 9 : BigInteger](https://github.com/AdoptOpenJDK/openjdk-jdk9/blob/f00b63d24697cce8067f468fe6cd8510374a46f5/jdk/src/java.base/share/classes/java/math/BigInteger.java)

근데 java 8 때도 일단 deprecated 되어 있다는 것을 확인할 수 있었다. (java 6 까지도 확인해봤는데 이때도 deprecated 였다. 꽤 오랜 세월동안 deprecated 상태였나보다.) 비교해 본 결과 로직은 변경되지 않았고, 이름을 좀 더 명확하게 하기 위해서 java9 부터 이름을 변경한 것 같다.

```java
public int bitCount() {
    int bc = bitCountPlusOne - 1;
    if (bc == -1) {

        // 중략 ...

        bitCountPlusOne = bc + 1;
    }
    return bc;
}
```

biginteger 에서는 성능을 위해서 필요시에 값을 갱신하는 방식을 채택하였다.

그래서 1 더 추가한 상태로 보관하고, 함수가 호출되었을 때 -1 하고 함수가 끝나기 전에 +1 해서 저장을 한다.
그러면 bit가 없는 0이 들어왔다고 하더라도 bc 값은 -1 이 아닌 0이 되기 때문에 다시 계산할 필요 없이 그냥 bc를 반환하면 된다.

## 정리

BigInteger의 내부 변수들의 상태가 어떻게 변경되는지 확인하였으나, 왜 이렇게 작성된 것인지는 다음에 기회가 되면 더 파봐야 할 것 같다.

## 참고

- [BigInteger](https://docs.oracle.com/javase/8/docs/api/java/math/BigInteger.html)
