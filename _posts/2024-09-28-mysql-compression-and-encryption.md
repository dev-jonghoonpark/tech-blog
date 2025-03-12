---
layout: "post"
title: "[MySQL] 압축과 암호화 - Real MySQL 스터디 3회차"
description:
  "MySQL 8.0에서 압축과 암호화 기능을 다룬 이 글에서는 InnoDB 스토리지 엔진을 기준으로 페이지 압축과 테이블 압\
  축의 장단점, 압축 테이블 생성 방법, 그리고 MySQL 서버의 암호화 방식과 키링 관리에 대해 설명합니다. 페이지 압축은 투명하게 동작하며,\
  \ 테이블 압축은 데이터 파일 크기를 줄일 수 있지만 성능 저하가 발생할 수 있습니다. 암호화는 디스크 I/O 단계에서만 적용되며, AES256을\
  \ 기본으로 지원합니다. 또한, 암호화와 압축을 함께 사용할 때의 성능 변화와 설정 방법도 다룹니다."
categories:
  - "스터디-데이터베이스"
tags:
  - "MySQL"
  - "compression"
  - "encryption"
  - "transparent"
  - "mysql 8.0"
  - "real mysql"
  - "table compression"
  - "page compression"
  - "keyring"
  - "2-tier encryption"
date: "2024-09-28 14:59:59 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-09-28-mysql-compression-and-encryption.jpg"
---

# 압축

MySQL에서 압축 기능이 어떻게 동작하는지 알아봅니다.

## MySQL 에서 압축할 경우 장점

압축을 하면 다음과 같은 장점이 있다.

- 쿼리 성능 향상
- 백업 및 복구 시간 감소

## 압축의 종류

- 페이지 압축
- 테이블 압축

## 본격적으로 들어가기 전 용어정리

ROW : 테이블의 개별 데이터 항목
PAGE : 실제적으로 저장되는 블록, 여러 ROW가 하나의 PAGE에 저장될 수 있음.

## 페이지 압축

Transparent Page Compression

디스크에 저장 하는 시점에 데이터 페이지가 압축되어 저장되고, 디스크가 디스크에서 데이터 페이지를 읽어올 때 압축이 해제된다.

MySQL 서버 입장에서는 압축 여부에 대해서 알지 못하며 그와 상관없이 **투명(Transparent)** 하게 동작한다.

![page-compression](/assets/images/2024-09-28-mysql-compression-and-encryption/page-compression.png)

페이지 압축의 경우 실제 데이터는 줄어들으나, 나머지 공간은 사용할 수 없다.
OS에서 펀치 홀 기능을 제공한다면 줄어들은 공간을 사용할 수 있지만 크게 효과적이지는 않다.
따라서 잘 사용되지는 않는다.

(펀치 홀을 지원한다고 해도 사용시 단편화가 발생된다.)

## 테이블 압축

운영체제나 하드웨어에 대한 제약 없이 사용할 수 있다.

- 장점
  - 디스크의 데이터 파일 크기를 줄일 수 있다.
- 단점
  - 버퍼 풀 공간 활용률이 낮음
  - 쿼리 처리 성능이 낮음
  - 빈번한 데이터 변경 시 압축률이 떨어짐

### 압축 테이블 생성하기

`innodb_file_per_table` 시스템 변수를 활성화한 후 다음과 같이 테이블을 생성한다.
`ROW_FORMAT=COMPRESSED` 는 `KEY_BLOCK_SIZE` 사용시 자동으로 설정되므로 생략할 수 있다.

![create-table-with-table-compression](/assets/images/2024-09-28-mysql-compression-and-encryption/create-table-with-table-compression.png)

### 동작 방식

`KEY_BLOCK_SIZE` 를 16KB 라고 가정했을 때 다음과 같이 동작한다.
(KEY_BLOCK_SIZE : 압축된 페이지가 저장될 페이지의 크기)

![table-compression-flow](/assets/images/2024-09-28-mysql-compression-and-encryption/table-compression-flow.png)

- 16KB의 데이터 페이지를 압축
  - 압축된 결과가 8KB 이하이면 그대로 디스크에 저장(압축 완료)
  - 압축된 결과가 8KB를 초과하면 원본 페이지를 스플릿(split)해서 2개의 페이지에 8KB씩 저장
- 나뉜 페이지 각각에 대해 1번 단계를 반복

### 적절한 KEY_BLOCK_SIZE 결정하기

테이블 압축시 KEY_BLOCK_SIZE 를 적절하게 설정해주는 것이 중요하다.

원본 데이터 페이지의 압축 결과가 목표 크기(KEY_BLOCK_SIZE)보다 작거나 같을 때까지 반복해서 페이지를 스플릿한다.

KEY_BLOCK_SIZE 는 2의 배수로 설정할 수 있다.

압축 실패율을 고려해서 크기를 설정해야 한다.
압축 실패율은 3~5% 미만으로 유지하는 것이 좋다.

> 압축 실패율 = 전체 압축 횟수 - 압축 성공 횟수 / 전체 압축 횟수 \* 100

### 압축된 페이지의 버퍼 풀 적재 및 사용

InnoDB 스토리지 엔진은 압축된 테이블의 데이터 페이지를 버퍼 풀에 적재하면 압축된 상태와 압축이 해제된 상태 2개 버전을 관리한다. 두 버전을 내부적으로 적절히 조합해서 사용한다. (매번 압축 해제하고 적용하는건 리소스 낭비다.)

## 결론 : 데이터베이스 압축 - 진짜 필요할까?

- 성능이 중요한 경우에는 하지 않는것이 좋다.
- 용량이 충분히 큰 (몇 십 기가가 되는) 경우가 아니라면 꼭 필요하지 않을 가능성이 높다.

# 암호화

MySQL에서 암호화 기능이 어떻게 동작하는지 알아봅니다.
Application 단에서의 암호화와는 어떻게 다른지 알아봅니다.

## Application 암호화와의 비교

- Application 암호화
  - 암호화된 컬럼은 인덱스의 기능을 활용하기 힘들다. (range search 응용 불가)
- MySQL 암호화
  - 데이터를 모두 처리한 후 최종적으로 디스크에 데이터를 저장할 때만 암호화
  - 데이터 파일, 리두 로그, 언두 로그, 바이너리 로그 등 모두 암호화 가능

## MySQL 서버 암호화

![mysql-encryption](/assets/images/2024-09-28-mysql-compression-and-encryption/mysql-encryption.png)

MySQL 서버 암호화 기능은 DB 서버와 디스크 사이의 데이터를 읽고 쓰는 지점에서 암호화 또는 복호화를 수행한다.
즉 MySQL 서버 (InnoDB 스토리지 엔진) 의 **I/O 레이어에서만** 데이터의 암호화 및 복호화 과정이 실행된다.
암호화를 사용해도 사용자 입장에서는 알지 못한다. (메모리나 네트워크 전송에서는 평문이고 저장 단계에서만 암호화 한다.) TDE(Transparent Data Encryption), Data at Rest 이라고도 부른다.

기본적으로 AES256 을 지원 및 사용한다.

## 키링(KeyRing)

암호화에 사용되는 키는 키링 플러그인에 의해 관리된다.
파일 기반 또는 외부의 키 관리 솔루션을 활용할 수도 있다.

- keyring_file
- keyring_okv : kmip
- keyring_aws
- hashicorp vault
- …

## 2단계 암호화 아키텍처

두 가지 키(마스터 키, 테이블스페이스 키 (private key))를 사용하여 암호화 한다.
암호화 된 테이블이 생성될 때마다 해당 테이블을 위한 임의의 테이블 스페이스 키를 발급한다. 마스터 키를 이용해 테이블 스페이스 키를 암호화해서 각 테이블의 데이터 파일 헤더에 저장한다.

![mysql-two-tier-encryption](/assets/images/2024-09-28-mysql-compression-and-encryption/mysql-two-tier-encryption.png)

### 키 갱신

테이블 키는 테이블이 삭제되지 않는 이상 절대 변경되지 않으며, 테이블 키는 MySQL 서버 외부로 노출되지 않는다.
마스터 키는 외부의 파일을 이용하기 때문에 노출될 가능성이 있다. 마스터 키는 주기적으로 변경해주는 것이 좋다.
마스터 키를 변경하면 변경 전 키를 이용해 각 테이블 키를 복호화 한 후 새 키로 다시 암호화한다.

```sql
ALTER INSTANCE ROTATE INNODB MASTER KEY
```

## 암호화에 따른 성능 변화

MySQL 서버 암호화는 TDE (Transparent Data Encryption) 방식이다.

디스크로부터 한 번 읽은 데이터 페이지는 복호화되어 InnoDB 버퍼 풀에 적재된다. 따라서 메모리에 적재된 이후로는 암호화되지 않은 테이블과 동일한 성능을 보인다.

메모리에 적재되지 않은 데이터 페이지를 읽어야 하는 경우에는 복호화 하는 시간동안 쿼리 처리가 지연된다. 하지만 데이터 저장은 백그라운드 스레드가 수행하기 때문에 실제 사용자 쿼리에는 영향을 미치지 않는다.

평균적으로 읽기의 경우 3~5배, 쓰기의 경우에는 5~6배 정도 느리다 (책 내용 기준)

## 암호화와 압축을 함께 적용하기

일반적으로 암호화된 데이터는 아주 랜덤한 바이트 배열을 가지게 된다. 이는 압축률을 상당히 떨어트린다.

메모리에서 압축을 진행하고 디스크 I/O 할때만 암호화를 하는 것이 더 좋다. (암호화를 한번만 해도 된다)

## 테이블 암호화 설정하기

keyring 설정 후 사용할 수 있다.

![create-table-with-table-encryption](/assets/images/2024-09-28-mysql-compression-and-encryption/create-table-with-table-encryption.png)

## 로그 암호화

- 언두 로그 : innodb_undo_log_encrypt
- 리두 로그 : innodb_redo_log_encrypt
- 바이너리 로그 : binlog_encryption

각 로그파일 별 프라이빗 키가 발급되고, 해당 프라이빗 키는 마스터 키로 암호화되어 리두 로그 파일과 언두 로그 파일의 헤더에 저장된다.
