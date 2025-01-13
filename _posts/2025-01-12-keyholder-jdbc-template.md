---
layout: post
title: "[Spring] jdbctemplate - keyholder 동작 분석"
categories: [스터디-자바]
tags:
  [
    Java,
    Spring,
    JDBC,
    Spring JDBC,
    Data,
    Database,
    Mysql,
    H2,
    PreparedStatement,
    Keyholder,
  ]
date: 2024-01-12 23:59:59 +0900
toc: true
---

# keyholder 동작 분석 해보기

## 개요

최근에 스터디에서 Spring JDBC 와 관련된 내용을 진행하였고 ([정리글](/2025/01/11/spring-in-action-working-with-data))
그 과정에서 keyholder를 통해 생성된 키(generated key)를 받아오는 방법에 대해서 설명을 하였다.

이 때 한 스터디 회원분께서 jdbc template 객체가 db model 에 대해서 따로 알고있지 않은데 어떻게 key 값을 얻어올 수 있는지에 대해서 질문을 주셨고
알아보고 말씀드리기로 하여서 이 글을 작성하게 되었다.

## JDBC와 JDBC Driver와 Spring JDBC

먼저 JDBC와 JDBC Driver와 Spring JDBC 를 설명하고 넘어가는것이 좋을 것 같다.

- JDBC(Java DataBase Connectivity)는 클라이언트가 데이터베이스에 액세스하는 방법을 정의하는 Java API 입니다.
- JDBC 드라이버는 JDBC API를 기반으로 구현된 소프트웨어이다. 애플리케이션이 개별 데이터베이스와 상호 작용할 수 있도록 돕는다.
- Spring JDBC는 Spring Data의 일부로 JDBC 기반의 레포지토리를 쉽게 구현할 수 있도록 돕는다.

우리가 궁금해 하고 있는 KeyHolder의 경우 Spring JDBC의 클래스이다.

KeyHolder는 JDBC에서 자동 생성된 키 값을 반환받기 위한 클래스이다.

다음과 같은 방식으로 사용할 수 있다.

```java
GeneratedKeyHolder keyHolder = new GeneratedKeyHolder();
jdbcOperations.update(psc, keyHolder);
long orderId = keyHolder.getKey().longValue();
order.setId(orderId);
```

여기서 사용되는 update 문은 다음과 같이 구현되어 있다.

먼저 `PreparedStatement`에서 SQL문을 수행한다. (executeUpdate) 그 과정에서 서버에서 받은 값을 보관해 둔다.

![jdbc-template-update-method](/assets/images/2025-01-12-keyholder-jdbc-template/jdbc-template-update-method.png)

이후 `storeGeneratedKeys` 메소드에서 keyholder 에 값 업데이트 한다.

![jdbc-template-store-generated-keys-method](/assets/images/2025-01-12-keyholder-jdbc-template/jdbc-template-store-generated-keys-method.png)

여기서 PreparedStatement 는 java.sql package 의 인터페이스이다. 구현 상세는 각 DB의 구현에 맡긴다.

MySQL 과 H2 DB 를 리서치 해보았다.

## MySQL

[mysql jdbc](https://github.com/mysql/mysql-connector-j)

MySQL JDBC 에서 `StatementImpl.java` 파일을 보면 `getGeneratedKeys` 메소드를 볼 수 있다.

이 메소드에는 아래와 같은 메소드가 있다.

```java
this.generatedKeysResults = this.resultSetFactory.createFromResultsetRows(ResultSet.CONCUR_READ_ONLY, ResultSet.TYPE_SCROLL_INSENSITIVE,
                    new ResultsetRowsStatic(this.batchedGeneratedKeys, new DefaultColumnDefinition(fields)));
```

`createFromResultsetRows` 메소드는 `ResultSetImpl` 타입을 반환하는데 `ResultSetImpl` 은 `NativeResultset` 을 상속한다.

`NativeResultset` 클래스를 살펴보면 `OkPacket` 이라는 재밌는 프로토콜을 다루고 있다는 것을 볼 수 있다.

![mysql-jdbc-native-result-set](/assets/images/2025-01-12-keyholder-jdbc-template/mysql-jdbc-native-result-set.png)

OKPacket은 은 명령이 성공적으로 완료되었다는 것을 server 에서 client 로 알려줄 떄 사용하는 프로토콜이다.

![mysql-ok-packet](/assets/images/2025-01-12-keyholder-jdbc-template/mysql-ok-packet.png)

다양한 정보를 제공하는데 그 가운데 `last_insert_id` 가 있는것을 볼 수 있다. 이를 통해 2번 쿼리하지 않고 한 번의 쿼리로 last_insert_id 를 받아올 수 있다.

참고 : [MySQL doc - OkPacket](https://dev.mysql.com/doc/dev/mysql-server/9.0.1/page_protocol_basic_ok_packet.html)

## H2

[h2 database](https://github.com/h2database/h2database)

h2의 경우에는 JdbcPreparedStatement 클래스에서 executeUpdateInternal 메소드를 보면 된다.

![h2-jdbc-update](/assets/images/2025-01-12-keyholder-jdbc-template/h2-jdbc-update.png)

여기서 `command.executeUpdate` 는 CommandContainer 클래스의 `executeUpdateWithGeneratedKeys` 메소드로 연결되고, 최종적으로 `new ResultWithGeneratedKeys.WithKeys(statement.update(new GeneratedKeysCollector(indexes, result), ResultOption.FINAL), result);` 를 반환한다.

`statement.update` 는 실제적으로 `org.h2.command.dml` 패키지의 `Insert` 클래스의 update를 트리거하며 여기서 insert 를 진행한 후 GeneratedKeysCollector 의 값을 업데이트 시킨다.

마찬가지로 별도의 select 쿼리 없이 insert 시에 generated key 값을 받아올 수 있도록 구조를 만들어 두었다.

## 주의사항

위에서 확인해본 바와 같이 KeyHolder의 동작은 jdbc 내부 구현에 따른다. 따라서 지원하지 않는 경우도 있다.

실제로 예를 들어보면 오라클 데이터베이스는 KeyHolder를 지원하지 않는다고 한다.

이로 인해 generated key 값을 어플리케이션에서 접근하려면 쿼리를 다음과 같이 2개로 분할하여 처리해야 한다고 한다.

- SELECT로 SEQUENCE 를 반환받으면서 시퀀스를 증가
- 반환 받은 키로 INSERT

참고글 : [(Spring JDBC) JdbcOperations](https://umbum.dev/894/)
