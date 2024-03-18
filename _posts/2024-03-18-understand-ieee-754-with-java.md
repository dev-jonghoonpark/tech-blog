---
layout: post
title: "컴퓨터에서 소수를 표현하는 방법 이해하기 (IEEE 754) with java"
categories: [스터디-자바, 스터디-CS]
tags: [
    IEEE 754
    실수,
    소수,
    decimal,
    부동소수점,
    floating point,
    이진법,
    binary,
    지수,
    exponent,
    가수,
    fraction,
    java,
    CS,
  ]
date: 2024-03-18 23:00:00 +0900
---

컴퓨터에서 소수를 어떻게 표현할 수 있을까?

## 부동소수점

[부동소수점](https://ko.wikipedia.org/wiki/%EB%B6%80%EB%8F%99%EC%86%8C%EC%88%98%EC%A0%90)은 실수를 컴퓨터상에서 근사하여 표현할 때 소수점의 위치를 고정하지 않고 그 위치를 나타내는 수를 따로 적는 것으로, 유효숫자를 나타내는 가수(假數, fraction)와 소수점의 위치를 풀이하는 지수(指數, exponent)로 나누어 표현한다.

> 실수 : 수학에서 실수(實數, 영어: real number)는 주로 실직선 위의 점 또는 십진법 전개로 표현되는 수 체계이다.

## IEEE 754

[IEEE 754](https://ko.wikipedia.org/wiki/IEEE_754)는 컴퓨터에서 부동소수점을 표현하는 가장 널리 쓰이는 표준이다.

> 가수 (fraction) : 유효숫자를 표현하는데 사용

> 지수 (exponent) : 소수점의 위치를 표현하는데 사용

### 구조

IEEE 754의 부동소수점 표현은 크게 세 부분으로 구성되는데

최상위 비트는 부호(sign)를 표시하는 데 사용되며, 지수 부분(exponent)과 가수 부분(fraction)이 있다.

![General_floating_point](/assets/images/2024-03-18-understand-ieee-754-with-java/General_floating_point_ko.svg)

주로 32비트 단정밀도(single-precision) 와 64비트 배정밀도(double-precision) 가 사용된다.

![single-precision](/assets/images/2024-03-18-understand-ieee-754-with-java/IEEE_754_Single_Floating_Point_Format.svg)

![double-precision](/assets/images/2024-03-18-understand-ieee-754-with-java/IEEE_754_Double_Floating_Point_Format.svg)

### 변환 과정 (+예시)

−118.625(십진법)를 32비트 단정밀도로 표현해 보자.

1. 음수이므로, 부호부는 1이 된다.

2. 그 다음, 절댓값을 이진법으로 나타내면 1110110.101(2)이 된다. (소수 부분을 이진법으로 나타내는 방법이 익숙하지 않다면 아래에 걸어둔 링크를 참고하자.)

3. 소수점을 왼쪽으로 이동시켜, 왼쪽에는 1만 남게 만든다. 예를 들면 1110110.101(2)=1.110110101(2)×2⁶ 과 같다. 이것을 정규화된 부동소수점 수라고 한다.

4. 가수부는 소수점의 오른쪽 부분으로, 부족한 비트 수 부분만큼 0으로 채워 23비트로 만든다. 결과는 11011010100000000000000 이 된다.

5. 지수는 6이다. 이 때 Bias를 더해야 한다. 32비트 IEEE 754 형식에서는 Bias는 127이므로 6+127 = 133이 된다. 이진법으로 변환하면 10000101(2)이 된다. (bias에 대한 부분은 바로 아래에서 구체적으로 설명한다.)

이 결과를 정리해서 표시하면 다음과 같다.

![Float_point_example_frac](/assets/images/2024-03-18-understand-ieee-754-with-java/Float_point_example_frac.svg)

### bias

bias를 쓰는 이유는 음수를 위한 별도의 bit 없이 음수를 표현하기 위해서이다.

single-precision 에서 지수부는 8bit 이므로 bias 값이 127 이고, double-precision 에서 지수부는 11bit 이므로 bias 값이 1023 이다. (맨 앞자리가 0이고 나머지 값이 1인 상태를 생각하면 된다.)

### 소수를 이진법으로 나타내기

[https://woo-dev.tistory.com/93](https://woo-dev.tistory.com/93) 이 블로그에서 쉽게 설명되어 있는 것 같아 참고하면 될 것 같다.

### Java 의 경우

Java의 경우에도 IEEE 754 규칙을 따라 소수를 처리한다.

**float**은 single-precision 을, **double**은 double-precision 을 따른다.

출처 : [https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/datatypes.html)

### 번외 : 순환소수는 어떻게 처리될까?

1/3 을 예시로 살펴보자. 소수로 나타내면 0.333333... 이다.

이를 확인하기 위해 java에서 다음과 같은 코드를 작성해보았다.

```java
public static void formatFloatingPointBinary(String floatingPointBinaryString) {
    int leftPad = 64 - floatingPointBinaryString.length();
    while (leftPad > 0) {
        floatingPointBinaryString = "0" + floatingPointBinaryString;
        leftPad--;
    }
    System.out.println(floatingPointBinaryString.charAt(0) + " " + floatingPointBinaryString.substring(1,12) + " " + floatingPointBinaryString.substring(12));
}
```

```java
formatFloatingPointBinary(Long.toBinaryString(Double.doubleToLongBits((double) 1/3)));
formatFloatingPointBinary(Long.toBinaryString(Double.doubleToLongBits((double) - 1/3)));
```

결과는 다음과 같다.

```
0 01111111101 0101010101010101010101010101010101010101010101010101
1 01111111101 0101010101010101010101010101010101010101010101010101
```

1. 앞에 부호에 따라 첫번째 bit를 설정한다.
2. 0.33333... 을 이진법으로 나타내면 0.010101...(2) 으로 바꿀 수 있다.
3. 이 상태에서 정규화를 하면 1.010101...(2)×2<sup>-2</sup> 가 된다.
4. 가수부는 소수점의 오른쪽 부분으로, 부족한 비트 수 부분만큼 0으로 채워 52비트로 만든다.
   (여기서는 순환소수이기 때문에 계속 01 로 반복되어 채우면 된다.) 저장될 수 있는 유효한 비트 수를 넘어선 경우 넘어선 비트는 생략한다.
   (이러한 경우에 근사값을 사용하게 되는 것이기 때문에 오차가 발생된다.)
   최종적으로 가수부는 `0101010101...(52bit)` 이 된다.
5. 지수는 -2이다. 이 때 Bias를 더해야 한다. 64비트 IEEE 754 형식에서는 Bias는 1023이므로 -2 + 1023 = 1021이 된다. 이진법으로 변환하면 1111111101(2)이 된다.

따라서 최종적으로 java에서 출력했던 값과 동일한 결과가 나오게 된다.

## 자료 출처

위키피디아
