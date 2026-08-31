---
layout: "post"
title: "PostgreSQL VACUUM과 VACUUM FULL"
description: "MySQL을 주로 쓰다가 PostgreSQL을 쓰게 되면서 MVCC와 VACUUM을 다시 들여다보게 되었다. DELETE를 해도 용량이 줄지 않는 이유부터 VACUUM과 VACUUM FULL의 차이, autovacuum이 일을 못 하게 되는 상황까지 정리해본다."
categories:
  - "스터디-데이터베이스"
tags:
  - "PostgreSQL"
  - "VACUUM"
  - "VACUUM FULL"
  - "MVCC"
  - "dead tuple"
  - "bloat"
  - "autovacuum"
  - "InnoDB"
date: "2026-08-31 01:40:00 +0900"
toc: true
---

## 들어가며

나는 주로 MySQL을 사용해온 개발자인데 최근에는 회사 프로젝트로 PostgreSQL을 쓰고 있다.

MVCC와 VACUUM이라는 것에 대해서는 어느 정도 알고 있었다. "PostgreSQL은 DELETE를 해도 데이터가 바로 지워지지 않고, VACUUM이 그걸 정리한다" 정도. 그런데 최근에 자세히 들여다볼 기회가 생겼다. 그 과정에서 알게 된 것들이 있어 정리해본다.

정리하면서 몇 가지는 실제로 확인해봤다. 아래에 나오는 수치는 컨테이너에 PostgreSQL 17을 띄워놓고 직접 재본 값이다.

```bash
podman run -d --name vacuum-demo -e POSTGRES_PASSWORD=pass -p 55432:5432 postgres:17
```

동작을 관찰하려고 실험용 테이블은 autovacuum을 꺼두었다. (실제 운영에서 이러면 안 되는 이유는 뒤에서 정리한다)

```sql
CREATE TABLE t (
  id   bigint PRIMARY KEY,
  name text,
  memo text
) WITH (autovacuum_enabled = off);

INSERT INTO t
SELECT i, 'name-' || i, repeat('x', 100)
FROM generate_series(1, 1000000) i;

CREATE INDEX idx_t_name ON t (name);
```

용어를 몇 개 먼저 정리해둔다. 아래에서 계속 나온다.

| 용어                       | 뜻                                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 튜플(tuple)                | 행(row) 하나. PostgreSQL은 한 행의 여러 버전을 각각 튜플이라고 부른다                                        |
| 힙(heap)                   | 테이블 본체가 저장된 파일. 인덱스 파일과 구분해서 부르는 말이다                                              |
| 페이지(page) / 블록(block) | 파일을 읽고 쓰는 기본 단위. 기본값 8KB. 같은 것을 저장 구조 관점에서 페이지, 입출력 관점에서 블록이라 부른다 |

## MVCC

VACUUM이 왜 필요한지 이해하려면 쓰레기가 왜 생기는지부터 봐야 한다.

MVCC(Multi-Version Concurrency Control)는 동시성 제어 방식의 하나다. 데이터를 덮어쓰지 않고 여러 버전을 함께 유지해서 각 트랜잭션이 자기 스냅샷에 맞는 버전을 읽게 한다. 목적은 하나다.

> 읽기는 쓰기를 막지 않고, 쓰기는 읽기를 막지 않는다.

락 기반이라면 누가 쓰는 동안 읽는 쪽이 기다려야 한다. MVCC는 읽는 쪽에게 옛 버전을 보여주므로 서로 기다리지 않는다.

### xmin과 xmax

PostgreSQL은 모든 행(튜플)에 숨은 시스템 컬럼을 붙여서 이걸 구현한다.

| 컬럼   | 의미                                             |
| ------ | ------------------------------------------------ |
| `xmin` | 이 버전을 만든 트랜잭션 ID                       |
| `xmax` | 이 버전을 지우거나 갱신한 트랜잭션 ID (없으면 0) |

숨은 컬럼이지만 명시하면 조회할 수 있다.

```sql
SELECT xmin, xmax, id FROM t WHERE id <= 3;
```

연산별로 실제 일어나는 일은 이렇다.

| 연산     | 실제로 하는 일                                            |
| -------- | --------------------------------------------------------- |
| `INSERT` | 새 튜플에 `xmin` 기록                                     |
| `DELETE` | 기존 튜플에 `xmax`만 기록. 데이터는 그대로 남음           |
| `UPDATE` | 새 튜플을 INSERT + 기존 튜플에 `xmax` 기록 = 삭제 후 삽입 |

가시성 판단은 "내 스냅샷 기준으로 `xmin`은 이미 커밋되어 보이고, `xmax`는 아직 안 보이는" 버전만 읽는 방식이다.

여기서 세 가지가 따라온다.

1. 롤백이 매우 싸다. 되돌릴 게 없고 그 트랜잭션이 만든 버전을 안 보이는 것으로 두면 끝이다.
2. UPDATE가 비싸다. 한 컬럼만 바꿔도 행 전체를 새로 쓰고 인덱스도 새 위치를 가리켜야 한다.
3. 쓰레기가 쌓인다. 이 글의 내용이 여기서 시작된다.

### MySQL(InnoDB)과 비교하면

MySQL을 쓰다 왔다면 이 지점이 가장 헷갈리는 부분인 것 같다. InnoDB도 MVCC를 쓰는데 옛 버전을 어디에 두느냐가 다르다.

|                | PostgreSQL                        | InnoDB                                  |
| -------------- | --------------------------------- | --------------------------------------- |
| 옛 버전 위치   | 테이블 안에 그대로 (새 튜플 추가) | undo log (별도 테이블스페이스)          |
| UPDATE 시      | 새 버전을 힙에 추가               | 레코드는 덮어쓰고, 이전 이미지를 undo에 |
| 과거 버전 읽기 | 힙에 있는 옛 튜플을 그대로 읽음   | undo를 거슬러 올라가 재구성             |
| 롤백 비용      | 저렴 (버려두면 됨)                | 비쌈 (undo로 복원해야 함)               |
| 정리 담당      | VACUUM / autovacuum               | purge 스레드                            |
| 주로 부푸는 곳 | 테이블·인덱스                     | undo 테이블스페이스                     |

InnoDB도 DELETE가 즉시 지우는 게 아니다. 레코드에 delete mark만 달아두고 purge 스레드가 나중에 실제로 제거한다. 오래 열린 트랜잭션이 purge를 막아 history list가 길어지는 현상도 PostgreSQL의 상황과 똑같다. `.ibd` 파일이 DELETE 후에 안 줄어들고 `OPTIMIZE TABLE`로 재구성해야 줄어드는 것도 마찬가지다.

그러니까 "즉시 안 지워진다 → 별도 프로세스가 정리한다 → 파일을 줄이려면 재구성이 필요하다"는 구조는 두 DB가 같다. 차이는 PostgreSQL이 옛 버전을 테이블 본체에 두기 때문에 그 영향이 테이블과 인덱스 크기로 직접 드러난다는 점이다. VACUUM이 MySQL의 purge보다 훨씬 자주 화제가 되는 이유도 여기 있는 것 같다.

## Dead tuple

Dead tuple은 어떤 트랜잭션의 스냅샷에서도 더 이상 보이지 않게 된 튜플이다. 공간은 차지하지만 아무도 읽지 않는다. UPDATE가 남긴 구 버전이 대표적이지만 그것만은 아니다. DELETE된 행도, 롤백된 트랜잭션이 INSERT했던 튜플도 같은 신세다.

두 가지를 구분해야 한다.

- 보이지 않는 것과 회수된 것은 다르다. DELETE는 앞의 것만 한다. 회수는 VACUUM의 일이다.
- 언제 dead가 되는지는 시계가 아니라 스냅샷이 정한다. 현재 살아 있는 가장 오래된 스냅샷에게도 안 보일 때 비로소 dead다. 오래된 트랜잭션 하나가 dead 판정 자체를 지연시킬 수 있는 것도 이 때문이다.

100만 행 중 90%를 지우고 크기를 재봤다.

```sql
DELETE FROM t WHERE id % 10 <> 0;

SELECT pg_size_pretty(pg_relation_size('t'))       AS heap,
       pg_size_pretty(pg_indexes_size('t'))        AS indexes,
       pg_size_pretty(pg_total_relation_size('t')) AS total,
       (SELECT count(*) FROM t)                    AS rows;
```

```
  heap  | indexes | total  |  rows
--------+---------+--------+--------
 149 MB | 52 MB   | 201 MB | 100000
```

행은 100만 개에서 10만 개로 줄었는데 파일 크기는 그대로다. 인덱스도 52MB 그대로였다.

처음에 궁금했던 것 중 하나가 이거였는데, 인덱스 엔트리도 DELETE 시점에 제거되지 않는다. 힙의 dead tuple을 가리키던 인덱스 엔트리는 VACUUM이 힙을 정리하면서 함께 걷어낸다. DELETE나 UPDATE가 잦은 테이블은 VACUUM이 밀리는 만큼 인덱스도 같이 부푼다.

이렇게 dead tuple이 회수되지 않으면 테이블과 인덱스가 실제 데이터보다 훨씬 커지는데, 이 상태를 **블로트(bloat)**라고 부른다. 위 결과가 딱 그 상태다. 유효한 데이터는 10만 행뿐인데 201MB를 차지하고 있다. 이게 왜 문제가 되는지는 뒤에서 따로 정리한다.

## VACUUM이 하는 일

VACUUM을 설명할 때 "공간을 재사용 가능하게 만든다"는 표현을 자주 보는데, 이게 무슨 뜻인지 잘 안 와닿았다. 재사용이 되는 쪽과 안 되는 쪽을 나란히 놓고 재보니 이해가 됐다.

먼저 90%를 지운 뒤 **VACUUM 없이** 50만 행을 새로 넣어봤다.

```
 step                             |  heap  |  idx  | total
----------------------------------+--------+-------+--------
 1. 초기 100만 행                 | 149 MB | 52 MB | 201 MB
 2. 90% DELETE 직후               | 149 MB | 52 MB | 201 MB
 3. 50만 행 INSERT (VACUUM 안 함) | 225 MB | 89 MB | 314 MB
```

90만 행 분량의 빈자리가 있는데도 파일 끝에 새 페이지를 붙여서 76MB를 더 썼다. 데이터베이스는 그 빈 공간이 있다는 걸 모른다.

같은 시나리오에서 INSERT 전에 `VACUUM t` 한 줄만 넣어봤다.

```
 step                     |  heap  |  idx  | total
--------------------------+--------+-------+--------
 1. 초기 100만 행         | 149 MB | 52 MB | 201 MB
 2. 90% DELETE 직후       | 149 MB | 52 MB | 201 MB
 3. VACUUM 직후           | 149 MB | 52 MB | 201 MB
 4. 50만 행 INSERT        | 149 MB | 87 MB | 237 MB
```

3번과 4번을 같이 봐야 의미가 보인다.

- 3번: VACUUM을 돌려도 파일은 안 줄어든다. VACUUM은 OS에 공간을 반납하지 않는다.
- 4번: 그런데 50만 행을 넣었는데도 힙이 149MB 그대로다. VACUUM을 안 했을 때는 225MB까지 커졌던 그 INSERT다.

VACUUM이 하는 일은 파일을 줄이는 게 아니다. 비어 있는 자리를 FSM(Free Space Map)에 등록해서 다음 INSERT가 그 자리를 찾아 쓸 수 있게 만든다. 파일 크기는 그대로여도 안쪽은 재활용된다. "용량이 안 줄어드는데 VACUUM이 무슨 소용인가" 싶었는데, 더 안 커지게 막아주는 것이 본래 역할이었다.

참고로 DELETE 직후에도 페이지 내부는 어느 정도 정리된다. 그 페이지를 읽는 스캔이 지나갈 때 opportunistic page pruning이 일어나 죽은 튜플의 몸통을 걷어내기 때문이다. 실제로 DELETE 직후 `pgstattuple('t')`을 보면 `free_percent`가 87%까지 올라가 있다. 그런데도 위에서 INSERT가 파일을 키운 건, pruning이 FSM을 갱신하지는 않기 때문이다. 공간은 비었는데 아무도 그 사실을 모르는 상태다. 그걸 장부에 적어주는 게 VACUUM이다.

### 인덱스는 어디까지 정리되나

위 표에서 인덱스는 52MB에서 87MB로 늘었다. 힙은 재사용이 됐는데 인덱스는 아니었다. 인덱스는 VACUUM이 아예 안 건드리는 걸까 싶어서 `pgstatindex`로 안을 들여다봤다.

```sql
SELECT index_size, leaf_pages, deleted_pages,
       round(avg_leaf_density::numeric, 2) AS density
FROM pgstatindex('idx_t_name');
```

```
 시점                          | index_size | leaf_pages | deleted_pages | density
-------------------------------+------------+------------+---------------+---------
 DELETE 전                     |   31563776 |       3832 |             0 |   90.02
 90% DELETE 직후 (VACUUM 안 함)|   31563776 |       3832 |             0 |   90.02
 VACUUM 후                     |   31563776 |       3832 |             0 |    9.36
```

리프 페이지의 밀도가 90%에서 9.36%로 떨어졌다. 지우고 남긴 비율이 딱 10%였으니 VACUUM이 죽은 엔트리를 실제로 걷어낸 셈이다. 그런데 `index_size`와 `leaf_pages`는 1바이트도 안 변했다. 엔트리는 비웠는데 껍데기는 그대로인 상태다.

여기서 두 가지를 구분해야 한다는 걸 알게 됐다.

- **회수**: 비워진 페이지를 free page list에 등록해서 다음에 인덱스가 다시 쓸 수 있게 만드는 것. 파일 크기는 그대로다
- **축소**: 파일 자체가 작아져서 OS에 공간이 반환되는 것. 인덱스를 처음부터 다시 만들어야 한다

힙에서 "VACUUM은 파일을 줄이는 게 아니라 재사용 가능하게 만든다"고 했던 것과 같은 구조다. 다만 인덱스는 회수 조건이 더 까다롭다. 페이지가 통째로 비어야 회수되는데, 위처럼 산발적으로 지우면 페이지마다 10%씩 살아남아 완전히 비는 페이지가 하나도 없다. `deleted_pages`가 0으로 나온 게 그래서다. 밀도만 9%로 떨어지고 그 공간은 재사용도 안 된다.

힙은 페이지에 빈자리만 있으면 새 행을 끼워 넣을 수 있는데, 인덱스는 키 순서가 정해져 있어서 아무 자리에나 못 넣는다. 인덱스 블로트가 힙보다 잘 안 풀리는 이유가 이것이었다.

인덱스는 따로 손을 봐야 한다.

```sql
DELETE FROM t WHERE id % 10 <> 0;
VACUUM t;
-- heap 149 MB, idx_t_name 30 MB

REINDEX INDEX CONCURRENTLY idx_t_name;
-- heap 149 MB, idx_t_name 3104 kB
```

VACUUM 후에도 30MB였던 인덱스가 REINDEX 후 3MB가 됐다. `REINDEX INDEX CONCURRENTLY`는 PostgreSQL 12부터 쓸 수 있고 배타 락을 잡지 않아 운영 중에도 쓸 수 있다. 단, 인덱스를 처음부터 다시 만드는 작업이라 그만큼 I/O를 쓴다. 작업 중에는 인덱스 크기만큼 디스크 여유도 필요하다.

## VACUUM FULL

파일을 실제로 줄이려면 `VACUUM FULL`이다.

```
 step               |  heap  |   idx   | total
--------------------+--------+---------+--------
 1. 90% DELETE 직후 | 149 MB | 52 MB   | 201 MB
 2. VACUUM 후       | 149 MB | 52 MB   | 201 MB
 3. VACUUM FULL 후  | 15 MB  | 5312 kB | 20 MB
```

201MB가 20MB가 됐다. 힙도 인덱스도 함께 줄었다.

이게 가능한 이유는 VACUUM FULL이 테이블을 통째로 새 파일에 다시 쓰기 때문이다. 살아 있는 튜플만 순서대로 새 파일에 옮겨 담고 인덱스도 전부 새로 만든다. 끝나면 옛 파일을 버린다. 결과물이 깨끗한 대신 대가가 있다.

### 락 차이

락을 관찰하려고 만든 `big` 테이블에 두 명령을 각각 돌려놓고 다른 세션에서 접근해봤다.

일반 VACUUM 실행 중에는 SELECT도 UPDATE도 그냥 통과한다.

```
           mode           | granted
--------------------------+---------
 ShareUpdateExclusiveLock | t
```

`ShareUpdateExclusiveLock`은 일반 DML을 막지 않는다.

VACUUM FULL 실행 중에는 이렇게 된다.

```
        mode         | granted |      query
---------------------+---------+-----------------
 AccessExclusiveLock | t       | VACUUM FULL big
```

```
ERROR:  canceling statement due to lock timeout
LINE 1: SET lock_timeout='2s'; SELECT count(*) FROM big;
```

`SELECT count(*)`조차 들어가지 못한다. `AccessExclusiveLock`은 그 테이블에 대한 모든 접근을 차단한다. 읽기도 안 된다.

10만 행 남은 테스트 테이블은 몇백 ms면 끝나지만, 수백 GB 테이블이면 그 시간 동안 해당 테이블을 쓰는 모든 요청이 멈춘다. 새 파일을 만드는 방식이라 작업 중에는 디스크 여유 공간이 테이블 크기만큼 더 필요하다. 용량이 부족해서 VACUUM FULL을 돌리려는 상황이라면 특히 조심해야 한다.

### 정리

|              | VACUUM                                                 | VACUUM FULL                                    |
| ------------ | ------------------------------------------------------ | ---------------------------------------------- |
| 동작 방식    | 페이지를 훑으며 죽은 튜플/인덱스 엔트리 제거, FSM 갱신 | 테이블 전체를 새 파일로 재작성 + 인덱스 재생성 |
| 파일 크기    | 보통 줄지 않음                                         | 줄어듦 (149MB → 15MB)                          |
| 공간 재사용  | 같은 테이블 안에서 재사용 가능                         | OS에 반환                                      |
| 인덱스       | 죽은 엔트리 제거·빈 페이지 회수는 하지만 파일은 그대로 | 처음부터 다시 만듦 (52MB → 5MB)                |
| 락           | ShareUpdateExclusive — DML과 병행 가능                 | AccessExclusive — 읽기조차 차단                |
| 추가 디스크  | 거의 불필요                                            | 테이블 크기만큼 더 필요                        |
| 운영 중 사용 | 가능 (보통 autovacuum이 알아서 함)                     | 사실상 불가                                    |

## 회수만 해도 속도가 개선될까

여기까지 정리하고 나니 다음 질문이 생겼다. 파일이 안 줄어드는 일반 VACUUM만으로도 조회가 빨라지는 걸까, 아니면 결국 VACUUM FULL을 해야 하는 걸까.

재보기 전에 실행 계획 읽는 법을 조금 짚고 가야 한다.

`BUFFERS` 옵션을 켜면 계획의 각 단계마다 `Buffers: shared hit=... read=...`가 붙는데, 이게 그 단계에서 읽은 8KB 블록 수다. `hit`은 버퍼 캐시에서 찾은 것, `read`는 캐시에 없어 가져온 것이다. 둘을 더하면 그 단계가 훑은 총 블록 수가 된다. 인덱스를 읽는 단계와 힙을 읽는 단계가 따로 찍히므로 나눠 셀 수 있다.

계획에 찍히는 스캔 방식도 몇 가지만 알아두면 된다.

| 계획               | 하는 일                                                                         |
| ------------------ | ------------------------------------------------------------------------------- |
| `Seq Scan`         | 힙 파일을 처음부터 끝까지 순서대로 다 읽는다. MySQL의 풀 테이블 스캔에 해당     |
| `Index Scan`       | 인덱스를 타고 해당 위치의 힙 튜플을 하나씩 읽는다                               |
| `Index Only Scan`  | 인덱스만 읽고 끝낸다. 힙을 안 봐도 되는 경우에만 선택된다                       |
| `Bitmap Heap Scan` | 인덱스로 읽을 힙 페이지 목록을 먼저 만든 뒤, 그 페이지들을 파일 순서대로 읽는다 |

MySQL을 쓰다 왔다면 `Seq Scan`이 낯설 수 있는데 풀 스캔과 같은 것이다. 다만 InnoDB는 테이블이 PK로 클러스터링되어 있어 풀 스캔이 곧 클러스터드 인덱스 리프를 순서대로 훑는 것인 반면, PostgreSQL의 힙은 정렬돼 있지 않아서(그래서 이름이 힙이다) 파일에 놓인 물리적 순서대로 읽는다.

산발적으로 90%를 지운 테이블에 같은 쿼리를 세 번 돌렸다.

```sql
SET max_parallel_workers_per_gather = 0;   -- 계획을 단순하게 고정
SET enable_seqscan = off;
EXPLAIN (ANALYZE, BUFFERS) SELECT count(*) FROM sparse;
```

| 상태       | 인덱스 블록 | 힙 블록 | 실행 시간 |
| ---------- | ----------- | ------- | --------- |
| VACUUM 전  | 2735        | 17242   | 92.8ms    |
| VACUUM 후  | **2736**    | 0       | 11.1ms    |
| REINDEX 후 | **276**     | 0       | 9.4ms     |

인덱스 스캔 비용만 보면 VACUUM은 개선이 0이다. 2735에서 2736으로 오히려 한 블록 늘었다. 죽은 엔트리를 90%나 걷어냈는데도 읽는 블록 수는 그대로인데, 앞에서 본 대로 빈 껍데기 페이지가 그대로 남아 있기 때문이다. 인덱스를 실제로 빠르게 만든 건 REINDEX였다.

### 힙 블록이 0이라는 건 무슨 뜻인가

이 쿼리는 테이블 파일을 한 번도 열지 않았다.

돌린 쿼리가 `SELECT count(*)`였다. 개수만 세면 되니 컬럼 값이 필요 없고 `id`는 PK라 인덱스 안에 이미 다 들어 있다. 그러면 인덱스만 읽고 답을 낼 수 있다. 문제는 인덱스 엔트리가 가리키는 행이 지금도 살아 있는지인데, 원래는 그걸 확인하러 힙에 가봐야 한다. VACUUM이 visibility map에 "이 페이지는 전부 유효하다"고 적어두면 그 확인을 건너뛸 수 있다. 계획에 `Heap Fetches: 0`이 찍히는 게 그래서다.

그러니까 저 0은 "테이블이 비었다"가 아니라 "테이블을 안 봐도 됐다"는 표시다.

반대로 VACUUM 전에는 왜 17242페이지를 전부 읽었을까. 그때 계획에는 이런 줄이 찍혀 있었다.

```
->  Bitmap Index Scan on sparse_pkey (actual rows=1000000)
```

visibility map을 못 믿으니 인덱스가 넘겨준 항목마다 힙에 가서 살아 있는지 확인해야 하는데, 그 항목이 죽은 것까지 포함해 100만 개였다. 결국 테이블 전체를 훑게 된다.

그럼 컬럼 값을 실제로 읽어야 하는 쿼리는 어떨까 싶어 `count(memo)`로 같이 재봤다.

| 쿼리          | VACUUM 전 힙 블록 | VACUUM 후 힙 블록 |
| ------------- | ----------------- | ----------------- |
| `count(*)`    | 17242             | **0**             |
| `count(memo)` | 17242             | **17242**         |

`memo` 값을 봐야 하니 힙을 읽을 수밖에 없다. 읽는 블록 수는 VACUUM 전후가 똑같다. 살아 있는 10만 행이 17242페이지에 흩어져 있으니 결국 전부 훑어야 한다.

그럼 시간도 똑같을까. 조건이 완전히 같은 테이블 두 개를 만들어 한쪽만 VACUUM하고, 각각 그 테이블의 첫 스캔부터 재봤다.

| `count(memo)` | 1차 스캔                       | 2차 스캔 |
| ------------- | ------------------------------ | -------- |
| VACUUM 안 함  | **95.8ms** (`dirtied=17242`)   | 18.1ms   |
| VACUUM 함     | **21.2ms** (`dirtied=0`)       | 17.8ms   |

1차 스캔은 네 배 넘게 차이 나는데 2차부터는 같아진다. 실행 계획의 `dirtied`가 이유를 알려준다.
VACUUM을 안 한 테이블은 **첫 스캔이 프루닝과 힌트 비트 기록까지 떠안아서** 17242페이지를 전부 더럽히며 지나간다.
VACUUM은 그 일을 미리 해두는 셈이고, 한 번 지나가고 나면 남는 이득은 없다.

읽는 블록이 같으니 I/O가 준 것도 아니다. 힙을 읽어야만 하는 쿼리에서 VACUUM이 주는 것은
**처음 한 번의 정리 비용을 대신 내주는 것**이지, 그 뒤로 계속 빨라지게 하는 게 아니다.

### 삭제 패턴에 따라 갈린다

그렇다고 "VACUUM은 인덱스 성능과 무관하다"고 잘라 말할 수는 없었다. 같은 VACUUM인데 결과가 갈리는 경우가 있다.

#### 인덱스에서 "회수"란

앞에서 회수라는 말을 힙과 인덱스에 모두 썼는데, 이 둘이 하는 일이 다르다는 걸 짚고 가야 한다.

힙 쪽 회수는 페이지 안에 빈자리를 만들고 그걸 장부(FSM)에 적는 일이다. 페이지 자체는 여전히 테이블에 속해 있으니 순차 스캔은 그 페이지를 그대로 다 읽는다. 앞에서 VACUUM 후에도 Seq Scan이 17242블록을 읽었던 게 이 때문이다.

인덱스 쪽 회수는 다르다. B-tree의 리프 페이지들은 옆 페이지를 가리키는 링크로 서로 이어져 있다. 범위 스캔은 이 사슬을 따라 훑는다. 그런데 어떤 리프 페이지가 통째로 비면 VACUUM이 그 페이지를 사슬에서 아예 떼어낸다. 그러면 이후의 스캔은 그 페이지를 지나가지 않는다.

말하자면 인덱스의 회수는 "빈자리 표시"가 아니라 "스캔 경로에서 제외"다. 이게 성능에 직접 영향을 준다.

|           | 힙에서의 회수                      | 인덱스에서의 회수                                     |
| --------- | ---------------------------------- | ----------------------------------------------------- |
| 조건      | 페이지에 죽은 튜플이 있으면 그만큼 | 페이지가 **통째로** 비어야                            |
| 하는 일   | 빈 공간을 FSM에 등록               | 리프 사슬에서 페이지를 떼어내고 free page list에 등록 |
| 스캔 비용 | 그대로 (페이지는 계속 읽힘)        | **줄어듦** (지나갈 페이지가 사라짐)                   |
| 파일 크기 | 그대로                             | 그대로                                                |

떼어낸 페이지는 파일 안에 그대로 남아 있다. 파일 크기는 안 줄고, 나중에 새 페이지가 필요할 때 그 자리를 재활용한다.

#### 그래서 삭제 패턴이 중요하다

문제는 페이지가 통째로 비어야 한다는 조건이다. 어디를 지웠느냐에 따라 이게 되기도 하고 안 되기도 한다.

```
산발 삭제 (id % 10 <> 0) — 페이지마다 10%씩 살아남음

  [■□□□□□□□□□] → [■□□□□□□□□□] → [■□□□□□□□□□] → ...   총 3832장
  한 장도 완전히 비지 않아 떼어낼 것이 없다. 사슬은 3832장 그대로.


연속 삭제 (id <= 900000) — 앞쪽 페이지들이 통째로 빔

  [□□□□□□□□□□] → ... → [□□□□□□□□□□] → [■■■■■■■■■■] → ...   총 2733장
  앞의 2467장이 완전히 비었다.

  VACUUM 후 →  [■■■■■■■■■■] → ...   남은 사슬 274장
```

조건이 완전히 같은(살아 있는 행 10만 개, 힙 135MB, 인덱스 21MB) 두 테이블을 삭제 패턴만 다르게 만들어 비교하면 이렇게 나온다.

| 상태                              | 인덱스 파일 | deleted_pages | 인덱스 블록 |
| --------------------------------- | ----------- | ------------- | ----------- |
| VACUUM 후 · 산발 삭제 (회수 0)    | 21MB        | 0             | 2736        |
| VACUUM 후 · 연속 삭제 (회수 2467) | 21MB        | 2467          | 277         |
| VACUUM FULL 후                    | 2.2MB       | —             | 275         |

`pgstatindex`의 `deleted_pages`가 바로 사슬에서 떼어낸 페이지 수다. 연속 삭제 쪽은 2467장이 빠지면서 리프 페이지가 2733개에서 274개가 됐다. 읽는 블록도 그만큼 줄었다.

그리고 2행과 3행을 보면 파일 크기가 10배 차이나는데도(21MB vs 2.2MB) 읽는 블록은 277 대 275로 사실상 같다. 회수만 제대로 되면 VACUUM FULL을 해도 더 얻을 게 없다.

VACUUM이 인덱스를 빠르게 해주느냐는 삭제 패턴에 달려 있는 셈이다. 페이지가 통째로 비는 형태로 지웠으면 VACUUM으로 충분하고, 산발적으로 지웠으면 REINDEX가 필요하다. 시계열 데이터를 오래된 것부터 지우는 경우가 전자에 가깝고, 상태값으로 여기저기 지우는 경우가 후자에 가깝다.

다만 인덱스를 안 타고 테이블 전체를 훑는 힙 순차 스캔(`Seq Scan`)은 또 얘기가 다르다.

|                | 힙 파일 | Seq Scan 블록 |
| -------------- | ------- | ------------- |
| VACUUM 후      | 135MB   | 17242         |
| VACUUM FULL 후 | 13MB    | 1725          |

10만 행만 남았는데 100만 행 시절의 페이지를 그대로 다 읽는다. 힙은 파일이 안 줄면 순차 스캔 비용도 줄지 않는다. VACUUM FULL이나 `pg_repack`(같은 결과를 내면서 긴 배타 락은 잡지 않는 확장)이 실제로 필요한 지점은 여기다.

정리하면 이렇게 나뉜다.

| 개선 항목                     | VACUUM              | VACUUM FULL     | REINDEX             |
| ----------------------------- | ------------------- | --------------- | ------------------- |
| 힙 접근 생략 (visibility map) | **O — 17242 → 0**   | X — 맵이 비워짐 | 영향 없음 (맵 유지) |
| 인덱스 블록 — 연속 삭제       | O — 2733 → 274      | 추가 이득 없음  | 추가 이득 없음      |
| 인덱스 블록 — 산발 삭제       | **X — 2735 → 2736** | **O — → 275**   | **O — → 276**       |
| 힙 순차 스캔                  | X — 17242 그대로    | **O — → 1725**  | X — 힙은 안 건드림  |

VACUUM FULL과 REINDEX를 한 칸에 묶으면 안 된다. 첫 줄이 그 이유다. VACUUM FULL은 힙을 새로 쓰므로
visibility map이 비워지지만, REINDEX는 인덱스만 다시 만들 뿐 힙을 건드리지 않아 맵이 그대로 남는다.
실제로 REINDEX 뒤에도 `all_visible` 17242/17242에 `Heap Fetches: 0`이 유지된다.

### VACUUM FULL 뒤에는 VACUUM을 한 번 더

VACUUM FULL은 테이블을 새 파일로 다시 쓰기 때문에 visibility map이 전부 비워진다. 파일 크기는 줄었는데도 index-only scan을 못 쓰게 되고 계획이 Bitmap Heap Scan으로 돌아간다. VACUUM을 한 번 더 돌려야 맵이 다시 채워지면서 제 성능이 나온다.

VACUUM FULL이나 `pg_repack`을 돌린 뒤에는 `VACUUM ANALYZE`까지 해주는 게 좋겠다.

## 일반 VACUUM도 파일이 줄어들 때가 있다

앞의 비교표에 "보통 줄지 않음"이라고 쓴 이유가 있다. VACUUM은 파일 끝쪽이 통째로 비었을 때는 그 부분을 잘라낸다. 어디를 지웠느냐에 따라 결과가 달라진다.

```sql
-- 앞쪽 90% 삭제 (앞이 비고 살아남은 행은 파일 끝에 남음)
DELETE FROM t WHERE id <= 900000;
VACUUM t;
-- 135 MB → 135 MB

-- 뒤쪽 90% 삭제 (파일 끝이 통째로 빔)
DELETE FROM t2 WHERE id > 100000;
VACUUM t2;
-- 135 MB → 13 MB
```

같은 명령에 같은 삭제량인데 하나는 그대로고 하나는 10분의 1이 됐다. VACUUM이 잘라낼 수 있는 건 **파일 끝**뿐이기 때문이다. 앞쪽을 지운 첫 번째는 빈 페이지가 아무리 많아도 살아남은 행이 파일 끝에 버티고 있어서 한 페이지도 못 자른다.

시계열 데이터처럼 오래된 것부터 지우는 패턴에서 "VACUUM만 했는데 용량이 줄더라"는 얘기가 나오는 것도 이 때문이다. 단, 이 절단 작업은 짧게 ACCESS EXCLUSIVE 락을 필요로 한다. 못 잡으면 그냥 건너뛴다.

## autovacuum

실무에서 VACUUM을 손으로 치는 일은 드물다. autovacuum이 알아서 돌기 때문이다. 문제는 언제 도느냐다.

```
dead tuple 수 > autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × 전체 행수
                        (기본 50)                         (기본 0.2 = 20%)
```

여기서 큰 테이블의 함정이 나온다. 1억 행 테이블은 dead tuple이 2천만 개 쌓여야 autovacuum이 시작된다. 그때까지 테이블은 계속 부푼다. 막상 시작되면 처리량이 많아 오래 걸린다. 큰 테이블에서는 테이블 단위로 기준을 낮춰 잡는다.

```sql
ALTER TABLE big_table SET (autovacuum_vacuum_scale_factor = 0.01);  -- 1%
ALTER TABLE big_table SET (autovacuum_vacuum_threshold = 1000);
```

autovacuum이 느리다면 워커 수보다 비용 제한이 원인인 경우가 많다.

```sql
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;   -- 기본 -1 (vacuum_cost_limit 인 200을 따라감)
ALTER SYSTEM SET autovacuum_naptime = '15s';            -- 기본 1min
ALTER SYSTEM SET autovacuum_max_workers = 5;            -- 기본 3
```

`autovacuum_vacuum_cost_limit`의 기본값이 `-1`인 게 헷갈리는데, 끄겠다는 뜻이 아니라
`vacuum_cost_limit`(기본 200)을 그대로 쓰겠다는 뜻이다. 그리고 이 한도는 워커 하나당이 아니라
**전체 워커가 나눠 쓴다.** 워커만 늘리면 각자 몫이 줄어들 뿐이라 총 처리량은 그대로다.

## autovacuum을 운영 환경에서 끄면 안 되는 이유

VACUUM에는 공간 회수 말고 임무가 하나 더 있다. 트랜잭션 ID는 32비트(약 42억)로 순환하는데, 아주 오래된 튜플의 XID를 영구히 과거로 표시(freeze)해두지 않으면 ID가 한 바퀴 돌았을 때 과거가 미래로 보이는 사고가 난다. 예전에 커밋된 데이터가 통째로 사라진 것처럼 보인다.

PostgreSQL은 이를 막기 위해 `autovacuum_freeze_max_age`(기본 2억)에 도달하면 autovacuum을 꺼둔 상태에서도 강제로 vacuum을 돌린다. 그래도 한계에 임박하면 쓰기를 전면 거부한다.

부하를 이유로 autovacuum을 꺼버리는 건 그래서 위험하다. 조절은 하되 끄지 않는다. 앞에서 실험 테이블에 `autovacuum_enabled = off`를 쓴 건 어디까지나 관찰을 위한 장치다.

## VACUUM이 일을 못 하는 경우

정리하면서 가장 인상적이었던 부분이다. VACUUM은 "살아 있는 가장 오래된 스냅샷보다 오래된" dead tuple만 지울 수 있다. 오래 열려 있는 트랜잭션 하나가 VACUUM을 무력화한다.

말로만 보면 잘 안 와닿아서 재현해봤다. 세션 A가 `REPEATABLE READ` 트랜잭션을 열어둔 채 대기한다.

```sql
-- 세션 A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM t;
SELECT pg_sleep(60);
```

그 사이 세션 B가 90%를 지우고 VACUUM을 돌린다.

```sql
-- 세션 B
DELETE FROM t WHERE id % 10 <> 0;
VACUUM (VERBOSE) t;
```

```
pages: 0 removed, 19126 remain, 19126 scanned (100.00% of total)
tuples: 0 removed, 1000000 remain, 900000 are dead but not yet removable
removable cutoff: 770, which was 1 XIDs old when operation ended
index scan not needed: 0 pages ... had 0 dead item identifiers removed
```

`900000 are dead but not yet removable`. 죽은 건 알지만 치우지는 못한다. VACUUM은 정상 종료했고 `last_vacuum`도 갱신됐지만 회수된 건 없다. "VACUUM은 돌고 있는데 왜 용량이 안 줄지?"의 답이 여기 있었다.

원인은 바로 찾을 수 있다.

```sql
SELECT pid, state, round(extract(epoch from now() - xact_start)) AS dur_sec, backend_xmin
FROM pg_stat_activity
WHERE xact_start IS NOT NULL AND pid <> pg_backend_pid()
ORDER BY xact_start;
```

```
 pid | state  | dur_sec | backend_xmin
-----+--------+---------+--------------
 544 | active |       4 |          770
```

`backend_xmin`이 위 VERBOSE 출력의 `removable cutoff: 770`과 같다. 이 세션이 회수 기준선을 붙들고 있다.

세션 A를 종료시키고 같은 VACUUM을 다시 돌렸다.

```
pages: 0 removed, 19126 remain, 19126 scanned (100.00% of total)
tuples: 900000 removed, 100000 remain, 0 are dead but not yet removable
index scan needed: 19126 pages from table (100.00% of total) had 900000 dead item identifiers removed
index "t_pkey": pages: 2745 in total, 0 newly deleted, 0 currently deleted, 0 reusable
```

명령도 데이터도 같은데 90만 개가 한 번에 정리됐다. 달라진 건 방해하던 트랜잭션이 사라진 것뿐이다. `index scan needed ... 900000 dead item identifiers removed` 줄을 보면 인덱스 엔트리도 이 시점에 함께 제거된다.

기준선을 붙잡는 건 열린 트랜잭션만이 아니다. 방치된 replication slot이나 버려진 prepared transaction도 같은 식으로 회수를 막는다. 각각 `pg_replication_slots`, `pg_prepared_xacts`에서 확인할 수 있다.

긴 배치 트랜잭션에 `REPEATABLE READ`를 걸면 스냅샷을 오래 유지하게 되므로 블로트를 직접 유발한다. 배치를 청크 단위로 나눠 자주 커밋하라는 얘기를 락 경합이나 롤백 비용 때문이라고만 생각했는데, VACUUM이 일할 틈을 준다는 이유도 있었다.

## 블로트가 왜 문제인가

앞에서 블로트를 "실제 데이터보다 훨씬 커진 상태"라고만 하고 넘어갔는데, 비용은 지금까지 잰 숫자 그대로다. 10만 행을 세는 데 17242블록을 읽어야 했고 VACUUM 전에는 죽은 인덱스 엔트리 100만 개를 훑고 있었다.

나머지도 같이 따라온다.

- 버퍼 캐시(`shared_buffers`)에 쓸모없는 페이지가 자리를 차지해 캐시 히트율이 떨어진다
- 통계가 실제와 어긋나면서 옵티마이저가 나쁜 실행 계획을 고른다
- autovacuum이 처리해야 할 양도 같이 늘어나서 정작 돌 때 더 오래 걸리고 부하도 커진다

index-only scan이 항상 되지는 않는 이유도 여기 있었다. VACUUM은 페이지가 전부 visible한지를 visibility map에 기록하고 index-only scan은 그 맵을 보고 힙 접근을 생략하는데, VACUUM이 밀리면 맵이 최신이 아니게 되어 결국 힙을 다시 읽는다.

## ANALYZE와의 차이

같이 언급되는데 하는 일이 다르다.

|         | VACUUM                                     | ANALYZE                              |
| ------- | ------------------------------------------ | ------------------------------------ |
| 목적    | 죽은 튜플 공간 회수                        | 옵티마이저용 통계 갱신               |
| 결과물  | FSM, visibility map, 인덱스 정리           | `pg_statistic` (행 수, 분포, 최빈값) |
| 안 하면 | 블로트, 최악의 경우 wraparound로 쓰기 중단 | 잘못된 실행 계획                     |

대량 INSERT나 대량 DELETE 직후처럼 데이터 분포가 크게 바뀌었을 때는 `VACUUM ANALYZE`로 둘 다 해주는 게 안전하다.

## 대량 DELETE 후에 할 일

1. `VACUUM ANALYZE table` — 공간 회수 + 통계 갱신
2. `pg_stat_user_tables`에서 `n_dead_tup`이 실제로 줄었는지 확인. 안 줄었다면 오래 열린 트랜잭션이나 방치된 replication slot을 의심
3. 인덱스 크기 확인. 커져 있으면 `REINDEX INDEX CONCURRENTLY`
4. 파일 크기 자체를 꼭 줄여야 한다면 `pg_repack`. `VACUUM FULL`은 멈춰도 되는 시간대에만. 돌린 뒤에는 visibility map이 비므로 `VACUUM ANALYZE`를 한 번 더
5. 반복적인 대량 삭제라면 파티셔닝을 검토. 파티션을 `DROP TABLE`로 통째로 떼면 dead tuple도 VACUUM도 블로트도 없다

## 마무리

- 데이터가 남는 건 힙만이 아니라 인덱스도 마찬가지다
- VACUUM은 파일을 줄이는 명령이 아니다. 더 커지지 않게 막아주는 명령에 가깝다
- VACUUM이 정상 종료했다고 회수가 된 건 아니다. `dead but not yet removable`이 나오면 다른 곳을 봐야 한다
- 인덱스도 VACUUM이 정리하긴 한다. 다만 회수와 축소는 다르고, 인덱스는 페이지가 통째로 비어야 회수되기 때문에 산발적으로 지운 경우엔 그마저도 안 된다. `REINDEX CONCURRENTLY`가 따로 필요하다
- 인덱스 스캔을 실제로 빠르게 하는 건 REINDEX다. 산발적으로 지운 인덱스는 VACUUM을 돌려도 읽는 블록이 2735에서 2736으로 그대로였다. VACUUM이 줄여준 건 인덱스가 아니라 힙 블록(17242 → 0)이었는데, 실행 계획의 총 버퍼 수만 보고 인덱스가 빨라진 걸로 착각했다
- 반대로 회수가 잘 된 경우엔 VACUUM만으로 충분하다. 파일 크기가 10배 차이나도 읽는 블록은 277 대 275였다. 파일 크기에 집착할 필요가 없었다
- VACUUM에는 freeze라는 두 번째 임무가 있고, 그래서 autovacuum은 조절 대상이지 제거 대상이 아니다
