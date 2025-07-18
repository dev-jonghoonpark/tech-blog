---
layout: "post"
title: "[MySQL] LOAD DATA로 대용량 데이터 빠르게 삽입하기"
description:
  "MySQL의 `LOAD DATA` 명령어를 활용해 대용량 데이터를 빠르게 삽입하는 방법을 소개합니다.
  \ 이 명령어는 텍스트 파일에서 데이터를 읽어와 테이블에 신속하게 삽입하며, 일반적인 `INSERT` 방식보다 더 빠른 성능을 제공합니다.
  \ Container를 사용해 MySQL 환경을 설정하고, CSV 파일을 통해 데이터를 삽입하는 과정을 설명합니다.
  \ 이를 통해 대량의 데이터를 효율적으로 처리할 수 있음을 확인했습니다."
categories:
  - "스터디-데이터베이스"
  - "개발"
tags:
  - "MySQL"
  - "LOAD DATA"
  - "LOAD"
  - "적재"
  - "대용량"
  - "INSERT"
  - "BULK INSERT"
  - "BULK"
  - "Podman"
  - "Docker"
  - "Container"
  - "Thread"
  - "Single Thread"
date: "2025-07-16 14:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-07-16-mysql-load-data.jpg"
---

# `LOAD DATA` 로 대용량 데이터 빠르게 삽입하기

작년 말에 K-DEVCON 스터디에서 MySQL을 공부하면서 `LOAD DATA` 명령어에 대해서 알게 되었다.

- [INSERT, UPDATE, DELETE 쿼리 작성 및 최적화 - Real MySQL 스터디 7회차](https://jonghoonpark.com/2024/12/21/mysql-insert-update-delete-optimize)

최근 대용량 테스트 데이터를 적재해야 하는 상황이 생기면서, `LOAD DATA` 를 실제로 사용해볼 기회가 생겼다.

## LOAD DATA 란?

[LOAD DATA](https://dev.mysql.com/doc/refman/8.4/en/load-data.html) 명령어는 텍스트 파일로부터 데이터를 읽어와 테이블에 매우 빠르게 삽입할 수 있다. Real MySQL에서는 일반적인 insert 방식보다 최대 약 20배의 성능차를 보여준다고 설명하고 있다.

`LOAD DATA` 는 빠르지만, **단일 스레드** 로 동작한다는 점에 유의하여 사용한다. Real MySQL에서는 여러개의 파일로 분할하여 병렬로 진행하라는 팁을 제공해주었다.

## LOAD DATA 사용해보기

### MySQL 세팅

**Docker Desktop** 을 사용하지 못하는 환경이라, **Podman Desktop** 을 사용하였다. [**Podman**](https://podman.io/) 은 이번에 처음 사용해 보았는데 Docker 와 호환되는(Compatible) 한 인터페이스를 제공하여, Docker 경험이 있다면 큰 어려움 없이 사용할 수 있었다.

실제 운영 환경과 동일하게 맞추기 위해 `MySQL 8.0.32` 버전으로 테스트를 진행하였다.

```sh
podman run -dit -e MYSQL_ROOT_PASSWORD=testtesttesttest -e MYSQL_DATABASE=test -p 3306:3306  --name local-mysql mysql:8.0.32 --innodb-buffer-pool-size=12GB
```

버퍼풀 사이즈는 메모리의 50~75% 정도를 할당해주는 것이 좋다. 이 글에서는 컨테이너에 16GB 메모리를 할당하였기 때문에 버퍼 풀 사이즈를 12GB로 설정하였다.

#### 버퍼풀 사이즈 확인 및 설정 방법

현재 설정된 버퍼풀 사이즈는 아래 SQL로 확인할 수 있다.

```sql
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
```

버퍼풀 사이즈 설정은 위에서 한것과 같이 mysql 을 실행할 때 옵션값을 전달해주거나, (서버 실행중 유지)

```sh
$> mysqld --innodb-buffer-pool-size=12GB
```

SET 문을 통해서 설정하거나, (서버 실행중 유지)

```sql
SET GLOBAL innodb_buffer_pool_size=12884901888; -- 12gb
```

my.ini 파일을 통해서 설정할 수 있다. (영구 유지)

```ini
[mysqld]
innodb_buffer_pool_size=12884901888 # 12gb
```

### 데이터 세팅

간단한 자바코드를 작성하여 파일로 csv 파일을 생성하도록 하였다. csv 파일에는 컬럼 헤더를 포함하지 않았다. [faker](https://github.com/DiUS/java-faker) 를 이용하여 어느 정도 랜덤한 있는 데이터가 나올 수 있도록 하였다. 실제 데이터와 유사성을 높이기 위해 일부 필드에 암호화를 적용해 생성했다.

```
USER0000001,7426C09FB3...,Rob,Gerlach,47a7e9bd9...,251FE112...,10,\N,10,\N,\N,N,0,40,...
...
```

csv 특성 상 `null` 처리가 까다로운데, `LOAD DATA` 는 `\N` 을 `null`로 인식한다.

그냥 빈 공백으로 처리할 경우 삽입 처리중에 아래와 같은 에러가 발생될 수 있으니 주의하자.

```
[22001][1292] Data truncation: Incorrect ... value: '' for column 'column_name' at row xxx
```

### Data 파일을 container 내부로 복사하기

다음과 같이 cp 명령어를 사용하여 데이터 파일을 container 내부로 복사할 수 있다.

```sh
podman cp /Users/jonghoonpark/project/slow-query-select-member-list/output.csv local-mysql:/var/lib/mysql-files/file.csv
```

### `LOAD DATA` 를 이용하여 데이터 삽입하기

파일을 컨테이너 내부로 옮겼다면, 아래 명령어를 통해 데이터를 삽입할 수 있다. `USER_TABLE` 이라는 이름의 테이블에 데이터를 삽입한다.

```sql
LOAD DATA INFILE '/var/lib/mysql-files/file.csv'
INTO TABLE USER_TABLE
FIELDS TERMINATED BY ',' -- csv 파일의 구분자 (쉼표인 경우)
ENCLOSED BY '"' -- 필드가 따옴표로 묶여 있는 경우
LINES TERMINATED BY '\n' -- 줄 바꿈 문자 (Unix/Linux 기준)
-- IGNORE 1 LINES; -- 헤더 있는 경우
```

## 테스트로 `LOAD TEST` 알아보기

### 테스트 1 : `INSERT VALUES` 와 `LOAD DATA` 간의 소요시간 비교

`INSERT VALUES` 와 `LOAD DATA` 의 속도는 얼마나 차이날까? 이를 알아보기 위해 다음과 같이 테스트를 진행하였다.

실행 환경은 다음과 같다.

- 데이터는 **400만개** 로 고정
- `vCPU 12`, `메모리 16GB` 할당으로 고정
- 실행을 마친 후에는 table 을 truncate 한 후, container를 재실행

| 방식            | 소요시간 |
| --------------- | -------- |
| `INSERT VALUES` | 16m 27s  |
| `LOAD DATA`     | 4m 10s   |

결과: 약 4배의 차이가 발생되었다.

### 테스트 2 : vCPU 할당에 따른 소요시간 비교

`LOAD DATA` 는 **단일 스레드** 로 동작한다. 그러면 vCPU 할당이 작업 소요시간에 크게 영향이 없을까? 이를 알아보기 위해 다음과 같이 테스트를 진행하였다.

실행 환경은 다음과 같다.

- 데이터는 **400만개** 로 고정
- `메모리 16GB` 할당으로 고정
- 실행을 마친 후에는 table 을 truncate 한 후, container를 재실행

| Podman vCPU 할당 | 소요시간 |
| ---------------- | -------- |
| vCPU 2           | 4m 25s   |
| vCPU 4           | 4m 12s   |
| vCPU 8           | 4m 18s   |
| vCPU 12          | 4m 10s   |

결과: `LOAD DATA`는 단일 스레드로 동작하다보니, 실제로 vCPU 할당에 크게 영향을 받지 않는 것을 확인할 수 있었다.

## 마무리

스터디를 하며 배웠던 `LOAD DATA` 를 실제로 사용해보았다.
대용량 데이터를 빠르게 삽입할 때, `LOAD DATA`가 `INSERT VALUES` 보다도 더 효과적인 방법임을 확인할 수 있었다.

`LOAD DATA` 는 단일 스레드로 동작하기 때문에 vCPU 할당을 늘려도 처리 속도에는 큰 영향을 미치지 않는다는 것을 직접 확인해 보았다. 다음에 더 큰 데이터를 적재해야할 일이 있다면 파일을 나누어 병렬로 적재하는 전략도 고려를 해봐야겠다.

이 글이 대용량 데이터 적재 작업에 참고가 되길 바란다.
