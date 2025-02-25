---
layout: post
title: 함수형 아키텍처와 출력 기반 테스트로의 전환 - 단위테스트 6장
date: "2023-07-15 01:33:08 +0900"
description: 함수형 아키텍처와 출력 기반 테스트로의 전환을 다룬 이 글에서는, 초기의 감사 시스템 구현에서 파일 시스템 의존성을 제거하고, 목(mock) 객체를 활용하여 테스트를 독립적으로 수행하는 방법을 설명합니다. 리팩토링을 통해 비즈니스 로직과 사이드 이펙트를 분리하고, 새로운 Persister 클래스를 도입하여 테스트의 속도와 유지 보수성을 개선했습니다. 최종적으로, 함수형 아키텍처를 적용함으로써 오류 처리도 간단해지고 명확해졌습니다.
categories:
  - 스터디-테스트
tags:
  - 테스트
  - 단위 테스트
  - test
  - unit test
  - 함수형 아키텍처
  - fuctional architecture
  - 출력 기반 테스트
  - output based testing
---

단위테스트 (블라디미르 코리코프)

---

아래 내용에서 이어지는 글입니다.

- [6장 단위 테스트 스타일](/2023/07/11/unit-test-style)
- [6장 단위 테스트 스타일 - 스타일 비교](/2023/07/12/unit-test-style-comparison)
- [6장 단위 테스트 스타일 - 함수형 아키텍처](/2023/07/13/functional-architecture)

---

두 가지 리팩터링 단계를 거친다.

- 프로세스 외부 의존성에서 목으로 변경
- 목에서 함수형 아키텍처로 변경

### 4.1 감사 시스템 소개

샘플로 사용할 프로젝트는 조직의 모든 방문자를 추적하는 감사 시스템이다.  
텍스트 파일을 기반 저장소로 사용한다.  
시스템은 가장 최근 파일의 마지막 줄에 방문자의 이름과 방문 시간을 추가한다.  
파일당 최대 항목 수에 도달하면 인덱스를 증가시켜 새 파일을 작성한다.

초기 구현은 다음과 같다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=1.%20AuditManager"></script>

위 코드는 다음과 같은 작업을 수행한다.

- 작업 디렉터리에서 전체 파일 목록을 검색한다.
- 인덱스별로 정렬한다.
- 아직 감사 파일이 없으면 단일 레코드로 첫 번째 파일을 생성한다.
- 감사 파일이 있으면 최신 파일을 가져와서 파일의 항목 수가 한계에 도달했는지에 따라 새 레코드를 추가하거나 새 파일을 생성한다.

현재의 AuditManager 클래스는 파일 시스템과 밀접하게 연결돼 있어 그대로 테스트하기가 어렵다. 테스트 전에 파일을 올바른 위치에 배치하고, 테스트가 끝나면 해당 파일을 읽고 내용을 확인한 후 삭제해야 한다. 여기서 병목 지점은 파일 시스템이다. 이는 테스트가 실행 흐름을 방해할 수 있는 공유 의존성이다. 또 파일 시스템은 테스트를 느리게 하기도 한다. 따라서 이 초기 버전은 빠른 피드백 어려우며 유지 보수성이 낮다고 할 수 있다.

파일 시스템에 직접 작동하는 테스트는 근본적으로 단위 테스트의 정의에 맞지 않다. (단위 테스트는 단일 동작 단위를 검증하고 빠르게 수행하고 다른 테스트와 별도로 처리한다. 파일 시스템에 직접 동작하는 테스트는 2번째와 3번째 특성을 만족하지 못한다.) 이는 통합테스트 범주에 속한다.

### 4.2 테스트를 파일 시스템에서 분리하기 위한 목 사용

테스트가 밀접하게 결합된 문제는 일반적으로 파일 시스템을 목으로 처리해 해결한다. 파일의 모든 연산을 별도의 클래스(IFileSystem)로 도출하고 AuditManager에 생성자로 해당 클래스를 주입할 수 있다. 그런 다음 테스트는 이 클래스를 목으로 처리하고 감사 시스템이 파일에 수행하는 쓰기를 캡쳐한다.

![테스트를 파일 시스템에서 분리하기 위한 목 사용](/assets/images/2023-07-15-transitioning-to-functional-architecture-and-output-based-testing/image1.png)

\* 목은 행동 검증을, 스텁은 상태 검증을 한다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=2-1. AuditManager 생성자를 통한 파일 시스템의 명시적 주입"></script>

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=2-2. 새로운 iFileSystem 인터페이스 사용"></script>

이제 AuditManager가 파일 시스템에서 분리되었기 때문에, 공유 의존성이 사라져 테스트를 서로 독립적으로 실행할 수 있다.

다음은 그러한 테스트다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=2-3. 목을 이용한 감사 시스템의 동작 확인"></script>

이 테스트는 현재 파일의 항목 수가 한계(이 예제에서는 3개)에 도달했을 때,. 감사 항목이 하나 있는 새 파일을 생성하는지 검증한다. 이는 목을 타당하게 사용하는 것이다. 애플리케이션은 최종 사용자가 볼 수 있는 파일을 생성한다. 따라서 파일 시스템과의 통신과 이러한 통신의 사이드 이펙트(파일 변경)는 애플리케이션의 식별할 수 있는 동작이다.

이 구현은 초기 버전보다 개선됐다. 테스트는 더 이상 파일 시스템에 접근하지 않으므로 더 빨리 실행된다. 테스트를 만족시키려고 파일 시스템을 다룰 필요가 없으므로 유지비도 절감된다.

|               | 초기 버전 | 목 사용 |
| ------------- | --------- | ------- |
| 회귀 방지     | 좋음      | 좋음    |
| 리팩토리 내성 | 좋음      | 좋음    |
| 빠른 피드백   | 나쁨      | 좋음    |
| 유지 보수성   | 나쁨      | 중간    |

하지만 여기서 더 개선할 수 있다.

### 4.3 함수형 아키텍처로 리팩터링하기

인터페이스 뒤로 사이드 이펙트를 숨기고 해당 인터페이스를 AuditManager에 주입하는 대신, 사이드 이펙트를 클래스 외부로 완전히 이동할 수 있다. 그러면 AuditManager는 파일에 수행할 작업을 둘러싼 결정만 책임지게 된다. 새로운 클래스인 Persister는 그 결정에 따라 파일 시스템에 업데이트를 적용한다.

![함수형 아키텍처로 리팩터링하기](/assets/images/2023-07-15-transitioning-to-functional-architecture-and-output-based-testing/image2.png)

다음 코드는 한번 더 리팩터링 한 AuditManager 다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=3. 리팩터링 후의 AuditManager"></script>

AuditManager는 이제 작업 디렉터리 경로 대신 FileContent 배열을 받는다. 이 클래스는 결정을 내리기 위해 파일 시스템이 알아야 할 모든 것을 포함한다. 또한 작업 디렉터리의 파일을 변경하는 대신 FileUpdate 클래스를 통해 수행하려는 사이드 이펙트에 대한 명령을 반환한다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=3-1. FileContent"></script>

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=3-2. FileUpdate"></script>

가변 셸 역할을 하는 Persister 의 코드는 다음과 같다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=3-3. Persister"></script>

이 클래스는 매우 간결하다. 작업 디렉터리에서 내용을 읽고 AuditManager에서 받은 업데이트 명령을 작업 디렉터리에 수행하기만 하면 된다.

모든 복잡도는 AuditManager 클래스에 있다.

이것이 **비즈니스 로직과 사이드 이펙트의 분리**다.

이렇게 분리를 유지하려면, FileContent와 FileUpdate의 인터페이스를 프레임워크에 내장된 파일 상호 작용 명령과 최대한 가깝게 둬야 한다.

AuditManager와 Persister를 붙이려면, 육각형 아키텍처 분류 체계상 애플리케이션 서비스 역할을 하는 또 다른 클래스가 필요하다.

애플리케이션 서비스의 코드는 다음과 같다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=4. Application Service"></script>

애플리케이션 서비스는 함수형 코어와 가변 셸을 붙이면서 외부 클라이언트를 위한 시스템의 진입점을 제공한다.

이제 모든 테스트는 작업 디렉터리의 가상 상태를 제공하고 AuditManager가 내린 결정을 검증하는 것으로 단축됐다.

![개선된 구조](/assets/images/2023-07-15-transitioning-to-functional-architecture-and-output-based-testing/image3.png)

이렇게 구조가 변경되면서 이제는 목 없이 테스트 작성이 가능하다.

다음 코드는 목 없이 작성된 테스트이다.

<script src="https://gist.github.com/dev-jonghoonpark/50148202c34029d912874b5c6b541ed6.js?file=5. 목 없이 작성된 테스트"></script>

이 테스트는 초기 테스트와 비교해서 빠른 피드백 뿐 아니라 유지 보수성 지표도 향상 됐다.

|               | 초기 버전 | 목 사용 | 출력기반 |
| ------------- | --------- | ------- | -------- |
| 회귀 방지     | 좋음      | 좋음    | 좋음     |
| 리팩토리 내성 | 좋음      | 좋음    | 좋음     |
| 빠른 피드백   | 나쁨      | 좋음    | 좋음     |
| 유지 보수성   | 나쁨      | 중간    | 좋음     |

함수형 코어가 생성한 명령은 항상 값이거나 값 집합이다. 같은 내용이 일치하는 한, 두 인스턴스를 서로 바꿀 수 있다.

함수형 아키텍처를 통해 오류 처리가 더욱 간단해지고 명확해진다. FileUpdate 클래스나 별도의 구성 요소로 메서드 시그니처에 오류를 포함할 수 있다.

```c#
public (FileUpdate update,Error error) AddRecord(
        FileContent[] files,
        string visitorName,
        DateTime timeOfVisit)
```

오류가 있으면 서비스는 업데이트 명령을 Persister에 넘기지 않고, 사용자에게 오류 메시지를 전달하도록 한다.

fin.
