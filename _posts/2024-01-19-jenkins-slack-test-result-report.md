---
layout: "post"
title: "jenkins pipeline 빌드 결과 슬랙으로 노티피케이션 전송하기"
description: "Jenkins Pipeline에서 빌드 결과를 Slack으로 노티피케이션 전송하는 방법을 다룹니다. Slack Notification\
  \ Plugin을 사용하여 메시지를 전송하고, Gradle 테스트 결과를 정리하여 슬랙에 전송하는 과정을 설명합니다. 멀티쓰레드 환경에서의 워크\
  스페이스 관리, Gradle 플러그인 추가, 한글 깨짐 문제 해결법, Regex를 활용한 데이터 추출 방법도 포함되어 있습니다. 최종적으로 빌드\
  \ 성공 및 실패 시 Slack에 알림을 보내는 코드를 제공합니다."
categories:
- "개발"
- "스터디-테스트"
- "스터디-자동화"
tags:
- "jenkins"
- "pipeline"
- "slack"
- "bot"
- "notification"
- "workspace"
- "multithread"
- "regex"
date: "2024-01-19 10:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-01-19-jenkins-slack-test-result-report.jpg"
---

어제의 '[jenkins pipeline 에서 데이터베이스 테스트 환경 세팅 자동화하기 (테스트용 데이터베이스 컨테이너 사용)](https://jonghoonpark.com/2024/01/18/automate-test-with-jenkins)' 글에서 이어지는 글입니다.

pipeline 빌드 결과를 슬랙으로 노티피케이션을 보내기 위해서 겪은 이슈들과 최종적인 결과물을 정리해보았습니다.

---

## slack에 notification 보내기

### slack notification plugin

#### 플러그인 소개

[https://plugins.jenkins.io/slack/](https://plugins.jenkins.io/slack/)

\* 삽질하고 싶지 않다면 문서를 꼼꼼하게 읽고 시작하는 것을 추천한다. 나는 한참 헤맸다.

좀 더 풍부한 기능을 사용하고 싶다면 custom bot을 만들어야 한다.  
기본적으로 제공되는 봇으로는 아래의 기능을 사용할 수 없다.

- Threading
- File upload
- Custom app emoji per message
- Blocks

봇은 [slack api](https://api.slack.com/apps) 페이지에서 만들 수 있다.  
봇을 만든 후 권한을 안내에 따라 부여해주면 된다.  
(플러그인 메인 페이지에서 "Creating your app" 부분 참고)

#### pipeline 내에서 사용하는법에 대한 문서

[https://www.jenkins.io/doc/pipeline/steps/slack/](https://www.jenkins.io/doc/pipeline/steps/slack/)

나는 메시지를 보내고 그 이후에 해당 메시지의 쓰레드에 로그 파일을 올리도록 처리하였다.

- slackSend
- slackUploadFile

참고로 jenkins pipeline에서 제공하는 함수에 대한 정보는 아래의 두 문서를 많이 참고하였다.

- [https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/](https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/)
- [https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/)

#### 아무리 해도 나 자신한테 DM이 보내지지 않는다. (channel_not_found)

나한테 보내려 하지 말고 봇의 프로필에 들어가서 대화를 시도해라. 그 채널이 봇이 나에게 연락할 수 있는 채널이다.

평소에 내가 나한테 메모 남기는 채널은 봇이 찾을 수 없는 채널이다.

봇과 대화하려면 message tab 에서 옵션을 켜줘야 한다.  
![message tab](/assets/images/2024-01-19-jenkins-slack-test-result-report/message-tab.png)

## ignore up-to-date checks

gradle 명령어에 `--rerun`를 붙이면 변경사항이 없더라도 task를 수행하게 할 수 있다.

\* `--rerun` 옵션의 경우 gradle 7.6 부터 생김

## gradle test logger plugin 추가하기.

![gradle-test-logger-plugin](/assets/images/2024-01-19-jenkins-slack-test-result-report/gradle-test-logger-plugin.gif)

[gradle-test-logger-plugin](https://github.com/radarsh/gradle-test-logger-plugin)

gradle 테스트에 대한 로그를 깔끔한 포멧으로 생성해준다.

gradle 명령어에 `--console=plain`를 붙이면 ansi-color 문자를 제거할 수 있다. jenkins console의 경우 ansi-color를 지원하지 않아 옵션을 추가해주었다.

해당 플러그인을 사용하는것에 대해서는 크게 반감이 없었지만 prod 코드에 영향을 주고 싶지는 않아서 아래와 같이 동적으로 추가하도록 처리하였다.

```groovy
stage('Add Gradle Plugin') {
    steps {
        script {
            // Gradle 플러그인을 추가할 파일 경로 설정
            def buildGradleFile = "${workspace}/build.gradle"
            // 추가할 플러그인 이름 설정
            def pluginName = "id 'com.adarshr.test-logger' version '4.0.0'"

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
```

[sonarqube 관련해서 세팅할때](/2023/11/07/sonarqube-with-jenkins)도 써먹었던 방식이다.

## jenkins console 한글 깨짐

Jenkins 관리 - System - Global properties - Environment variables 에 가서

- 이름(key) : `JAVA_TOOL_OPTIONS`
- 값(value) : `-Dfile.encoding=UTF-8`

등록.

## groovy에서 regex로 원하는 데이터 추출하기

내가 추출하기 원하는 데이터는 테스트에 대한 요약 정보였다. 다음과 같은 형태를 띄고 있으며 빌드 로그 중간에 나오게 된다.

```
SUCCESS: Executed 123 tests in 1m 24s
FAILURE: Executed 125 tests in 1m 36s (1 failed, 1 skipped)
```

다음과 같이 regex를 작성해서 데이터를 추출하였다.

```groovy
def resultPattern = /(SUCCESS|FAILURE): (.*)/
def matcher = (testResult =~ resultPattern)
if (matcher.find()) {
    testSummary = "${matcher[0][0]}"
}
```

## 멀티쓰레드 환경에서의 workspace

pipeline script 내에서 `env.WORKSPACE` 를 통해 워크스페이스 경로를 받아올 수 있다.
그런데 메인 스레드가 아닌 다른 스레드에서 `env.WORKSPACE` 값을 호출하면 값이 조금 다르다.

예를 들어서 나의 경우에는 처음 workspace 경로는 `/var/jenkins_home/workspace/integration-test` 이다.
하지만 중간에 호출 되는 다른 agent에서는 `/var/jenkins_home/workspace/integration-test@2` 가 workspace 경로가 된다.

따라서 내가 처리해야하는 파일이 어느 workspace 저장/호출되는지 확인하는 것이 중요하다.

## 마무리

최종적으로 파이프라인이 빌드 될 때마다 슬랙으로 아래와 같이 메시지가 오게 처리하였다.

![slack notification example](/assets/images/2024-01-19-jenkins-slack-test-result-report/slack-notification-example.png)

최종 코드는 다음과 같다.

```groovy
def _workspace
def testSummary

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
                            _workspace = pwd();
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
                stage('Add Gradle Plugin') {
                    steps {
                        script {
                            // Gradle 플러그인을 추가할 파일 경로 설정
                            def buildGradleFile = "${workspace}/build.gradle"
                            // 추가할 플러그인 이름 설정
                            def pluginName = "id 'com.adarshr.test-logger' version '4.0.0'"

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
                stage ('run integration test') {
                    steps {
                        script {
                            docker.image('mysql:8.0.33')
                                .withRun('--network {NETWORK_NAME}'
                                + ' -e MYSQL_ROOT_PASSWORD={YOUR_PASSWORD}'
                                + ' -e MYSQL_DATABASE={YOUR_DATABASE}') { c ->

                                // Wait until mysql is up
                                sh "while ! docker exec ${c.id} mysqladmin --user=root --password={YOUR_PASSWORD} --host '127.0.0.1' ping --silent ; do sleep 5; done;"

                                // integrationTest는 커스텀 task이다.
                                def testResult = sh(returnStdout: true, script: "GRADLE_USER_HOME=./.gradle DATASOURCE_HOST=${c.id.substring(0,12)} DATASOURCE_PORT=3306 ./gradlew integrationTest --rerun --console=plain")

                                // jenkins 로그상에도 기록하고 싶어서 echo 처리
                                echo "${testResult}"

                                // 테스트 결과 로그를 txt 파일로 저장 (이후에 slack으로 보내줄 것임)
                                writeFile file: 'test-result.txt', text: "${testResult}", encoding: "UTF-8"

                                // 테스트 한줄 summary 추출 (이후에 slack으로 보내줄 것임)
                                def resultPattern = /(SUCCESS|FAILURE): (.*)/
                                def matcher = (testResult =~ resultPattern)
                                if (matcher.find()) {
                                    testSummary = "${matcher[0][0]}"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

  post {
    success {
        script {
            def blocks = [
            	[
            		"type": "section",
            		"text": [
            			"type": "mrkdwn",
            			"text": "Build success - integration-test (<${env.BUILD_URL}|Open>)\n${testSummary}"
            		]
            	],
            ]

            def attachments = [
                [
                    "color": "#2db372",
                    "blocks": blocks
                ]
            ]

            def slackResponse = slackSend(
                channel: env.SLACK_CHANNEL,
                attachments: attachments
            )

            // 혹시나 workspace에 이전 실행을 통해 생긴 파일이 있을까 싶어 제거 시도 후 복사
            // 복사를 하는 이유는 slackUploadFile 가 다른 workspace에 접근할 수 없는 구조로 되어있어서임.
            sh "rm -f ${env.WORKSPACE}/test-result.txt"
            sh "cp ${_workspace}/test-result.txt ${env.WORKSPACE}/test-result.txt"
            slackUploadFile(channel: slackResponse.threadId, filePath: "test-result.txt", initialComment:  "integration test result log")
        }
    }
    failure {
        script {
            def blocks = [
            	[
            		"type": "section",
            		"text": [
            			"type": "mrkdwn",
            			"text": "Build failure - integration-test (<${env.BUILD_URL}|Open>)\n${testSummary}"
            		]
            	],
            ]

            def attachments = [
                [
                    "color": "#b3312d",
                    "blocks": blocks
                ]
            ]

            slackSend(
              channel: env.SLACK_CHANNEL,
              attachments: attachments
            )
        }
    }
  }
}
```
