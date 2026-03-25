# os_windows.cpp 분석

## os_windows.cpp 파일 개요

`os_windows.cpp`는 JVM(HotSpot)의 **Windows 플랫폼 추상화 계층**이다. (6391줄)

JVM은 여러 OS에서 동작해야 하므로, OS별로 다른 기능을 `os::` 네임스페이스 아래 통일된 인터페이스로 구현한다. 이 파일은 **Windows 전용 구현체**이며, Linux용은 `os_linux.cpp`, macOS용은 `os_bsd.cpp`가 대응한다.

### 주요 기능 영역

| 영역 | 예시 함수 | 설명 |
|---|---|---|
| **스레드 관리** | `create_thread`, `free_thread`, `set_native_thread_name` | Windows 스레드 생성/해제, Java 스레드와 OS 스레드 매핑 |
| **메모리 관리** | `available_memory`, `physical_memory`, `pd_map_memory`, `pd_unmap_memory` | Windows API로 메모리 할당/해제/매핑, VirtualAlloc 등 사용 |
| **시간** | `javaTimeMillis`, `javaTimeNanos`, `elapsedTime` | Windows 고해상도 타이머(QueryPerformanceCounter) 기반 시간 제공 |
| **파일/디렉토리** | `opendir`, `readdir`, `open`, `stat`, `native_path` | POSIX 스타일 API를 Windows 파일시스템 위에 구현 (`/` -> `\` 변환 등) |
| **DLL 로딩** | `dll_load`, `dll_unload`, `dll_lookup` | LoadLibrary/GetProcAddress 래핑 |
| **시그널 처리** | `install_signal_handler`, `print_signal_handlers` | Windows SEH(Structured Exception Handling) 기반 시그널 처리 |
| **시스템 정보** | `print_os_info`, `print_cpu_info`, `print_memory_info`, `processor_id` | Windows 버전, CPU, 메모리 등 시스템 정보 출력 |
| **프로세스** | `fork_and_exec`, `current_process_id`, `abort`, `exit` | 프로세스 생성/종료 |
| **네트워크** | `socket_close`, `connect`, `recv`, `send` | Winsock 소켓 래핑 |
| **디버깅/진단** | `print_memory_mappings`, `start_debugging`, `find` | 크래시 덤프, 메모리 매핑 정보, 디버거 연결 |

### Java 개발자 관점에서 보면

`System.currentTimeMillis()`, `Thread.start()`, `Runtime.loadLibrary()` 같은 Java API를 호출하면 결국 네이티브 레이어를 거쳐 이 파일의 함수들이 실행된다. JVM이 Windows 위에서 동작하기 위한 **기반 인프라** 전체가 이 파일 하나에 들어 있다.

### OS 추상화 구조

`os` 클래스는 `src/hotspot/share/runtime/os.hpp:175`에 정의되어 있으며, 모든 OS가 공유하는 공통 인터페이스 역할을 한다.

```
os.hpp (share/runtime/)          <- 공통 인터페이스 선언 (모든 OS가 공유)
  ├── os_windows.cpp             <- Windows 구현
  ├── os_linux.cpp               <- Linux 구현
  └── os_bsd.cpp                 <- macOS/BSD 구현
```

- `os` 클래스는 `AllStatic`을 상속한다. 인스턴스를 만들지 않고 **static 메서드만으로 구성**되는 유틸리티 클래스이다.
- `pd_`로 시작하는 메서드들(**platform dependent**)이 핵심이다. `os.hpp`에서 `pd_reserve_memory`, `pd_commit_memory` 등으로 선언하고, 각 OS별 `.cpp` 파일에서 구현한다.
- 외부 코드는 `os::reserve_memory()` 같은 공개 메서드를 호출하면, 내부적으로 `pd_reserve_memory()`를 호출하여 OS별 구현으로 위임하는 방식이다.

Java의 인터페이스/구현체 패턴과 달리, C++에서는 **조건부 컴파일**로 해결한다. 빌드 시 타겟 OS에 해당하는 `.cpp` 파일만 컴파일에 포함시키므로, 런타임 다형성 없이 OS별 분기가 이루어진다.

---

# PostMortemDump 미사용 선언 분석

## 질문 1: PostMortemDump용 함수 선언이 정의 없이 존재함

`os_windows.cpp:2532-2535`에 다음 선언이 있음:

```cpp
// Used for PostMortemDump
extern "C" void safepoints();
extern "C" void find(int x);
extern "C" void events();
```

### 조사 결과

- 이 세 함수의 **정의(본체)가 코드베이스 어디에도 없음**
- **호출하는 코드도 없음**
- **"PostMortemDump"** 문자열도 이 주석 외에는 존재하지 않음
- 2007년 초기 JDK 레포지토리 로드 시점부터 존재하던 코드
- 오픈소스 전환 이전의 Windows 디버깅/포스트모템 덤프 기능의 잔재로 추정
- 4줄(주석 + 선언 3개) 모두 안전하게 삭제 가능

---

## 질문 2: `extern "C"`의 의미

`extern "C"`는 C++ 컴파일러에게 해당 함수를 **C 방식으로 처리**하라고 지시하는 것.

핵심은 **네임 맹글링(name mangling)** 차이:

- **C++**: 함수 오버로딩 지원을 위해 함수 이름을 `_Z4findi` 같은 형태로 변환(맹글링)
- **C**: 오버로딩이 없으므로 함수 이름이 `find` 그대로 유지

```cpp
// C++ 맹글링 적용 -> 심볼 이름이 _Z4findi 같은 형태
void find(int x);

// C 링킹 규약 사용 -> 심볼 이름이 그냥 find
extern "C" void find(int x);
```

`extern "C"` 사용 이유:
1. C 라이브러리와 링크할 때 (C로 컴파일된 코드의 함수를 C++에서 호출)
2. 디버거나 외부 도구에서 심볼 이름으로 함수를 찾을 수 있게 할 때

이 경우 크래시 덤프 분석 도구(WinDbg 등)에서 `safepoints`, `find`, `events`라는 이름으로 직접 호출할 수 있도록 C 링킹을 사용한 것으로 추정.

---

## 질문 3: 본체가 없는데 어떻게 컴파일이 되는가

C/C++에서는 **선언(declaration)과 정의(definition)가 분리**되어 있음.

**호출하지 않으면 문제없다:**

```cpp
extern "C" void safepoints();  // 선언만 - "이런 함수가 어딘가에 있다"는 약속
```

- **컴파일 단계**: 선언만 보고 넘어감. 본체가 없어도 에러 아님.
- **링크 단계**: 실제로 그 함수를 **호출하는 코드가 있을 때만** 링커가 본체를 찾음. 못 찾으면 `undefined reference` 에러.

이 경우 호출하는 코드가 없으니 링커가 본체를 찾을 필요 자체가 없어서 빌드가 정상적으로 됨.

**Java와의 차이:**

| | Java | C/C++ |
|---|---|---|
| 인터페이스 미구현 | 컴파일 에러 | 해당 개념 없음 |
| 선언만 있고 정의 없음 | 불가능 | 호출 안 하면 OK |
| 검증 시점 | 컴파일 시 | 링크 시 (호출될 때만) |

C/C++의 빌드는 **컴파일 -> 링크** 2단계로 나뉘고, 선언은 컴파일러를 위한 것이고 정의는 링커를 위한 것. 호출이 없으면 링커가 관여하지 않으므로 선언만 있는 채로 남아 있을 수 있음.

---

## `extern "C"` 상세 정리

### 왜 필요한가 — Name Mangling 문제

C++은 함수 오버로딩을 지원하기 때문에, 컴파일러가 같은 이름의 함수를 구별하기 위해 함수 이름을 변형한다. 이를 **name mangling**이라고 한다.

```cpp
// C++ 컴파일 후 심볼 이름 (예시)
void foo(int x)    →  _Z3fooi
void foo(float x)  →  _Z3foof
void foo()         →  _Z3foov
```

반면 C 컴파일러는 함수 이름을 그대로 유지한다.

```c
// C 컴파일 후 심볼 이름
void foo(int x)  →  foo  (또는 _foo)
```

C로 컴파일된 라이브러리를 C++에서 링크하면, C++은 mangled된 이름으로 함수를 찾지만 라이브러리엔 원본 이름만 있어서 **링크 오류가 발생**한다. `extern "C"`가 이 문제를 해결한다.

### 기본 사용법

```cpp
// 단일 함수에 적용
extern "C" void my_c_function(int x);

// 블록으로 여러 함수에 적용
extern "C" {
    void func_a(int x);
    int  func_b(float y);
    void func_c();
}
```

### 주요 사용 시나리오

**1. C 라이브러리를 C++에서 사용할 때**

```cpp
extern "C" {
    #include "my_c_library.h"
}
```

**2. C/C++ 공용 헤더 작성 (가장 흔한 패턴)**

```cpp
// my_library.h
#ifdef __cplusplus
extern "C" {
#endif

void my_function(int x);
int  another_function(float y);

#ifdef __cplusplus
}
#endif
```

`__cplusplus` 매크로로 C++ 컴파일 시에만 `extern "C"`가 적용되도록 한다. C 컴파일러는 `extern "C"`를 모르기 때문에 이 가드가 필수다.

**3. C++로 작성한 함수를 C에서 호출할 때**

```cpp
extern "C" void my_cpp_function(int x) {
    // C++ 코드 작성 가능
    std::vector<int> v;
    // ...
}
```

### 제약사항

```cpp
extern "C" {
    // 오버로딩 불가 — C는 오버로딩 개념이 없음
    void foo(int x);
    void foo(float x);  // 컴파일 오류

    // 클래스 멤버 함수에는 적용 불가
    class MyClass {
        extern "C" void method();  // 오류
    };

    // 전역 함수, 변수에는 가능
    int global_var;
    void normal_function(int x);
}
```

| 항목 | 내용 |
|---|---|
| 목적 | C++ name mangling 비활성화 |
| 효과 | C 방식의 링킹 심볼 생성 |
| 주 용도 | C ↔ C++ 상호 운용성 |
| 주의 | 오버로딩, 클래스 멤버에는 사용 불가 |

---

## 컴파일하면 기계어로 떨어지는 거 아닌가?

### 컴파일 전체 과정

```
소스코드 (.cpp)
    ↓  전처리 (Preprocessor)
전처리된 코드
    ↓  컴파일 (Compiler)
어셈블리 코드 (.s)
    ↓  어셈블 (Assembler)
오브젝트 파일 (.o / .obj)   ← 여기서 심볼 테이블 존재
    ↓  링크 (Linker)
실행 파일 (.exe / ELF)      ← 진짜 기계어
```

### 오브젝트 파일 단계가 핵심

`.o` 파일은 기계어 코드는 맞지만, 아직 **미완성**이다.

함수 호출 주소가 빈칸으로 남아있고, **심볼 테이블**이라는 함수 이름 목록을 여전히 가지고 있다.

```
[ foo.o 의 심볼 테이블 ]
_Z3fooi   → 0x0000  (내가 정의함)
_Z3barv   → ???     (다른 파일에 있음, 링커가 채워줘야 함)
```

### 링커가 하는 일

여러 `.o` 파일을 합치면서 빈칸을 채운다.

```
foo.o  +  bar.o  +  libc.a
         ↓ 링커
    실행파일 (주소가 모두 확정된 진짜 기계어)
```

이때 링커는 **심볼 이름으로 함수를 찾는다**. C++ 파일은 `_Z3fooi`, C 파일은 `foo`라는 이름으로 찾으려 하기 때문에 이름이 안 맞으면 링크 오류가 난다.

### name mangling은 심볼 이름의 문제

```
C++ 코드가 찾는 이름:  _Z3fooi   ← mangled
C 라이브러리의 이름:   foo        ← 원본

→ 이름이 달라서 링커가 못 찾음 → undefined reference 오류
```

`extern "C"`는 **"이 함수는 mangling 하지 말고 `foo` 그대로 심볼을 만들어라"** 라는 뜻이다.

---

## `extern "C"`를 안 쓰면 링커가 연결을 못하는가?

그렇다. 상황별로 보면:

### `extern "C"` 없이 C 라이브러리를 C++에서 사용할 때

```
[C로 컴파일된 라이브러리]       [C++로 작성한 코드]
심볼: foo                      찾는 이름: _Z3fooi
                                          ↑ mangled
              링커: "foo" 없는데? → 오류!
```

실제로 이런 오류가 발생한다:

```
undefined reference to `_Z3fooi'
```

### `extern "C"`를 쓰면

```
[C로 컴파일된 라이브러리]       [C++로 작성한 코드]
심볼: foo                      찾는 이름: foo
                                          ↑ mangling 안 함
              링커: "foo" 찾았다! → 연결 성공
```

### 예외: C 표준 헤더는 이미 처리되어 있음

`<stdio.h>`, `<stdlib.h>` 등 C 표준 헤더는 이미 내부적으로 `extern "C"`가 적용되어 있어서 따로 안 써도 된다.

```cpp
// 이게 되는 이유
#include <stdio.h>
printf("hello");  // extern "C" 없어도 동작

// stdio.h 내부를 보면
#ifdef __cplusplus
extern "C" {
#endif
    int printf(const char*, ...);
#ifdef __cplusplus
}
#endif
```

즉, 직접 만든 C 라이브러리나 `extern "C"` 처리가 안 된 서드파티 라이브러리를 C++에서 쓸 때 빠뜨리면 링크 오류가 발생한다.
