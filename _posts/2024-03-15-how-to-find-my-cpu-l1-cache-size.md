---
layout: "post"
title: "운영체제별 L1 Cache 사이즈 확인하기"
description: "운영체제별 L1 Cache 사이즈를 확인하는 방법을 소개합니다. Macbook Pro M2에서는 `sysctl hw.l1dcachesize`\
  \ 명령어로 64KB를 확인할 수 있으며, Ubuntu의 AMD Ryzen 5 3600X는 `lscpu` 명령어로 192KB(6 인스턴스)를 확\
  인할 수 있습니다. Windows에서는 작업관리자에서 각 코어의 L1 Cache가 96KB임을 확인할 수 있으며, CPU-Z를 통해 L1 데이터\
  \ 캐시가 32KB임을 알 수 있습니다. 각 운영체제에서의 L1 Cache 사이즈를 쉽게 확인하는 방법을 알아보세요."
categories:
- "개발"
tags:
- "CPU"
- "L1"
- "Cache"
- "hardware"
- "windows"
- "ubuntu"
- "mac"
date: "2024-03-15 14:35:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-03-15-how-to-find-my-cpu-l1-cache-size.jpg"
---

이전글([[자바 최적화] 캐시 미스 이해하기 (L1 Cache) + 코드 warm up 이해하기](/2024/03/15/java-l1-cache-miss))을 작성하다가 궁금해서 찾아보았다.

## 내 컴퓨터의 L1 cache는 사이즈가 어떻게 될까?

내가 주로 사용하는 기기들의 L1 cache 사이즈를 찾아보았다.

### Macbook Pro M2

애플의 경우 아래 명령어를 통해 L1 data cache 의 사이즈를 알아볼 볼 수 있다.

```shell
$ sysctl hw.l1dcachesize
```

```shell
hw.l1dcachesize: 65536
```

65536 는 2^16 이다. 2^10 을 1KB라고 할 때, 65536 = 2^6 \* 1KB = 64KB

검증을 위해 Apple M 시리즈 관련 문서를 찾아보았는데 더 재밌는게 있었다.

![m1-cache-size](/assets/images/2024-03-15-how-to-find-my-cpu-l1-cache-size/m1-cache-size.png)

애플 실리콘 시리즈의 경우 Performance Core 라는 것이 있고, Efficiency Core 라는 것이 있는데
일반적인 상황에는 Efficiency Core가 사용되고 무거운 작업을 해야 하는 경우에 Performance Core 가 사용된다고 한다.

### ubuntu (AMD Ryzen 5 3600X)

ubuntu의 경우 lscpu 명령어를 사용하면 된다.

```shell
$ lscpu
```

```shell
L1d: 192 KiB (6 instances)
```

[amd 공식 홈페이지 스펙 정보](https://www.amd.com/en/support/cpu/amd-ryzen-processors/amd-ryzen-5-desktop-processors/amd-ryzen-5-3600x)에는 `L1 Cache : 384KB` 으로 되어있는데 data cache 와 instruction cache를 합쳐서 명시해둔것으로 보인다.

### windows (intel N100)

Cache L1: 96 KB (per core)

![windows-task-manager](/assets/images/2024-03-15-how-to-find-my-cpu-l1-cache-size/windows-task-manager.png)

윈도우의 경우 작업관리자에서 볼 수 있는데 모든 코어의 L1 을 합쳐놓은 것으로 보인다. (384 = 96 \* 4)

![windows-cpuz](/assets/images/2024-03-15-how-to-find-my-cpu-l1-cache-size/windows-cpuz.png)

cpuz 로 보면 더 자세한 내용을 볼 수 있는데 l1 data cache가 32K 였다.
