---
layout: "post"
title: "[SQL] JOIN 알고리즘"
description: "관계형 데이터베이스에서 JOIN 알고리즘은 여러 테이블의 데이터를 연결하여 원하는 결과를 얻기 위해 사용되며, 효율적인 실\
  행 계획을 위해 데이터 통계 정보를 활용한다. 주요 JOIN 알고리즘으로는 중첩 루프 JOIN, 해시 JOIN, 머지 JOIN이 있으며, 각각의\
  \ 알고리즘은 데이터 양과 구조에 따라 성능 차이가 있다. 효율적인 JOIN을 위해서는 실행 계획을 이해하고 쿼리 구조를 최적화하는 것이 중요하\
  다."
categories:
- "스터디-데이터베이스"
tags:
- "DATABASE"
- "SQL"
- "Join"
- "Join Performance"
- "Performance"
- "Nested Loop Join"
- "Hash Join"
- "Merge Join"
- "JPA (ORM) 개발자를 위한 고성능 SQL"
date: "2025-05-09 00:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-05-09-join-algorithms.jpg"
---

# JOIN 알고리즘

관계형 데이터베이스에서는 여러 테이블의 데이터를 연결하여 원하는 결과를 얻기 위해 JOIN을 자주 사용하게 된다.
데이터베이스에서 JOIN을 효율적으로 수행하기 위해 다양한 알고리즘이 사용된다.
데이터베이스는 효율적인 실행 계획을 짜기 위해 테이블의 데이터량, 분포 등 통계 정보를 이용하며, 상황에 따라 nested loop, hash join, merge join 등 최적 알고리즘을 선택한다.
데이터베이스 옵티마이저는 항상 최소 자원 소비를 목표로 하며, 이를 비용 기반 옵티마이저(cost-based optimizer)라고 한다.

일반적으로 사용되는 주요 JOIN 알고리즘은 다음과 같다.

## Nested Loop Join

중첩 반복문을 생각하면 된다.
한 컬렉션을 반복하면서 다른 컬렉션을 반복하여 조인 조건에 따라 일치하는 레코드를 찾아 projection을 생성한다.
데이터가 적을 때는 효율적으로 동작하지만, 수백만 건의 데이터로 확장되면 성능 저하가 심하다. (`O(n*m)` 복잡도)

## Hash Join

대용량 데이터셋에서 효율적인 알고리즘이다.
해시 맵이나 해시 테이블을 만든다. 내부적으로 버킷이 있고, 각 버킷은 레코드들의 해시 값으로 식별된다.
중첩 루프(nested loops) 대신 훨씬 적은 비교로 일치하는 데이터를 찾을 수 있다. Hash Join은 선형(Linear) 복잡도에 가깝다. (`O(n + m)` 복잡도)
메모리를 많이 사용할 수 있다.

## Merge Join

Merge Join은 정렬된 상태에서 사용할 수 있는 알고리즘이다.

두 테이블을 조인 조건에 따라 처음부터 끝까지 한 번씩만 순회하며, 같은 방향으로 스캔한다.
좌측과 우측 레코드를 하나씩 비교하면서 일치하는 경우만 결과에 추가한다. 이터레이터 기반으로 진행되며, 여러 번 반복하지 않아도 된다는 점이 특징이다.
결과물 역시 정렬된 상태이다.

로그 복잡도(`O(n*log(n) + m*log(m))`)를 가진다.

## 예시

**문제 상황**: 댓글이 가장 많은 상위 게시글 3개와 그 댓글을 가져오기

**초기 솔루션**

```sql
SELECT
  p.title AS post_title,
  COUNT(pc.*) AS comment_count
FROM post p
JOIN post_comment pc ON p.id = pc.post_id
GROUP BY p.title
ORDER BY comment_count DESC
```

**개선 솔루션**

쿼리는 더 복잡해졌지만. 속도는 훨씬 줄어든다.

```sql
SELECT
  p.title AS post_title,
  pc.comment_count AS comment_count
FROM post p
JOIN (
  SELECT
    post_id,
    COUNT(*) as comment_count
  FROM post_comment
  GROUP BY post_id
  ORDER BY comment_count DESC
  LIMIT 3
) pc ON p.id = pc.post_id
ORDER BY comment_count DESC
```

조인을 하기 전에 집계를 선행하면, 조인의 대상이 되는 레코드 수가 매우 줄어들어 훨씬 빠른 실행이 가능해진다.

## 정리

효율적인 JOIN을 위해서는 실행 계획을 이해하고 이를 활용할 줄 알아야 하겠고 그에 따라 쿼리 구조를 최적화하는 것이 중요하겠다.
