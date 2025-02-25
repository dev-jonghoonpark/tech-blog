---
layout: post
title: "[Java] protobuf builder 에서 null을 허용하지 않는 이유"
description: Java의 protobuf builder에서 null 값을 허용하지 않는 이유는 'null'과 'cleared'가 의미적으로 다르기 때문이며, 이는 플랫폼 독립적인 개념을 고려한 결과입니다. null을 설정하면 NullPointerException이 발생하고, 이는 혼란을 초래할 수 있습니다. 프로토콜 버퍼는 기본값 개념을 가지고 있어 null을 설정하면 해당 필드에 접근 시 기본값이 반환됩니다. 이에 대한 대안으로 명시적으로 null을 처리하는 함수 제안이 있지만, 현재까지 수용되지 않고 있습니다.
categories: [스터디-자바]
tags:
  [
    자바,
    java,
    protobuf,
    builder,
    "null",
    cleared,
    set,
    exception,
    NullPointerException,
    NPE,
    language,
    c++,
  ]
date: 2024-04-19 13:00:00 +0900
---

protobuf 라이브러리를 통해 생성된 builder 를 통해서 인스턴스를 생성할 때 null값을 입력하면 에러가 발생된다.
optional 이여도 마찬가지이다. 최근에 디버깅을 하다가 이러한 이유로 인해 조금 헤맸던 경험을 하였다.

생성된 builder를 열어보면 다음과 같이 null이 들어왔을 때 NullPointerException 이 나오게 처리되어 있다는 것을 확인할 수 있다.

![builder set example](/assets/images/2024-04-19-java-why-protobuf-builder-not-allow-null/builder-set-example.png)

자바 개발자 입장에서는 set 하는 부분에서 null이 들어간다고 해서 NullPointerException 이 발생되도록 하는 것이 일반적으로 잘 이해되는 구조는 아닐 것이다.
나 역시도 그랬고, 그래서 왜 그렇게 처리했는지 확인해보려고 했다. 기회가 된다면 풀리퀘스트를 할수도 있지 않을까 생각하면서.

관련되어 찾다보니 아래 글들을 찾을 수 있었다.

- [github - Builder set methods null friendly](https://github.com/protocolbuffers/protobuf/issues/1451)
- [google groups - why protobuf optional field does not take null](https://groups.google.com/g/protobuf/c/KcLoxlJGVMY/m/KiBtdlZHPnMJ)
- [stackoverflow - Handling null values in protobuffers](https://stackoverflow.com/questions/21227924/handling-null-values-in-protobuffers)

정리해보자면 해당 부분은 의도된 것이며, protobuf의 member 개발자는 해당 api를 바꿀 계획이 없다는 것을 언급 하였다.

![comment of member](/assets/images/2024-04-19-java-why-protobuf-builder-not-allow-null/comment-of-member.png)

이유에 대해서는 다음과 같이 소개 해두었다.

> Problem is that 'null' and 'cleared' are semantically different things.
>
> Sometimes in the software world they're used to mean the same thing but protocol buffers shouldn't follow that, because that notion is not universal if you think platform independently. In C++ for instance, you won't deal with a 'NULL' string (unlike Java, no pointers, pardon, references are used there).
>
> Note, that protocol buffers have as well the notion of 'default values'.
>
> So if you set a field to 'null' but meaning to clear it, then accessing that field will return the default value.
> This is confusing at best.

번역해보면 다음과 같다.

> 문제는 'null'과 'cleared'가 의미적으로 다르다는 것입니다.
>
> 때로는 소프트웨어 세계에서 둘을 같은 것으로 사용하지만, 그러한 개념이 보편적이지 않기 때문에 프로토콜 버퍼는 따르지 않습니다. 플랫폼 독립적으로 생각한다면 이러한 개념은 일관성이 없습니다. 예를 들어, C++에서는 'NULL' 문자열을 다루지 않습니다 (Java와는 달리 포인터가 아닌 참조가 사용됩니다).
>
> 또한, 프로토콜 버퍼에는 '기본 값'의 개념도 있습니다. 따라서 필드를 'null'로 설정하지만 지우려는 경우에는 해당 필드에 접근하면 기본값이 반환됩니다. 이는 혼란스러울 수 있습니다.
>
> 이러한 이유로 플랫폼 독립적인 개념을 고려할 때, 'null'이 자동으로 필드를 지우는 것을 마법처럼 처리하는 대신 명시적으로 처리하는 것이 더 나은 것 같습니다.

---

그래서 이에 대한 대안으로 명시적으로 null을 처리할 수 있는 함수를 따로 만들면 어떻겠냐는 다양한 의견이 있지만, 아직까지는 수용되지는 않은 것으로 보인다.

![one of the comments for improvement](/assets/images/2024-04-19-java-why-protobuf-builder-not-allow-null/comment-for-improvement.png)

이도 마찬가지로 플랫폼에 특정되지 않는다는 원칙에 의한것이 아닐까 생각된다.
