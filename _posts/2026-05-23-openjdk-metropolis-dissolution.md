---
layout: "post"
title: "OpenJDK Project Metropolis는 왜 해산되었나"
description: "OpenJDK Project Metropolis가 2018년 'Java-on-Java'라는 야심으로 출범해 2021년 사실상 동결되고 2026년 4월 공식 해산되기까지의 흐름을 정리합니다. HotSpot의 일부를 Java로 재작성하려던 실험이 왜 본류 안에서 자리를 잡지 못했는지, JEP 410으로 Graal/AOT가 제거된 배경, 그리고 외부에서 성장한 GraalVM과의 관계를 살펴봅니다."
categories:
  - "오픈소스"
tags:
  - "JDK"
  - "OpenJDK"
  - "Metropolis"
  - "Graal"
  - "HotSpot"
date: "2026-05-23 15:30:00"
toc: true
---

지금까지 [JVMCI 제거](/2026/05/23/jdk-8382582-remove-jvmci)와 [Project Galahad의 해산](/2026/05/23/openjdk-galahad-dissolution)을 정리하면서, 둘 다 그 배경에 **"Galahad·Graal·Metropolis 프로젝트가 모두 종료되어 JVMCI를 쓸 사람이 본류에 남지 않았다"** 는 [JDK-8385105](https://bugs.openjdk.org/browse/JDK-8385105) CSR의 한 줄을 인용했다.

세 프로젝트 중 마지막으로 남은 **Project Metropolis** 차례다. Galahad와 한 묶음으로 묶기 쉬운 이름이지만, 사실 Metropolis는 더 오래된 프로젝트이고, 멈춘 시점과 이유도 다르다. 이 글에서는 Metropolis가 어떤 야심으로 출발했고, 왜 OpenJDK 본류 안에서 자리를 잡지 못했는지를 정리한다.

## Project Metropolis는 무엇이었나

[Project Metropolis](https://openjdk.org/projects/metropolis/)는 **2018년**, John Rose의 [제안서](https://cr.openjdk.org/~jrose/metropolis/Metropolis-Proposal.html)를 거쳐 정식 OpenJDK 프로젝트로 발족했다. 핵심 정보는 다음과 같다.

- **스폰서**: HotSpot Group
- **Lead**: Vladimir Kozlov (HotSpot JIT 리드, AOT 핵심 엔지니어)
- **목표**: HotSpot의 C++ 런타임 컴포넌트 중 일부를 **Java로 다시 작성**해 HotSpot에 통합 — 이른바 "**Java-on-Java**"

### "Java-on-Java"라는 야심

Java-on-Java는 다음과 같은 가설 위에 있다.

> "JVM의 상당 부분은 C++로 작성되어 있는데, 그 일부는 사실 Java로 작성해도 되는 영역이다. Java로 옮기면 자동 메모리 관리, 좋은 IDE, 단위 테스트 인프라, 자기 자신을 최적화할 수 있는 능력 등을 얻을 수 있다."

특히 컴파일러는 이 가설에 매우 잘 맞는 영역이다. 바이트코드 인터프리터나 GC처럼 저수준 자원 제어가 핵심인 영역과 달리, 컴파일러는 본질적으로 복잡한 데이터 구조와 알고리즘 위에서 동작한다. JEP 243(JVMCI)이 "Java로 컴파일러를 만들 수 있게 하는 인터페이스"였다면, Metropolis는 그 한 발 더 나아가 **"실제로 Java로 만든 컴파일러를 HotSpot에 통합해보자"** 는 시도였다.

### 핵심 실험들

[제안서](https://cr.openjdk.org/~jrose/metropolis/Metropolis-Proposal.html)에서 명시된 핵심 실험은 다음과 같다.

1. **Graal을 native하게 AOT 컴파일**해서, JVM 시작 시점에 native code로 로드되는 JIT 컴파일러로 동작하게 한다. — Java로 작성된 컴파일러가 JIT의 자기 부트스트랩 부담 없이 빠르게 동작할 수 있는지 검증.
2. 그렇게 컴파일된 Graal을 **C2의 후계자**로 평가한다. — 장기적으로 C2를 Graal로 교체할 수 있는지 살펴보기 위한 발판.
3. 더 나아가, HotSpot의 다른 C++ 컴포넌트 중 일부도 Java로 다시 쓸 수 있는지 실험한다.

요약하면, **Metropolis는 JVMCI와 Graal을 도구로 삼아 "Java로 작성된 HotSpot의 일부"가 실제 운영 환경에서 통하는지 검증하는 인큐베이터**였다.

## 왜 멈췄나 — 2020~2021

야심에 비해, Metropolis의 가시적인 산출물은 많지 않았다.

- **JDK 15 기반 Early Access 빌드**를 끝으로 EA 빌드 생산이 중단되었다(약 2020년).
- 2021년 6월, [metropolis-dev에 status 메일](https://mail.openjdk.org/pipermail/metropolis-dev/2021-June/000046.html)이 올라오면서 사실상 동결 상태가 공식화되었다.

해당 status 메일의 결론을 요약하면 대략 다음과 같다.

1. **"Java-on-Java" 방향성 자체는 옳다고 본다.** HotSpot의 일부 컴포넌트에는 여전히 적절한 접근이라고 판단함.
2. **다만 지금은 한 발 물러선다.** 나중에 다시 돌아올 수 있다는 단서를 달면서.
3. **JDK 안의 Graal과 AOT 컴파일러를 제거하기로 결정했다.** 도입 이후 사용량이 매우 적었고, 유지/개선 비용이 상당했기 때문.
4. **AOT 관련 경험은 Project Leyden으로 흡수**된다.

이 결정의 후속 작업이 바로 JDK 17의 **[JEP 410: Remove the Experimental AOT and JIT Compiler](https://openjdk.org/jeps/410)** 다.

## JEP 410 — 본류에서 Graal/AOT가 제거된 순간

JEP 410은 짧지만 결정적인 JEP다. 이 JEP로 다음이 본류에서 제거되었다.

- **`jaotc` 도구** — 메서드를 native code로 AOT 컴파일하는 명령행 도구.
- **HotSpot의 Graal 기반 AOT 컴파일러 코드** (`src/jdk.aot` 등).
- **Experimental Java-based JIT** — [JEP 317](https://openjdk.org/jeps/317)으로 도입되었던 Graal JIT 옵션.

JEP 410의 Motivation 섹션은 정리의 이유를 매우 담담하게 적었다.

> "These experimental features have seen little use since their introduction. The amount of effort required to maintain and enhance them is significant. They have therefore been removed in JDK 16."

도입 후 사용량이 적었고, 유지/개선 비용이 컸기 때문에 정리한다는 것이다. 단순한 사실 진술 같지만, 이는 **"본류 안에서 Graal/AOT 실험은 더 진행할 수 없다"** 는 선언이었다.

JEP 410 이후, OpenJDK 본류 안에서 **"Java로 작성된 JIT"** 를 켜는 길은 사실상 사라졌다. 외부의 GraalVM을 통하지 않고서는 더 이상 Graal JIT을 끼울 수 없게 된 것이다.

## 더 깊은 이유 — "외부에서의 자기 자신에 의해 고아가 된 프로젝트"

표면적인 이유("사용량 적음 + 유지비 큼")는 이해하기 쉽지만, 한 단계 더 들어가 보면 더 흥미로운 그림이 나온다.

Metropolis가 본류 안에서 검증하려던 가설은 결국 두 부분으로 나눌 수 있다.

- "Java로 작성된 JIT 컴파일러가 실제로 쓸 만한가?" — **Graal 자체의 검증**
- "그 컴파일러를 HotSpot 안에서 정식 JIT으로 굴릴 수 있는가?" — **본류 통합의 검증**

이 중 첫 번째 가설은 **OpenJDK 본류가 아닌 외부 GraalVM 프로젝트에서 검증**되어 갔다. GraalVM은 별도의 릴리즈 주기, 별도의 사용자 기반, 별도의 마케팅을 가지고 **본류보다 훨씬 빠르게 성장**했다. 사용자 입장에서는 "본류에 끼워 넣는 실험적 Graal" 대신 "외부 GraalVM의 잘 정돈된 배포본"을 쓰는 것이 훨씬 자연스러웠다.

결과적으로:

- 본류 안의 Graal/AOT는 외부 GraalVM의 그림자에 가려 사용량이 적었다.
- 그럼에도 두 곳을 동시에 유지하는 비용은 누적되었다.
- "본류 안에서 Java-on-Java를 증명한다"는 Metropolis의 임무는, 외부에서 이미 그 일부가 증명되고 있었기에 본류 안에서는 명분을 잃었다.

표현을 빌리자면, **Metropolis는 외부에서의 자기 자신(GraalVM)의 성공에 의해 본류 안에서는 고아가 된** 셈이다.

## 공식 해산 — 2026년 4월

2021년 동결 이후 Metropolis는 사실상 잠들어 있었고, 한동안 OpenJDK 프로젝트 목록 한구석에 이름만 남아 있었다. 공식 해산은 **2026년 4월**, Vladimir Kozlov가 주도한 Call For Votes를 통해 마무리되었다. 같은 흐름에서 OpenJDK Project Graal(GraalVM과 별개의 OpenJDK 프로젝트)도 함께 정리되었다.

타임라인으로 보면 다음과 같다.

- **2025년 9월** — Oracle, "[Detaching GraalVM from the Java Ecosystem Train](https://blogs.oracle.com/java/detaching-graalvm-from-the-java-ecosystem-train)" 발표.
- **2026년 3월** — Project Galahad 해산.
- **2026년 4월** — Project Metropolis, OpenJDK Project Graal 해산.
- **2026년 5월** — JVMCI 제거 작업 본격화 ([JDK-8382582](https://bugs.openjdk.org/browse/JDK-8382582), CSR [JDK-8385105](https://bugs.openjdk.org/browse/JDK-8385105) Approved).

즉 2026년 봄, **Graal/GraalVM 관련 OpenJDK 프로젝트들이 연쇄적으로 정리**되는 큰 흐름의 한 부분으로 Metropolis도 마지막을 맞았다.

## Galahad와의 차이

Galahad와 Metropolis는 둘 다 "GraalVM 관련 OpenJDK 프로젝트"라는 점, 그리고 비슷한 시기에 해산되었다는 점에서 함께 묶이기 쉽다. 하지만 본질적으로는 다른 종류의 시도였다.

| 항목                | Metropolis (2018~2026)                         | Galahad (2022~2026)                                |
| ------------------- | ---------------------------------------------- | -------------------------------------------------- |
| **방향**            | HotSpot의 C++ 컴포넌트를 Java로 재작성          | GraalVM의 Java 기술을 본류로 흡수                   |
| **핵심 도구**       | JVMCI + Graal (AOT 컴파일된 형태)              | GraalVM JIT, Native Image                          |
| **결정적 둔화**     | 2021년, JEP 410로 Graal/AOT 제거               | 2025년 9월, Oracle Detaching 발표                   |
| **본질적 이유**     | 본류 안 실험의 사용량 부족, GraalVM의 외부 성공 | 흡수할 기술의 공급원(GraalVM)이 Java를 떠남         |
| **공식 해산**       | 2026년 4월                                     | 2026년 3월                                          |

거칠게 말하면, **Metropolis는 "본류 안에서의 실험"으로 시작했다가 외부에서 추월당했고, Galahad는 그 외부의 성과를 다시 본류로 가져오려다 외부가 방향을 틀어서 막혔다**. 두 프로젝트 모두 GraalVM이라는 거대한 외부 흐름과의 관계 속에서 자리를 잃었다는 공통점이 있다.

## 남긴 것 — Project Leyden

Metropolis가 검증하려던 큰 그림 중 일부는 [Project Leyden](https://openjdk.org/projects/leyden/)으로 이어졌다. 다만 Leyden은 Metropolis와 결이 다르다.

- Metropolis는 "**HotSpot을 Java로 다시 쓴다**"는 비교적 급진적인 방향이었다.
- Leyden은 "**HotSpot을 그대로 두고, CDS와 AOT 캐시를 점진적으로 확장**해서 startup time/footprint를 줄인다"는 보수적인 방향이다.

[JEP 514](https://openjdk.org/jeps/514), [JEP 515](https://openjdk.org/jeps/515)처럼 JDK 25에 이미 들어간 결과물은, Metropolis가 미처 완성하지 못한 "본류 안에서의 AOT" 이야기의 후속이라고 볼 수 있다. **본류 안에서 점진적으로**라는 단어가 핵심이다.

## 정리하며

Metropolis는 약 8년에 걸친 긴 실험이었다. "JVM의 일부를 Java로 다시 쓰자"는 야심은 한 시점에 무척이나 매력적으로 들렸지만, 본류 입장에서는 다음과 같은 현실에 부딪혔다.

- 본류 안에 들여놓은 실험적 Graal/AOT는 사용자가 충분히 따라오지 않았다.
- 같은 기술이 외부 GraalVM에서 더 빠르게 성장하면서, 본류 안의 실험은 점점 명분을 잃었다.
- 유지/개선 비용은 줄지 않았고, 결국 JEP 410으로 본류에서 제거되었다.
- 그 이후 5년간 사실상 동면 상태였다가, 2026년 봄의 정리 흐름과 함께 공식적으로 마무리되었다.

개인적으로 흥미로운 점은, Metropolis의 종료 과정이 **"실험이 어떻게 끝나야 하는가"** 에 대한 한 가지 답처럼 보인다는 것이다. 무리하게 본류에 묶어두지 않고, 사용량과 비용을 차분히 평가하고, 얻은 경험은 다음 프로젝트(Leyden)로 이어가는 흐름. "실험은 실험으로 두고, 본류는 본류답게 굴린다"는 OpenJDK의 문화가 잘 드러나는 사례이기도 하다.

이렇게 해서 [JVMCI 제거](/2026/05/23/jdk-8382582-remove-jvmci) → [Galahad 해산](/2026/05/23/openjdk-galahad-dissolution) → 이번 Metropolis 해산까지, 2026년 봄에 OpenJDK가 마무리한 "Graal 관련 정리 3부작"을 한 차례 훑어본 셈이다. Java라는 큰 줄기가 어떤 분기점에서 어떤 결정을 내렸는지를 기록해두는 의미에서, 한동안 두고두고 다시 들여다볼 만한 흐름이라는 생각이 든다.
