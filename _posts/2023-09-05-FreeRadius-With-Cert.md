---
layout: post
title: FreeRadius 로컬 인증서 갱신 및 인증서 파일별 역할 (crt, csr, key, p12, pem)
description: FreeRadius를 활용한 무선 네트워크 인증서 갱신 과정과 각 인증서 파일(.crt, .csr, .key, .p12, .pem)의 역할을 정리한 포스트입니다. 인증서 재생성 절차와 파일의 의미를 설명하며, 특히 .pem은 ASCII 형식의 X.509 디지털 인증서와 개인 키를 포함하고, .p12는 Windows 환경에서 주로 사용되는 바이너리 파일입니다. .key는 개인 키, .csr은 인증서 서명 요청, .crt는 공개 키 및 디지털 인증서 정보를 저장하는 파일입니다.
categories: [개발]
tags: [FreeRadius, 무선인터넷, 보안, WIFI, 와이파이, 인증서, crt,csr, key, p12, pem]
date: 2023-09-5 12:00:00 +0900
---

우리 회사에서는 무선 네트워크 인증을 위해 FreeRadius 로 radius 서버를 구축해서 사용중에 있다.

![auth](/assets/images/2023-09-05-FreeRadius-With-Cert/image1.jpg)  
Image by Freepik

지난 금요일에 휴가였는데
생각도 못하고 있다가 마침 처음으로 인증서 만료가 발생되었다.
비교적 최근에 구축한지라 처음 겪는 일이였다.

mac쪽은 크게 영향이 없었는데 windows 쪽은 영향을 많이 받으신 것 같았다.
(인증서 무시하도록 하는 설정을 찾아서 설정하는걸로 임시 방편으로 해결하신것 같다.)

그래서 월요일날 회사에 서버 인증서를 교체를 진행하였는데
진행하는 중에 생각보다 인증서 파일이 이것저것 많았다.

일단 재생성 과정과 함께 생성되는 각 파일의 의미에 대해서 알아두면 좋겠다 싶어서 정리해둔다.

# freeradius 로컬 인증서 재생성 절차
회사에서는 freeradius 구축을 위해 freeradius 의 공식 docker 이미지를 받아 사용하였다.

freeradius의 기본 인증서 위치는 `/etc/freeradius/certs` 이다.

여기서 먼저 눈 여겨 볼 것은
`ca.cnf` 와 `server.cnf` 이다.
여기서 인증서와 관련된 부분들을 설정할 수 있다.

```
[certificate_authority]
countryName =
stateOrProvinceName =
localityName =
organizationName =
emailAddress =
commonName =
```

인증서 기간에 대한 부분도 설정할 수 있는데
보안과 관련된 분야는 잘 모르다보니 일단 기본 설정 값을 따라갔다.

인증서를 생성하려면 `ca.cnf` 와 `server.cnf` 의 정보를 작성한 후
기본적으로 제공되는 Makefile을 이용하면 된다.
```
make ca.cnf
make server.cnf
```

여기서 기존에 있던 파일들이 있으면 에러가 발생되기 때문에 기존에 있던 파일들을 다른곳으로 옮겨 백업한 후 make 를 하면 인증서가 재 생성된다.

생성 완료 후 컨테이너를 재시작 하면 적용이 된다.

글 작성하면서 찾아보다보니 [레드헷](https://access.redhat.com/documentation/ko-kr/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/proc_creating-a-set-of-certificates-on-a-freeradius-server-for-testing-purposes_assembly_setting-up-an-802-1x-network-authentication-service-for-lan-clients-using-hostapd-with-freeradius-backend "레드헷") 에서 잘 정리된 정보를 찾을 수 있었다.
참고하면 좋을 것 같다


# 인증서 파일별 역할
make 명령어를 통해 인증서를 생성해보면 생성되는 파일이 생각보다 많다. 다섯 종류의 파일이 생성된다. (.crt, .csr, .key, .p12, .pem)

구체적인 설명은 참고 링크에서 확인하면 되고
여기에는 간단하게만 정리한다.

## .pem
[Privacy Enhanced Mail](https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail "Privacy Enhanced Mail") 의 약자이다.

PEM이 무엇인지는 정확하게 몰라도
```
-----BEGIN PRIVATE KEY-----
... BASE64 DATA ...
-----END PRIVATE KEY-----
```
이런 형태를 가진 것을 본 적은 꽤 있을 것이다. (일단은 내가 그랬다.)
이게 PEM의 형태라고 한다.

이 파일은 X.509 디지털 인증서와 개인 키를 ASCII 형식으로 인코딩한 파일이라고 한다.
주로 unix/linux 환경에서 사용

## .p12 (or .pfx)
[PKCS 12](https://en.wikipedia.org/wiki/PKCS_12 "PKCS 12") 기반의 파일이라고 한다.
binary 파일 형태로 보인다. (vim으로는 정상적으로 열리지 않았음.)
주로 windows 환경에서 사용

## .key
공개 키와 짝을 이루는 개인 키를 저장하는 파일
키 값만 담겨있다.

## .csr
Certificate Signing Request 의 약자라고 한다.
CSR은 공개 키와 인증서 정보 (일반적으로 조직 정보 및 도메인 정보)를 포함하며, CA는 이 정보를 기반으로 디지털 인증서를 발급.
키 값만 담겨있다.

## .crt
CRT 파일은 X.509 디지털 인증서의 확장자라고 한다.

주로 공개키 및 디지털 인증서 정보를 저장하는데 사용되며
CRT 파일에 포함된 키를 사용하여 암호화 및 복호화가 이루어진다고 한다

직접 열어보니 가장 구조화된 데이터가 담겨있었다.
어떤 알고리즘을 쓸지, 인증서의 기간은 어떻게 되는지 와 같은 구체적인 내용들이 담겨있다.

# 참고
- [https://www.sslcert.co.kr/guides/kb/54](https://www.sslcert.co.kr/guides/kb/54 "https://www.sslcert.co.kr/guides/kb/54")
- [https://crypto.stackexchange.com/a/43700](https://crypto.stackexchange.com/a/43700 "https://crypto.stackexchange.com/a/43700")
