---
layout: post
title: "[MySQL] 잠금 과 트랜잭션 (Lock and Transacdtion) - Real MySQL 스터디 2회차"
categories: [스터디-데이터베이스]
tags: [MySQL, real mysql]
date: 2024-09-07 23:59:59 +0900
toc: true
---

[K-DEVCON](https://k-devcon.com) 대전 오프라인 스터디에서 Real Mysql 책으로 스터디를 진행해보기로 했다.

발표하면서 준비한 내용을 블로그로도 옮겨보려고 한다.

발표를 위해 ppt도 만들어야하고, 블로그에 올리려면 글도 남겨야 하는게 아쉽긴 하지만, 아직 좋은 방법을 찾지는 못했기 때문에 번거로움을 감수해야할 것 같다.

이 글의 내용은 Mysql 8.0 에서 InnoDB 를 기준으로 정리되었다. 이 글은 정리글이기에 생략이 있으며, 책에서는 이전 버전이나 다른 스토리지 엔진에 대해서도 다루기도 하고 더 자세한 내용들을 다루고 있다. 책의 구성이 이미 안다는것을 전제하에 진행된 부분들도 있어 해당 부분에 대해서 보충설명을 넣기도 하였다.

---

# 아키텍처 - Real MySQL 스터디 2회차

## 트랜잭션

트랜잭션은 데이터의 정합성을 보장한다. 다른 말로 하면 작업의 완전성을 보장한다.

트랜잭션은 아래 두 가지 중 한가지 상태가 될 수 있도록 보장해준다.
논리적인 작업셋 (쿼리의 갯수는 중요하지 않음) 에 대해

- 100% 적용되거나 (COMMIT을 실행했을 때)
- 아무것도 적용되지 않음 (ROLLBACK 또는 트랜잭션을 ROLLBACK 시키는 오류가 발생했을 때)

작업의 일부만 적용되는 현상(Partial update)이 발생하지 않게 한다.

### 잠금

잠금은 동시성을 제어를 보장한다.

여러 커넥션에서 동시에 동일한 자원을 요청할 경우, 순서대로 하나의 커넥션만 변경할 수 있게 해준다.

### 트랜잭션과 잠금의 관계

트랜잭션은 잠금을 사용하여 데이터의 일관성을 보장합니다.
트랜잭션이 시작되면 데이터베이스 시스템은 필요한 데이터에 잠금을 걸고, 트랜잭션이 성공적으로 완료되면 잠금을 해제합니다.

- 트랜잭션은 데이터베이스 시스템이 제공하는 추상적인 개념
- 잠금은 실제로 데이터베이스 엔진이 데이터에 대한 접근을 제어하는 방법

> 트랜잭션이 잠금보다 큰 개념인 것은 아님. 서로 독립적인 개념으로 동작.

### AUTO-COMMIT 모드

MySQL InnoDB는 기본적으로 AUTO COMMIT 모드가 활성화되어 있다.

InnoDB에서 모든 사용자 활동은 트랜잭션 내부에서 발생한다.

auto commit 모드가 활성화 된 경우 각 SQL 문은 자체적으로 단일 트랜잭션을 형성한다.
해당 SQL문이 수행 중 오류를 반환하지 않으면 이후에 커밋을 수행한다.

### 트랜잭션 유무 비교

아래 SQL의 수행 결과는 어떻게 될까? (참고로 myisam는 transaction 이 없는 storage engine 이다.)

```sql
mysql> CREATE TABLE tab_myisam ( fdpk INT NOT NULL, PRIMARYKEY(fdpk) ) ENGINE=MyISAM:
mysql> INSERT INTO tab_myisam (fdpk) VALUES (3);
mysql> CREATE TABLE tab_inodb ( fdpk INT NOT NULL, PRIMARYKEY(fdpk) ) ENGINE=INNODB;
mysql> INSERT INTO tab_innodb (fdpk) VALUES (3);

mysql> INSERT INTO tab_myisam (fdpk) VALUES (1), (2), (3);
mysql> INSERT INTO tab_innodb (fdpk) VALUES (1), (2), (3);

mysql> INSERT INTO tab_myisam (fdpk) VALUES (1), (2), (3);
ERROR 1062 (23000): Duplicate entry '3' for key 'PRIMARY'
mysql> INSERT INTO tab_innodb (fdpk) VALUES (1), (2), (3);
ERROR 1062 (23000): Duplicate entry '3' for key 'PRIMARY'
```

정답은 MyISAM 엔진은 트랜잭션이 없기 때문에 1, 2, 3 이 모두 테이블에 insert 되어있다.
반면에 InnoDB 엔진은 트랜잭션이 있기 때문에 3 만 남아있다. (100% 적용되거나, 아무것도 적용되지 않아야 한다.)

코드로 예시를 들어 비교하면 다음과 같다.

트랜잭션이 없다면, 각 상황에 대해서 성공했는지 실패했는지를 체크하고 성공 하였을 때 이후 단계를 진행하도록 해야한다.

```sql
INSERT INTO tab_a ;
IF (_is_insert1_succeed) {
	INSERT INTO tab_b ...;
	IF (_is_insert2_succeed) {
		// 처리완료
	} ELSE {
		DELETE FROM tab_a WHERE ...;
		IF (_is_delete_succeed) {
		  // tab_a, tab_b 복구완료
		} ELSE {
		  // 해결 불가능한 심각한 상황 발생
		  // 이제 어떻게 하지?
		}
	}
}
```

하지만 트랜잭션이 있다면 `try ... catch` 와 같이 좀 더 편리하게 예외 처리를 할 수 있다.

```sql
try {
	START TRANSACTION;
	INSERT INTO tab_a ...;
	INSERT INTO tab_b ...;
	COMMIT;
} catch(exception) {
    ROLLBACK;
}
```

### 트랜잭션 주의사항

트랜잭션은 꼭 필요한 최소의 코드에만 적용해야 한다.

아래의 로직을 예시로 들어보자.

```
1) 처리 시작
	=> 데이터베이스 커넥션 생성
	=> 트랜잭션 시작
2) 사용자의 로그인 여부 확인
3) 사용자의 글쓰기 내용의 오류 여부 확인
4) 첨부로 업로드된 파일 확인 및 저장
5) 사용자의 입력 내용을 DBMS에 저장
6) 첨부파일 정보를 DBMS에 저장
7) 저장된 내용 또는 기타 정보를 DBMS에서 조회
8) 게시물 등록에 대한 알림 메일 발송
9) 알림 메일 발송 이력을 DBMS 에 저장
	<= 트랜잭션 종료(COMMIT)
	<= 데이터베이스 커넥션 반납
10) 처리완료
```

중간에 있는 몇몇 과정은 꼭 트랜잭션 안에 들어오지 않아도 된다. 따라서 다음과 같이 개선할 수 있다.

```
1) 처리 시작
2) 사용자의 로그인 여부 확인
3) 사용자의 글쓰기 내용의 오류 여부 확인
4) 첨부로 업로드된 파일 확인 및 저장
	=> 데이터베이스 커넥션 생성
	=> 트랜잭션 시작
5) 사용자의 입력 내용을 DBMS에 저장
6) 첨부파일 정보를 DBMS에 저장
	<= 트랜잭션 종료(COMMIT)
7) 저장된 내용 또는 기타 정보를 DBMS에서 조회
8) 게시물 등록에 대한 알림 메일 발송
	=> 트랜잭션 시작
9) 알림 메일 발송 이력을 DBMS 에 저장
	<= 트랜잭션 종료(COMMIT)
	<= 데이터베이스 커넥션 반납
10) 처리완료
```

트랜잭션을 어떻게 설정하면 좋을지는 어떤 작업을 하느냐에 따라 달라질 것이다.

## 잠금

아래의 잠금(락, Lock) 에 대해서 설명한다.

- MySQL Engine Level Lock
  - Global Lock : MySQL 서버 전체를 잠금
  - Table Lock : 테이블 데이터 동기화를 위해 잠금
  - Metadata Lock : 테이블의 구조를 잠금
  - Named Lock : 사용자의 필요에 따라 잠금
- Storage Engine Level Lock
  - Record Lock
  - Gap Lock
  - Auto increment Lock

### MySQL Engine Level Lock

#### 글로벌 락

- FLUSH TABLES WITH READ LOCK 명령으로 획득 가능
- 모든 테이블을 닫고 잠금을 건다.
  - 이전에 수행되고 있는 잠금이 있다면 완료될 때까지 기다린다.
- 서비스용 DB에서는 쓰지 않는 것이 좋다.
- InnoDB 이전 DB들에서 데이터 백업을 할 때 주로 사용됨.

#### 백업 락

- MySQL 8.0 부터는 더 가벼운 글로벌 락인 백업 락 이 도입되었음. (InnoDB용)
- 백업을 더 안정적으로 할 수 있게 되었음.
- 특정 세션에서 백업 락을 획득하면 모든 세션에서 다음과 같이 테이블의 스키마나 사용자의 인증 관련 정보를 변경할 수 없게 된다.
  - 데이터 베이스 및 테이블 등 모든 객체 생성 및 변경, 삭제
  - REPAIR TABLE 과 OPTIMIZE TABLE 명령
  - 사용자 관리 및 비밀번호 변경
- 백업락은 일반적인 테이블의 데이터 변경은 허용된다
- 백업은 주로 레플리카 서버에서 진행한다.
- 백업이 진행 되던 중 소스 서버에서 스키마 변경이 실행되면, 백업에 실패하므로 주의한다.

#### 테이블 락

- 테이블락(Table Lock)은 개별 테이블 단위로 설정되는 잠금이다.
- 명시적 또는 묵시적으로 특정 테이블의 락을 획득할 수 있다.
- 묵시적인 테이블 락은 MyISAM 이나 MEMORY 테이블에 데이터를 변경하는 쿼리를 실행하면 발생한다.
- InnoDB 테이블에도 테이블 락이 설정되지만 대부분의 데이터 변경(DML) 쿼리에서는 무시되고 스키마를 변경하는 쿼리(DDL) 의 경우에만 영향을 미친다.

##### 테이블락을 이용해서 효율적인 데이터 마이그레이션 하기

락을 걸고 전체 데이터를 옮긴다? 데이터가 많을 경우 많은 시간이 소모될 수 있다. 따라서 책에서는 아래의 방식을 소개한다.

데이터를 옮길 테이블을 생성한다.

![migration_data_using_table_lock_1](/assets/images/2024-09-07-mysql-lock-and-transaction/migration_data_using_table_lock_1.png)

최근(e.g. 1시간 직전 또는 하루전)의 데이터까지는 프라이머리 키인 id값을 범위별로 나눠서 여러개의 스레드로 빠르게 복사한다 (1~9999, 10000~19999, 20000~29999, …)

![migration_data_using_table_lock_2](/assets/images/2024-09-07-mysql-lock-and-transaction/migration_data_using_table_lock_2.png)

이후 다음과 같이 Lock을 활용하여 나머지 데이터를 이동 및 테이블 이름을 변경한다.

![migration_data_using_table_lock_3](/assets/images/2024-09-07-mysql-lock-and-transaction/migration_data_using_table_lock_3.png)

참고로 DDL(데이터 정의 언어) 문은 자동으로 커밋되기 때문에 COMMIT 문이 필요하지 않다고 한다.

##### `SET autocommit = 0` vs `START Transaction (BEGIN)`

둘 다 트랜잭션을 수동으로 실행하는 명령어이다.

하지만 주석 내용을 보면 `SET autocommit = 0` 을 사용하라고 되어있는데

`LOCK TABLES` 명령어는 `SET autocommit = 0` 을 쓴 경우가 아니면 테이블을 잠그기 전에 모든 활성 트랜잭션을 암묵적으로 커밋한다고 한다. 따라서 여기서는 `SET autocommit = 0` 를 써야 한다.

참고 : [https://dev.mysql.com/doc/refman/8.4/en/lock-tables.html](https://dev.mysql.com/doc/refman/8.4/en/lock-tables.html)

#### 네임드 락

네임드 락(Named Lock)은 임의의 문자열(key, id)에 대해 잠금을 설정한다.

자주 사용되지는 않지만 다음과 같이 사용할 수 있다.

- 데이터베이스 서버 1대에 5대의 웹 서버가 접속해서 서비스하는 상황에서 5대의 웹 서버가 상호 동기화를 처리해야 할 때
- 많은 레코드에 대해서 복잡한 요건으로 레코드를 변경해야 할 때

락에 이름을 지정한다고 이해하면 편할 것 같다.

#### 메타데이터 락

데이터베이스 객체(대표적으로 테이블이나 뷰 등)의 이름이나 구조를 변경하는 경우에 획득하는 잠금

### Storage Engine Level Lock

InnoDB 스토리지 엔진은 MySQL에서 제공하는 잠금과는 별개로 스토리지 엔진 내부에서 레코드 기반의 잠금 방식을 탑재하고 있다.
이를 통해 뛰어난 동시성 처리를 제공한다.

#### InnoDB 스토리지 엔진 잠금 조회하기

infomation_schema 데이터베이스의 테이블들로 조회할 수 있다.

- innodb_trx: 현재 활성화된 트랜잭션에 대한 정보
- innodb_locks: 현재 설정된 모든 락에 대한 정보
- innodb_lock_waits: 현재 락 대기 상태에 대한 정보

조회하여 장시간 잠금을 가지고 있는 클라이언트를 찾아서 종료시킬 수 있다.

- KILL [CONNECTION | QUERY] processlist_id

#### InnoDB 스토리지 엔진 락 종류

![innodb_storage_lock](/assets/images/2024-09-07-mysql-lock-and-transaction/innodb_storage_lock.png)

- 레코드 락 (Record Lock)
  - 레코드 기반의 잠금
  - 작은 공간으로 관리 가능
- 갭 락 (Gap Lock)
  - 레코드와 레코드 사이를 잠금
- 넥스트 키 락 (Next Key Lock)
  - 레코드 락 + 갭 락
- 자동증가 락 (Auto Increment Lock)

#### 레코드 락

InnoDB의 레코드락은 정확하게는 레코드 자체가 아니라 인덱스의 레코드를 잠금.

예시로 들면 다음과 같다.

```sql
UPDATE employees
SET hire_date=NOW()
WHERE first_name='Georgi' AND last_name='Klassen';
```

위 쿼리를 수행한다고 했을 때

![record_lock](/assets/images/2024-09-07-mysql-lock-and-transaction/record_lock.png)

인덱스로는 first_name 만 설정되어 있기 때문에 first_name 이 Georgi 인 모든 레코드를 잠그게 된다.
last_name 은 인덱스가 설정되지 않았기 때문에 레코드 락에 영향을 미치지 않았다.

그러면 만약 테이블에 인덱스가 없으면 어떻게 될까? 테이블을 풀 스캔하면서 UPDATE를 진행한다. 이 때 테이블의 모든 레코드를 잠그게 된다.

#### 갭 락

레코드와 레코드 사이를 잠금

#### 넥스트 키 락

레코드 락 + 갭 락

#### 자동증가 락

자동 증가하는 숫자 값(AUTO_INCREMENT)을 추출하기 위한 락 이다. 버전 별로 다음과 같은 특정을 지닌다.

- MySQL 8.0 (innodb_autoinc_lock_mode=2)
  - 락을 걸지 않고 경량화된 래치를 사용한다.
  - 연속된 자동 증가 값을 보장하지는 않는다. (유니크는 보장한다.)
  - ROW 포맷 바이너리 로그에 적합
- 이전 버전 (innodb_autoinc_lock_mode=1)
  - 테이블 수준의 잠금을 사용. INSERT, REPLACE 시 잠금이 걸렸다 즉시 해제된다.
  - STATEMENT 포맷 바이너리 로그에 적합

##### 바이너리 로그 - ROW 포맷 과 STATEMENT 포맷

- Row 포맷은 각 행(row)의 변경된 값을 기록합니다.

  - 일관성 보장에 이점이 있음.
  - 다만 데이터를 더 보관하게 됨.
  - MySQL 8.0 부터는 ROW 포맷이 기본값. (STATEMENT 포맷에 비해 최근 나온 포맷)

- STATEMENT 포맷은 SQL 문(statement) 자체를 바이너리 로그에 기록한다.

  - 복제 환경에서 일관성 보장이 되지 않는 경우가 있음.

## 격리 수준

하나의 트랜잭션 내에서 또는 여러 트랜잭션 간의 작업 내용을 어떻게 공유하고 차단할 것인지를 결정하는 레벨을 의미한다.

### READ UNCOMMITTED

commit 되지 않은 것을 우선으로 가져온다.

![read_uncommited](/assets/images/2024-09-07-mysql-lock-and-transaction/read_uncommited.png)

### READ COMMITTED

commit 된 것을 우선으로 가져온다.

![read_commited](/assets/images/2024-09-07-mysql-lock-and-transaction/read_commited.png)

### REPEATABLE READ

한 트랜잭션 내에서 동일한 결과를 보장한다.(각 레코드에 대해)

![repeatable_read](/assets/images/2024-09-07-mysql-lock-and-transaction/repeatable_read.png)

#### REPEATABLE READ - 팬텀리드 발생 사례 및 해결방법

REPEATABLE READ 에서 팬텀리드가 발생되는 사례는 다음과 같다.

![repeatable_read_phantom_read](/assets/images/2024-09-07-mysql-lock-and-transaction/repeatable_read_phantom_read.png)

이럴 경우에는 Gap Lock 을 이용해서 팬텀리드 발생을 방지할 수 있다.
(`select ... for update` 를 통해서 gap lock을 걸었다.)

![repeatable_read_phantom_read_fix](/assets/images/2024-09-07-mysql-lock-and-transaction/repeatable_read_phantom_read_fix.png)

## 기타

### 리두 로그와 바이너리 로그

리두 로그는 엔진 차원이고, 바이너리 로그는 server 차원이다
리두 로그는 트랜잭션의 내구성을 보장하기 위한 것이고, 바이너리 로그는 복원을 위한 것이다. (데이터 복제에도 사용된다.)
