---
layout: post
title: 소나큐브 정적 분석 자동화 하기 (with Jenkins)
description: Jenkins를 활용하여 소나큐브의 정적 분석을 자동화하는 방법을 소개합니다. 도커를 이용해 Jenkins를 설정하고, Git 리포지토리에서 코드를 체크아웃한 후, Gradle 플러그인을 동적으로 추가하여 정적 분석을 수행합니다. 또한, 주기적인 실행을 위해 cron 스케줄러를 설정하고, Typescript 프로젝트에서도 Node.js를 설정하여 분석을 진행하는 방법을 설명합니다. 이 글은 Jenkins와 소나큐브를 통합하여 CI/CD 파이프라인을 구축하는 과정을 자세히 다룹니다.
categories: [개발, 스터디-테스트, 스터디-자동화]
tags:
  [
    Sonarqube,
    소나큐브,
    Jenkins,
    CI/CD,
    Docker,
    automation,
    pipeline,
    schedule,
    cron,
    nodejs,
    sonar scanner,
    gradle,
    build.gradle,
    build,
  ]
date: 2023-11-07 22:30:00 +0900
---

- [소나큐브 에 PostgreSQL DB 설정하기 (with PostgreSQL)](/2023/11/07/sonarqube-db-설정하기)
- [소나큐브 프로젝트 설정하고 정적 분석 해보기](/2023/11/07/create-sonarqube-project)

에서 이어지는 글입니다.

---

지난 글에서는 sonarqube를 통해 정적 분석을 직접 진행해보았다.

우리 회사의 경우 소나큐브를 통한 코드 정적 검사를 자동화 해두었다.

Jenkins를 통해서 자동화가 진행되는데, 평소에도 Jenkins와 같은 CI/CD 도구에도 관심을 가지고 있었기 때문에 직접 세팅을 해봤다.

---

## Jenkins 설정하기

Jenkins도 도커 컨테이너를 이용하여 띄운다.

> 참고로 구글에 "jenkins docker" 라고 검색하면 첫번째로 나오는 페이지([https://hub.docker.com/\_/jenkins/](https://hub.docker.com/_/jenkins/)) 는 deprecated 된 docker image 이다.
>
> [https://hub.docker.com/r/jenkins/jenkins](https://hub.docker.com/r/jenkins/jenkins) 가 현재 운영중인 docker image 이다. 이 이미지를 받아야 한다.

---

아래 명령어로 jenkins이미지를 실행하였다.

```
docker run -p 8080:8080 -p 50000:50000 -v /home/jonghoonpark/jenkins:/var/jenkins_home -d jenkins
```

-v 옵션 부분은 본인한테 맞게 설정해주면 되고, 빼도 문제는 없다.

실행을 하고 조금 기다린 후 `docker logs` 명령어를 입력하면 32자 hex인 `initialAdminPassword` 값을 확인할 수 있다.
이 값은 `/var/jenkins_home/secrets/initialAdminPassword` 에서 다시 확인 가능하다.
컨테이너의 bash를 실행해서 들어가서 직접 확인해도 된다.
이 값을 잘 보관해두자.

8080 포트로 들어가보면 아래와 같은 화면을 볼 수 있다.

![unlock jenkins](/assets/images/2023-11-06-sonarqube-with-jenkins/unlock-jenkins.png)

아까 보관해 두었던 initialAdminPassword을 여기서 입력하면 된다.

initialAdminPassword을 올바르게 입력했다면 이후로는 내가 사용할 admin 계정을 만드면 단계이다.

![create first admin user](/assets/images/2023-11-06-sonarqube-with-jenkins/create-admin-user.png)

admin 계정을 만들고 나서는 plugin 을 설정하는 단계로 이동되는데
plugin 들은 어떤게 필요할지 잘 모르고, 이후에 설치가 가능하기 때문에
초기화 단계에서는 추천해주는 것들으로 그냥 설치했다.

## jenkins 파이프라인 만들기

![create-jenkins-pipeline](/assets/images/2023-11-06-sonarqube-with-jenkins/create-jenkins-pipeline.png)

프로젝트 이름을 생성하고 Pipeline을 클릭하면 된다.

파이프라인이 생성되었으면 해당 파이프라인 페이지로 들어가 좌측 메뉴에서 구성(configure)을 누른다.

![pipeline-configure](/assets/images/2023-11-06-sonarqube-with-jenkins/pipeline-configure.png)

구성에 들어가면 Pipeline 의 script를 작성할 수 있다. jenkins의 script는 groovy 를 사용한다.

pipeline에서 sonarqube를 사용하기 위해서는 먼저 프로젝트를 checkout을 해야한다.
아래와 같이 구성하여 checkout을 할 수 있다.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main',
                        url: 'https://your-git-repository-url'
                }
            }
        }
    }
}
```

여기서 문제는 모든 repository 가 public 하지는 않기 때문에 credential을 추가해주어야 한다는 것이다.

### git credential 추가하기

credential 정보는 jenkins 메인페이지 - manage - Credentials 에서 추가할 수 있다.

키를 생성하는 방법은 아래와 같다.

```
ssh-keygen -o -t rsa -C "your@git-email.com"
```

![generate-ssh-key](/assets/images/2023-11-06-sonarqube-with-jenkins/generate-ssh-key.png)

`~/.ssh/id_rsa` 가 private key, `~/.ssh/id_rsa.pub` 가 public key이다. 키 값은 cat 명령어로 쉽게 확인할 수 있다.  
jenkins에는 private 키를 bitbucket에는 public 키를 등록해야 한다.
(양쪽 다 public을 등록했다가 한참 해맸으니 주의할 것)

![add-git-credentials](/assets/images/2023-11-06-sonarqube-with-jenkins/add-git-credentials.png)

jenkins에서 credential을 등록할 때 `id` 는 jenkins script 내에서 사용하는 id 이다.

이 아이디를 방금 전 작성했던 pipeline script에 추가해주면 된다.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'YourCredentialsId',
                        url: 'https://your-git-repository-url'
                }
            }
        }
    }
}
```

정상적으로 등록했다면 checkout이 문제없이 완료될 것이다.

### Gradle 기반 프로젝트에서 build.gradle에 id 추가 없이 동적분석 하기

이전 포스트([소나큐브 프로젝트 설정하고 정적 분석 해보기](/2023/11/07/create-sonarqube-project)) 에서 build.gradle 에 plugins 파트에 sonarqube id를 추가했었다.

근데 내가 정적 분석을 하겠다고 백엔드 코드에 수정을 주고 싶지는 않았다.
그래서 checkout을 통해 받아온 코드에서 동적으로 sonarqube id를 추가하고 정적 분석을 돌리도록 하고 싶었다.

그 결과가 아래 코드이다.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'YourCredentialsId',
                        url: 'https://your-git-repository-url'
                }
            }
        }
        stage('Add Gradle Plugin') {
            steps {
                script {
                    // Gradle 플러그인을 추가할 파일 경로 설정
                    def buildGradleFile = "${workspace}/build.gradle"
                    // 추가할 플러그인 이름 설정
                    def pluginName = 'id "org.sonarqube" version "4.2.1.3168"'

                    // build.gradle 파일을 읽어옴
                    def buildGradle = readFile(buildGradleFile)

                    // 플러그인을 추가할 위치 확인
                    def insertIndex = buildGradle.indexOf("plugins {") + 10

                    // sonarqube 플러그인을 추가
                    buildGradle = buildGradle.substring(0, insertIndex) + "\n    " + pluginName + "\n" + buildGradle.substring(insertIndex)

                    // build.gradle 파일 업데이트
                    writeFile(file: buildGradleFile, text: buildGradle)
                }
            }
        }
        stage('Build') {
            steps {
                sh '''
                ./gradlew sonar \
                  -Dsonar.projectKey=YourProjectKey \
                  -Dsonar.projectName='YourProjectName' \
                  -Dsonar.host.url='http://{SONARQUBE_SERVER}:9000' \
                  -Dsonar.token=sqp_YourToken
                '''
            }
        }
    }
}
```

이렇게 하면 pipeline을 빌드하면 checkout을 받아와서 정적 분석까지 진행한다.

여기에 주기적인 실행을 위해 cron을 추가하려면 stages 부분 위에 triggers를 추가해주면 된다. 최종 코드는 다음과 같다.

```groovy
pipeline {
    agent any

    triggers {
        cron('0 0 * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'YourCredentialsId',
                        url: 'https://your-git-repository-url'
                }
            }
        }
        stage('Add Gradle Plugin') {
            steps {
                script {
                    // Gradle 플러그인을 추가할 파일 경로 설정
                    def buildGradleFile = "${workspace}/build.gradle"
                    // 추가할 플러그인 이름 설정
                    def pluginName = 'id "org.sonarqube" version "4.2.1.3168"'

                    // build.gradle 파일을 읽어옴
                    def buildGradle = readFile(buildGradleFile)

                    // 플러그인을 추가할 위치 확인
                    def insertIndex = buildGradle.indexOf("plugins {") + 10

                    // sonarqube 플러그인을 추가
                    buildGradle = buildGradle.substring(0, insertIndex) + "\n    " + pluginName + "\n" + buildGradle.substring(insertIndex)

                    // build.gradle 파일 업데이트
                    writeFile(file: buildGradleFile, text: buildGradle)
                }
            }
        }
        stage('Build') {
            steps {
                sh '''
                ./gradlew sonar \
                  -Dsonar.projectKey=YourProjectKey \
                  -Dsonar.projectName='YourProjectName' \
                  -Dsonar.host.url='http://{SONARQUBE_SERVER}:9000' \
                  -Dsonar.token=sqp_YourToken
                '''
            }
        }
    }
}
```

> triggers를 설정하고 나면 jenkins에서 아래와 같은 워닝을 띄울 수 있다.
> Spread load evenly by using ‘H 0 \* \* _’ rather than ‘0 0 _ \* \*’
>
> H 를 쓰는게 좋다고 하는데 여기서 H 는 랜덤한 시간을 의미한다. 랜덤한 시간 설정을 통해 작업을 분산시키고 부하를 줄이는 용도라고 한다. 하지만 나는 정해진 시간에 수행되기를 바라기 때문에 수정하지 않았다.

### Typescript 기반 프로젝트를 jenkins 를 통해 동적분석 하기

Typescript도 별 차이는 없다. 직접 수행하던 것을 script를 통해 실행될 수 있도록 작성하면 된다.

말은 쉽지만 직접 작성해보니 크게 두 가지 이슈가 있었어서 공유해본다.

#### node.js 설정하기

처음 Typescript (Javascript) 기반 프로젝트에 대한 파이프라인 스크립트를 실행하면 다음과 같이 나올 것이다.

```
ERROR: Error when running: 'node -v'. Is Node.js available during analysis?
org.sonar.plugins.javascript.nodejs.NodeCommandException: Error when running: 'node -v'. Is Node.js available during analysis?
```

말 그대로 nodejs가 없다는 것이다. 해결하려면 pipeline의 빌드과정에서 node.js를 설정해주면 된다.

pipeline의 빌드과정에서 node.js를 설정하는 방법은 다음과 같다.

1. [node.js 플러그인](https://plugins.jenkins.io/nodejs/)을 설치한다. (플러그인 설치는 jenkins 메인페이지 에서 manage에 들어가면 있는 plugin 관리메뉴에서 할 수 있다.)

2. node.js 플러그인 설치를 마쳤다면 "jenkins 메인페이지 - manage - Tools" 로 이동한다. 해당 페이지의 하단으로 내려보면 node.js 가 추가된 것을 볼 수 있을 것이다.  
   ![nodejs-installation](/assets/images/2023-11-06-sonarqube-with-jenkins/nodejs-installation.png)
   여기서 내가 사용할 node.js 버전 과 이름을 지정한다. (나의 경우에는 버전과 동일하게 이름을 설정했다. 이 이름을 build script 에서 사용하기 때문에 주의하자.)

3. build script의 상단에 `tools {nodejs "YOUR_NODEJS_NAME"}` 를 추가해준다.

이 방법에 따른 pipeline script 는 다음과 같다.

```groovy
pipeline {
    agent any

    tools {nodejs "NodeJS 18.18.2"}
    triggers {
        cron('0 0 * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'YourCredentialsId',
                        url: 'https://your-git-repository-url'
                }
            }
        }
        stage('Build') {
            steps {
                // sonar
                sh """
                /var/jenkins_home/sonar-scanner/bin/sonar-scanner \
                    -Dsonar.projectKey=YourProjectKey \
                    -Dsonar.sources=${workspace} \
                    -Dsonar.host.url=http://{SONARQUBE_SERVER}:9000 \
                    -Dsonar.token=sqp_YourToken
                """
            }
        }
    }
}
```

그리고 위 스크립트에서도 보이지만 sonar-scanner의 경우 jenkins_home 아래에 넣어두었다. 문제없이 잘 동작한다.

## 스케줄러 정상 동작하는지 확인하기

![scheduled-build](/assets/images/2023-11-06-sonarqube-with-jenkins/scheduled-build.png)

다음날 확인해보았더니 잘 동작한다. (다만 timezone 이슈로 0시 0분 으로 설정했지만 9시에 실행되었다.)

직접 jenkins와 sonarqube를 구축하고 자동으로 pipeline build 까지 동작하도록 설정한 경험을 기록해보았다.

끝.
