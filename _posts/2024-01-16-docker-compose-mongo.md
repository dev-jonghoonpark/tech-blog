---
layout: "post"
title: "mongodb docker compose 구성하기 (+ db 연결 안될 때)"
description: "MongoDB를 Docker Compose로 구성하는 방법과 데이터베이스 연결 문제 해결을 다룬 포스트입니다. Docker\
  \ Compose YAML 파일을 작성하여 MongoDB 컨테이너를 설정하고, 데이터베이스 연결 시 발생하는 인증 문제를 해결하기 위해 `?authSource=admin`을\
  \ URL에 추가해야 하는 이유를 설명합니다. 환경변수로 설정한 사용자 정보는 admin 데이터베이스에 저장되며, 이를 통해 연결 문제를 해결할\
  \ 수 있습니다."
categories:
- "개발"
tags:
- "mongodb"
- "docker docker compose"
- "compose"
- "env"
- "authSource"
- "admin"
date: "2024-01-16 09:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-01-16-docker-compose-mongo.jpg"
---

![mongodb logo](/assets/images/2024-01-16-docker-compose-mongo/MongoDB_Logo.png)

## docker compose yml 구성하기

기존에 mysql만 사용하던 서비스에 mongo를 하기로 하였다.

기존의 경우 mysql을 로컬에서 테스트 할 수 있도록 docker compose 를 이용하여 로컬에서 DB서버를 사용하였다.  
그래서 마찬가지로 로컬에서 개발/테스트를 할 수 있도록 mongo에 대한 정보를 compose yml 파일에 추가하였다.

간단하게 compose 파일의 형태를 적어보자면 다음과 같다.

```yml
version: "3"
services:
  mysql:
    # 생략
  mongo:
    image: mongo:7.0.5
    container_name: dev-mongo
    ports:
      - 27017:27017 # HOST:CONTAINER
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: RootPassword123!
      MONGO_INITDB_DATABASE: mydatdabase
    volumes:
      - mongo:/data/db
volumes:
  mysql:
  mongo:
```

버전은 현시점 기준 7.0.5 버전이 최신인 것 같아서, 해당 버전으로 리서치를 진행해보기로 결정하였다.

docker compose yml 을 작성하고 나서는 아래와 같이 명령어를 입력해주면 테스트 환경 구성이 완료된다.

```sh
COMPOSE_PROJECT_NAME=YOUR_COMPOSE_PROJECT_NAME docker-compose -f .docker/docker-compose.yml up -d
```

- COMPOSE_PROJECT_NAME 는 탑레벨 `name:` 과 동일하다.
- -f 옵션은 어떤 yml을 바라볼지 결정한다.
- -d 옵션은 background로 컨테이너를 실행한다.

## 문제 : 데이터베이스에 연결 안됨.

db 컨테이너가 정상적으로 올라왔기에 설정한 유저 정보를 토대로 data grip을 통해 접속을 시도하였지만 잘 되지 않았다.

해당 이슈를 검색해보면 연결 이슈 있을 경우 url 뒤에 `?authSource=admin` 를 추가하라고 한다.

그러면 문제가 해결이 되긴 한다.  
근데 그 이유에 대해서는 구체적으로 나와있지 않은 것 같아서 내용을 찾아보았다.

[mongo의 docker hub 페이지](https://hub.docker.com/_/mongo)를 보면 아래와 같은 내용이 있다.

> **MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD**
> These variables, used in conjunction, create a new user and set that user's password. This user is created in the `admin` authentication database and given the role of root, which is a "superuser" role.

우리가 환경변수로 설정한 유저 정보는 admin 데이터베이스에 저장이 된다 한다.

또, [mongo의 connection string 페이지](https://www.mongodb.com/docs/manual/reference/connection-string/)를 보면 아래와 같은 내용이 있다.

> Specify the database name associated with the user's credentials. If authSource is unspecified, authSource defaults to the defaultauthdb specified in the connection string. If defaultauthdb is unspecified, then authSource defaults to admin.

mongo 의 standard connection string은 아래와 같은 형태로 구성된다.

```
mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]
```

여기서 defaultauthdb 는 내가 연결하고자 하는 데이터베이스로 이해하면 된다.

connection string에 authSource는 지정하지 않고 defaultauthdb 부분을 지정해주었다면, authSource 값은 defaultauthdb 값과 동일하게 설정된다 한다.

## 마무리

두 가지 내용을 합쳐서 정리해보면 다음과 같다.

MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD 환경변수를 통해 mongo db 유저를 생성했을 경우 auth 정보가 admin 데이터베이스에서 생성된다.

그 상태에서 connection string에 authSource는 지정하지 않고 defaultauthdb 부분을 지정해주었다면, authSource 값은 defaultauthdb 값과 동일하게 설정된다.

우리가 환경변수로 설정한 유저 정보는 admin에 저장이 되었기 때문에 defaultauthdb 에는 우리가 찾고 있는 유저 정보가 없다.  
따라서 authSource를 지정해줘야 admin 데이터베이스에서 인증정보를 가져올 수 있다.

그래서 연결 이슈 있을 경우 url 뒤에 `?authSource=admin` 를 추가하라고 했던 것이다.
