---
layout: "post"
title: "OpenJDK Project Galahad는 왜 해산되었나"
description: "OpenJDK Project Galahad가 2026년 3월 공식 해산되기까지의 흐름을 정리합니다. 2022년 GraalVM의 Java 기술을 OpenJDK 본류로 가져오겠다는 야심으로 출범한 이 프로젝트가, 2025년 9월 Oracle의 'Detaching GraalVM from the Java Ecosystem Train' 발표를 거쳐 스폰서 그룹의 철회로 어떻게 해산에 이르게 되었는지, 그리고 그 빈자리를 Project Leyden이 어떻게 채우고 있는지 살펴봅니다."
categories:
  - "오픈소스"
tags:
  - "JDK"
  - "OpenJDK"
  - "Graal"
  - "GraalVM"
  - "Leyden"
date: "2026-05-23 15:00:00"
toc: true
---

[지난 글](/2026/05/23/jdk-8382582-remove-jvmci)에서 JVMCI 제거 동향을 정리하면서, 그 결정의 가장 큰 배경 중 하나로 **Project Galahad의 해산**을 언급했다. 이번 글에서는 그 해산 자체를 더 깊이 들여다본다.

Project Galahad는 OpenJDK 커뮤니티가 GraalVM의 Java 관련 기술을 본류로 가져오려고 시작한 야심찬 프로젝트였다. 그런데 2026년 3월, 약 3년 만에 공식 해산(dissolved)되었다. 왜 이런 결정이 있었을까?

## Project Galahad는 무엇이었나

[Project Galahad](https://openjdk.org/projects/galahad/)는 2022년 12월 [메일링 리스트 제안](https://mail.openjdk.org/pipermail/discuss/2022-December/006164.html)을 거쳐 2023년 초 정식 출범한 OpenJDK 프로젝트다. 스폰서는 **HotSpot Group**이었다.

핵심 목표는 명확했다.

> "Contribute Java-related GraalVM technologies to the OpenJDK Community and prepare them for possible incubation in a JDK main-line release."

좀 더 풀어 말하면 다음과 같다.

- **GraalVM의 Java 관련 기술을 OpenJDK 본류로 기증**한다.
- 초기 초점은 **GraalVM JIT 컴파일러**를 HotSpot의 기존 JIT(C2)의 대안으로 통합하는 것.
- 이후 **Native Image** 등 AOT 관련 기술도 본류로 점진적으로 흡수.

당시 분위기에서는 충분히 그럴 만했다. Graal은 Java로 작성된 JIT 컴파일러로, JEP 243을 통해 도입된 JVMCI 위에서 동작하며 C2에 견줄 만한 peak performance를 보여주고 있었다. GraalVM Native Image는 startup time과 footprint를 극적으로 줄여주는 AOT 기술로 자리잡고 있었다. 이런 기술들이 OpenJDK 본류로 합쳐진다면 Java의 미래는 한 단계 도약할 것이라는 기대가 있었다.

## 결정적 분수령 — 2025년 9월 Oracle의 발표

상황이 뒤집힌 것은 **2025년 9월**이다. Oracle은 공식 Java 블로그에 ["Detaching GraalVM from the Java Ecosystem Train"](https://blogs.oracle.com/java/detaching-graalvm-from-the-java-ecosystem-train)라는 제목의 글을 게시했다. 제목 그대로, **GraalVM을 Java 생태계 열차에서 분리**한다는 선언이다.

핵심 내용은 다음과 같다.

### 1. GraalVM 팀의 방향 전환

GraalVM 팀은 앞으로 Java가 아닌 **Polyglot 언어 런타임 — GraalPy(Python), GraalJS(JavaScript) 등 — 에 집중**한다. 즉, GraalVM의 정체성을 "Java의 차세대 런타임"에서 "다국어 런타임"으로 재정의한 것이다.

### 2. Graal JIT의 단종

- **Oracle JDK 24가 experimental Graal JIT을 포함하는 마지막 릴리즈**가 된다.
- 즉, JDK 25부터는 `-XX:+UseGraalJIT` 같은 옵션이 더 이상 의미를 갖지 않는다.

### 3. Native Image의 단종

- Oracle Java SE Products 고객에게 제공되던 **GraalVM Early Adopter 기술(Native Image 포함)이 단계적으로 중단**된다.
- **GraalVM for JDK 24가 Oracle Java SE Products의 일부로 라이선스되는 마지막 GraalVM 릴리즈**가 된다.

### 4. 후속 권고

- AOT/startup 성능에 관심 있는 사용자에게는 **Oracle JDK 25 + [JEP 514 (AOT Command-Line Ergonomics)](https://openjdk.org/jeps/514) + [JEP 515 (AOT Method Profiling)](https://openjdk.org/jeps/515)** 사용을 권고.
- 시작 시간 단축/peak 성능 도달 시간 최적화/메모리 풋프린트 감소 같은 목표는 **Project Leyden을 통해 표준 Java의 일부**로 추진된다.

요약하면, **"GraalVM이 짊어지던 Java의 미래는 이제 본류 OpenJDK가 직접 가져간다"** 는 선언이었다.

## "Detaching"의 진짜 의미 — GraalVM이 Java를 버린 건 아니다

"Detaching from the Java Ecosystem Train"이라는 강한 표현 때문에 "오라클이 GraalVM의 Java 지원을 완전히 손 뗀 것 아니냐"고 오해하기 쉽지만, 실제 의미는 좀 더 좁다. **GraalVM이 Java를 떠난 것이 아니라, "OpenJDK 본류에 완전히 흡수되어 하나로 합쳐지려던 계획"을 철회한 것**에 가깝다.

### GraalVM의 Java 지원은 계속된다

특히 **Native Image** 쪽은 여전히 GraalVM의 핵심 자산이고, 오라클도 이를 적극적으로 지원하고 있다.

- **Native Image는 Spring Boot, Quarkus, Micronaut 같은 프레임워크 생태계의 핵심**이다. 클라우드 환경에서 startup time과 메모리 사용량을 줄이려는 모든 시나리오에서 사실상 표준 도구다.
- 오라클은 **GraalVM Free Terms and Conditions(GFTC)** 라이선스로 GraalVM을 무료로 배포하면서, Java 개발자가 Native Image를 빌드해 상용 환경에서 사용할 수 있도록 기술 지원과 업데이트를 지속한다.
- 오픈소스 트랙인 **GraalVM Community Edition** 역시 계속 유지된다.

즉, "Java 개발자 입장에서 GraalVM을 못 쓰게 되는" 변화는 아니다.

### 그럼 무엇이 바뀌었는가 — "독자 노선"으로의 전환

과거 오라클의 큰 그림은 대체로 다음과 같았다.

> "결국 HotSpot의 기본 JIT/AOT 엔진을 GraalVM 기술로 대체하여 본류와 하나로 통합한다."

Project Galahad는 이 통합을 위한 다리였다. 그런데 이 큰 그림 자체를 접고, **GraalVM을 본류와 별개의 "독자 고성능 다국어 런타임"으로 키우는 쪽**으로 방향을 튼 것이다.

이 결정의 이면에는 크게 두 가지 이유가 있어 보인다.

**1. OpenJDK와의 속도 차이**

OpenJDK는 6개월 주기로 움직이지만, 엄격한 하위 호환성과 신중한 리뷰 문화를 가진다. C2, GC, JVMTI, JFR 같은 본류 컴포넌트에 새로운 메커니즘을 끼워 넣으려면 그에 맞는 정도의 인내심과 점진적 합의가 필요하다.

반면 GraalVM 팀은 더 빠르게 기능을 추가하고 실험하고 싶어 했다. JVMCI를 본류에 둘 때 발생하던 마찰(이전 글에서 정리한 252개의 `#if INCLUDE_JVMCI`, 1.5%의 부수 비용 등)이 그 마찰의 일부를 보여준다.

**2. 다국어(Polyglot) 플랫폼이라는 본래 정체성**

GraalVM은 태생부터 Java 전용이 아니다. Python(GraalPy), JavaScript(GraalJS), Ruby, R, LLVM 기반 언어 등을 **하나의 런타임에서 함께 돌리는 다국어 플랫폼**이 그 본질이다.

이런 정체성을 가진 런타임을 "JDK의 하위 컴포넌트"로 종속시키는 것은 비즈니스/기술적으로 부자연스럽다. 오라클은 GraalVM을 본류에 흡수시키는 대신, **독자적인 고성능 다국어 플랫폼**으로 성장시키는 쪽이 더 낫다고 판단한 것으로 보인다.

### 정리: 역할 분담

결과적으로 OpenJDK와 GraalVM은 같은 문제를 다른 방식으로 접근하는, 깔끔한 역할 분담을 갖게 되었다.

| 구분          | Project Leyden (OpenJDK 표준)                           | GraalVM (독자 런타임)                                                      |
| ------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- |
| **목표**      | Java 표준 안에서 warmup/메모리 최적화                   | Java 포함 다국어 환경 최적화, 극단적 AOT 빌드                              |
| **접근 방식** | CDS, AOT 캐싱 등으로 Java의 동적 특성을 유지하며 최적화 | Closed-World Assumption 기반으로 동적 특성을 제한하고 100% 바이너리 컴파일 |
| **위상**      | 표준 Java(Java SE)의 일부                               | 독자적인 고성능 확장 플랫폼                                                |

즉, **"GraalVM이 Java를 버린 것"이 아니라, "Java 표준에 흡수되는 길 대신, Java를 매우 잘 지원하는 독자 다국어 플랫폼으로 남겠다"** 고 선언한 것이다. 백엔드 개발자 입장에서는 Spring Boot 등에서 고성능 Native Image를 빌드할 때 여전히 GraalVM을 주력으로 사용하면 된다.

## 그래서 Galahad는 어떻게 되었나

Project Galahad의 출발 명분은 명확했다. **"Graal/Native Image를 본류로 가져온다"**. 그런데 그 기술을 만들고 있던 Oracle GraalVM 팀이 Java에서 손을 떼면서, Galahad는 기술의 공급원과 추진 동력을 동시에 잃어버린 셈이 되었다.

### 활동 정체

`openjdk/galahad` 저장소의 `galahad` 브랜치는 2025년 8월 이후로 사실상 업데이트가 멈췄다. [oracle/graal 디스커션 #12561](https://github.com/oracle/graal/discussions/12561)에서는 2025년 11월 시점에 한 사용자가 "3개월째 업데이트가 없는데, Detaching 발표 이후 본류 통합 시도는 사실상 포기된 것이냐"고 묻기도 했다. 공식 응답은 끝내 달리지 않았다.

### 스폰서 그룹의 철회와 공식 해산

2026년 3월, 스폰서였던 **HotSpot Group**(Vladimir Kozlov 등 Oracle 측 리드를 포함)이 공식적으로 **스폰서십을 철회**했다. 사유는 단순하고 명확했다. _"2025년 9월 GraalVM 분리 발표 이후, 이 프로젝트가 더 이상 존재할 이유가 없다."_

OpenJDK 절차상 프로젝트는 **스폰서 그룹을 잃으면 해산**된다. 별도의 반대 의견 없이 lazy consensus로 통과되면서, Galahad는 OpenJDK 프로젝트 목록에서 공식적으로 해산 처리되었다.

OpenJDK의 [Galahad 페이지](https://openjdk.org/projects/galahad/)에는 이제 다음 문구가 박혀 있다.

> "This Project was dissolved March 2026 by virtue of losing its sponsoring Group. This Project became unnecessary in light of the September 2025 announcement to detach GraalVM from the Java ecosystem."

## 그럼 원래 목표는 어디로 — Project Leyden

여기서 중요한 점은, Galahad가 추구하던 **목표 자체가 사라진 것은 아니라는 점**이다.

- **시작 시간 단축**
- **peak 성능 도달 시간 최적화**
- **메모리 footprint 감소**

이 세 가지 목표는 본류 OpenJDK의 [Project Leyden](https://openjdk.org/projects/leyden/)으로 흡수되었다. Leyden은 GraalVM과 달리 **"순수 Java 표준 스펙의 일부로서"** 같은 목표를 추진한다.

JDK 25에 들어간 JEP 514/515는 그 가시적인 첫 결과물이다.

- **[JEP 514: Ahead-of-Time Command-Line Ergonomics](https://openjdk.org/jeps/514)** — AOT 캐시 생성과 사용의 명령행 옵션을 간소화.
- **[JEP 515: Ahead-of-Time Method Profiling](https://openjdk.org/jeps/515)** — 메서드 프로파일을 미리 캐시하여 JIT의 warmup 시간을 단축.

Galahad가 Graal/Native Image라는 **별도의 거대한 컴파일러 스택**으로 같은 문제를 풀려 했다면, Leyden은 **기존 HotSpot의 C2와 CDS(Class Data Sharing) 인프라를 점진적으로 확장**해서 푸는 쪽이다. 본류 입장에서는 후자가 훨씬 점진적이고 통제 가능한 길이다.

## JVMCI 제거와의 인과관계

이 흐름을 다시 펼쳐 보면, [JVMCI 제거 결정](/2026/05/23/jdk-8382582-remove-jvmci)의 인과관계가 매우 또렷해진다.

1. **2014~2015** — JVMCI(JEP 243) 도입. 명분은 "Java로 JIT 컴파일러를 작성하는 실험".
2. **2018~** — Graal이 JVMCI의 대표 소비자로 자리잡음. GraalVM Native Image까지 활용 확장.
3. **2022 말** — Project Galahad 발족. "Graal을 본류로 가져올 다리"로서 JVMCI의 명분 강화.
4. **2025년 9월** — Oracle, GraalVM을 Java 생태계에서 분리. Graal JIT/Native Image 단종 예고.
5. **2026년 3월** — Project Galahad 해산.
6. **2026년 4월** — Project Metropolis 해산. JVMCI의 본류 통합 명분이 사라짐.
7. **2026년 5월** — JVMCI 제거 작업 본격화. [JDK-8385105](https://bugs.openjdk.org/browse/JDK-8385105) CSR Approved, [JDK-8382582](https://bugs.openjdk.org/browse/JDK-8382582) 이슈 진행.

JDK-8385105 CSR Summary가 이 흐름을 한 문장으로 압축한다.

> "After dissolving Galahad, Graal and Metropolis projects there are no consumers of JVMCI experimental API left in OpenJDK."

Galahad 해산은 단순히 한 프로젝트의 종료가 아니라, **JVMCI라는 "10년짜리 실험"의 마지막 사용처가 사라진 사건**이었다.

## 정리하며

Project Galahad는 한 시점의 야심을 보여주는 프로젝트였다. "Java의 미래는 Graal/Native Image와 함께 간다"는 가설 위에서, 본류와 GraalVM을 **하나로** 합치려는 시도. 약 3년이 지난 지금, 그 가설은 "**합치지 않고 각자의 길로 간다**"는 결론으로 정리되었다.

- **GraalVM**: 본류 흡수 트랙에서 내려와 **독자 다국어 런타임**으로 성장. Java도 계속 강력하게 지원하지만, Java 표준 스펙의 한 부분이 되는 길은 포기.
- **본류 OpenJDK**: 시작 시간/AOT/footprint 같은 목표를 **Project Leyden**을 통해 표준 Java의 일부로 직접 추진.
- **JVMCI**: "Graal을 본류로 가져올 다리"라는 명분이 사라지면서, 본류에서 제거. 필요한 프로젝트는 자체 트리에서 유지.

개인적으로 흥미로웠던 것은, OpenJDK 커뮤니티가 이 변화를 다루는 방식이었다. 거대한 정치적 선언이 아니라, "스폰서 그룹의 철회 → lazy consensus → 프로젝트 해산"이라는 매우 절차적이고 담담한 흐름을 따랐다. 같은 일이 곧이어 JVMCI 제거([JDK-8382582](https://bugs.openjdk.org/browse/JDK-8382582)) 결정에서도 반복되었다 — 정량적 데이터(`#if INCLUDE_JVMCI` 252개, 1.5% 부수 비용, tier1 42분), 구체적 회귀 사례, 그리고 명확한 근거.

Java 생태계의 큰 줄기 하나가 정리되는 과정을 가까이서 볼 수 있어, 한 단락의 역사를 직접 따라가본 기분이다.
