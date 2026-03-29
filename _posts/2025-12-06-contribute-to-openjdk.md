---
layout: "post"
title: "OpenJDK 기여하기"
description: "DevFest 2025 Incheon에서 발표한 OpenJDK 기여 경험을 정리한 글입니다. OpenJDK Author가 되기까지의 과정, 기여 방법, 빌드 환경 구성, 이슈 선택부터 PR 제출까지의 전체 워크플로우를 소개합니다."
categories:
  - "오픈소스"
  - "발표"
tags:
  - "JDK"
  - "OpenJDK"
  - "오픈소스 기여"
  - "DevFest"
date: "2025-12-06 12:00:00"
toc: true
---

발표 했던 내용을 정리해보면 좋겠다 싶어 AI로 내용을 정리하여 기록으로 남깁니다. AI로 정리하여 일부 내용은 발표했던 내용과 다를 수 있고, 오류가 있을 수 있습니다.

---

이 글은 [DevFest 2025 Incheon](https://event-us.kr/gdgincheon/event/116226)에서 발표한 "OpenJDK 기여하기" 내용을 블로그 글로 정리한 것이다.

나는 올해 다양한 오픈소스에 기여를 해왔다. Playwright, Spring AI, GraalVM, OpenJDK 등. 그 중에서도 OpenJDK에 기여하여 한국인으로서는 몇 안 되는 OpenJDK Author 자격을 얻게 되었는데, 이 소식을 공유했을 때 생각보다 많은 관심을 받았다. 국내에서는 OpenJDK 기여가 아직 생소한 것 같아 관련된 이야기를 좀 더 나눠보고자 한다.

이 글은 OpenJDK에 어떻게 기여할 수 있는지를 소개한다. 이 글의 내용이, 누구라도 기여하고 싶다는 생각이 들었을 때 OpenJDK에 기여하는 데 도움이 되기를 바란다.

## Java와 OpenJDK

### Java는 지루하다, 그게 좋은 것이다

Java는 지루한(boring) 언어라는 이야기를 종종 듣는다. 하지만 그 지루함이야말로 Java의 강점이라고 생각한다. 큰 변화(breaking change) 없이 안정적으로 운영할 수 있다는 의미이기 때문이다.

리누스 토발즈도 Opensource Summit Korea 2025에서 이런 말을 했다.

> 저는 지루함을 좋아합니다. 그리고 저에게 지루함이란, 전 세계 수백만 명의 사람들에게 머신을 고장 낼 만한 매우 흥미로운 새로운 기능이 없는 것입니다.

안정적인 언어는 성숙한 커뮤니티와 풍부한 생태계를 만들어낸다. Java는 올해로 30주년을 맞이했다. 논란 속에서도 계속 발전하며 살아남아 왔고, LLM 시대에서도 여전히 널리 쓰이고 있다. JetBrains의 [Developer Ecosystem Survey](https://www.jetbrains.com/ko-kr/lp/devecosystem-2023/java)에서도 Java의 꾸준한 사용률을 확인할 수 있다.

### Java와 OpenJDK의 관계

Java라는 언어 자체는 오픈소스이다. 그런데 Java의 구현체에는 여러 종류가 있다.

**Oracle JDK**는 Sun Microsystems의 JDK를 Oracle이 인수한 것이다. 상업적으로 오랫동안 유료 라이선스로 제공되었으나, Java 11 이후로는 대부분의 기능이 OpenJDK와 동일해졌다.

**OpenJDK**는 Java의 오픈소스 구현체다. Java는 원래 오픈소스가 아니었는데, Sun Microsystems가 Oracle에 인수되기 전인 2006년에 OpenJDK라는 이름으로 오픈소스로 공개하기 시작했다. 요약하면, OpenJDK는 커뮤니티에서 관리하는 오픈소스 레퍼런스 구현체이고, Oracle JDK는 이를 기반으로 Oracle에서 관리하는 상용 배포판이다.

참고로 Java 유료화 논란은 Java 자체에 대한 유료화가 아니라 Oracle JDK에 대한 유료화이다. 버전/시기마다 라이선스에 변동이 있으므로 주의가 필요하다.

## OpenJDK 기여 준비하기

### OpenJDK Developer Guide

기여를 시작하기 전에 [OpenJDK Developer Guide](https://openjdk.org/guide/)를 읽어보는 것이 좋다. 분량이 꽤 있지만(약 124분 분량), 기여하면서 필요한 내용을 참고하면 된다.

Java는 수백만 명의 사람들과 수천 개의 기업이 사용하기 때문에 모든 변경 사항을 면밀히 검토한다. 그래서 아무나 바로 쉽게 기여하지는 못하게 되어 있지만, 잘 정리된 가이드 문서가 있다는 점이 좋았다.

### 역할(Role) 체계

OpenJDK에는 5가지 역할이 있다.

- **Participant**: 프로젝트에 관심을 가지고 참여하기 시작한 사람. 메일링 리스트에 가입한 사람.
- **Author**: OpenJDK 프로젝트에 최소 2건의 기여를 한 사람. 프로젝트 멤버로서 공식적으로 인정받게 되며, JBS(이슈 트래커)를 사용할 수 있다.
- **Committer**: 최소 8건의 의미있는 기여를 한 사람. 기존 Committer에게 추천을 받아야 하며, 직접 코드를 커밋할 수 있다.
- **Reviewer**: 최소 32건의 의미있는 기여를 한 사람. 기존 Reviewer에게 추천을 받아야 하며, 다른 사람의 코드를 리뷰하고 승인할 수 있다.
- **Project Lead**: 해당 프로젝트의 전반적인 방향을 결정한다. 프로젝트 멤버십을 관리하고, 기술적 결정을 내린다.

### 소통 방식

OpenJDK에서는 다음과 같은 방식으로 소통한다.

- **메일링 리스트**: OpenJDK에 참여하는 개발자들이 다양한 주제에 대해 소통하기 위해 운영하는 공개 이메일 토론 목록이다. 누군가가 메일링 리스트에 메시지를 보내면 해당 목록에 등록된 사람 모두에게 동일한 메시지가 전달된다. 각 프로젝트/모듈별로 메일링 리스트가 운영되며, [https://mail.openjdk.org/mailman/listinfo](https://mail.openjdk.org/mailman/listinfo)에서 확인할 수 있다. 처음에는 다소 낯설 수 있지만, OpenJDK 커뮤니티에서 소통하는 핵심 수단이다.
- **이슈 트래커**: JBS(JDK Bug System)라는 Jira 기반 이슈 트래커를 사용한다.
- **코드 리뷰**: GitHub PR을 통해 진행한다.

#### 메일링 리스트 활용

다른 오픈소스들은 issue 탭에서 자유롭게 이슈를 만들 수 있고, 진입 장벽이 낮은 편이지만, OpenJDK에서는 메일링 리스트를 통해 소통한다. 처음에는 낯설 수 있다.

질문하는 것을 두려워하지 말자. OpenJDK 커뮤니티는 친절하다. 단, 존중과 예의를 기반으로 소통해야 한다. 명확하고 정확한 표현을 사용하고, 글로벌 커뮤니티를 고려한 배려가 필요하다.

기여에 관심이 있다면 처음에는 어떤 이슈에 대해 작업하고 싶다는 내용의 메일을 보내보면 된다. 내가 어떤 것을 해결하고자 하는지, 그 배경과 함께 구체적으로 설명하고, 코드를 수정하여 어떤 장점이 발생하는지, 변경 후 발생되는 리스크는 없는지를 함께 작성하면 좋다.

그러면 스폰서(Sponsor)가 붙어줄 수 있다. 스폰서는 새로운 기여자가 커뮤니티에 적응할 수 있도록 돕는 역할을 한다. 이슈 생성, 코드 리뷰, 머지 등 전반적인 과정을 함께 한다.

#### PR 전에 메일링 리스트에서 확인받기

논의되지 않은 PR은 무의미할 수 있다. PR을 올리기 전에 메일링 리스트에서 먼저 의견을 구하는 것이 좋다. 기존에 같은 작업을 하고 있는 사람이 있을 수 있고, 작업 방향에 대해 미리 피드백을 받을 수 있다. 모든 아이디어가 실제로 좋은 것은 아니다. 숨겨진 제약 조건, 안정성, 유지보수성, 호환성 등 다양한 측면에서 고려되어야 하기 때문이다.

또한 기술적인 관점에서, 패치를 기여한다는 것은 예측 가능한 미래에 해당 코드를 유지 관리하겠다는 약속을 의미한다. 특히 처음 기여할 때는 메일링 리스트에서 확인을 받고 시작하는 것이 좋다.

#### OpenJDK 주요 프로젝트

메일링 리스트는 각 프로젝트/주제별로 운영된다. 참고로 OpenJDK에는 다양한 프로젝트가 있다.

- **JDK**: JDK 주요 기능 개발과 관련된 일반적인 기술 문제를 논의
- **Hotspot**: JVM 대표 구현체
- **Loom**: 가상 스레드(virtual thread) 도입으로 동시성 향상
- **Leyden**: AoT(Ahead of Time)로 시작 시간, peak 성능 도달 시간, 메모리 사용량 개선
- **Valhalla**: 값 타입(Value/Primitive class)과 Vector API로 객체 접근·메모리 효율 개선
- **Galahad**: GraalVM JIT 기술을 OpenJDK에 재통합
- **Panama**: 네이티브 라이브러리 연동을 쉽게 (JNI 대체), 메모리 접근 방식 개선

### JDK Bug System (JBS)

[JBS](https://bugs.openjdk.org/)는 OpenJDK 프로젝트에서 사용하는 이슈 트래커다. 이름에는 Bug이 들어가지만 Bug 외에도 기능 개선, task 등에도 사용된다. Jira 기반 시스템이다.

JBS는 기본적으로 공개되어 있지만, 이슈를 직접 등록하거나 수정하려면 Author 이상의 자격이 필요하다. Author가 되기 전까지는 Jira에 대한 접근 권한이 제한되어 있다.

## 이슈 찾기

### 좋은 이슈를 고르는 팁

다른 오픈소스에서는 `starter`, `good first commit` 같은 라벨이 있지만, OpenJDK에서는 그런 라벨 체계가 잘 되어 있지는 않다.

대신 다음과 같은 전략을 사용하면 좋다.

- **Priority P4~P5 이슈 노리기**: JBS에 등록된 이슈 중 Priority가 P4~P5인 이슈에서 할 만한 이슈를 골라보자. 상대적으로 난이도가 낮고 접근하기 좋다.
- **라벨과 컴포넌트 활용**: 라벨과 컴포넌트를 잘 활용하면 관심 분야에 맞는 이슈를 찾을 수 있다. JDK 내에서도 다양한 컴포넌트(라벨)가 있다.
- **Unassigned 필터 활용**: JBS 상단의 "View all issues and filters"에서 Assignee가 비어있는(Unassigned) 이슈를 필터링하면 아직 아무도 작업하지 않는 이슈를 찾을 수 있다.
- **명확한 이슈 선택**: 무엇을 해야 하는지 명확하고, 범위가 한정적이며 이해하기 쉬운 이슈를 선택하는 것이 좋다. Committer나 Reviewer들이 이미 방향을 잡아놓은 이슈라면 더 좋다.

### Author 자격 빠르게 얻기 위한 전략

Author 자격을 얻으려면 최소 2건의 PR이 머지되어야 한다. Author가 되면 JBS에 이슈를 등록하거나 수정할 수 있게 되므로, 기여가 훨씬 수월해진다.

메일링 리스트에 글을 남기는 것이 부담스러울 수 있다. 다른 오픈소스들은 쌓여있는 issue들에 댓글이라도 남길 수 있는데, OpenJDK는 그런 구조가 아니기 때문이다. 내가 택한 전략은 JBS에 생성되어 있는 일감에서 논란의 여지가 없이, 깔끔하고 명확하게 할 일이 정리된 이슈를 찾아서 작업하는 것이었다. Committer나 Reviewer들이 새로운 기여자를 위해 적절한 일감들을 남겨두기도 한다. 빠르게 Author가 되어서 JBS에 코멘트를 남길 수 있게 되는 것을 목표로 했다. 다만, 이것이 정석적인 루트는 아닐 수 있다는 점은 참고하자.

## 프로젝트 셋업

### OpenJDK는 어떤 언어로 개발되어 있나?

GitHub 기준으로 OpenJDK의 언어 비율은 대략 Java 73.9%, C++ 14.1%, C 8.0%, Assembly 2.7%, 기타 1.3% 정도이다.

- JVM은 C++/C/어셈블리로 작성되어 있다.
- 표준 라이브러리는 Java로 작성되어 있다.
- C1/C2 컴파일러는 C++로 작성되어 있다. (Graal 컴파일러는 Java)

여러 언어를 다룰 수 있지만, Java 표준 라이브러리 쪽에 기여한다면 Java만 알아도 충분하다.

### 빌드 환경 구성

OpenJDK를 빌드하려면 다음이 필요하다.

1. 소스 코드 클론
2. 빌드에 사용할 기존 JDK(Boot JDK) 설치. `JAVA_HOME`으로 설정하거나, configure 시 `--with-boot-jdk` 옵션으로 지정할 수 있다.
3. 관련 라이브러리 설치 및 configure, make 실행

```bash
# linux
sudo apt-get install autoconf zip make gcc g++ libx11-dev libxext-dev libxrender-dev \
  libxrandr-dev libxtst-dev libxt-dev libcups2-dev libfontconfig1-dev libasound2-dev

# mac
sudo port install autoconf
```

```bash
bash configure
make images
```

### 테스트 실행하기

OpenJDK에서는 두 가지 테스트 도구를 사용한다. 이 도구들은 별도로 설치해야 한다.

- **jtreg**: JDK 전용 회귀 테스트 도구
- **gtest** (Google Test): C++ 테스트 프레임워크

테스트 도구를 configure에 등록한다.

```bash
bash configure \
    --with-jtreg={JTREG_PATH} \
    --with-gtest={GTEST_PATH}
```

특정 테스트를 실행하려면 다음과 같이 한다.

```bash
make run-test TEST=test/jdk/java/lang/String/
```

### Test Tier

OpenJDK 테스트는 tier1부터 tier4까지 나뉘어 있다. 숫자가 낮을수록 기본적이고 빠른 테스트이다. PR을 올리면 최소 tier1 테스트는 통과해야 한다.

```bash
make run-test TEST=tier1
```

## PR 제출 과정

### OCA 서명하기

PR을 올리기 전에 [OCA(Oracle Contributor Agreement)](https://oca.opensource.oracle.com/)에 서명해야 한다. 이를 통해 Oracle과 기여한 코드에 대한 라이선스 사용/지적재산/재기여 허락을 교환하게 된다.

OCA 서명 절차는 다음과 같다.

1. [OCA 사이트](https://oca.opensource.oracle.com/)에서 양식을 작성한다.
2. 기여할 프로젝트, GitHub 계정, 서명, 이름, 이메일, 소속 등을 입력한다.
3. 유형은 Individual과 Corporation이 있다. 본인이 만든 코드의 지적재산권(IP)을 소속 회사가 주장하는 경우 Corporation으로, 그렇지 않은 경우(학생, 프리랜서, IP를 본인이 보유하는 경우 등) Individual로 서명한다. 등록한 사람/회사는 공개된다.
4. 승인까지 보통 며칠에서 최대 몇 주 정도 소요된다. 승인 전에는 PR을 올려도 빌드가 실패한다.
5. OCA 서명이 완료되면 PR의 comment에 `/signed`라고 남기면 된다.

### PR 작성 및 리뷰

GitHub에서 OpenJDK 저장소를 fork하고, 변경사항을 작성한 후 PR을 올린다.

PR이 올라가면 bridgekeeper bot이 OCA 서명 여부를 확인하고, 자동으로 라벨을 붙인다. 이후 리뷰어들이 코드를 검토한다. 큰 프로젝트이기 때문에 리뷰어들이 꽤 꼼꼼하게 확인한다. 인내심을 가지고 기다리자.

### /integrate와 /sponsor

OpenJDK에서는 GitHub의 일반 merge 버튼 대신, 봇 커맨드를 사용하여 PR을 머지한다.

- **/integrate**: Committer 이상의 권한이 있는 사람이 자신의 PR을 머지할 때 사용한다.
- **/sponsor**: Committer가 아닌 기여자의 PR을 머지해줄 때, Committer가 이 커맨드를 사용한다.

즉, Author나 Participant인 경우 리뷰가 완료되면 `/integrate`를 입력하고, 스폰서가 `/sponsor`를 입력해야 PR이 머지된다.

## 기여 사례: JDK-8364927

실제로 내가 기여한 사례를 공유한다.

### 이슈 내용

[JDK-8364927](https://bugs.openjdk.org/browse/JDK-8364927): `TestReclaimStringsLeaksMemory.java`에 `@requires` 어노테이션을 추가하는 작업이었다.

이 테스트는 Full GC 시 interned string 메모리가 완전히 회수되는지 확인하는 스트레스 테스트다. 기존 테스트 코드는 다음과 같았다.

```java
/*
 * @test TestReclaimStringsLeaksMemory
 * @bug 8180048
 * @summary Ensure that during a Full GC interned string memory is reclaimed completely.
 * @requires vm.gc == "null"
 * @requires !vm.debug
 * @library /test/lib
 * @modules java.base/jdk.internal.misc
 * @run driver/timeout=480 gc.stress.TestReclaimStringsLeaksMemory
 * @run driver/timeout=480 gc.stress.TestReclaimStringsLeaksMemory -XX:+UseSerialGC
 * @run driver/timeout=480 gc.stress.TestReclaimStringsLeaksMemory -XX:+UseParallelGC
 * @run driver/timeout=480 gc.stress.TestReclaimStringsLeaksMemory -XX:+UseG1GC
 */
```

### 문제 발견

이 테스트에서는 기본 GC, Serial GC, Parallel GC, G1 GC 네 가지 경우를 테스트하고 있었다. 그런데 테스트에 필요한 GC를 지원하지 않는 환경에서는 어떻게 될까? 또한 ZGC나 Shenandoah GC에 대한 테스트는 빠져 있었다.

기존의 하나의 큰 테스트를 분리하여 각 GC별 테스트로 나누기로 했다.

### 리뷰 과정

처음에는 GC를 지정하지 않은 기본 테스트를 그대로 유지했는데, 리뷰어로부터 "첫 번째 테스트를 넣은 의도가 무엇인가?" 라는 질문을 받았다. 기존 테스트에 있었기 때문에 그대로 유지했다고 답변했더니, 리뷰어는 "그런 방식을 선호하지 않으니 명시적으로 케이스를 분리해달라"고 했다. 그리고 ZGC와 Shenandoah GC에 대한 테스트도 추가해달라는 요청을 받았다.

### 해결

각 GC별로 `@requires` 어노테이션을 추가하여 해당 GC가 지원되는 환경에서만 테스트가 실행되도록 수정하고, 빠져있던 GC에 대한 테스트도 추가했다.

```java
/*
 * @test id=Z
 * @bug 8180048
 * @summary Ensure that during a Full GC interned string memory is reclaimed completely with ZGC.
 * @requires vm.gc.Z
 * @requires !vm.debug
 * @library /test/lib
 * @modules java.base/jdk.internal.misc
 * @run driver/timeout=480 gc.stress.TestReclaimStringsLeaksMemory -XX:+UseZGC
 */
```

### 리뷰와 머지

리뷰어들의 Approve를 받았지만, 이 PR은 한 달이 넘도록 머지되지 못했다. 왜 머지를 안 해주시는 거지... 하고 기다리고 있었는데, 알고 보니 내가 `/integrate` 커맨드를 입력해야 했던 것이었다. 리뷰어는 "왜 integrate 요청을 안 하지?" 하고 기다리고 있었고, 나는 "왜 머지를 안 해주시는 거지?" 하고 기다리고 있었던 것이다.

`/integrate`를 입력하고 스폰서가 `/sponsor`를 입력하여 이 PR도 결국 무사히 머지되었다.

## Author 신청

### 자격 요건

OpenJDK 프로젝트에 최소 2건의 기여를 하면 Author 자격을 신청할 수 있다.

### 신청 과정

1. [OpenJDK Census](https://openjdk.org/census)에서 프로젝트 리더를 찾는다. JDK 프로젝트의 경우 Mark Reinhold이다.
2. 프로젝트 리더에게 JDK Author request 메일을 보낸다. full name, email, 그리고 기여한 PR들의 참조 링크(references)를 함께 포함한다.
3. 승인되면 "Thanks! You should receive a registration invitation shortly."와 같은 답변과 함께 OpenJDK register invitation 메일을 받게 된다.
4. username을 등록한다. username은 미리 정해져 있으며(아마 Project Lead가 설정하는 것 같다), 원하는 username이 있다면 registrar에게 변경을 요청해야 한다. 변경까지 추가 시간이 소요되므로 처음 신청할 때 미리 이야기하는 것도 좋다.
5. 등록이 완료되면 Census에서 자신의 이름을 확인할 수 있다. 2025년 11월 기준 Census에 등록된 인원은 643명이며, 그중 한국인으로 보이는 이름은 손에 꼽을 정도로 적다.

## 팁

### 오픈소스 기여 에티켓

- 다른 사람에게 할당된 이슈는 절대 처리하지 말자. 중복 작업은 무의미하다.
- 누군가에게 할당된 후 오랫동안 진행되지 않았다면, 그 사람에게 연락하여 현재 상황을 물어보자. 이전에 작업한 사람이 고민하면서 만들어 둔 반쯤 완성된 해결책이 있을 수도 있다. 그런 기반을 활용하면 이전 개발자가 이미 빠졌던 함정을 피할 수 있다.
- 봇으로 자동화된 PR을 올리거나, 무분별하게 다량의 이슈를 선점하는 것은 좋지 않다.

### rebase 사용하지 않기

OpenJDK에서는 PR이 게시된 후 rebase나 force-push를 하지 않는다. 이러한 작업은 기존 리뷰 코멘트를 무효화시키고, PR 브랜치를 가져와 리뷰하는 리뷰어의 작업 흐름을 방해할 수 있기 때문이다. 실제로 rebase를 하면 봇이 경고 메시지를 남긴다. 참고로 봇이 PR 머지 시 자동으로 모든 변경사항을 하나의 커밋으로 squash 해주기 때문에 rebase를 직접 할 필요가 없다. PR이 오래되어 충돌이 발생하면, 새 브랜치에서 작업을 다시 하는 것이 좋다.

### AI를 도구로 활용하되 대체하지 않기

AI를 활용하는 것은 좋지만, AI에 의존하는 것은 좋지 않다. AI를 도구로 사용하되, 이해하지 못한 코드를 그대로 제출하는 것은 바람직하지 않다.

### OpenJDK Mail 검색 도구

비공식이지만 [https://openjdk.barlasgarden.com](https://openjdk.barlasgarden.com)에서 OpenJDK 메일링 리스트를 편리하게 검색할 수 있다.

## 마무리

규모가 큰 프로젝트이지만, 리뷰어들의 반응속도가 굉장히 빠르고 친절하다. 봇으로 프로세스를 잘 만들어 두어서 처음에는 복잡해 보이지만 적응하면 합리적으로 보인다.

OpenJDK와 같은 큰 프로젝트에 기여할 수 있는 것은 영광스러운 일이었다. 대형 프로젝트의 프로세스를 경험해볼 수 있어서 좋았다. 많은 사람들이 오픈소스에 기여했으면 좋겠다.
