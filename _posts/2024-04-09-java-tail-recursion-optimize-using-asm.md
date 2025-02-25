---
layout: post
title: "[Java] tail recursion 최적화하기 (using asm)"
description: 자바에서 tail recursion 최적화를 구현하는 방법을 소개합니다. 기본적으로 자바의 재귀 함수는 스택 오버플로우 문제를 일으킬 수 있으며, javac는 tail recursion 최적화를 지원하지 않습니다. 그러나 ASM 라이브러리를 사용하면 최적화를 수행할 수 있습니다. 이 글에서는 factorial 함수를 tail recursion 형태로 수정하고, ASM을 통해 최적화된 클래스를 생성하는 방법을 설명합니다. 최적화된 클래스 파일을 실행하는 방법과 Gradle 설정에 대한 정보도 포함되어 있습니다. 자세한 내용은 GitHub에서 확인할 수 있습니다.
categories: [스터디-자바]
tags: [자바, java, asm, bytecode, class, classpath, classfile, optimize]
date: 2024-04-09 21:30:00 +0900
---

자바에서 factorial 코드를 작성해보면 다음과 같은 코드가 나올 것이다.

```java
// version 1
public static long factorial(long n) {
    if (n <= 0) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```

이 코드는 n이 100,000 정도 들어오게 되면 StackOverFlow가 발생된다. 스택에 계속 데이터가 쌓이는 구조이기 때문이다.

이런 문제를 해결하기 위해 tail recursion optimize 라는 것을 지원하는 언어들이 있다.

tail recursion 은 resursion(재귀)의 한 형태이다. 단, 추가적인 연산이 없도록 한 형태이다.

위에서 작성한 factorial 코드를 tail recursion 형태로 되게 하려면 다음과 같이 수정하면 된다.

```java
// version 2
public static long factorial(long n) {
    if (n <= 0) {
		return 1;
	}
    return helpFact(n, 1);
}

private static long helpFact(long i, long j) {
    if (i == 0) {
		return j;
	}
    return helpFact(i - 1, i * j);
}
```

그러면 이제 최적화가 되었을까? 이를 확인하기 위해 n에 다시 100,000 을 넣고 동작시켜보면 아쉽게도 동일하게 StackOverFlow가 발생된다.
이유는 단순하다. java에서 recursion optimize를 지원하지 않기 때문이다.

Wellgrounded java developer 를 읽다보면 다음과 같은 내용이 나온다. (15.2)

> Now for the bad news: javac does not perform this operation automatically, despite it being possible. This is yet another example of how the compiler tries to translate Java source into bytecode as exactly as possible.
>
> \[NOTE] In the Resources project that accompanies this book is an example of how to use the ASM library to generate a class that implements the previous bytecode sequence because javac will not emit it from recursive code.

요약하면 javac는 기본적으로 tail recursion 최적화를 지원해주지 않는다는 것이다. 그럼에도 불구하고 아예 불가능하지는 않다. asm 라이브러리를 통해서 최적화를 할 수 있다.

> asm 라이브러리는 바이트코드 조작 및 분석 프레임워크이다.

asm 라이브러리를 통해 tail recursive를 최적화 한 예제는 [https://github.com/well-grounded-java/resources/blob/main/Ch15/src/main/java/ch15/TailRecASM.java](https://github.com/well-grounded-java/resources/blob/main/Ch15/src/main/java/ch15/TailRecASM.java) 에서 확인할 수 있다.

<script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fwell-grounded-java%2Fresources%2Fblob%2Fmain%2FCh15%2Fsrc%2Fmain%2Fjava%2Fch15%2FTailRecASM.java&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>

위 코드를 실행시키면 TailRecFactorial 이라는 클래스 파일이 나온다. 이 클래스는 tail recursive가 적용된 클래스파일이다.

```sh
java TailRecFactorial 100000
```

다음과 같이 실행시키면 0 이라는 값이 나오면 성공이다. 더 큰 값도 충분히 허용된다.

---

그런데 asm을 통해 생성된 class 파일을 실제로 사용하려면 어떻게 해야할까?

이 질문에 대한 답을 찾아보려고 했으나 적절한 답이 나오지 않았고 직접 한참 시도해본 결과 다음과 같이 구성하는데 성공하였다.

![run](/assets/images/2024-04-09-java-tail-recursion-optimize-using-asm/run.png)

gradle에 아래와 같이 설정 한 후

```java
sourceSets {
    main {
        java {
            srcDir("$projectDir/asm")
        }
    }
}

repositories {
    mavenCentral()
}

dependencies {
    runtimeOnly(files("$projectDir/asm"))

    implementation("org.ow2.asm:asm:9.6")

    testImplementation(platform("org.junit:junit-bom:5.9.1"))
    testImplementation("org.junit.jupiter:junit-jupiter")
}
```

TailRecASM.java 에서 생성되는 `TailRecFactorial.class` 의 패키지를 `org.example.util` 로 수정해주었다. 또한 asm path로 파일을 생성하도록 하였다. 이후에 build 폴더에도 생성된 `TailRecFactorial.class` 를 올바른 경로에 복사해준다.

그러면 실행이 된다.

작업물은 깃헙 [dev-jonghoonpark/java-tail-recursion-optimize-using-asm](https://github.com/dev-jonghoonpark/java-tail-recursion-optimize-using-asm)에서 확인할 수 있다.
