---
layout: "post"
title: "[SQL] 조인과 서브쿼리 어느 것을 사용해야할까?"
description: "조인과 서브쿼리의 사용에 대한 최적의 선택을 다루는 본 포스트에서는 학생과 성적 테이블을 예로 들어, 성능 개선을 위한 쿼\
  리 작성 방법을 설명합니다. 학생 정보를 조회할 때, 서브쿼리를 활용하여 필터링만 필요한 경우 성능을 높일 수 있음을 보여주며, 복합 projection이\
  \ 필요한 상황에서는 조인을 사용하는 것이 바람직하다는 점을 강조합니다."
categories:
- "스터디-데이터베이스"
tags:
- "DATABASE"
- "SQL"
- "Join"
- "Join Performance"
- "Performance"
- "Subquery"
- "JPA (ORM) 개발자를 위한 고성능 SQL"
date: "2025-05-09 00:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-05-09-join-and-subquery.jpg"
---

# 조인과 서브쿼리

어느 때 조인을 쓰는것이 좋고 어느 때 서브쿼리를 쓰는게 좋을까?

## 문제 상황

다음과 같은 상황이 있다고 하자.

<pre class="mermaid">
erDiagram
    STUDENT {
        bigint id PK
        double admission_score
        varchar first_name
        varchar last_name
    }
    STUDENT_GRADE {
        bigint id PK
        varchar class_name
        double grade
        bigint student_id FK
    }
    STUDENT ||--o{ STUDENT_GRADE: "student_id:id"
</pre>

- 학생(student) 테이블과 성적(student_grade) 테이블이 있음.
- 목표: grade 값이 10인 student_grade 레코드가 연결된 student만 조회하고 싶음.

일단 student 는 성적에 대한 내용을 알지 못하기 때문에, student_grade 테이블을 활용해야한다는 것은 알았을 것이다.
그리고 단순히 목표를 그대로 해석한다면 다음과 같이 쿼리문을 작성할수도 있다.

```sql
SELECT DISTINCT
    s.id
    s.first_name,
    s.last_name,
FROM student s
INNER JOIN student_grade sg ON sg.student_id = s.id
WHERE sg.grade = 10
ORDER BY s.id
```

이 쿼리는 원하는 결과를 얻어낼 수 있다. 하지만 성능 측면에서 개선할 여지가 있는 쿼리이다.
실행 계획을 수행해보면 이 쿼리는 모든 학생 데이터를 스캔하게 만든다.

## 개선

그러면 어떻게 개선해야할까?

요구사항을 다시보면 **student만 조회** 라고 되어있다. 이에 따라 학생 정보만 projection 하면되고, 그렇게 하였다.
student_grade 는 projection이 필요하지 않다. student_grade는 필터링 용도로만 사용된다.

이럴 경우 subquery를 사용하는 것이 성능적으로 더 유리할 수 있다.
다음과 같이 쿼리를 수정해보자.

```sql
SELECT DISTINCT
    s.id
    s.first_name,
    s.last_name,
FROM student s
WHERE EXISTS (
    SELECT 1
    FROM student_grade sg
    WHERE sg.student_id = s.id AND sg.grade = 10
)
ORDER BY s.id
```

쿼리는 복잡해진 것으로 보인다.
`where` 문은 `correlated subquery` 이다. (각 row가 조건을 비교)
하지만 수정된 쿼리는 `sg.grade = 10` 인 레코드만 확인하면 되어, 더 적은 record를 거치게 될 수 있다.

### 정리

JOIN 은 복합 projection을 제공하지만, Subquery는 그렇지 않다. 복합 projection이 필요하다면 당연히 JOIN 을 써야 한다.
하지만 필터링만 필요한 경우에는 Subquery가 더 효율적일 가능성이 높다.
