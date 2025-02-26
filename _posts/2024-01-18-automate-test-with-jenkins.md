---
layout: "post"
title: "jenkins pipeline 에서 데이터베이스 테스트 환경 세팅 자동화하기 (테스트용 데이터베이스 컨테이너 사용)"
description: "Jenkins 파이프라인을 활용하여 데이터베이스 테스트 환경을 자동으로 설정하는 방법을 다룹니다. 이 과정에서는 최신 코드\
  를 가져오고, 비어있는 테스트 데이터베이스 서버를 구축하여 Gradle 통합 테스트를 수행하며, 테스트 완료 후 데이터베이스 서버를 정리하는 과\
  정을 설명합니다. 또한, Docker와 Jenkins의 통합 사용법과 발생할 수 있는 여러 이슈 및 해결 방법도 포함되어 있습니다."
categories:
- "개발"
- "스터디-테스트"
- "스터디-자동화"
tags:
- "jenkins"
- "pipeline"
- "git"
- "checkout"
- "docker"
- "network"
- "bridge"
- "docker cli"
- "test container"
- "gradle"
- "mysql"
date: "2024-01-18 14:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-01-18-automate-test-with-jenkins.jpg"
---

최근 며칠 동안 시간날 때마다 jenkins상에서 데이터베이스 테스트(통합 테스트)를 실행할 수 있도록 만들기위해 매우 많은 삽질을 하였습니다. 어느 정도 진행이 되어서 진행상황을 블로그에 정리해보기로 하였습니다.

막혔을 때 도와주신 devops님께 감사드립니다.

## 만들고자 목표한 것

젠킨스 파이프라인을 빌드하면

1. 최신 코드 가져와서
2. gradle integration test task 수행

   - 이때 데이터가 비어있는 테스트 데이터베이스 서버를 구축
   - 테스트 데이터베이스에 연결하여 테스트를 수행
   - 테스트 수행이 완료되었을 경우 테스트 데이터베이스 서버를 정리

3. 결과를 slack으로 전송

위 과정을 수행하도록 하고 싶었다.

이 글에서는 3번은 다루지 않으며 오직 1, 2번에 대해서만 다룬다.
아직 작업중이기 때문에 3번에 대한 부분도 작업이 완료되는대로 정리해보도록 하겠다.

## 최신 코드 가져오기

![Passing test parameters](/assets/images/2024-01-18-automate-test-with-jenkins/passing-test-parameters.png)

현재 프로젝트에서는 버전별로 브랜치를 관리하고 있기 때문에 **매개변수와 함께 빌드(Passing test parameters)** 할 수 있도록 옵션을 설정해주었다.

```
def scmVars = checkout([
    $class: 'GitSCM',
    branches: [[name: "release/${params.VERSION}"]],
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
        credentialsId: 'YOUR_CREDENTIAL_ID',
        url: env.GIT_URL
    ]]
])
```

빌드시 입력한 버전 (`params.VERSION`) 으로 해당 브랜치의 최신 코드를 checkout 해온다.

## 테스트 데이터베이스를 띄워서 통신하기

이 부분에서 많은 시간과 시도가 필요하였다.
jenkins pipeline에 사용되는 groovy script에 익숙하지 않은 부분도 있었고 관련된 자료도 많지 않았다.

이것보다 더 좋은 방법도 있을 것이라 생각된다.
하지만 자료가 일단 없었기 때문에 더 좋은 정보가 공유되기를 기대하면서 작성해본다.

jenkins와 docker의 공식 문서를 최대한 참고하려고 노력하였다. 특히 아래의 문서를 많이 본 것 같다.

- [Using Docker with Pipeline](https://www.jenkins.io/doc/book/pipeline/docker/)

위 문서에 있는 기능을 사용하려면 jenkins에서 `docker` 와 `docker pipeline` plugin 설치가 필요하다.

> 참고로 위 문서에 있는 docker 기능을 사용하려고 하면 `Use Groovy Sandbox` 를 off 처리해야하고, 그와 동시에 코드를 수정할 때 마다 jenkins admin에게 코드 수정에 대한 허가를 받아야 한다. 허가를 받지 않으면 pipeline 빌드 시도시 에러와 함께 바로 종료된다.  
> devops님께 계속 부탁드리기도 뭐해서 그냥 나는 로컬에서 실행 환경을 구축하여 진행하였다.

최종적으로 아래와 같은 구조로 파이프라인이 동작하게 구성하게 되었다.

![how-does-it-work](/assets/images/2024-01-18-automate-test-with-jenkins/how-does-it-work.png)

총 3개의 docker 컨테이너가 사용된다.

첫번째 컨테이너는 docker network를 생성하기 위해 사용된다.
network를 생성하는 이유는 gradle 명령어를 수행할 컨테이너에서 database가 올라와 있는 컨테이너와 통신을 해야하기 때문이다.
host 입장에서는 각각의 컨테이너에 대한 정보를 알고 있지만 각 컨테이너의 입장에서는 서로에 대한 정보를 알지 못한다. 그렇기 때문에 network를 생성하여 연결을 해줘야했다.

최종 코드는 다음과 같다.

```groovy
pipeline {
    agent {
        docker {
          // 이미지는 본인 상황에 맞게 변경해줘야 함.
          // 단순히 docker-cli 사용을 위한 이미지.
          image 'docker-cli'
        }
    }

    environment {
        GIT_URL = "YOUR_GIT_URL"
    }

    stages {
        stage ('check network bridge') {
            steps {
                script {
                    // 있으면 사용하고 없으면 생성하도록 처리하였다.
                    sh '''
                    docker network inspect {NETWORK_NAME} >/dev/null 2>&1 || \
                    docker network create --driver bridge {NETWORK_NAME}
                    '''
                }
            }
        }
        stage ('start test') {
            agent {
                docker {
                  // 이미지는 본인 상황에 맞게 변경해줘야 함.
                  // Gradle 실행을 위한 자바 환경 이미지가 필요.
                  // 나의 경우에는 아래에서 데이터베이스 health 체크용으로 `docker exec` 명령어를 수행하도록 하기 위해 docker cli 추가 해서 사용하였다.
                  image 'GRADLE'
                  args '-v /var/run/docker.sock:/var/run/docker.sock --network {NETWORK_NAME}'
                }
            }
            stages {
                stage ('checkout') {
                    steps {
                        script {
                            def scmVars = checkout([
                                $class: 'GitSCM',
                                branches: [[name: "release/${params.VERSION}"]],
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
                                    credentialsId: 'YOUR_CREDENTIAL_ID',
                                    url: env.GIT_URL
                                ]]
                            ])
                        }
                    }
                }
                stage ('run integration test') {
                    steps {
                        script {
                            docker.image('mysql:8.0.33')
                                .withRun('--network {NETWORK_NAME}'
                                + ' -e MYSQL_ROOT_PASSWORD={YOUR_PASSWORD}'
                                + ' -e MYSQL_DATABASE={YOUR_DATABASE}') { c ->

                                // Wait until mysql is up
                                sh "while ! docker exec ${c.id} mysqladmin --user=root --password={YOUR_PASSWORD} --host '127.0.0.1' ping --silent ; do sleep 5; done;"

                                sh "GRADLE_USER_HOME=./.gradle DATASOURCE_HOST=${c.id.substring(0,12)} DATASOURCE_PORT=3306 ./gradlew integrationTest"
                                // integrationTest는 커스텀 task이다.
                            }
                        }
                    }
                }
            }
        }
    }

//   post {
//     always {
//         script {
//             ...
//         }
//     }
//     ...
//   }
}
```

이렇게 되면 초기에 구상했던데로 테스트 데이터베이스를 통한 테스트가 진행된다.  
pipeline 과정을 통해 3개의 컨테이너가 실행되었다가 테스트를 마치면 컨테이너들도 함께 종료된다.

## 만났던 이슈들

### read-only file system

```
docker run -p 8080:8080 -p 50000:50000 -v /home/jonghoonpark/jenkins:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock -v $(which docker):/usr/bin/docker --privileged --name jenkins -d jenkins/jenkins
0e75f7c0ff73f3fc2b0cbc62d7770a4b40fba9d2d73ac1278a9d8ec6b9bb5582
docker: Error response from daemon: error while creating mount source path '/usr/bin/docker': mkdir /usr/bin/docker: read-only file system.
```

#### 해결법

snap을 통해 설치한 docker를 삭제하고 apt를 통해서 재설치 하면 되었다.
[https://stackoverflow.com/a/52566470](https://stackoverflow.com/a/52566470)

### jenkins에서 docker.sock 접근 가능하도록 설정하기

```sh
docker exec -it -u root jenkins /bin/bash
groupadd docker
usermod -aG docker jenkins
chmod 666 /var/run/docker.sock
```

### docker: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32` not found, version `GLIBC_2.34` not found

docker 안에서 docker 를 수행하게 되었을 때 아래와 같은 이슈가 발생되었다.

```
docker: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found (required by docker)
docker: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found (required by docker)
```

딱 아래 링크한 블로그 글에 있는 상황과 동일한 상황이였다.  
[https://velog.io/@yaaloo/CICD-Jenkins](https://velog.io/@yaaloo/CICD-Jenkins)

젠킨스 컨테이너 실행 옵션에 `-v /var/bin/docker:/var/bin/docker` 를 넣어서 발생하는 이슈였다.
각 이미지별 환경을 맞춰주기는 쉽지 않았기 때문에 나는 다음과 같이 해결했다.

어처피 `docker.sock` 은 공유가 가능하기 때문에 우리에게는 docker cli만 있으면 된다.
따라서 내 환경에 맞는 docker cli 만 수동으로 설치해주는 방향으로 진행하였다.

#### 1. 아래 명령어를 통해서 내 ubuntu codename을 확인

```sh
lsb_release -a
```

#### 2. 내 ubuntu에 맞는 파일 확인

[https://download.docker.com/linux/ubuntu/dists/](https://download.docker.com/linux/ubuntu/dists/)

```
{codename}/pool/stable/amd64/원하는 버전
```

#### 3. Dockerfile 작성

```sh
FROM ubuntu:22.04

RUN \
      apt-get update && apt-get install curl -y && \
      curl -o docker-ce-cli.deb https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-ce-cli_24.0.7-1~ubuntu.22.04~jammy_amd64.deb && \
      dpkg -i ./docker-ce-cli.deb
```

## 마무리

일단은 동작하도록 스크립트를 작성을 완료해서 어느정도 만족스럽다.  
내일 devops 님께 리뷰를 받아보고 개선할 부분이 있으면 개선해 볼 예정이다.

커뮤니티 유저분이 글을 봐주시고 도커 컴포즈로 묶어보는건 어떨지에 대한 조언을 해주셨다.
