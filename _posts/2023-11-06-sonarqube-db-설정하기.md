---
layout: post
title: 소나큐브 에 PostgreSQL DB 설정하기 (with PostgreSQL)
categories: [개발, 스터디-테스트]
tags: [
    Sonarqube,
    소나큐브,
    PostgreSQL
    DB,
    데이터베이스,
    Docker,
  ]
date: 2023-11-07 12:50:00 +0900
---

예전에 소나큐브(Sonarqube)와 관련된 글을 작성한 적이 있다.  
[소나큐브 설치하기 (with Docker, macOS)](/2023/08/02/install-sonarqube-with-docker-in-local-macos)

이번에도 macOS에다 설치한 것은 아니고 이번에는 평범하게 ubuntu 서버에 설치하였다.

이전 글 작성 당시 DB 연결과 관련된 부분은 포함하지 않았기 때문에
이번 글에서는 ubuntu 서버에서 docker를 이용해 sonarqube를 구축하면서 DB를 연결해본 경험을 기록해보려 한다.

그리고 다음 글에서는 jenkins와 연동한 경험까지 적어보려고 한다.

## DB 설정

**[sonarqube - install-the-server](https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/)**

Sonarqube는 Database로 `MSSQL` 과 `Oracle` 과 `PostgreSQL` 을 사용할 수 있다.

일단은 셋 중에서 가장 설치하기 쉬운 PostgreSQL을 선택하였다.  
[supabase](https://supabase.com/) 에서 무료로 지원해주는 것으로 알고있으니 사용해봐도 좋을 것 같다.

하지만 나는 클라우드 DB를 사용하는 것이 아니라 로컬 DB를 사용하고 싶어서
docker를 이용해서 컨테이너를 생성하였다.

`MSSQL` 과 `Oracle` 은 사용해봤는데 `PostgreSQL` 은 처음 사용해보지만 RDBMS 끼리는 기본적인 부분은 비슷하다고 생각하므로 바로 시작하였다.

```
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres
```

PostgreSQL의 기본 포트는 5432 이다
그리고 기본 user name은 `postgres` 이다

root 계정을 그대로 쓸 생각은 없으므로, root 계정으로 로그인 한 후 별도의 유저 계정을 생성해주었다.  
user 생성은 다음과 같이 쿼리하면 된다. CREATEDB 권한이 필요할 것으로 예상되서 추가해주었다.

```
CREATE USER sonarqube PASSWORD 'mysecretpassword' CREATEDB;
```

![test-connection](/assets/images/2023-11-06-sonarqube-db-설정하기/test-connection.png)
테스트 연결을 해보았을 때 잘 되는걸 볼 수 있다.

특이하게 PostgreSQL에는 Database 라는 개념 외에도 Schema 라는 개념도 있었다.  
이 부분은 이 글에서 다루지는 않는다.

Database와 Schema까지 추가를 해주면 된다.  
나는 모두 sonarqube라는 이름으로 통일해서 진행하였다. (Database 이름도, Schema 이름도, User이름도 모두 sonarqube로 진행하였다.)

결론적으로 sonarqube 라는 데이터베이스 안에 sonarqube 라는 스키마를 만들었다. 진행하면서 권한 관련 설정도 필요 할 수 있다.

그 이후 문서를 보면 search_path 설정을 해주라고 되어있어서 아래와 같이 설정 해주었다.
(나의 경우에는 mySonarQubeSchema 를 sonarqube 로 치환했다.)

```
ALTER USER sonarqube SET search_path to mySonarQubeSchema
```

위 SQL의 의미를 찾아보니 search_path 설정을 하면 스키마 표기를 생략할 수 있다고 한다.

## 소나큐브 설정

이후에는 conf 파일을 수정해야 한다.

근데 그 전에 docker 컨테이너에서 호스트 로컬로 분리하고 싶었다.
지난번에 회사 개발서버에서 그냥 docker 컨테이너 안에서 설정 파일들을 보관하고 있다가, 서버 스펙 업그레이드를 하는 도중에 컨테이너가 날아간 적이 있었다. 데이터는 개인적으로 자체 백업 해둬서 금방 복구하긴 했다.
같은 미리 방지해야겠다고 생각했다.

일단 기존에 생성되어 있는 conf 파일을 옮겼다.

```
sudo docker cp sonarqube:/opt/sonarqube/conf /home/jonghoonpark/sonarqube
```

이후 새로 컨테이너를 띄우면서 conf를 연결하였다.

```sh
docker run -d --name sonarqube -p 9000:9000 \
  -v /home/jonghoonpark/sonarqube/conf:/opt/sonarqube/conf \
  -v /home/jonghoonpark/sonarqube/data:/opt/sonarqube/data \
  -v /home/jonghoonpark/sonarqube/temp:/opt/sonarqube/temp \
  sonarqube
```

v 옵션에 대해서 간단하게 설명 하자면 `-v A:B` 라고 되어 있다면
A는 호스트의 경로이고, B는 컨테이너의 경로이다. 그리고 두 가지를 연결해준다고 생각하면 되겠다.
따라서 컨테이너에서 B라는 경로를 접속할 한다면 A로 연결된다. (마운트된다고 표현)
더 자세한 내용이 궁금하다면 검색해보자.

data 와 temp는 Eleasticsearch storage path 인데 별도의 경로를 세팅하는 것이 좋다고 해서 같이 빼주었다.

이후 `/conf/sonar.properties` 에서 아래 부분들을 수정해주면 된다. (참고로 서로 모여있지는 않다.)

```yml
sonar.jdbc.username=sonarqube
sonar.jdbc.password=mysecretpassword
sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
sonar.path.data=/var/sonarqube/data
sonar.path.temp=/var/sonarqube/temp
```

![sonarqube-properties](/assets/images/2023-11-06-sonarqube-db-설정하기/sonarqube-properties.png)

## 에러 해결

설정을 마치고 실행하면 여러 에러가 뜨는데 해결하는 방법은 다음과 같다.

### 에러 1.

```
Unable to create shared memory
Cleaning or creating temp directory /opt/sonarqube/temp
```

이 에러의 경우 아까 만들어준 data 폴더와, temp 폴더를 777로 설정해주면 해결된다.

```
sudo chmod -R 777 data
sudo chmod -R 777 temp
```

자세한 내용이 궁금하다면 [unable-to-create-shared-memory-permission-denied](https://community.sonarsource.com/t/unable-to-create-shared-memory-permission-denied/61498) 참고

### 에러 2.

```
max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]
```

이 에러의 경우 docker가 실행중인 host 에서

```
sudo sysctl -w vm.max_map_count=262144
```

명령어 실행하여 해결할 수 있다.

자세한 내용은 [stackoverflow](https://stackoverflow.com/a/57998152) 답변 참고

## 완료

이렇게 정상적으로 마치고 sonarqube를 실행하여 진입하였다면 아래와 같이 데이터베이스가 생성된다.

![database-created](/assets/images/2023-11-06-sonarqube-db-설정하기/database-created.png)

이후 글에서는

- [소나큐브 프로젝트 설정하고 정적 분석 해보기](/2023/11/07/create-sonarqube-project)
- [소나큐브 코드 정적 검사 자동화 하기 (with Jenkins)](/2023/11/07/sonarqube-with-jenkins)

에 대해서 이야기 해본다.
