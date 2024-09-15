---
layout: post
title: "[MySQL] Optimistic Lock 과 Pessimistic Lock 이해하기 (컨셉)"
categories: [스터디-데이터베이스]
tags: [MySQL, real mysql, lock, transaction, jpa, optimistic, pessimistic]
date: 2024-09-13 19:30:00 +0900
toc: true
---

지난 K-DEVCON 스터디에서 **Real Mysql - 5장 락과 트랜잭션** 파트를 다루고 나서 추가적으로 더 알아보고 정리해보면 좋겠다 싶어서 인프런 영상도 살펴보았다. 살펴보면서 알게된 것도 있어서 스터디에서 발표한 내용을 정리한 문서에도 업데이트 하였는데 추가적으로 Optimistic Lock 과 Pessimistic Lock 에 대한 이야기도 정리해보면 좋을 것 같아서 기록을 남긴다.

항상 이해한 것 같으면서도 다시 들으면 정확하게 기억하지 못하는것 같아 이번에 확실하게 정리를 해보기로 하였다.

- [[MySQL] 잠금 과 트랜잭션 (Lock and Transacdtion) - Real MySQL 스터디 2회차](/2024/09/07/mysql-lock-and-transaction)

## Optimistic Lock 과 Pessimistic Lock 설명

업데이트를 할 때 여러 트랜잭션이 동시에 진행이 되면 동시성 이슈가 발생될 수 있다. 예를 들어, 데이터가 0 미만으로 떨어지면 안 되는 상황에서, 잘못된 트랜잭션 처리로 값이 0 미만으로 떨어지는 일이 발생할 수 있다. 이러한 상황을 방지하기 위해 Optimistic Lock 과 Pessimistic Lock 을 사용할 수 있다.

### Optimistic Lock

- 트랜잭션이 충돌할 가능성이 낮다고 가정한다.
- 추가적인 데이터(버전, 타임스탬프 등)를 사용하여 다른 사람이 동일한 조건으로 값을 수정할 수 없도록 합니다.
- 수정 시점에 충돌이 발생했는지 확인합니다.

### Pessimistic Lock

- 트랜잭션이 충돌할 가능성이 높다고 가정한다.
- 락을 사용하여 다른 사람이 데이터를 수정할 수 없도록 합니다.

### MySQL은 기본적으로 Optimistic Lock 을 사용하는가 Pessimistic Lock 을 사용하는가

강의 중간에 나온 질문이다. 개발자들이 자주 묻는 질문이라고 소개해주셨다.
그리고 이에 대한 답변을 아래와 같이 해주셨다.

> MySQL 에서 레코드를 변경할 때 Optimistic Lock은 존재하지 않는다.
> 레코드를 변경할 떄는 락을 걸지 않고 변경할 수 없다. 따라서 모든 insert, update, delete는 pessimistic lock으로 사용된다.

그리고 이어서 다음과 같이 설명 해주셨다 설명이다.

> JPA 에서 이야기 하는 Optimistic Lock, Pessimistic Lock 은 Mysql 의 기능이 아니다.
> 트랜잭션 내에서 어떤 SQL문을 수행하냐에 따라 트랜잭션이 Optimistic 이 될수도 있고, Pessimistic 이 될수도 있다.

정리하자면 Optimistic Lock은 DB에서 제공해주는 특징을 이용하는 것이 아닌 Application Level에서 잡아주는 Lock이다.

## JPA 에서의 Optimistic Lock, Pessimistic Lock 사용 이해하기

직접적인 코드 레벨이라기 보다는 어떻게 동작하는지 컨셉을 설명해주셨다.

### 문제가 되는 케이스 예시 (Lost Update Anomaly)

![lost_update_anomaly](/assets/images/2024-09-13-mysql-jpa-optimistic-lock-and-pessimistic-lock/lost_update_anomaly.png)

동시에 업데이트가 진행되면서, 요구사항인 `balance 는 0보다 커야한다.`라는 조건이 깨져버렸다.

사용자 A 입장에서 balance 는 200 이지만 사용자 B가 도중에 업데이트를 진행하였기 때문에 실제 레코드는 50인 상태이다.
조건 체크는 application 에서 진행하고 있기 때문에 사용자 A 는 record가 변경된 것을 알지 못하고 업데이트를 진행한다.
따라서 최종적으로 값은 `-100` 이 되어 요구사항을 지키지 못하게 된다.

이러한 현상을 아래의 두가지 방법으로 해결해본다.

### Optimistic Lock 으로 해결하기

MySQL에서 제공하는 Lock이 아님에 주의하자.

레코드에 버전을 추가하여 해결한다. select 해온 version 을 이용하여 update시에 조건을 추가한다.

![optimistic_lock](/assets/images/2024-09-13-mysql-jpa-optimistic-lock-and-pessimistic-lock/optimistic_lock.png)

사용자 B가 먼저 update를 진행하여 version 을 2로 올려뒀기 때문에 사용자 A는 업데이트할 레코드가 없다.
이렇게 업데이트 되지 못했을 경우 JPA 에서 ObjectOptimisticLockingFailureException 를 발생시킨다.
(MySQL은 affectedRow만 반환해준다.)

### Pessimistic Lock 으로 해결하기

어플리케이션에서 예외 처리를 해야하는 것을 줄이고 싶다면 Optimistic Lock 보다 Pessimistic Lock 을 선택하는게 도움이 될 수 있다.

Pessimistic Lock 은 MySQL의 Lock을 사용한다. Exclusive Lock을 사용해서 동시 변경을 제어한다.

![pessimistic_lock](/assets/images/2024-09-13-mysql-jpa-optimistic-lock-and-pessimistic-lock/pessimistic_lock.png)

사용자 B가 먼저 `SELECT ... FOR UPDATE` 를 통해 Exclusive Lock을 획득하였다. 사용자 A는 사용자 B가 락을 반환할 떄까지 락이 걸려있는 레코드에 접근할 수 없다. 사용자 B가 락을 반환하면 이후 사용자 A가 접근할 수 있다.

## 참고

- 인프런 [Real MySQL 시즌 1 - Part 1](https://www.inflearn.com/course/real-mysql-part-1)
- 사바라다 님의 [[database] 낙관적 락(Optimistic Lock)과 비관적 락(Pessimistic Lock)](https://sabarada.tistory.com/175)
