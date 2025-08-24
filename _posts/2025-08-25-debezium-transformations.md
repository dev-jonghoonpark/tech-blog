---
layout: "post"
title: "Debezium 에서 이벤트 필터링 및 데이터 수정하기 (with SMT, Single Message Transformations)"
description:
  "Debezium에서 이벤트 필터링 및 데이터 수정을 위한 방법을 소개합니다. Single Message Transformations(SMT)를\
  \ 활용하여 소스와 싱크 커넥터에서 메시지를 변환할 수 있으며, `is_cdc_sync` 컬럼을 추가하여 CDC 동기화에 의해 발생한 변경 사항\
  을 필터링합니다. 이를 통해 사용자 업데이트와 CDC 동기화 업데이트를 구분하고, 커넥터 설정을 통해 Kafka 토픽에 필요한 데이터만 전송할\
  \ 수 있습니다. 이 글에서는 SMT를 사용한 필터링 및 데이터 수정 과정과 설정 방법을 상세히 설명합니다."
categories:
  - "개발"
tags:
  - "Debezium"
  - "Connector"
  - "Kafka"
  - "Kafka Connect"
  - "MySQL"
  - "SMT"
  - "Single Message Transformations"
  - "filter"
  - "unwrap"
  - "ReplaceField"
  - "InsertField"
  - "Cast"
date: "2025-08-24 12:00:00 +0900"
toc: true
image:
  path: "/assets/thumbnails/2025-08-25-debezium-transformations.jpg"
---

# Debezium 에서 이벤트 필터링 및 데이터 수정하기

최근 [Debezium 으로 DB 변경사항 캡처하기](https://jonghoonpark.com/2025/08/19/debezium-with-kafka-4) 글과
[Debezium Sink Connector로 DB 변경사항을 다른 DB에 자동으로 동기화하는 방법](https://jonghoonpark.com/2025/08/23/debezium-sink-connector) 글을 작성하였다.

여기서 조금 더 나아가서 이벤트를 필터링 하거나, 데이터를 수정할 수 있는 방법에 대해서 알아보겠다.

물론 Application에서 처리를 한다면 더 높은 자유도가 있을 것이다.
하지만, 이 글을 작성하면서 어플리케이션의 변경은 최소화 하자는 생각을 가지고 테스트를 진행하였기 때문에, Connector 자체적으로 처리하는 방법에 대해서 소개한다.

## SMT

SMT는 Single Message Transformations 의 약자이다.
SMT를 사용하여 소스 커넥터가 Kafka에 기록되기 전에나, 싱크 커넥터로 전송되기 전 메시지를 변환할 수 있다.

## 시나리오

다음과 같은 시나리오를 생각해본다.

> A DB는 한국, B DB는 미국에 있다고 해보자.
> A DB에서 customer 테이블에 대해 변경된 사항을 B DB으로 전송 하고, B DB에서 customer 테이블에 대해 변경된 사항을 A DB로 전송 해서 서로의 싱크를 맞춘다.

이 때, 테이블의 변경 사항이 유저에 의해 발생 된 것인지 된 것인지, 변경사항 싱크를 위해 발생된 것인지 알지 못한다면 계속 업데이트 되는 상황이 발생될 것이다.

이걸 어떻게 해결할 수 있을까?

## 해결방향

만약 데이터가 cdc sync 에 의해 변경된 것이라면, source connector 에서 무시하도록 하고
그런 것이 아니라면 sink connector 를 통해 데이터를 업데이트 한다.

이를 위해 테이블에 `is_cdc_sync` 라는 컬럼을 추가한다. `bit(1)` 로 설정하였다. 해당 컬럼이 `0` 이라면 사용자에 의한 업데이트라고 가정하고, `1` 이라면 cdc sync 에 의한 업데이트라고 가정한다.

## 시스템 구성 및 커넥터 설정

SMT를 사용하기 위해서는 connect에 `ENABLE_DEBEZIUM_SCRIPTING` 환경변수를 주입해줘야 한다.

```yaml
connect:
  image: quay.io/debezium/connect:3.2.1.Final
  container_name: kafka_connect
  ports:
    - "8083:8083"
  depends_on:
    - kafka-1
    - kafka-2
    - kafka-3
    - mysql
  environment:
    BOOTSTRAP_SERVERS: "kafka-1:29092,kafka-2:29093,kafka-3:29094"
    GROUP_ID: 1
    CONFIG_STORAGE_TOPIC: my_connect_configs
    OFFSET_STORAGE_TOPIC: my_connect_offsets
    STATUS_STORAGE_TOPIC: my_connect_statuses
    ADVERTISED_HOST_NAME: connect
    ENABLE_DEBEZIUM_SCRIPTING: true
  networks:
    - kafka-net
```

그리고 connect 를 bash로 접근하여 groovy 관련 jar를 추가해준다.
debezium-connector-mysql 와 debezium-connector-jdbc 에 아래와 같이 jar를 다운로드 하여 추가해주었다.

- groovy 외에도 다른 스크립트 언어도 지원하지만, 이 글에서는 groovy를 사용한다.

```bash
cd ~/connect/debezium-connector-mysql
curl -O https://repo1.maven.org/maven2/org/apache/groovy/groovy/4.0.28/groovy-4.0.28.jar
curl -O https://repo1.maven.org/maven2/org/apache/groovy/groovy-jsr223/4.0.28/groovy-jsr223-4.0.28.jar

cd ~/connect/debezium-connector-jdbc
curl -O https://repo1.maven.org/maven2/org/apache/groovy/groovy/4.0.28/groovy-4.0.28.jar
curl -O https://repo1.maven.org/maven2/org/apache/groovy/groovy-jsr223/4.0.28/groovy-jsr223-4.0.28.jar
```

## 필터링 (Source Connector)

> [Note] **시스템 구성 및 커넥터 설정** 을 마치고 이 섹션을 참고한다.

참고: [Debezium - Message Filtering](https://debezium.io/documentation/reference/stable/transformations/filtering.html)

아래와 같이 커넥터를 업데이트 한다.

```bash
curl -i -X PUT -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/mysql-inventory-connector -d '{
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "root",
    "database.password": "debeziumrootpassword",
    "database.server.id": "184054",
    "topic.prefix": "dbserver1",
    "database.server.name": "mysql-server-1",
    "database.include.list": "mydb",
    "table.include.list": "mydb.customers",
    "schema.history.internal.kafka.bootstrap.servers": "kafka-1:29092,kafka-2:29093,kafka-3:29094",
    "schema.history.internal.kafka.topic": "dbhistory.inventory",
    "include.schema.changes": true,
    "transforms": "filter",
    "transforms.filter.language": "jsr223.groovy",
    "transforms.filter.type": "io.debezium.transforms.Filter",
    "transforms.filter.condition": "value.after.is_cdc_sync == 0"
  }'
```

아래 4줄이 핵심 파트이다.

```json
"transforms": "filter",
"transforms.filter.language": "jsr223.groovy",
"transforms.filter.type": "io.debezium.transforms.Filter",
"transforms.filter.condition": "value.after.is_cdc_sync == 0"
```

이렇게 커넥터 설정이 업데이트가 되었다면 `value.after.is_cdc_sync == 0` 일 때만 kafka topic에 produce 를 한다.

## 데이터 수정 (Sink Connector)

> [Note] **시스템 구성 및 커넥터 설정** 을 마치고 이 섹션을 참고한다.

아래와 같이 커넥터를 업데이트 한다.

```bash
curl -i -X PUT -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/my-debezium-sink-connector/config -d '{
    "connector.class": "io.debezium.connector.jdbc.JdbcSinkConnector",
    "tasks.max": "1",
    "connection.url": "jdbc:mysql://mysql2:3306/mydb?useSSL=false&allowPublicKeyRetrieval=true",
    "connection.username": "mysqluser",
    "connection.password": "mysqlpw",
    "insert.mode": "upsert",
    "delete.enabled": "true",
    "primary.key.mode": "record_key",
    "schema.evolution": "basic",
    "use.time.zone": "UTC",
    "topics": "dbserver1.mydb.customers",
    "table.name.format": "customers",
    "transforms": "unwrap,removeField,insertField,cast",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.drop.tombstones": "true",
    "transforms.unwrap.delete.handling.mode": "none",
    "transforms.removeField.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
    "transforms.removeField.exclude": "is_cdc_sync",
    "transforms.insertField.type": "org.apache.kafka.connect.transforms.InsertField$Value",
    "transforms.insertField.static.field": "is_cdc_sync",
    "transforms.insertField.static.value": 1,
    "transforms.cast.type": "org.apache.kafka.connect.transforms.Cast$Value",
    "transforms.cast.spec": "is_cdc_sync:int8"
  }'
```

아래 transforms 부분이 핵심 파트이다.

```json
"transforms": "unwrap,removeField,insertField,cast",
"transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
"transforms.unwrap.drop.tombstones": "true",
"transforms.unwrap.delete.handling.mode": "none",
"transforms.removeField.type": "org.apache.kafka.connect.transforms.ReplaceField$Value",
"transforms.removeField.exclude": "is_cdc_sync",
"transforms.insertField.type": "org.apache.kafka.connect.transforms.InsertField$Value",
"transforms.insertField.static.field": "is_cdc_sync",
"transforms.insertField.static.value": 1,
"transforms.cast.type": "org.apache.kafka.connect.transforms.Cast$Value",
"transforms.cast.spec": "is_cdc_sync:int8"
```

unwrap 과정을 통해 레코드를 추출하고, `is_cdc_sync` 를 강제로 `1`로 덮어씌운다. (삭제 후 재추가 과정을 통해)
kafka connector 설정에서는 1으로 넣어도 문자열로 변환되기 때문에, Cast를 해줘야 한다는 부분도 주의할 포인트이다.

이를 통해 cdc sync 로 발생된 데이터 변경건 일 경우 `is_cdc_sync`이 `1`로 기록되도록 한다.
이제 이 변경 사항이 cdc 과정중 캡처되겠지만, 이후 필터링에 걸려 topic에 produce 되지는 않게 되었다.

데이터를 확인해보면 실제로 값이 1 인 상태로 동기화 되고 있는 것을 볼 수 있다.

## 단점

Application에서 사용자가 업데이트 할 경우에는 `is_cdc_sync` 컬럼을 0 으로 업데이트 해줘야 한다.
만약 사용자가 업데이트 했음에도 is_cdc_sync 컬럼의 값이 1인 상태라면 Source Connector 의 필터링을 통과하지 못할 것이다.

이런식으로 Application 에서 신경쓰는게 번거롭다면 trigger를 사용해보는것도 하나의 방법이 될 것이다.

## 마무리

Debezium 에서 SMT를 사용한 이벤트 필터링 및 데이터 수정 방법에 대해서 알아보았다.

해당 부분들을 어플리케이션에서 직접 제어하는 할 수도 있겠지만, 커넥터 레벨에서 처리할 수 있다는 포인트도 상황에 따라 유용하게 쓸 수 있을 것 같다.
