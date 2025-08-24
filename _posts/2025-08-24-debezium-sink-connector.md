---
layout: "post"
title: "Debezium Sink Connector로 DB 변경사항을 다른 DB에 자동으로 동기화하는 방법"
description:
  "Debezium Sink Connector를 사용하여 DB 변경사항을 다른 DB에 자동으로 동기화하는 방법을 설명합니다.\
  \ 이 글에서는 Sink Connector의 개념과 설정 방법을 다루며, Kafka Connector API를 이용한 JdbcSinkConnector\
  \ 설정 예시를 제공합니다. 이를 통해 애플리케이션에서 직접 이벤트를 소비하지 않고도 데이터 복제 파이프라인을 쉽게 구성할 수 있습니다."
categories:
  - "개발"
tags:
  - "Debezium"
  - "Connector"
  - "Kafka"
  - "Kafka Connect"
  - "Sink"
  - "Sink Connector"
  - "MySQL"
  - "sync"
  - "database sync"
date: "2025-08-22 15:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-08-24-debezium-sink-connector.jpg"
---

# Debezium Sink Connector로 DB 변경사항을 다른 DB에 자동으로 동기화하는 방법

최근 [Debezium 으로 DB 변경사항 캡처하기](https://jonghoonpark.com/2025/08/19/debezium-with-kafka-4) 라는 글을 작성했었다.
해당 글에서는 변경사항을 캡쳐 한 후, 어플리케이션 에서 직접 컨슘하여 활용하는 방법에 대해서 소개했었다.
이번 글에서는 Sink Connector 를 사용하여 캡처된 변경사항을 다른 DB에 동기화 하는 방법에 대해 설명한다.

## Sink Connector

여기서 Sink는 싱크대 할 때의 싱크이다.

싱크대에서 물이 흘러 하수구로 모이는 것처럼, Sink Connector 는 이벤트를 컨슘하여 데이터를 외부 시스템으로 전달해주는 역할을 한다.

참고로 데이터를 produce 하는 커넥터는 Source Sonnector 라고 한다.

Source Connector가 DB 변경사항을 Kafka 토픽으로 보내면, Sink Connector는 해당 토픽에서 데이터를 읽어 다른 DB로 동기화한다.

## 시스템 구성 (compose)

[지난 글에서 작성한 compose.yml](https://jonghoonpark.com/2025/08/19/debezium-with-kafka-4#%EC%8B%9C%EC%8A%A4%ED%85%9C-%EA%B5%AC%EC%84%B1-compose) 에서 데이터 복제를 위한 2번째 mysql 설정만 추가해준다.

```yaml
mysql2:
  image: mysql:8.0.32
  container_name: mysql_db2
  ports:
    - "3307:3306"
  environment:
    - MYSQL_ROOT_PASSWORD=debeziumrootpassword
    - MYSQL_USER=mysqluser
    - MYSQL_PASSWORD=mysqlpw
    - MYSQL_DATABASE=mydb
  volumes:
    - poc_debezium_mysql_data2:/var/lib/mysql
  networks:
    - kafka-net
```

volumes 에 poc_debezium_mysql_data2 도 놓치지 말고 추가해준다.

## Connector 설정

Sink Connector도 Source Connector와 동일하게 Kafka Connector API를 사용한다.

JdbcSinkConnector를 커넥터 클래스도 사용한다.

```bash
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{
  "name": "my-debezium-sink-connector",
  "config": {
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
    "table.name.format": "customers"
  }
}'
```

table.name.format 을 지정해주지 않으면, 토픽 이름을 기반으로 테이블이 요구된다.
(ex. `dbserver1_mydb_customers`)

정상적으로 connector 가 설정되었다면, 데이터가 복제되는 것을 볼 수 있다.

## 마무리

Debezium Sink Connector를 활용하여 DB 변경사항을 다른 DB에 자동으로 동기화하는 방법을 알아보았다.

애플리케이션에서 직접 이벤트를 컨슘하지 않고도, Kafka Connect의 Sink Connector를 통해 데이터 복제 파이프라인을 손쉽게 구성할 수 있는 것을 확인해볼 수 있었다.

다음 글에서는 **Single Message Transform(SMT)**을 활용해, 이벤트를 필터링 하거나 가공처리 하는 방법에 대해 작성해보도록 하겠다.
