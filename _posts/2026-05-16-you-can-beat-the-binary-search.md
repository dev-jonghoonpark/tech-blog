---
layout: post
title: "이진 탐색보다 빠르게 (You can beat the binary search)"
description: "Daniel Lemire의 글을 번역한 포스트. SIMD 명령어와 사분 탐색(quaternary search)을 결합하여 정렬된 배열에서 이진 탐색보다 빠른 검색을 수행하는 SIMD Quad 알고리즘을 소개한다."
categories: ["개발"]
tags: [binary search, SIMD, 알고리즘, 성능 최적화, 번역]
date: 2026-05-16 18:00:00 +0900
toc: true
math: true
---

> 이 글은 Daniel Lemire의 [You can beat the binary search](https://lemire.me/blog/2026/04/27/you-can-beat-the-binary-search/)를 요약 번역한 글이다.

## 배경

정렬된 배열에서 값을 찾는 가장 대표적인 알고리즘은 이진 탐색(binary search)이다. 하지만 현대 프로세서의 병렬 처리 능력을 활용하면 이진 탐색보다 더 빠른 검색이 가능하다.

Lemire는 [Roaring Bitmap](https://roaringbitmap.org/) 포맷에서 사용하는 16비트 정수 정렬 배열(1~4096개 원소)을 대상으로, SIMD와 사분 탐색(quaternary search)을 결합한 **SIMD Quad** 알고리즘을 제안한다.

---

## 핵심 아이디어

두 가지 관찰에서 출발한다.

### 1. 데이터 병렬성 (SIMD)

SIMD(Single Instruction, Multiple Data)는 하나의 명령어로 여러 데이터를 동시에 처리하는 방식이다. 예를 들어, 128비트 SIMD 레지스터에 16비트 정수 8개를 채우면 한 번의 비교 명령으로 8개 값을 동시에 검사할 수 있다. ARM NEON과 x64 SSE 모두 이를 지원한다.

8개의 값을 한 번에 비교 가능하므로, 8개 미만의 원소를 다루는 탐색은 불필요하다.

### 2. 메모리 수준 병렬성 (Quaternary Search)

최근 프로세서는 메모리 수준 병렬성(memory-level parallelism)이 뛰어나서 여러 메모리 위치를 동시에 로드할 수 있다. 이진 탐색은 이전 비교 결과가 나와야 다음 위치를 알 수 있어 순차 대기가 발생한다.

**사분(quaternary) 탐색**은 이름 그대로 배열을 **4등분**하여 3개의 피벗을 동시에 비교한다 (binary가 2등분이라면 quaternary는 4등분). 3곳의 메모리를 동시에 요청하더라도 현대 프로세서의 파이프라인이 이를 병렬로 처리하므로, 3번 읽는 비용이 1번 읽는 비용과 거의 같다. 한 번의 반복으로 탐색 범위를 1/2이 아닌 약 1/4로 줄일 수 있다.

---

## SIMD Quad 알고리즘

알고리즘의 동작 방식은 다음과 같다.

1. **원소가 16개 미만**이면 선형 탐색 수행
2. 배열을 **16개씩 블록**으로 나눔
3. 블록 경계값을 대상으로 **사분 탐색(quaternary search)** 수행 → 후보 블록 결정
4. 후보 블록 내에서 **SIMD 명령어로 16개 원소를 동시 비교**
5. 나머지(블록에 포함되지 않는 꼬리 원소)는 선형 탐색

### 소스코드

```c
bool simd_quad(const uint16_t *carr, int32_t cardinality,
                uint16_t pos) {
    constexpr int32_t gap = 16;
    if (cardinality < gap) {
      for (int32_t j = 0; j < cardinality; j++) {
          if (carr[j] == pos) return true;
        }
        return false;
    }
    int32_t num_blocks = cardinality / gap;
    int32_t base = 0;
    int32_t n = num_blocks;
    while (n > 3) {
      int32_t quarter = n >> 2;

      int32_t k1 = carr[(base + quarter + 1) * gap - 1];
      int32_t k2 = carr[(base + 2 * quarter + 1) * gap - 1];
      int32_t k3 = carr[(base + 3 * quarter + 1) * gap - 1];

      int32_t c1 = (k1 < pos);
      int32_t c2 = (k2 < pos);
      int32_t c3 = (k3 < pos);

      base += (c1 + c2 + c3) * quarter;
      n -= 3 * quarter;
    }
    while (n > 1) {
        int32_t half = n >> 1;
        base = (carr[(base + half + 1) * gap - 1] < pos)
                 ? base + half : base;
        n -= half;
    }
    int32_t lo = (carr[(base + 1) * gap - 1] < pos)
                ? base + 1 : base;

    if (lo < num_blocks) {
        const uint16_t *blk = carr + lo * gap;
#ifdef __ARM_NEON
        uint16x8_t needle = vdupq_n_u16(pos);
        uint16x8_t v0 = vld1q_u16(blk);
        uint16x8_t v1 = vld1q_u16(blk + 8);
        uint16x8_t hit = vorrq_u16(vceqq_u16(v0, needle),
                  vceqq_u16(v1, needle));
        return vmaxvq_u16(hit) != 0;
#else
        __m128i needle = _mm_set1_epi16((short)pos);
        __m128i v0 = _mm_loadu_si128((const __m128i *)blk);
        __m128i v1 = _mm_loadu_si128((const __m128i *)(blk + 8));
        __m128i hit = _mm_or_si128(_mm_cmpeq_epi16(v0, needle),
                                   _mm_cmpeq_epi16(v1, needle));
        return _mm_movemask_epi8(hit) != 0;
#endif
    }

    for (int32_t j = num_blocks * gap; j < cardinality; j++) {
        uint16_t v = carr[j];
        if (v >= pos) return (v == pos);
    }
    return false;
}
```

코드를 살펴보면:

- quaternary search 부분에서 3개의 피벗(`k1`, `k2`, `k3`)을 동시에 읽어 비교한다. 브랜치 없이 `c1 + c2 + c3`로 다음 탐색 범위를 결정한다.
- SIMD 부분에서는 16개 원소를 두 번의 128비트 로드로 가져와 동시에 비교한다.

### 예시

256개 원소(0~255)가 있는 정렬 배열에서 `150`을 찾는다고 하자.

**Step 1: 블록 분할**

16개씩 나누면 16개 블록이 생긴다.

```
블록0:  [  0,  1,  2, ...,  15]  ← 경계값: 15
블록1:  [ 16, 17, 18, ...,  31]  ← 경계값: 31
블록2:  [ 32, 33, 34, ...,  47]  ← 경계값: 47
...
블록9:  [144,145,146, ..., 159]  ← 경계값: 159
...
블록15: [240,241,242, ..., 255]  ← 경계값: 255
```

**Step 2: Quaternary Search (사분 탐색)**

`num_blocks=16`, `base=0`, `n=16`으로 시작한다.

**1회차** (`n=16`, `quarter = 16 >> 2 = 4`):

16개 블록을 4등분하는 경계 지점에서 3개의 피벗을 브랜치(조건문) 없이 **동시에** 읽어 비교한다:

```
[구간]  |-- 1분면 --|-- 2분면 --|-- 3분면 --|-- 4분면 --|
[블록]  0  1  2  3 | 4  5  6  7 | 8  9  10 11 | 12 13 14 15
                 ↑ k1          ↑ k2           ↑ k3
            (블록3 끝)     (블록7 끝)     (블록11 끝)
```

- $k_1$ = `carr[79]` (블록3 경계값) = 79 → $79 < 150$ ? → Yes (c1 = 1)
- $k_2$ = `carr[143]` (블록7 경계값) = 143 → $143 < 150$ ? → Yes (c2 = 1)
- $k_3$ = `carr[207]` (블록11 경계값) = 207 → $207 < 150$ ? → No (c3 = 0)

$$\text{base} \leftarrow \text{base} + (1 + 1 + 0) \times 4 = 8$$

$$n \leftarrow 16 - (3 \times 4) = 4$$

→ 16개 블록에서 4개 블록(블록8~11)으로 범위가 줄었다.

**2회차** (`n=4`, `quarter = 4 >> 2 = 1`):

남은 4개 블록을 다시 4등분한다:

```
[블록]  8  |  9  |  10  |  11
         ↑ k1  ↑ k2   ↑ k3
     (블록8 끝) (블록9 끝) (블록10 끝)
```

- $k_1$ = `carr[159]` (블록8 경계값) = 159 → $159 < 150$ ? → No (c1 = 0)
- $k_2$ = `carr[175]` (블록9 경계값) = 175 → $175 < 150$ ? → No (c2 = 0)
- $k_3$ = `carr[191]` (블록10 경계값) = 191 → $191 < 150$ ? → No (c3 = 0)

$$\text{base} \leftarrow 8 + (0+0+0) \times 1 = 8, \quad n \leftarrow 4 - 3 = 1$$

→ while 루프 종료.

이후 `lo` 보정: `carr[(8+1)*16 - 1] = carr[143] = 143 < 150` → `lo = 9` → **블록9**가 최종 후보.

**Step 3: SIMD 비교 (블록9 내부)**

최종 후보인 블록9의 16개 원소 `[144, 145, ..., 159]`를 128비트 레지스터 크기($16\text{bit} \times 8$개)에 맞춰 두 번에 나눠 로드한 뒤 일괄 비교한다:

```
[상위 8개 원소 비교 (v0)]
v0:     [ 144, 145, 146, 147, 148, 149, 150, 151 ]
needle: [ 150, 150, 150, 150, 150, 150, 150, 150 ]
-------------------------------------------------
결과0:  [   0,   0,   0,   0,   0,   0,  FF,   0 ]  ← 150 발견!

[하위 8개 원소 비교 (v1)]
v1:     [ 152, 153, 154, 155, 156, 157, 158, 159 ]
needle: [ 150, 150, 150, 150, 150, 150, 150, 150 ]
-------------------------------------------------
결과1:  [   0,   0,   0,   0,   0,   0,   0,   0 ]
```

두 벡터 결과(결과0, 결과1)를 OR 연산으로 병합한 뒤, 단 하나의 비트라도 세팅되어 있다면(`vmaxvq` 또는 `_mm_movemask` 이용) 즉시 `true`를 반환한다.

**정리**

이진 탐색이라면 log₂(256) = 8번의 순차적 비교가 필요하다. SIMD Quad는 사분 탐색 2회(각 3개 피벗 동시 비교) + SIMD 로드/비교 2회로 끝난다. 사분 탐색이 반복될수록 매번 범위를 약 1/4로 줄여나가는 것을 확인할 수 있다.

## 벤치마크 결과

2~4096개 원소의 정렬 배열 100,000개를 생성하고, 각 크기에 대해 1000만 번의 쿼리를 수행했다. Cold cache(매번 다른 배열 접근)와 warm cache(같은 배열을 100회 연속 접근) 두 시나리오를 테스트했다.

### Intel Emerald Rapids / GCC

| 시나리오   | SIMD Quad vs Binary Search                      |
| ---------- | ----------------------------------------------- |
| Warm cache | **2배 이상** 빠름                               |
| Cold cache | 일관되게 빠름 (quaternary의 메모리 병렬성 효과) |

### Apple M4 / LLVM

| 시나리오   | SIMD Quad vs Binary Search      |
| ---------- | ------------------------------- |
| Cold cache | **2배 이상** 빠름               |
| Warm cache | 빠르지만 차이가 상대적으로 작음 |

Quaternary vs Binary(둘 다 SIMD 적용) 비교에서는:

- Apple 플랫폼: quaternary의 추가 이점이 미미함
- Intel 플랫폼: 큰 배열의 cold cache에서 quaternary가 유의미한 개선을 보임

## 원문의 마무리

> 교과서적인 이진 탐색은 괜찮은 알고리즘이지만, 실질적으로 의미 있는 수준으로 더 잘할 수 있다. 표준 알고리즘은 이렇게 많은 병렬성을 가진 컴퓨터를 위해 설계된 것이 아니었다.

소스 코드: [github.com/lemire/Code-used-on-Daniel-Lemire-s-blog](https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/tree/master/2026/04/26/benchmark)

---

## 내 마무리

현대 프로세서의 SIMD와 메모리 수준 병렬성을 활용하여, 단순한 알고리즘 개선으로 성능 향상을 얻어낸 점이 인상적이다.

사실 이 글을 번역하게 된 계기는 OpenJDK에 위 방식으로 탐색을 개선하자는 의견이 올라왔기 때문이다. 개선을 진행해보고, 또 글을 남겨보겠다.
