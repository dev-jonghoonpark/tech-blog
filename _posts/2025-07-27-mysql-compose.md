---
layout: "post"
title: "MySQL Docker Compose Yaml 구성 예시"
categories:
  - "스터디-데이터베이스"
  - "개발"
tags:
  - "MySQL"
  - "Docker"
  - "Compose"
  - "Docker Compose"
  - "yaml"
  - "yml"
date: "2025-07-27 13:00:00 +0900"
---

기록을 위해 남겨두는 자주 사용하는 mysql docker compose yaml.

`innodb-buffer-pool-size` 는 메모리의 50~75% 로 할당해준다.

```yaml
services:
  mysql:
    image: mysql:8.0.33
    container_name: test-mysql
    ports:
      - "3306:3306" # HOST:CONTAINER
    environment:
      MYSQL_ROOT_PASSWORD: mysqlrootpassword
      MYSQL_DATABASE: test
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --innodb-buffer-pool-size=8GB
    volumes:
      - test-mysql-data:/var/lib/mysql
    healthcheck:
      test: '/usr/bin/mysql --user=root --password=mysqlrootpassword --execute="SHOW DATABASES;"'
      timeout: 60s
      retries: 30
      interval: 1s

volumes:
  test-mysql-data:
```
