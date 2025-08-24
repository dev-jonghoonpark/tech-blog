---
layout: "post"
title: "Debezium 으로 DB 변경사항 캡처하기 (with Kafka 4)"
description:
  "Debezium은 Apache Kafka 위에서 동작하는 오픈 소스 분산 플랫폼으로, 데이터베이스의 변경 사항을 실시간으로\
  \ 캡처하여 Kafka 토픽으로 스트리밍합니다. 이 글에서는 Debezium을 사용하여 MySQL 데이터베이스의 변경 이벤트를 Kafka를 통해\
  \ 수신하고 처리하는 방법을 설명합니다. Kafka 4.0 버전으로 KRaft 알고리즘을 사용하여 Zookeeper 없이 설정하는 방법에 대해서 설명합니다.\
  \ 예제를 통해 데이터 변경 시 발생하는 이벤트를 수신하고, 이를 기반으로 다양한 활용방안을 모색할 수 있습니다."
categories:
  - "개발"
tags:
  - "Debezium"
  - "Connector"
  - "Kafka"
  - "Connect"
  - "Kafka Connect"
  - "Zookeeper"
  - "KRaft"
  - "DB"
  - "MySQL"
  - "PODMAN"
  - "DOCKER"
date: "2025-08-19 13:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-08-19-debezium-with-kafka-4.jpg"
---

# Debezium 으로 DB 변경사항 캡처하기 (with Kafka 4)

DB의 변경사항을 모니터링 하여, 변경이 발생되었을 때 다른 DB에도 업데이트를 해줘야 하는 요구사항이 있으면 어떤 방법을 사용할 수 있을까?

Application 단에서 변경이 발생될 때, 명시적으로 변경사항에 대해 처리하는 것도 방법 중 하나이다. 하지만, 사람은 항상 실수를 한다. 처리를 누락하게 되는 경우도 발생할 수 있을 것이다.

따라서, DB 가 변경 되었을 때 해당 변경을 캐치하여 전파를 할 수 있다면 좋을 것이다.

그럴 때 고려해볼 수 있는 솔루션 중 하나가 Debezium 이 되겠다. 이번 글에서는 Debezium이 어떻게 이런 문제를 해결할 수 있는지 살펴보겠다.

## Debezium 소개

Debezium 은 스스로 다음과 같이 소개하고 있다.

> Debezium is an open source distributed platform for change data capture

> Debezium 은 변경 데이터 캡처(Change Data Capture, CDC)를 위한 오픈 소스 분산 플랫폼입니다.

Debezium 은 Apache Kafka 위에서 동작한다. Kafka Connect와 호환되는 커넥터를 제공하는데, 커넥터는 DBMS에서 발생하는 데이터 변경 사항을 실시간으로 감지하여 각 변경 이벤트의 기록을 Kafka 토픽으로 스트리밍한다.

어플리케이션에서는 Kafka 토픽에서 생성된 이벤트 기록을 읽을 수 있다.

## 실습 예제: 직접 사용해보기

직접 사용해보기 위해 다음과 같은 예제를 만들어 보겠다.

> A 라는 서버에서 DB를 변경하였을 때, B 라는 서버에서 이를 캐치한다.

기본적인 내용은 Debezium의 공식 문서인 [Debezium Tutorial](http://debezium.io/documentation/reference/stable/tutorial.html) 을 따라가 보겠다.

하지만 아쉬운 점은 해당 문서가 업데이트 되지 않은지 좀 된 것으로 보인다. 아직 Zookeeper를 사용한 방법으로 설명하고 있다.

Kafka 는 꽤 오래전부터 Zookeeper 와의 종속성을 끊고자 준비하였고, 오랜 테스트를 거쳐 최근 출시한 4.0 버전부터는 Zookeeper 가 아닌, [KRaft 알고리즘](https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum)을 기본 설정값으로 사용하고 있다.

그래서 나는 최신 버전인 Kafka 4 를 기준으로 설정을 시도해보았다. DB는 MySQL로 진행한다.

### 시스템 구성 (compose)

아래 시스템 구성은 Podman에서 테스트 되었다. Docker에서 동작시켜도 크게 문제 없이 호환될 것으로 예상된다. (개인적으로 요즘은 Docker 보다는 Podman을 사용하려고 노력하고 있다.)

다음과 같이 `compose.yml` 을 구성하였다.

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0.32
    container_name: mysql_db
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=debeziumrootpassword
      - MYSQL_USER=mysqluser
      - MYSQL_PASSWORD=mysqlpw
      - MYSQL_DATABASE=mydb
    volumes:
      - poc_debezium_mysql_data:/var/lib/mysql
    networks:
      - kafka-net

  kafka-1:
    container_name: kafka-1
    image: confluentinc/cp-kafka:8.0.0
    ports:
      - "9092:9092"
    volumes:
      - ./data/kafka-1:/var/lib/kafka/data
    networks:
      - kafka-net
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-1:29092,EXTERNAL://localhost:9092
      KAFKA_LISTENERS: INTERNAL://:29092,CONTROLLER://:29093,EXTERNAL://0.0.0.0:9092
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:29093,2@kafka-2:29094,3@kafka-3:29095
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      CLUSTER_ID: "clusterid"

  kafka-2:
    container_name: kafka-2
    image: confluentinc/cp-kafka:8.0.0
    ports:
      - "9093:9093"
    volumes:
      - ./data/kafka-2:/var/lib/kafka/data
    networks:
      - kafka-net
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-2:29093,EXTERNAL://localhost:9093
      KAFKA_LISTENERS: INTERNAL://:29093,CONTROLLER://kafka-2:29094,EXTERNAL://0.0.0.0:9093
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:29093,2@kafka-2:29094,3@kafka-3:29095
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      CLUSTER_ID: "clusterid"

  kafka-3:
    container_name: kafka-3
    image: confluentinc/cp-kafka:8.0.0
    ports:
      - "9094:9094"
    volumes:
      - ./data/kafka-3:/var/lib/kafka/data
    networks:
      - kafka-net
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka-3:29094,EXTERNAL://localhost:9094
      KAFKA_LISTENERS: INTERNAL://:29094,CONTROLLER://kafka-3:29095,EXTERNAL://0.0.0.0:9094
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-1:29093,2@kafka-2:29094,3@kafka-3:29095
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      CLUSTER_ID: "clusterid"

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
    networks:
      - kafka-net

networks:
  kafka-net:
    driver: bridge

volumes:
  poc_debezium_mysql_data:
```

위 yml 파일에 이미 녹아져 있는 부분이긴 하지만, 구성시 아래 부분에서 서치가 필요하였다.

- `confluentinc/cp-kafka` 기준 8.0.x 부터 Apache Kafka 4.0.x 에 해당된다. ([Supported Versions and Interoperability for Confluent Platform](https://docs.confluent.io/platform/current/installation/versions-interoperability.html) 참고)
- KRaft 는 최소 3개의 브로커를 권장하고 있기 때문에, 3개의 Kafka 컨테이너를 설정하였다.
- `debezium` 은 dockerhub 에서 quay.io 로 옮겨갔다. (dockerhub 에서는 3.0 이후로 업데이트가 중단되었다.) 따라서 최신 버전을 찾아보려면 quay.io 에서 검색해봐야 한다.

yml 파일을 작성한 후 podman compose 로 실행 시켰다.

```bash
podman compose up -d
```

### mysql 설정

참고로 mysql에서 debezium 을 사용할 때는 `binlog_format` 이 반드시 'ROW' 여야 한다. (MySQL 기본 값은 `ROW` 이다. 따라서 별도로 설정하지 않았다면 문제가 없을 것이다.)

아래 명령어로 어떻게 설정되어있는지 확인해볼 수 있다.

```SQL
SHOW VARIABLES LIKE 'binlog_format';
```

테스트를 위해 아래와 같이 테이블을 생성해주었다.

```sql
CREATE TABLE IF NOT EXISTS customers (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255)
);
```

### 서버 A: 데이터 변경

데이터를 변경한다.

while 문을 통해 새로운 유저를 삽입/업데이트 한다.

```java
private static final String DB_URL = "jdbc:mysql://localhost:3306/mydb?useSSL=false&allowPublicKeyRetrieval=true";
private static final String USER = "mysqluser";
private static final String PASS = "mysqlpw";

public static void main(String[] args) throws Exception {
    Connection conn = null;
    Statement stmt = null;
    try {
        Class.forName("com.mysql.cj.jdbc.Driver");

        System.out.println("Connecting to database...");
        conn = DriverManager.getConnection(DB_URL, USER, PASS);
        stmt = conn.createStatement();

        // Insert and Update data periodically
        int recordId = 1;
        while (true) {
            // Insert a new record
            System.out.println("\nInserting a new record...");
            String insertSql = String.format(
                "INSERT INTO customers(first_name, last_name, email) VALUES ('John%d', 'Doe%d', 'john.doe%d@example.com')",
                recordId, recordId, recordId);
            stmt.executeUpdate(insertSql, Statement.RETURN_GENERATED_KEYS);
            System.out.println("Inserted record with id: " + recordId);

            TimeUnit.SECONDS.sleep(5);

            // Update the record
            System.out.println("Updating the record...");
            String updateSql = String.format(
                "UPDATE customers SET email = 'john.doe.updated%d@example.com' WHERE id = %d",
                recordId, recordId);
            stmt.executeUpdate(updateSql);
            System.out.println("Updated record with id: " + recordId);

            recordId++;
            TimeUnit.SECONDS.sleep(5);
        }

    } catch (Exception e) {
        e.printStackTrace();
    } finally {
        if (stmt != null) stmt.close();
        if (conn != null) conn.close();
    }
}
```

### 서버 B: 변경 이벤트 수신

Kafka Topic을 통해 변경 이벤트를 수신한다.

토픽 이름은 주석에도 적어두었지만 `topic-prefix.databaseName.tableName` 으로 지어진다.

이 예제에서는 `dbserver1` 이라는 topic prefix로 `mydb` database 의 `customers` 테이블에 대한 변경 이벤트를 수신하기 때문에 토픽명이 `dbserver1.mydb.customers` 가 된다.

(`topic-prefix` 는 아래의 커넥터 설정 에서 다시 언급된다.)

```java
// Debezium 토픽 이름 (topic-prefix.databaseName.tableName)
private static final String TOPIC_NAME = "dbserver1.mydb.customers";

public static void main(String[] args) {
    Properties props = new Properties();
    props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092,localhost:9093,localhost:9094");
    props.put(ConsumerConfig.GROUP_ID_CONFIG, "debezium-consumer-group");
    props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
    props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

    KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
    consumer.subscribe(Collections.singletonList(TOPIC_NAME));

    System.out.println("Listening for change events on topic: " + TOPIC_NAME);

    ObjectMapper mapper = new ObjectMapper();

    try {
        while (true) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records) {
                System.out.println("\n--- New Change Event ---");
                try {
                    System.out.println("record.value(): " + record.value());
                    JsonNode payload = mapper.readTree(record.value()).path("payload");
                    String op = payload.path("op").asText(); // c = create, u = update, d = delete

                    JsonNode dataState = null;
                    if ("d".equals(op)) {
                        dataState = payload.path("before");
                    } else {
                        dataState = payload.path("after");
                    }

                    System.out.println("Operation: " + op);
                    System.out.println("Data: " + dataState.toString());

                } catch (Exception e) {
                    System.err.println("Failed to parse JSON: " + record.value());
                    e.printStackTrace();
                }
            }
        }
    } finally {
        consumer.close();
    }
}
```

### 커넥터 설정

커넥터는 HTTP 요청으로 설정을 할 수 있다.

- 위에서 설명했던 `topic.prefix` 가 여기서 나온다.
- [`database.server.id`](https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-property-database-server-id) 의 경우 unique한 정수 String 으로 설정해주면 된다고 한다.
- [`database.history.kafka.topic`] 의 경우 schema의 변경 이력을 저장하는데 사용된다고 한다. (DDL 문)

```bash
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{
  "name": "mysql-inventory-connector",
  "config": {
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
    "schema.history.internal.kafka.topic": "dbhistory.inventory"
  }
}}'
```

Update 는 PUT 으로 가능하다.

```bash
curl -i -X PUT -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/<connector-name>/config -d '{
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
    "schema.history.internal.kafka.topic": "dbhistory.inventory"
  }'
```

조회와 삭제도 마찬가지로 HTTP 요청으로 할 수 있으며 다음과 같이 요청하면 된다.

```bash
curl -X GET http://<kafka-connect-host>:8083/connectors
```

```bash
curl -i -X DELETE http://<kafka-connect-host>:8083/connectors/<connector-name>
```

Connector 관련 API 들은 [Kafka Connect REST Interface for Confluent Platform](https://docs.confluent.io/platform/current/connect/references/restapi.html) 에서 확인해볼 수 있다.

### 실행하기

서버 A 와 B를 실행하고 지켜보면 아래와 같이 A에서 수행한 DB의 변경사항을 카프카를 통해 B에서 받아와 출력하는 것을 확인할 수 있다.

이제 변경 이벤트를 기반으로 원하는대로 가공하여 사용하면 된다.

```
...

--- New Change Event ---
record.value(): {"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"int32","optional":false,"field":"id"},{"type":"string","optional":true,"field":"first_name"},{"type":"string","optional":true,"field":"last_name"},{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"before"},{"type":"struct","fields":[{"type":"int32","optional":false,"field":"id"},{"type":"string","optional":true,"field":"first_name"},{"type":"string","optional":true,"field":"last_name"},{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,first,first_in_data_collection,last_in_data_collection,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":true,"field":"table"},{"type":"int64","optional":false,"field":"server_id"},{"type":"string","optional":true,"field":"gtid"},{"type":"string","optional":false,"field":"file"},{"type":"int64","optional":false,"field":"pos"},{"type":"int32","optional":false,"field":"row"},{"type":"int64","optional":true,"field":"thread"},{"type":"string","optional":true,"field":"query"}],"optional":false,"name":"io.debezium.connector.mysql.Source","version":1,"field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"dbserver1.mydb.customers.Envelope","version":2},"payload":{"before":null,"after":{"id":230,"first_name":"John230","last_name":"Doe230","email":"john.doe230@example.com"},"source":{"version":"3.2.1.Final","connector":"mysql","name":"dbserver1","ts_ms":1755598922000,"snapshot":"false","db":"mydb","sequence":null,"ts_us":1755598922000000,"ts_ns":1755598922000000000,"table":"customers","server_id":1,"gtid":null,"file":"binlog.000003","pos":168709,"row":0,"thread":12,"query":null},"transaction":null,"op":"c","ts_ms":1755598922571,"ts_us":1755598922571964,"ts_ns":1755598922571964844}}
Operation: c
Data: {"id":230,"first_name":"John230","last_name":"Doe230","email":"john.doe230@example.com"}

--- New Change Event ---
record.value(): {"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"int32","optional":false,"field":"id"},{"type":"string","optional":true,"field":"first_name"},{"type":"string","optional":true,"field":"last_name"},{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"before"},{"type":"struct","fields":[{"type":"int32","optional":false,"field":"id"},{"type":"string","optional":true,"field":"first_name"},{"type":"string","optional":true,"field":"last_name"},{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,first,first_in_data_collection,last_in_data_collection,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":true,"field":"table"},{"type":"int64","optional":false,"field":"server_id"},{"type":"string","optional":true,"field":"gtid"},{"type":"string","optional":false,"field":"file"},{"type":"int64","optional":false,"field":"pos"},{"type":"int32","optional":false,"field":"row"},{"type":"int64","optional":true,"field":"thread"},{"type":"string","optional":true,"field":"query"}],"optional":false,"name":"io.debezium.connector.mysql.Source","version":1,"field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"dbserver1.mydb.customers.Envelope","version":2},"payload":{"before":{"id":230,"first_name":"John230","last_name":"Doe230","email":"john.doe230@example.com"},"after":{"id":230,"first_name":"John230","last_name":"Doe230","email":"john.doe.updated230@example.com"},"source":{"version":"3.2.1.Final","connector":"mysql","name":"dbserver1","ts_ms":1755598927000,"snapshot":"false","db":"mydb","sequence":null,"ts_us":1755598927000000,"ts_ns":1755598927000000000,"table":"customers","server_id":1,"gtid":null,"file":"binlog.000003","pos":169054,"row":0,"thread":12,"query":null},"transaction":null,"op":"u","ts_ms":1755598927581,"ts_us":1755598927581026,"ts_ns":1755598927581026596}}
Operation: u
Data: {"id":230,"first_name":"John230","last_name":"Doe230","email":"john.doe.updated230@example.com"}

...
```

## Adanced

### 데이터 스냅샷과 스트리밍 시점

데이터는 어디서부터 가져와지는걸까?

debezium은 binlog를 스트리밍 한다. 그런데 어떤 시점부터 스트리밍을 하는걸까? binlog의 처음부터? 아니면 이전 데이터는 무시하고 커넥터를 설정한 시점부터?

이 것을 결정하는 옵션이 `snapshot.mode` 이다.

기본 동작(snapshot.mode=initial)은 최초에 스냅샷을 만든 후 이후 내용들을 스트리밍하는 방식이다.

[Debezium connector for MySQL](https://debezium.io/documentation/reference/stable/connectors/mysql.html) 에서 **Table 2. Settings for snapshot.mode connector configuration property** 를 참고하면 된다.

### 특정 컬럼 필터링하기

특정 테이블의 특정 컬럼의 변경만 받아올 수 있을까?

`column.include.list` 를 쓰면 가능하다.

이 방식은 필터링에 가깝다. 토픽명은 변경되지 않는다.

아래 결과값은 `column.include.list` 로 email 컬럼을 설정했을 때의 결과값이다.

```
--- New Change Event ---
record.value(): {"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,first,first_in_data_collection,last_in_data_collection,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":true,"field":"table"},{"type":"int64","optional":false,"field":"server_id"},{"type":"string","optional":true,"field":"gtid"},{"type":"string","optional":false,"field":"file"},{"type":"int64","optional":false,"field":"pos"},{"type":"int32","optional":false,"field":"row"},{"type":"int64","optional":true,"field":"thread"},{"type":"string","optional":true,"field":"query"}],"optional":false,"name":"io.debezium.connector.mysql.Source","version":1,"field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"dbserver1.mydb.customers.Envelope","version":2},"payload":{"before":null,"after":{"email":"john.doe335@example.com"},"source":{"version":"3.2.1.Final","connector":"mysql","name":"dbserver1","ts_ms":1755599974000,"snapshot":"false","db":"mydb","sequence":null,"ts_us":1755599974000000,"ts_ns":1755599974000000000,"table":"customers","server_id":1,"gtid":null,"file":"binlog.000003","pos":246094,"row":0,"thread":12,"query":null},"transaction":null,"op":"c","ts_ms":1755599974874,"ts_us":1755599974874808,"ts_ns":1755599974874808063}}
Operation: c
Data: {"email":"john.doe335@example.com"}

--- New Change Event ---
record.value(): {"schema":{"type":"struct","fields":[{"type":"struct","fields":[{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"before"},{"type":"struct","fields":[{"type":"string","optional":true,"field":"email"}],"optional":true,"name":"dbserver1.mydb.customers.Value","field":"after"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"version"},{"type":"string","optional":false,"field":"connector"},{"type":"string","optional":false,"field":"name"},{"type":"int64","optional":false,"field":"ts_ms"},{"type":"string","optional":true,"name":"io.debezium.data.Enum","version":1,"parameters":{"allowed":"true,first,first_in_data_collection,last_in_data_collection,last,false,incremental"},"default":"false","field":"snapshot"},{"type":"string","optional":false,"field":"db"},{"type":"string","optional":true,"field":"sequence"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"},{"type":"string","optional":true,"field":"table"},{"type":"int64","optional":false,"field":"server_id"},{"type":"string","optional":true,"field":"gtid"},{"type":"string","optional":false,"field":"file"},{"type":"int64","optional":false,"field":"pos"},{"type":"int32","optional":false,"field":"row"},{"type":"int64","optional":true,"field":"thread"},{"type":"string","optional":true,"field":"query"}],"optional":false,"name":"io.debezium.connector.mysql.Source","version":1,"field":"source"},{"type":"struct","fields":[{"type":"string","optional":false,"field":"id"},{"type":"int64","optional":false,"field":"total_order"},{"type":"int64","optional":false,"field":"data_collection_order"}],"optional":true,"name":"event.block","version":1,"field":"transaction"},{"type":"string","optional":false,"field":"op"},{"type":"int64","optional":true,"field":"ts_ms"},{"type":"int64","optional":true,"field":"ts_us"},{"type":"int64","optional":true,"field":"ts_ns"}],"optional":false,"name":"dbserver1.mydb.customers.Envelope","version":2},"payload":{"before":{"email":"john.doe335@example.com"},"after":{"email":"john.doe.updated335@example.com"},"source":{"version":"3.2.1.Final","connector":"mysql","name":"dbserver1","ts_ms":1755599979000,"snapshot":"false","db":"mydb","sequence":null,"ts_us":1755599979000000,"ts_ns":1755599979000000000,"table":"customers","server_id":1,"gtid":null,"file":"binlog.000003","pos":246439,"row":0,"thread":12,"query":null},"transaction":null,"op":"u","ts_ms":1755599979883,"ts_us":1755599979883677,"ts_ns":1755599979883677932}}
Operation: u
Data: {"email":"john.doe.updated335@example.com"}
```

## 마무리

이번 글을 작성하면서, 대략적으로만 알고 있던 Debezium을 직접 사용해보며 알아볼 수 있었다. Debezium을 사용하면 DB 변경 이벤트를 효율적으로 캡처하여 Kafka로 스트리밍할 수 있고, 수집된 변경 데이터를 다양한 시나리오에 활용 할 수 있다.

## 참고자료

- [Debezium Tutorial](http://debezium.io/documentation/reference/stable/tutorial.html)
