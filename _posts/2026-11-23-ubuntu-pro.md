---
layout: "post"
title: "개인 서버에 Ubuntu Pro 붙이기 (Universe 패키지 보안 패치와 Livepatch)"
description: "서버 보안 점검을 하다가 Ubuntu Pro를 알게 됐다. Ubuntu LTS의 기본 보안 패치는 Main 저장소까지만 보장되고, podman이나 fail2ban 같은 Universe 패키지는 Ubuntu Pro의 esm-apps를 붙여야 보장받는다. 개인은 5대까지 무료다. Ubuntu Pro가 무엇을 해 주는지, 어떻게 붙이는지, 붙이기 전에 알아둘 점을 정리했다."
categories:
  - "개발"
tags:
  - "Ubuntu"
  - "Ubuntu Pro"
  - "ESM"
  - "esm-apps"
  - "Livepatch"
  - "보안"
  - "podman"
date: "2026-11-23 00:00:00 +0900"
toc: true
---

집에서 돌리는 Ubuntu 24.04 서버의 보안 설정을 점검하다가 Ubuntu Pro를 알게 됐다. 이름만 보고 기업용 유료 구독이라고 생각해서 지나쳐 왔는데, 개인은 무료로 쓸 수 있고 내 서버에는 꽤 의미가 있었다.

## Ubuntu Pro가 뭔가

Ubuntu Pro는 Canonical이 제공하는 확장 보안 구독이다. 기업에는 유료지만 개인 용도로는 **5대까지 무료**다. Ubuntu One 계정만 있으면 된다.

개인 서버 입장에서 쓸 만한 기능은 세 가지다.

| 서비스      | 하는 일                                                |
| ----------- | ------------------------------------------------------ |
| `esm-apps`  | Universe 저장소 패키지의 보안 패치를 제공한다          |
| `esm-infra` | Main 저장소 패키지의 보안 패치 기간을 5년 더 연장한다  |
| `livepatch` | 커널 보안 패치를 재부팅 없이 실행 중인 커널에 적용한다 |

Universe 저장소와 Main 저장소에 대해서는 바로 아래에서 설명하겠다.

## 기본 보안 패치는 Main까지만 보장된다

"LTS는 5년 동안 보안 패치를 받는다"고 알고 있었는데, 정확히는 **Main 저장소의 패키지**에 대한 약속이다.

Ubuntu 패키지 저장소는 크게 둘로 나뉜다.

- **Main**: Canonical이 직접 관리한다. 릴리스마다 2,300개 정도다.
- **Universe**: Debian과 Ubuntu 커뮤니티에서 온 나머지 오픈소스 패키지다. 24.04 기준으로 36,000개가 넘는다.

Universe 패키지는 커뮤니티가 관리하고 Canonical이 보안 패치를 보장하지 않는다. Ubuntu Pro를 붙이면 Universe 패키지도 Main과 같은 수준으로 Canonical이 보안 패치를 제공한다. 이것이 `esm-apps`다.

24.04 기준으로 정리하면 다음과 같다.

| 저장소   | Pro 없이            | Pro 있으면                   |
| -------- | ------------------- | ---------------------------- |
| Main     | 2029년 5월까지 패치 | 2034년 5월까지 (`esm-infra`) |
| Universe | 보장하지 않음       | 2034년 5월까지 (`esm-apps`)  |

이름은 둘 다 ESM(Expanded Security Maintenance)이지만 성격이 다르다.

- `esm-infra`는 **기간 연장**이다. 기본 지원 5년이 끝난 뒤부터 의미가 있다. 24.04라면 2029년까지는 차이가 없다.
- `esm-apps`는 **범위 확대**다. Universe는 출시 첫날부터 보장 대상이 아니므로, 붙이는 순간부터 효과가 있다.

그래서 지원 기간이 한참 남은 24.04에서도 "Pro에서만 받을 수 있는 보안 업데이트"가 생긴다. Canonical이 Universe 패키지용으로 만든 보안 패치는 무료 저장소가 아니라 `esm-apps` 저장소에 올라가기 때문이다. 패치는 이미 나와 있는데 Pro를 붙이지 않으면 받지 못한다.

## 내 서버에서는 어땠나

내 서버에 설치된 패키지를 저장소별로 세어 보니 Main 쪽이 1,122개, Universe 쪽이 235개였다.

숫자보다 중요한 건 어떤 패키지가 Universe에 있느냐였다. `podman`, `buildah`, `conmon`, `aardvark-dns`, `fail2ban`이 전부 Universe에 있었다. 이 서버의 서비스는 모두 rootless podman 위에서 돌아간다. 컨테이너 런타임 자체가 보안 패치를 보장받지 못하는 상태였던 셈이다.

Pro를 붙이기 전에 확인했을 때, Pro에서만 받을 수 있는 보안 업데이트가 24개 대기 중이었다.

- 컨테이너 관련: `podman`, `buildah`
- 미디어 라이브러리: `ffmpeg`, `libavcodec60` 등
- 그 외: `libmbedcrypto7t64`, `libcjson1`, `python3-pip`, `libsrt1.5-gnutls` 등

자기 서버의 상황은 Pro를 붙이지 않아도 다음 명령으로 확인할 수 있다.

```bash
pro security-status
```

저장소별 설치 패키지 수와, `esm-apps`를 켜면 받을 수 있는 보안 업데이트 수를 보여 준다. `apt upgrade`를 실행했을 때 "Get more security updates through Ubuntu Pro with 'esm-apps' enabled"라는 안내와 함께 패키지 목록이 나오는 것도 같은 이야기다. 광고라고 생각하고 넘겼던 메시지였다.

## Livepatch

Livepatch는 심각도가 높음(High) 이상인 커널 취약점의 패치를 재부팅 없이 실행 중인 커널에 적용한다.

내 서버는 이중화되어 있지 않아서 재부팅하면 그동안 서비스가 그대로 멈춘다. 재부팅을 마음 편히 하기 어려운 환경이라 재부팅 횟수를 줄일 수 있다는 점이 반가웠다.

다만 재부팅을 완전히 대신하지는 못한다. 모든 커널 취약점을 다루는 것이 아니고 커널 패키지를 업그레이드한 뒤에는 결국 재부팅해야 새 커널로 올라간다. "급한 커널 패치가 재부팅을 기다리는 동안 열려 있는 시간을 줄여 준다" 정도로 이해하면 된다.

또 Livepatch의 대상은 커널뿐이다. `openssl`이나 `glibc` 같은 사용자 공간 패키지는 업그레이드해도 이미 떠 있는 프로세스가 예전 라이브러리를 메모리에 올린 채로 돌기 때문에, 그 프로세스를 다시 시작해야 패치가 적용된다. `openssl`은 관련 서비스만 재시작하면 되지만 `glibc`는 거의 모든 프로세스가 쓰고 있어서 사실상 재부팅하는 편이 간단하다. 그러니 Livepatch를 켰다고 재부팅 일정을 없앨 수는 없다. 재부팅할 시간대를 정해 두고, 그때까지 버티게 해 주는 용도로 쓰는 것이 안전하다.

## 붙이는 방법

1. [ubuntu.com/pro](https://ubuntu.com/pro)에 Ubuntu One 계정으로 로그인하고 토큰을 복사한다.
2. 서버에서 다음을 실행한다.

```bash
sudo apt update
sudo apt install ubuntu-pro-client       # 클라이언트를 최신으로 올린다
sudo pro attach <토큰>
sudo apt update && sudo apt full-upgrade # 대기 중이던 ESM 패치가 여기서 설치된다
```

3. 상태를 확인한다.

```bash
pro status                 # 켜진 서비스 확인
canonical-livepatch status # Livepatch 동작 확인
```

내 서버에서는 `pro attach`만으로 `esm-infra`, `esm-apps`, `livepatch`가 켜졌다. 다만 attach만 하고 끝내면 일부가 꺼진 채로 남는 경우가 있다고 하니, `pro status`에서 `esm-apps`, `esm-infra`, `livepatch` 세 줄이 모두 `enabled`인지 확인하자. 꺼져 있는 것은 따로 켠다.

```bash
sudo pro enable esm-apps   # esm-infra, livepatch도 같은 방식
```

특히 `esm-apps`가 꺼져 있으면 Pro를 붙여 놓고도 Universe 패키지 패치는 들어오지 않는다.

일반 업데이트도 밀려 있다면 Pro를 먼저 붙이고 업그레이드하는 편이 낫다. 일반 업데이트와 ESM 패치를 한 번에 받고 재부팅도 한 번으로 끝난다.

`unattended-upgrades`를 쓰고 있다면 ESM 저장소가 자동 업데이트 대상에 들어 있는지도 확인한다. Ubuntu의 기본 설정(`/etc/apt/apt.conf.d/50unattended-upgrades`)에는 ESM 저장소가 이미 허용 대상으로 들어 있다.

```
Unattended-Upgrade::Allowed-Origins {
        "${distro_id}:${distro_codename}";
        "${distro_id}:${distro_codename}-security";
        "${distro_id}ESMApps:${distro_codename}-apps-security";
        "${distro_id}ESM:${distro_codename}-infra-security";
};
```

내 서버는 기본 설정 그대로라 따로 할 일이 없었다. 하지만 이 파일을 직접 고쳐 썼거나 다른 설정으로 덮어쓴 서버라면 ESM 두 줄이 빠져 있을 수 있다. 그러면 패치가 저장소에는 올라와 있어도 자동으로 설치되지는 않는다.

```bash
grep -n ESM /etc/apt/apt.conf.d/50unattended-upgrades
```

두 줄이 보이지 않으면 `Allowed-Origins`에 추가한다.

## 알아둘 점

- **대수 제한**: 개인 무료 플랜은 5대까지다. 다른 Ubuntu 기기에도 붙일 생각이라면 같이 세어야 한다.
- **Canonical 계정에 서버가 등록된다**: 붙인 서버는 Ubuntu One 계정의 구독에 묶인다. 원치 않으면 `sudo pro detach`로 언제든 해제할 수 있다.
- **Livepatch는 커널만 패치한다**: NVIDIA 드라이버 같은 커널 밖의 것은 상관이 없다. 드라이버는 지금처럼 apt 업그레이드로 받아야 한다.
- **FIPS는 켜지 않는다**: `pro status`에 `fips`, `fips-updates` 같은 항목도 보이는데, 정부 규정 준수용이라 개인 서버에는 필요 없다. 켜면 커널이 바뀌고 되돌리기도 까다롭다.

## 마무리

최근 보안 이슈가 많아서 서버 보안을 다시 챙겨 보고 있다. 그 과정에서 Ubuntu Pro를 알게 되어 적용해 봤고 알게 된 내용을 정리해 두었다.

## 참고

- [Ubuntu Pro](https://ubuntu.com/pro)
- [Expanded Security Maintenance (ESM)](https://ubuntu.com/security/esm)
- [Livepatch](https://ubuntu.com/security/livepatch)
