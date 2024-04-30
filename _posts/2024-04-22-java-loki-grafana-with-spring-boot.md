---
layout: post
title: "[Java] spring boot 프로젝트에 loki 추가해서 로그 수집하기"
categories: [스터디-자바, 개발]
tags:
  [
    자바,
    java,
    스프링,
    스프링 부트,
    spring,
    spring boot,
    grafana,
    loki,
    로그,
    로그 수집기,
    log,
    logging,
    jenkins,
    젠킨스,
    그라파나,
    로키,
  ]
date: 2024-04-22 22:20:00 +0900
toc: true
---

## 개요

최근에 테스트 환경을 좀 더 디테일하게 구성하는 작업을 하고 있다.

로컬 기기(맥북)에서 모든걸 다 돌리기에는 성능이 부족하기 때문에, 개인 서버로 옮길 부분들을 옮겼고,
최근에는 jenkins를 이용하여 파이프라인을 통해, git에서 최신 코드를 가져와서 테스트 환경을 최신버전으로 갱신하도록 하였다.

그런데 이 과정에서 파이프라인이 돌 때 마다 컨테이너가 교체되기도 하고, 컨테이너 수들이 늘어남에 따라 로그를 추적하기가 어려워지고 있다고 판단 하였기 때문에, 이 부분을 개선보기로 하였고 loki를 도입해봐야겠다고 생각하였다.

### Grafana 와 Loki에 대한 간단한 설명

![grafana logo](/assets/images/2024-04-22-java-loki-grafana-with-spring-boot/grafana.png)

> 로키(Loki)는 모든 애플리케이션과 인프라의 로그를 저장하고 쿼리하도록 설계된 로그 집계 시스템이다.

> 그라파나(Grafana)는 오픈 소스 분석 및 모니터링 솔루션이다.

회사에서는 데이터독(Datadog)을 쓰고 있다. 하지만 지금 내가 하고 있는 작업은 개인적으로 테스트 환경을 구축하고 있는 것이기 때문에 LOKI를 선택하였다.

## Grafana + Loki 설치

공식 document 에서 docker-compose 를 이용하여 설치하는 방법을 제공해서 docker compose 로 설치하였다.

[Install with Docker Compose](https://grafana.com/docs/loki/latest/setup/install/docker/#install-with-docker-compose)

```sh
wget https://raw.githubusercontent.com/grafana/loki/v2.9.2/production/docker-compose.yaml -O docker-compose.yaml
docker-compose -f docker-compose.yaml up -d
```

글을 작성한 시점에는 v3.0.0 버전이 나와있는 상태였기 때문에 다운로드 된 yaml 파일을 수정하여 3.0.0 버전으로 진행하였다.(아직 문서와 yaml 파일은 아직 업데이트 되지 않았지만.)

최종적으로 작성된 docker-compose.yaml 은 다음과 같다.

```yaml
version: "3"

networks:
  loki:

services:
  loki:
    image: grafana/loki:3.0.0
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - loki

  promtail:
    image: grafana/promtail:3.0.0
    volumes:
      - /var/log:/var/log
    command: -config.file=/etc/promtail/config.yml
    networks:
      - loki

  grafana:
    environment:
      - GF_PATHS_PROVISIONING=/etc/grafana/provisioning
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    entrypoint:
      - sh
      - -euc
      - |
        mkdir -p /etc/grafana/provisioning/datasources
        cat <<EOF > /etc/grafana/provisioning/datasources/ds.yaml
        apiVersion: 1
        datasources:
        - name: Loki
          type: loki
          access: proxy
          orgId: 1
          url: http://loki:3100
          basicAuth: false
          isDefault: true
          version: 1
          editable: false
        EOF
        /run.sh
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    networks:
      - loki
```

grafana 의 초기 로그인 계정은 `admin/admin` 이다.

## jenkins 에서 loki와 관련된 설정들을 삽입처리하기

참고로 jenkins에서 삽입 처리를 하는 이유는 **개인 테스트 환경을 구축하는 용도 이기 때문에 코드에 영향을 주지 않도록 하는 것을 목표로 하였기 때문**이다.
(만약 그냥 코드를 수정해도 되는 상황이라면 필요한 부분들만 참고하면 된다.)

최종적으로 다음과 같이 pipeline script 를 작성하게 되었다. (이 코드는 실제 코드에서 일부를 가져온 것이며, 예제로 사용할 수 있도록 처리한 코드이다.)

```groovy
stages {
    // 이전 빌드의 변경사항들이 새 빌드에 영향이 가지 않도록 pipeline이 본격적으로 진행되기 전에 초기화를 진행하였다.
    stage ('reset prev build changes') {
        steps {
            sh 'git reset --hard HEAD || true'
        }
    }
    // 업데이트 된 항목들을 가져온다.
    stage ('checkout') {
        steps {
            script {
                def scmVars = checkout([
                    $class: 'GitSCM',
                    branches: [[name: "${params.GIT_BRANCH}"]],
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [[
                        $class: 'SubmoduleOption',
                        disableSubmodules: false,
                        parentCredentials: true,
                        recursiveSubmodules: true,
                        reference: '',
                        trackingSubmodules: false
                    ]],
                    submoduleCfg: [],
                    userRemoteConfigs: [[
                        credentialsId: 'bitbucket',
                        url: env.GIT_URL
                    ]]
                ])
            }
        }
    }
    // loki 와 관련된 부분을 추가한다.
    stage ('add loki') {
        stages {
            // 어떻게 해야 build.gradle에 dependency를 깔끔하게 추가할 수 있을까 찾아보았는데 아직 이 방법보다 깔끔한 방법은 찾지 못하였다.
            stage ('update build.gradle') {
                steps {
                    script {
                        def buildGradleFile = "${workspace}/build.gradle"
                        def dependencyName = "implementation 'com.github.loki4j:loki-logback-appender:1.5.1'"
                        def buildGradle = readFile(buildGradleFile)
                        def insertIndex = buildGradle.indexOf("dependencies {") + 15
                        buildGradle = buildGradle.substring(0, insertIndex) + "\n    " + dependencyName + "\n" + buildGradle.substring(insertIndex)
                        writeFile(file: buildGradleFile, text: buildGradle)
                    }
                }
            }
            // logback.xml 을 미리 작성된 파일로 교체한다. logback.xml 은 하단에서 정리한다.
            stage ('replace logback.xml') {
                steps {
                    configFileProvider([configFile(fileId: 'ooo-logback', variable: 'OOO_LOGBACK')]) {
                        sh "cp ${OOO_LOGBACK} ${workspace}/src/main/resources/logback.xml"
                    }
                }
            }
        }
    }
    stage ('gradle build') {
        steps {
            sh 'rm -r caches || true'
            sh 'GRADLE_USER_HOME=. ./gradlew build'
        }
    }
    stage ('docker build') {
        steps {
            sh 'docker build -t DOCKER_REGISTRY_IP:5000/example:latest .'
        }
    }
    stage ('docker image push') {
        steps {
            sh 'docker login http://DOCKER_REGISTRY_IP:5000 -u registry_id -p registry_password'
            sh 'docker image push DOCKER_REGISTRY_IP:5000/example:latest'
        }
    }
    stage ('docker run example-1') {
        steps {
            sh 'docker stop example-1 || true && docker rm example-1 || true'
            sh 'docker run -dit --name example-1 ' +
                '-e LOKI_ENV=local ' + // logback.xml 에서 사용한다. 검색시 환경을 구분하는데 사용된다.
                '-e LOKI_SERVICE=example-1 ' + // logback.xml 에서 사용한다. 검색시 서비스(서버)를 구분하는데 사용된다.
                'DOCKER_REGISTRY_IP:5000/example:latest'
        }
    }
}
```

logback.xml은 다음과 같다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <appender name="LOKI" class="com.github.loki4j.logback.Loki4jAppender">
        <http>
            <url>http://{YOUR_LOKI_IP}:3100/loki/api/v1/push</url>
        </http>
        <format>
            <label>
                <pattern>service_name=${LOKI_SERVICE},host=${HOSTNAME},level=%level,env=${LOKI_ENV}</pattern>
                <readMarkers>true</readMarkers>
            </label>
            <message class="com.github.loki4j.logback.JsonLayout" />
        </format>
    </appender>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <!-- ... -->
    </appender>
    <root level="debug">
        <appender-ref ref="LOKI"/>
        <appender-ref ref="STDOUT"/>
    </root>
    <root level="info">
        <appender-ref ref="LOKI"/>
        <appender-ref ref="STDOUT"/>
    </root>
</configuration>
```

위 코드를 Jenkins 관리의 Managed files에 등록해주면 된다.

![managed files](/assets/images/2024-04-22-java-loki-grafana-with-spring-boot/managed-files.png)

## 결과

목표했던 대로 loki를 통해 로그를 모아서 한 곳(grafana)에서 조회할 수 있게 되었고, 원한다면 환경과 서버를 특정해서도 검색할 수 있게 되었다.

![loki-query-result](/assets/images/2024-04-22-java-loki-grafana-with-spring-boot/loki-query-result.png)

## 기타

이 글에서는 log4j를 이용하여 처리하는 방식을 사용하였기 때문에 다루지 않았지만 프롬테일을 이용한 방법도 있다고 한다.

> Promtail은 로컬 로그의 내용을 Loki 인스턴스로 전송하는 에이전트이다.
