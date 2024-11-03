---
layout: post
title: "[MySQL] 풀 스캔 패턴 및 튜닝  - Real MySQL 스터디 5회차"
categories: [스터디-데이터베이스]
tags:
  [
    MySQL,
    index,
    scan,
    index scan,
    full scan,
    table full scan,
    query,
    pattern,
    optimize,
    optimizer,
    explain,
    access type,
  ]
date: 2024-11-03 23:00:00 +0900
toc: true
---

[K-DEVCON](https://k-devcon.com) 대전 개발자 스터디에서 Real Mysql 책으로 스터디를 진행해보기로 했다.

발표하면서 준비한 내용을 블로그로도 옮겨보려고 한다.

이 글의 내용은 Mysql 8.0 에서 InnoDB 를 기준으로 정리되었다. 이 글은 정리글이기에 생략이 있으며, 책에서는 이전 버전이나 다른 스토리지 엔진에 대해서도 다루기도 하고 더 자세한 내용들을 다루고 있다. 책의 구성이 이미 안다는것을 전제하에 진행된 부분들도 있어 해당 부분에 대해서 보충설명을 넣기도 하였다.

---

# MySQL 풀스캔 쿼리 패턴 및 튜닝

[지난 시간](https://jonghoonpark.com/2024/10/19/mysql-index)에는 MySQL 에서 인덱스를 어떻게 처리하는지에 대해서 정리해보았다.
이번시간에는 풀 스캔이 발생되는 패턴과 어떻게 튜닝을 해야하는지에 대해서 알아본다.

먼저 그에 앞서 실행계획에 대해서 간단하게 알아본다.

## 실행계획 (Explain)

실행계획은 MySQL이 쿼리를 어떻게 처리할지에 대한 정보를 제공해준다. 개발자는 실행계획을 바탕으로 쿼리를 최적화 할 수 있다.
오늘 내용을 위해 중요한 부분만 간단하게 정리해본다. (더 자세한 내용은 추후에 다뤄보도록 한다.)

### 실행계획 사용법

실행게획은 실행하고자 하는 쿼리문의 앞에 `EXPLAIN` 을 붙여주면 확인해볼 수 있다.

```
{EXPLAIN} explainable_stmt

explainable_stmt: {
    SELECT statement
  | TABLE statement
  | DELETE statement
  | INSERT statement
  | REPLACE statement
  | UPDATE statement
}
```

### 실행계획 출력 형식

실행 계획의 주요 값은 다음과 같다.

| 이름    | 설명                  |
| ------- | --------------------- |
| table   | 참조 테이블 이름      |
| type    | 조인 유형 (접근 방식) |
| key     | 선택한 인덱스 이름    |
| key_len | 선택한 키의 길이      |
| rows    | 검사할 행의 수 (추정) |

이 중 오늘 주요하게 볼 부분은 `type` 이다.

### 실행계획 접근 방식

| type        | 설명                                                                                                                                   |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| system      | 테이블에 행이 하나일 경우.                                                                                                             |
| const       | 기본 키 또는 고유키를 사용 테이블에는 최대 하나의 일치하는 행이 있는 경우 한 번만 읽기 때문에 매우 빠르다.                             |
| ref         | 인덱스를 사용, 여러 개 행에 접근할 가능성이 있다. 일치하는 인덱스 값이 있는 모든 행이 읽음.                                            |
| ref_or_null | ref 와 비슷하지만 null 에 대해서도 처리한다.                                                                                           |
| index_merge | 여러 인덱스를 동시에 사용할 경우 사용. 여러 인덱스의 검색 결과를 합쳐서 최종 결과를 생성하는 방식.                                     |
| range       | 인덱스 특정 범위의 행에 접근한다. =, <>, >, >=, <, <=, IS NULL, <=>, BETWEEN, LIKE, or IN() 중 하나를 사용하여 상수와 비교될 때 사용   |
| index       | 인덱스를 사용하여 모든 행을 스캔. 테이블의 실제 데이터를 읽지 않고 인덱스만 사용하여 데이터를 가져올 수 있는 경우 사용 (커버링 인덱스) |
| all         | 인덱스를 사용하지 않고 테이블 전체를 스캔                                                                                              |

#### 주의 해야 하는 타입

- ALL, index : 테이블 또는 특정 인덱스가 전체 행에 접근하기 때문에 테이블 크기가 크면 효율이 떨어진다.
- ref_or_null : NULL이 들어있는 행은 인덱스의 맨 앞에 모아서 저장하지만 그 건수가 많으면 MySQL 서버의 작업량이 방대해질 수 있으므로 주

## 테이블 풀 스캔 패턴

- 컬럼이 가공되는 경우
- 인덱싱 되지 않은 컬럼을 조건절에 사용
  - 인덱싱 되지 않은 컬럼을 조건절에 OR 연산과 함께 사용
- 복합 인덱스의 컬럼들 중 선행 컬럼을 조건에서 누락
- LIKE 연산에서 시작 문자열로 와일드 카드를 사용
- REGEXP 연산 사용
- 테이블 풀 스캔이 인덱스 사용보다 더 효율적인 경우

각각의 케이스에 대해서 알아본다.

EXPLAIN 출력 값의 type을 중심으로 보면 좋다. 풀 스캔이 발생되는 패턴과 개선된 결과를 함께 정리하였다.

### 컬럼이 가공되는 경우

가능하면 컬럼 값을 그대로 사용할 수 있는 방향으로 설계하자.

#### 연산

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  account_type varchar(10) NOT NULL,
  joined_at datetime NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_accounttype (account_type),
  KEY ix_joinedat (joined_at)
)
```

```sql
EXPLAIN SELECT * FROM users WHERE id * 1 = 12345;
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users WHERE id = 12345;
```

| id  | table | type  | key     | key_len | rows |
| --- | ----- | ----- | ------- | ------- | ---- |
| 1   | users | const | PRIMARY | 4       | 1    |

id 에 1을 곱하는 연산이 추가될 경우 type이 all로 지정된 것을 볼 수 있다.
현실에서 1을 곱할 일은 크게 없겠지만 컬럼 값이 가공되었을 경우에 대한 예시이다.

#### 함수

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  joined_at datetime NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_joinedat (joined_at)
)
```

```sql
EXPLAIN SELECT * FROM users WHERE DATE(joined_at) = '2022-07-21';
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users
WHERE joined_at >= '2022-07-21 00:00:00'
AND joined_at < '2022-07-22 00:00:00';
```

| id  | table | type  | key         | key_len | rows  |
| --- | ----- | ----- | ----------- | ------- | ----- |
| 1   | users | range | ix_joinedat | 5       | 18466 |

`DATE` 함수를 사용하여 datetime에서 date만 분리하는 쿼리를 작성하였을 때 풀 스캔을 하는 것을 볼 수 있다.

#### 형변환

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  account_type varchar(10) NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_accounttype (account_type)
)
```

```sql
EXPLAIN SELECT * FROM users WHERE account_type=3
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users WHERE account_type='3'
```

| id  | table | type | key            | key_len | rows   |
| --- | ----- | ---- | -------------- | ------- | ------ |
| 1   | users | ref  | ix_accounttype | 42      | 104196 |

account_type 이 문자열(`varchar`)을 다루는데 where 문에서는 정수를 사용하여 풀 스캔이 되었다.

##### 예외 (형 변환 처리 우선순위)

```sql
EXPLAIN SELECT * FROM users WHERE id=1234;
EXPLAIN SELECT * FROM users WHERE id='1234';
```

| id  | table | type  | key     | key_len | rows |
| --- | ----- | ----- | ------- | ------- | ---- |
| 1   | users | const | PRIMARY | 4       | 1    |

두 SQL 문은 동일한 실행 결과가 나오게 된다. 그 이유는 mysql 내부적으로 형변환 우선순위가 있어 숫자를 문자로 변경하는 것보다 문자를 숫자로 변경하는 것에 더 우선순위를 두기 때문에 여기서는 id 컬럼값을 형변환 처리하는것이 아니라 조건으로 주어진 문자열 값을 숫자로 형변환 하게 된다. 그래서 id 컬럼이 가공되지 않기 때문에 정상적으로 primary key 를 사용할 수 있다.

가능하면 컬럼값과 일치하게 주는것이 좋다.

### 인덱싱 되지 않은 컬럼을 조건절에 OR 연산과 함께 사용

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  account_type varchar(10) NOT NULL,
  joined_at datetime NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_accounttype (account_type),
)
```

```sql
EXPLAIN SELECT * FROM users
WHERE account_type='7' OR joined_at >= '2022-07-24 00:00:00'
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
ALTER TABLE users ADD KEY ix_joinedat (joined_at); -- 인덱스 추가

EXPLAIN SELECT * FROM users
WHERE account_type='7' OR joined_at >= '2022-07-24 00:00:00'
```

| id  | table | type        | key                         | key_len | rows |
| --- | ----- | ----------- | --------------------------- | ------- | ---- |
| 1   | users | index_merge | ix_accounttype, ix_joinedat | 42,5    | 5492 |

인덱싱 되지 않은 컬럼을 조건절에 OR 연산과 함께 사용하여 풀 스캔이 되었다. 익덱스 되지 않는 컬럼인 `joined_at` 에 인덱스를 추가하여 성능을 개선할 수 있다.

인덱스를 무작정 추가하는 것은 좋지 않다. 상황에 따라 판단하자.

### 복합 인덱스의 컬럼들 중 선행 컬럼을 조건에서 누락

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  account_type varchar(10) NOT NULL,
  joined_at datetime NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_accounttype_joinedat (account_type, joined_at) -- 복합 인덱스
)
```

```sql
EXPLAIN SELECT * FROM users
WHERE joined_at >= '2022-07-24 00:00:00'
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users
WHERE account_type='3' OR joined_at >= '2022-07-24 00:00:00'
```

| id  | table | type  | key                     | key_len | rows |
| --- | ----- | ----- | ----------------------- | ------- | ---- |
| 1   | users | range | ix_accounttype_joinedat | 47      | 1112 |

index는 있지만 제대로 사용하지 못한 케이스라고 볼 수 있다.
b-tree 는 왼쪽부터 시작하기 때문에 왼쪽이 없으면 사용할 수 없다.

### LIKE 연산에서 시작 문자열로 와일드 카드를 사용

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  first_name varchar(14) NOT NULL,
  ...,
  PRIMARY KEY(id),
  KEY ix_firstname (first_name)
)
```

```sql
EXPLAIN SELECT * FROM users WHERE first_name LIKE '%Esther%'
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users WHERE first_name LIKE 'Esther%'
```

| id  | table | type  | key          | key_len | rows |
| --- | ----- | ----- | ------------ | ------- | ---- |
| 1   | users | range | ix_firstname | 58      | 1    |

마찬가지로 b-tree는 왼쪽부터 시작한다. 따라서 왼쪽이 비어있으면 사용할 수 없다.

### REGEXP 연산 사용

```sql
EXPLAIN SELECT * FROM users WHERE first_name REGEXP '^[abc]...'
```

```sql
EXPLAIN SELECT * FROM users WHERE first_name REGEXP '^Esther'
```

두 케이스에 있는 REGEX는 앞부분부터 시작하지만, 모든 컬럼에 REGEXP를 적용해봐야 하므로 풀 스캔을 하게 된다.

### 테이블 풀 스캔이 인덱스 사용보다 더 효율적인 경우

```sql
CREATE TABLE users (
  id int NOT NULL AUTO_INCREMENT,
  ...,
  group_name varchar(10) DEFAULT NULL,
  dormant_at datetime DEFAULT NULL,
  ...,
  PRIMARY KEY (id),
  KEY ix_groupname (group_name),
  KEY ix_dormantat (dormant_at)
)
```

| group_name | count(\*) |
| ---------- | --------- |
| A          | 150012    |
| B          | 149982    |
| C          | 15        |
| D          | 15        |

| dormant_at | count(\*) |
| ---------- | --------- |
| NULL       | 299994    |
| NOT NULL   | 30        |

```sql
EXPLAIN SELECT * FROM users WHERE group_name IN ('A', 'B')
```

| id  | table | type | key  | key_len | rows   |
| --- | ----- | ---- | ---- | ------- | ------ |
| 1   | users | ALL  | NULL | NULL    | 299342 |

```sql
EXPLAIN SELECT * FROM users WHERE group_name IN ('C', 'D')
```

| id  | table | type  | key          | key_len | rows |
| --- | ----- | ----- | ------------ | ------- | ---- |
| 1   | users | range | ix_groupname | 43      | 30   |

데이터 통계상 대부분의 데이터가 A,B에 해당하기 때문에 이 경우에는 index가 있지만, 그래도 풀 스캔을 한다.

### 기타

NOT 이 들어간다고 무조건 풀 스캔인 것은 아니다.

## 정리

- 컬럼이 가공되는 경우 인덱스를 사용하지 못한다.
- 인덱싱 되지 않은 컬럼에 대한 조건을 OR 연산과 함께 사용하는 경우 인덱스를 사용하지 못한다.
- 복합 인덱스로 구성돼있는 컬럼들 중 선행 컬럼을 제외하고 조건으로 사용하는 경우 인덱스를 사용하지 못한다.
- LIKE 연산에서 시작 문자열로 와일드카드(%)를 사용하는 경우 인덱스를 사용하지 못한다.
- REGEXP 연산을 사용하는 경우 인덱스를 사용하지 못한다.
- 테이블 풀스캔이 인덱스를 사용하는 것보다 효율적인 경우 인덱스를 사용하지 않는다.

## 참고

- [Mysql Documentation - EXPLAIN Output Format](https://dev.mysql.com/doc/refman/8.4/en/explain-output.html)
- [Real MySQL 시즌 1 - Part 2](https://www.inflearn.com/course/real-mysql-part-2)
- [Mysql Explain](https://cheese10yun.github.io/mysql-explian/)
