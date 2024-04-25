---
layout: post
title: "[Java] Don't cross 32GB! (32기가 이상으로 힙 메모리를 설정하지 않는게 좋은 이유)"
categories: [스터디-자바]
tags:
  [
    java,
    jvm,
    hotspot,
    openjdk,
    oop,
    compressed oop,
    mark,
    klass,
    trick,
    optimizing,
    jvm optimizing,
  ]
date: 2024-03-29 22:00:00 +0900
image:
  path: /assets/images/2024-03-29-dont-cross-32gb/compressed_oop.png
---

**요약** : heap 메모리에 대한 이야기, compressed oop 에 대한 이야기

## 본문

"최바 최적화 : 6장 가비지 수집 기초" 파트를 읽다보면 oop에 대한 이야기가 나온다.

oop는 ordinary object pointer의 줄임말로, 포인터 구조체이다.

핫스팟은 런타임에 oop 구조체로 자바 객체를 나타낸다.

> 핫스팟(HotSpot)은 데스크톱과 서버 컴퓨터를 위한 자바 가상 머신이다. 오픈소스 자바 프로젝트인 OpenJDK의 JVM엔진이기도 하다.

oop는 모든 객체에 대해 기계어 워드 2개로 구성된 헤더로 시작한다. **Mark 워드**(인스턴스 관련 메타데이터를 저장하는 공간)가 먼저 나오고, 그 다음은 **Klass 워드**(클래스 메타데이터를 가리키는 포인터)가 나온다.

이 두 워드는 각각 32비트 시스템에서는 32비트(4B), 64비트 시스템에서는 64비트(8B) 의 크기를 가진다.

32비트는 최대 4GB(2^32)의 메모리를 다룰 수 있다. 64비트는 최대 16EB(2^64)의 메모리를 다룰 수 있다.

> [Note] jvm만 메모리를 사용하는 것은 아니기 때문에 그 안에서 jvm이 실제로 다룰 수 있는 heap 사이즈는 더 작다. 오라클 문서에는 다음과 같이 나와 있다.
>
> On most modern 32-bit Windows systems the maximum heap size will range from 1.4G to 1.6G. On 32-bit Solaris kernels the address space is limited to 2G

다룰 수 있는 메모리가 크다고 해서 항상 좋은 것은 아니다. 64기가 시스템의 경우 32기가 시스템에 비해 힙의 크기를 크게 설정할 수 있지만, 이는 더 많은 공간이 낭비되는 오버헤드가 되기도 한다.

이러한 문제를 해결하기 위해 hotspot jvm에서는 힙 사이즈가 약 32GB 미만일 때 객체 포인터(klass word)를 압축하는 트릭을 사용한다. 이 기술을 **compressed oop** 라고 한다.

이 옵션은 `-XX:+UseCompressedOops` 를 통해 활성화 할 수 있으며, java 7 버전 이상인 64비트 머신이라면 디폴트 값으로 활성화 되는 옵션이다. 다만 설정한 힙의 크기가 32기가를 넘어선다면 사용할 수 없기 때문에 비활성화 된다.

Integer Object 를 기준으로 compressed oop 를 적용했을 때와 적용하지 않았을 때의 차이를 확인해보면 다음과 같다.
(참고로 java에서 int는 32/64 bit에 상관 없이 항상 4byte의 공간을 사용한다.)

![compressed_oop](/assets/images/2024-03-29-dont-cross-32gb/compressed_oop.png)

### compressed oop 를 사용했을 때의 장점은 무엇일까?

크기를 줄일 수 있기 때문에 더 많은 데이터를 저장할 수 있다.

### 32GB 보다 큰 힙 사이즈를 할당하면 어떻게 될까?

32GB의 경계를 넘으면 compressed oop를 사용하지 못한다. compressed oop를 사용할 수 있는 최대 힙 크기(32기가 미만)에서 만큼의 데이터를 저장하려면 약 40~50GB의 힙 크기를 할당해야 한다고 한다. 물론 거기에 더 많은 CPU 성능을 사용해야 한다.

따라서 메모리에 여유가 있더라도 32GB 힙 경게를 넘지 않는 것이 좋다.

### 어떤 트릭으로 객체 포인터를 압축하였을까

위 이미지를 보았을 때 klass word를 8B에서 4B로 줄인 것을 볼 수 있다.

그러면 여기서 생각해 볼 것이 4B로는 2^32(4GB) 까지밖에 표현이 안된다는 것이다. 그러면 어떻게 32GB까지 compressed oop를 사용할 수 있는 것일까?

여기서 포인트는 klass word는 8비트(1바이트)단위로 값을 표시한다.
따라서 다음과 같은 형태의 데이터들을 가진다.

- 0비트 : 0000 (2)
- 8비트 : 1000 (2)
- 16비트 : 10000 (2)
- 24비트 : 11000 (2)
- ...

여기서 볼 수 있는 것은 **뒷 세자리(bit)가 항상 0** 이라는 것이다.

그래서 여기서 트릭이 진행된다. 뒷 세자리가 어처피 0이니깐. 그걸 알고있다는 것을 전제로 뒷 세자리를 빼고 카운트하자 라는 것이다.
이를 통해 2^(32+3) 즉 2^35 = 32GB 까지 표현할 수 있게 된다.

실제로 포인터 위치로 찾아갈때는 3자리만큼 시프트 처리를 해주기만 하면 된다.

![trick.png](/assets/images/2024-03-29-dont-cross-32gb/trick.png)

## 참고

- [Compressed OOPs in the JVM](https://www.baeldung.com/jvm-compressed-oops)
- [ElasticSearch와 Heap 메모리](https://brunch.co.kr/@alden/35)
- [elasticsearch heap sizing - Don’t Cross 32 GB!](https://www.elastic.co/guide/en/elasticsearch/guide/current/heap-sizing.html#compressed_oops)
