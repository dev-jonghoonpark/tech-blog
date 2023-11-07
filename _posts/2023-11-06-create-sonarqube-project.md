---
layout: post
title: 소나큐브 프로젝트 설정하고 정적 분석 해보기
categories: [스터디-테스트]
tags:
  [
    Sonarqube,
    소나큐브,
    Java,
    Gradle,
    Binary,
    SonarScanner,
    Scanner,
    Typescript,
    TS,
    Javascript,
    JS,
    code analysis,
    static code analysis,
  ]
date: 2023-11-07 22:00:00 +0900
---

[소나큐브 에 PostgreSQL DB 설정하기 (with PostgreSQL)](/2023/11/07/sonarqube-db-설정하기) 에서 이어지는 글입니다.

---

소나큐브를 세팅했으니 이제 정적 검사를 진행할 프로젝트에 대한 설정을 진행해보자.

## 소나큐브 프로젝트 설정

프로젝트 생성(Create Project)을 눌러보면 다음과 같은 화면이 나온다.

![integration-or-manually](/assets/images/2023-11-06-create-sonarqube-project/integration-or-manually.png)

유명 플랫폼과 연동할 수 있는 기능을 제공해준다. 나는 manually하게 진행하였다.

![create-a-project](/assets/images/2023-11-06-create-sonarqube-project/create-a-project.png)

`display name`은 소나큐브 콘솔에서 볼 수 있는 프로젝트 이름이다.  
`project key`은 소나스캐너(sonar scanner)에서 스캔을 진행할 때 사용하는 값이다.  
`main branch`는 내가 scan을 진행할 branch의 이름이다.
branch의 값을 중간에 바꾸지 못한다. (최근 버전에서는 된다는 것 같기도 한데. 적어도 구버전에서는 안되었고, 이번에 다시 살펴봤을 때도 따로 보이거나 하지는 않는 것 같다.)  
다른 branch를 정적 검사하고 싶다면 새로 sonarqube project를 생성해야 한다.

![project-config-step1](/assets/images/2023-11-06-create-sonarqube-project/project-config-step1.png)

`token name`은 곧 생성할 토큰을 추후에 관리하는데 사용된다. (기본적으로 값이 입력되어 있음.)  
`Expires in`은 생성할 토큰이 언제 만료될 것인지를 나타낸다. 나의 경우에는 만료되지 않도록 하였다.

![project-config-step1-1](/assets/images/2023-11-06-create-sonarqube-project/project-config-step1-1.png)

`sqp_` 로 시작하는 키값이 생성된다. 이 키 값을 잘 보관해주자.

이후 단계에서는 sonar scanner와 관련된 세팅을 진행하는데

sonarqube에서 설정 가능한 프로젝트는

- Maven
- Gradle
- .Net
- Other(for JS, TS, Go, Python, PHP, ...)

으로 나눠지는데

이 글에서는 Gradle과 TypeScript 를 기준으로 설정한 경험을 공유한다. (Typescript뿐 아니라 Maven, Gradle, .Net을 제외한 그 외의 모든 케이스에 해당된다.)

선택한 유형에 따라 가이드를 잘 해주기 때문에 크게 걱정하거나 할 필요는 없다.

### Gradle

![project-config-step2-gradle](/assets/images/2023-11-06-create-sonarqube-project/project-config-step2-gradle.png)

Gradle 프로젝트의 루트에 있는 build.gradle 파일의 plugins 파트에 아래 내용을 추가한다.

```
plugins {
  id "org.sonarqube" version "4.2.1.3168"
}
```

이후 gradlew를 이용하여 sonar scanner를 실행하면 된다.

```
./gradlew sonar \
  -Dsonar.projectKey=YourProjectKey \
  -Dsonar.projectName='YourProjectName' \
  -Dsonar.host.url='http://{SONARQUBE_SERVER}:9000' \
  -Dsonar.token=sqp_YourToken
```

### Typescript (TS)

![project-config-step2-other](/assets/images/2023-11-06-create-sonarqube-project/project-config-step2-other.png)

먼저 os에 맞는 scanner를 다운로드 후 압축해제를 해주면 된다.

[official documentation of the Scanner](https://docs.sonarsource.com/sonarqube/10.2/analyzing-source-code/scanners/sonarscanner/)를 눌러 다운로드 페이지로 이동할 수 있다.

![download-binary](/assets/images/2023-11-06-create-sonarqube-project/download-binary.png)

나는 Linux 64-bit을 다운로드 하였다. 다운로드 링크를 복사하여 curl 명령어를 작성하여 cli 상에서 다운로드 하고 unzip 하였다.

```
curl -o sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip?_gl=1*h1pbks*_gcl_au*MTI2NzAxNjM0Mi4xNjk3NjgyMTUz*_ga*MTM5NzQ5MjQzNi4xNjk3NjgyMTUz*_ga_9JZ0GZ5TC6*MTY5OTI2MTY1MC40LjEuMTY5OTI2MTcyMC42MC4wLjA.
```

unzip 한 후, sonar-scanner는 bin 파일에서 찾을 수 있다. 명령어는 Gradle 때와 큰 차이는 없다. `-Dsonar.sources` 옵션에 차이가 있다. `-Dsonar.sources` 에 내가 정적 검사를 하고 싶은 프로젝트의 경로를 기록해주자.

```
sonar-scanner \
    -Dsonar.projectKey=YourProjectKey \
    -Dsonar.sources=${YOUR_WORKSPACE_PATH} \
    -Dsonar.host.url='http://{SONARQUBE_SERVER}:9000' \
    -Dsonar.token=sqp_YourToken
```

## 결과

위에서 작성한 sonar-scanner를 이용해서 정적 분석을 마쳤다면 다시 소나큐브 콘솔로 돌아가보자. 돌아가면 결과를 볼 수 있다.

![static-code-analysis-result](/assets/images/2023-11-06-create-sonarqube-project/static-code-analysis-result.png)

각 아이템을 눌러 상세 항목을 확인할 수 있다.

---

이렇게 소나큐브 프로젝트 설정 마쳤다.
방금 진행한 코드 정적 검사를 CI/CD를 통해 자동화 할 수 있다면 더 좋을 것이다.
이 부분은 다음 글인 [소나큐브 코드 정적 검사 자동화 하기 (with Jenkins)](/2023/11/07/sonarqube-with-jenkins) 에서 설명한다.
