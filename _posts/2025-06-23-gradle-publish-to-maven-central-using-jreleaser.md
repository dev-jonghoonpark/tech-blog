---
layout: "post"
title: "[Gradle] 내가 만든 라이브러리 maven 에 배포하기 (using JReleaser)"
description:
  "JReleaser를 사용하여 Gradle 기반 프로젝트를 Maven Central에 배포하는 방법을 설명합니다. \
  계정 생성, namespace 등록, GPG 키 생성 및 배포 설정을 포함한 단계별 가이드를 제공하며, GitHub Actions를 통한 자동화 배포 방법도 다룹니다."
categories:
  - "스터디-자바"
tags:
  - "Java"
  - "Gradle"
  - "Maven"
  - "Maven Central"
  - "JReleaser"
  - "GPG Key"
  - "deploy"
  - "publish"
  - "library"
  - "GitHub Actions"
  - "배포"
  - "등록"
date: "2025-06-23 17:00:00 +0900"
toc: true
image:
  path: "/assets/thumbnails/2025-06-23-gradle-publish-to-maven-central-using-jreleaser.jpg"
---

# 내가 만든 라이브러리 maven에 배포하기 (using JReleaser)

## JReleaser

Java 뿐만 아니라 다양한 프로젝트의 Publishing 을 제공하는 도구이다.

이 글에서는 JReleaser 를 통해 Gradle 기반 프로젝트를 Maven Central 에 배포하는 방법에 대해서 알아본다.

### JReleaser 를 선택한 이유

[JReleaser](https://jreleaser.org/) 는 maven central 에서 권장하는 plugin 이다.

![maven central publish plugin list](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/publish-plugin-list.png)

<small><a href="https://central.sonatype.org/publish/publish-portal-gradle/">Publishing By Using a Gradle Plugin</a></small>

사실 처음에는 [gradle-maven-publish-plugin](https://github.com/vanniktech/gradle-maven-publish-plugin) 이라는 도구를 사용해보려고 했다. 프로젝트 레포지토리에 스타가 좀 더 많았고, 설명도 더 자세하다고 느껴졌기 때문이였다.

그러나 하루종일 `Cannot get stagingProfiles for account ***: (401)` 에러에서 벗어날 수 없었다. 이것 저것 시도해보고 검색도 해보았으나, 마땅한 해결책을 찾을수는 없었다.

만약 나처럼 이 에러에서 벗어날 수 없었던 사람이라면 처음부터 `JReleaser` 로 시도해보는것을 추천한다. 바로 해결되었다.

마침 JReleaser 로 배포하는 방법에 대한 글은 한글로 적힌게 없는 것 같아 이 글이 작성해본다.

## Maven Central 에 배포하기

제목에도 적혀있듯, 이 글에서는 Gradle 프로젝트를 Maven Central 에 배포하는 것을 설명한다.
만약 Maven 이나 다른 프로젝트 기반이라면 문서에서 해당 부분을 찾아보길 바란다.

배포를 위한 작업 단계는 다음과 같다.

1. Maven Central Portal
   1. 계정 생성
   2. namespace 등록
   3. User Token 발급
2. GPG key pair 생성
3. GPG public key 배포하기
4. 프로젝트 설정
5. 배포

### Maven Central Portal

#### 계정 생성

참고: [Register to Publish Via the Central Portal](https://central.sonatype.org/register/central-portal)

[https://central.sonatype.com/](https://central.sonatype.com/) 에 들어가 계정을 생성한다.

계정 생성은 간단하니 따로 설명하지는 않는다.

### namespace 등록

참고: [Register a Namespace](https://central.sonatype.org/register/namespace)

groupId 로 사용할 도메인의 소유를 검증하는 단계이다.

`Register New Namespace` 버튼을 누르면 아래 팝업이 나온다.

![register popup](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/register-new-namespace.png)

groupId 로 사용할 도메인을 입력한 후 submit 을 누르면 아래와 같이 목록에 추가된다.

![register list](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/register-a-namespace.png)

Verification Key 를 TXT Record 로 등록해주면 된다. `verify namespace` 버튼을 누르면 자세한 설명이 나온다. TXT Record 등록은 본인의 도메인 관리 플렛폼에서 할 수 있다.

![verify namespace](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/verify-namespace.png)

등록후 얼마 되지 않아, namespace 등록이 마무리 되었다. (1분도 안걸렸다.)

직접 사용할 도메인이 없다면 GitHub, GitLab, Gitee, Bitbucket 과 같은 Code Hosting Service 의 계정도 활용할 수 있는 것으로 보인다. 자세한 내용은 참고 링크의 내용을 확인.

### User Token 발급

참고: [Generating a Portal Token for Publishing](https://central.sonatype.org/publish/generate-portal-token)

[https://central.sonatype.com/account](https://central.sonatype.com/account) 로 이동하여 **Generate User Token** 버튼을 눌러 User Token 을 생성한다.

![user token generation page](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/user-token-generation-page.png)

버튼을 누르면 아래와 같이 팝업이 나오는데 `username` 과 `password` 를 잘 복사해둔다. 참고로 팝업은 자동으로 1분 후에 닫힌다. 다른 곳에 잘 복사해두자.

![generated user token](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/generated-user-token.png)

### GPG key pair 생성

참고: [Working With GPG](https://central.sonatype.org/publish/requirements/gpg/)

먼저 GnuPG 를 설치해준다.
Maven Central 문서에서는 [GnuPG 의 공식 문서](https://gnupg.org/download/index.html#sec-1-2)를 소개해주는데, brew 에도 있길래 나는 brew 로 다운로드 하였다.

```sh
brew install gnupg
```

gnupg 가 설치되었다면 아래 명령어로 key 를 생성한다.
**이름** 과 **이메일** 을 입력한 후, **비밀번호(passphrase)** 를 입력하는데, 이 비밀번호는 잘 기억해두자.

```sh
gpg --gen-key
```

키 생성을 마치면 아래와 같은 나올 것이다.

```
pub   rsa3072 2021-06-23 [SC] [expires: 2023-06-23]
      CA925CD6C9E8D064FF05B4728190C4130ABA0F98
uid                      Central Repo Test <central@example.com>
sub   rsa3072 2021-06-23 [E] [expires: 2023-06-23]
```

참고로 `rsa3072` 가 아니여도 문제 없다. 나의 경우에는 `ed25519/cv25519` 이 사용되었다.

### GPG public key 배포하기

참고: [Distributing Your Public Key](https://central.sonatype.org/publish/requirements/gpg/#distributing-your-public-key)

public key를 key server에 배포하여, 내 private key 를 검증하는데 사용할 수 있도록 한다. 아래 명령어를 통해서 배포한다.

```sh
gpg --keyserver keys.openpgp.org --send-keys CA925CD6C9E8D064FF05B4728190C4130ABA0F98
```

문서에서는 아래 3개의 key server 를 소개해주는데, `keys.openpgp.org` 외에는 잘 동작하지 않았다. 수동으로 keyserver에 직접 접속하여 등록하는 방법도 있긴 하다.

- keys.openpgp.org
- keyserver.ubuntu.com
- pgp.mit.edu

한 곳에만 등록해도 된다고 하니 참고하자.

### 프로젝트 설정

참고: [Publising to Maven Central - Gradle](https://jreleaser.org/guide/latest/examples/maven/maven-central.html#_gradle)

build.gradle 에 아래 내용을 추가하고 본인의 상황에 맞게 변경한다.

```groovy
publishing {
    publications {
        maven(MavenPublication) {
            groupId = 'com.acme'
            artifactId = 'app'

            from components.java

            pom {
                name = 'app'
                description = 'Sample application'
                url = 'https://github.com/aalmiray/app'
                inceptionYear = '2021'
                licenses {
                    license {
                        name = 'Apache-2.0'
                        url = 'https://spdx.org/licenses/Apache-2.0.html'
                    }
                }
                developers {
                    developer {
                        id = 'aalmiray'
                        name = 'Andres Almiray'
                    }
                }
                scm {
                    connection = 'scm:git:https://github.com/aalmiray/app.git'
                    developerConnection = 'scm:git:ssh://github.com/aalmiray/app.git'
                    url = 'http://github.com/aalmiray/app'
                }
            }
        }
    }

    repositories {
        maven {
            url = layout.buildDirectory.dir('staging-deploy')
        }
    }
}

jreleaser {
    signing {
        active = 'ALWAYS'
        armored = true
    }
    deploy {
        maven {
            mavenCentral {
                sonatype {
                    active = 'ALWAYS'
                    url = 'https://central.sonatype.com/api/v1/publisher'
                    stagingRepository('target/staging-deploy')
                }
            }
        }
    }
}
```

예시는 다음과 같다

<script src="https://emgithub.com/embed-v2.js?target=https%3A%2F%2Fgithub.com%2Fdev-jonghoonpark%2Fspring-http-logger%2Fblob%2Fmain%2Fmaven-publishing.gradle&style=default&type=code&showBorder=on&showLineNumbers=on&showFileMeta=on&showFullPath=on&showCopy=on"></script>

#### config.toml 설정하기

`~/.jreleaser/config.toml` 파일을 생성하여 아래 내용을 입력한다. 본인이 위에서 설정한 데이터들을 잘 입력해주면 된다. `~/.jreleaser` 디렉토리가 없다면 디렉토리 생성 후, 파일을 생성해주면 된다.

```toml
JRELEASER_MAVENCENTRAL_USERNAME = "<your-publisher-portal-username>"
JRELEASER_MAVENCENTRAL_PASSWORD = "<your-publisher-portal-password>"
JRELEASER_GPG_PASSPHRASE = "<your-pgp-passphrase>"

JRELEASER_GPG_PUBLIC_KEY="""-----BEGIN PGP PUBLIC KEY BLOCK-----

<contents-of-your-public-key>

-----END PGP PUBLIC KEY BLOCK-----"""

JRELEASER_GPG_SECRET_KEY="""-----BEGIN PGP PRIVATE KEY BLOCK-----

<contents-of-your-private-key>

-----END PGP PRIVATE KEY BLOCK-----"""
```

`JRELEASER_MAVENCENTRAL_USERNAME`, `JRELEASER_MAVENCENTRAL_PASSWORD` 는 Meven Central Portal 에서 발급한 User Token 정보를 입력해주면 된다.

`JRELEASER_GPG_PASSPHRASE` 는 `GPG key pair 생성` 시 사용한 비밀번호(passphrase)를 입력해주면 된다.

`JRELEASER_GPG_PUBLIC_KEY`, `JRELEASER_GPG_SECRET_KEY` 는 아래 명령어를 통해 `public.pgp`, `private.pgp` 파일을 추출한다.
이후 추출된 파일의 내용을 옮겨서 넣어주면 된다. (내용을 어떻게 봐야 하는지 모른다면 `cat` 명령어를 사용하면 된다. ex. `cat public.pgp`)

username@email 의 경우 `GPG key pair 생성` 시 사용한 email 주소를 넣어주면 된다.

```
$ gpg --output public.pgp --armor --export username@email
$ gpg --output private.pgp --armor --export-secret-key username@email
```

문서에 있는 `NEXUS2` 관련 값은 현재 하고자 하는 작업과 관련이 없어 따로 설정하지 않고 제외하였다.

#### Github Token 설정 관련

환경변수 설정 시에 github publication이 기본적으로 활성화 되어있다.
필요하지 않다면 `disable` 시켜주거나, `JRELEASER_GITHUB_TOKEN` 환경변수를 설정해주자.
(둘 중 하나를 하지 않으면 배포 중 에러가 발생될 것이다.)

```groovy
jreleaser {
  release {
    github {
      enabled = false
      ...
```

참고: https://jreleaser.org/guide/latest/reference/release/github.html

> 나는 진행하면서 이 부분을 몰랐어서, 나는 Maven Central 배포만 성공하고, Github Release 에는 배포되지 않은 상황이 발생되었다. Github에는 수동으로 등록해도 문제는 없으니 걱정하지는 말자.

### 배포

1\. configuration 검사

```sh
./gradlew jreleaserConfig
```

2\. clean (optional)

의도하지 않은 다른 파일이 배포에 포함 들어가지 않도록 clean 을 해준다.

```sh
./gradlew clean
```

3\. 로컬 디렉토리에 배포 준비

```sh
./gradlew publish
```

4\. 배포

```sh
./gradlew jreleaserFullRelease
```

## Github action workflow 작성하기

위에서 `./gradlew jreleaserFullRelease` 를 수행하면 배포가 진행될 것이지만, 나는 **github action** 에서 트리거 하기를 원하였기 때문에 조금 더 진행하보았다.

이 때 문제는 config.toml 파일과 관련된 처리였는데, github action 에서는 secret 으로 파일을 직접 설정할 수는 없기 때문에 파일의 내용을 base64 로 encoding 하여 환경변수에 넣은 후, github action 이 수행될 때 decode 하여 파일을 생성하는 방향으로 진행하였다.

```sh
cat .jreleaser/config.toml | base64
```

위에서 나온 값을 github project 에 secret 환경 변수로 넣어준다. 나는 `JRELEASER_CONFIG_BASE64` 라는 key 로 등록했다.

이후 다음과 같이 workflow 를 작성하여 등록하였다.

```yaml
name: publish to maven central

on:
  workflow_dispatch:

permissions:
  deployments: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout sources
        uses: actions/checkout@v4
      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: "temurin"
          java-version: 17
      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4
      - name: create config file from secret env
        run: |
          mkdir ~/.jreleaser
          echo ${{ secrets.JRELEASER_CONFIG_BASE64 }} | base64 --decode > ~/.jreleaser/config.toml
      - name: Validate jreleaser config
        run: ./gradlew jreleaserConfig
        env:
          JRELEASER_GITHUB_TOKEN: ${{ secrets.JRELEASER_GITHUB_TOKEN }}
        continue-on-error: false
      - name: Stage artifacts to a local directory
        run: ./gradlew publish
        continue-on-error: false
      - name: Publish to Maven Central
        run: ./gradlew jreleaserFullRelease
        env:
          JRELEASER_GITHUB_TOKEN: ${{ secrets.JRELEASER_GITHUB_TOKEN }}
        continue-on-error: false
```

Github Token 의 경우, action 내에서 변수로 자체 제공되는 GITHUB_TOKEN 변수도 있지만, jreleaser 에서는 사용자가 직접 주입해주는 것을 권장하고 있다. 배포시 제약이 있단다. 그래서 `JRELEASER_GITHUB_TOKEN` 이라는 추가 환경 변수를 사용하였다.

[jreleaser 공식 github action](https://github.com/marketplace/actions/jreleaser) 도 있지만 나는 직접 gradle task 를 수행하는 방식을 선택하였다.

`workflow_dispatch` 로 설정하였기 때문에, github action 페이지에 들어가서 수동 트리거를 하면 된다.

## 라이브러리 소스코드

완성된 라이브러리의 소스 코드는 [spring-http-logger](https://github.com/dev-jonghoonpark/spring-http-logger) 에서 확인해볼 수 있다.

## 배포후 정상 동작 확인

이 라이브러리를 배포하고 싶었던 이유는 다음과 같다.

Spring AI 에 등록된 issue 들을 보면 종종 http 통신 중 에러가 발생되는데, 그 에러가 왜 발생되는것인지 에러 로그만으로는 파악하기 어려운 경우가 종종 있다. 이 때 HTTP 통신에 사용된 request/response 원본을 확인해보고 싶은 경우가 있는데 Spring AI 자체 기능으로는 추적하기 어려운 경우가 있다. `SimpleLoggerAdvisor` 라는 `Advisor` 를 통한 데이터 접근을 제공하긴 하나, http 요청 자체를 볼 수 있다기 보다는 인스턴스의 변수값을 볼 수 있는 것에 가까워, 제한적인 정보만 습득할 수 있다. 이럴 때 http 통신 자체를 올려줄 수 있는지 설명과 함께 답변을 남기곤 하는데 좀 더 간단하게 접근할 수 있다면 좋을 것 같다는 생각으로 라이브러리로 만들었다.

간단한 Spring AI 프로젝트에 `build.gradle` 에 라이브러리 dependency를 추가한 뒤 적용하여 보았다.

```groovy
implementation 'com.jonghoonpark:spring-http-logger:1.0.0'
```

```java
OpenAiApi openAiApi = OpenAiApi.builder()
        .restClientBuilder(
            RestClient.builder()
              .requestInterceptor(new ClientLoggerRequestInterceptor())
        )
        .apiKey("OPENAI_API_KEY")
        .build();

var chatModel = OpenAiChatModel.builder().openAiApi(openAiApi).build();

ChatResponse response = chatModel.call(
    new Prompt("Generate the names of 5 famous pirates."));
```

배포한 라이브러리에서 제공하는 `ClientLoggerRequestInterceptor` 를 import 후, 생성하여 `RestClient` 에 interceptor 로 추가하여주었다.

실행해보면 다음과 같이 request/response body 값이 콘솔에 출력되는것을 확인해볼 수 있다.

![logging example](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/logging-example.png)

## 기타

![new version released with cause](/assets/images/2025-06-23-gradle-publish-to-maven-central-using-jreleaser/release-with-caution.png)

마침 내가 장애를 겪었던 어제, 새로운 버전이 배포되었다. 내가 겪었던 에러가 해결되었을지는 모르겠다.

> 참고로 [github docs 에서 소개하는 방식](https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-java-packages-with-maven) 은 문서에도 적혀있지만 옛날(legacy) 방식이다.

> [오픈소스 라이브러리 Maven Central에 배포하기](https://cares-log.tistory.com/40#Maven%20Central%20Repository%EC%97%90%20%EB%B0%B0%ED%8F%AC%ED%95%98%EA%B8%B0-1) : `gradle-maven-publish-plugin` 를 사용한 글이지만, 겹치는 부분들이 많다. 설명이 잘 되어있으니 막힌다면 참고하면 좋을 것 같다.

## 마무리

이번 글에서는 JReleaser를 활용하여 Gradle 기반의 프로젝트를 Maven Central에 배포하는 과정을 자세히 다뤄보았다. 이 글이 Maven Central 배포 과정에서 어려움을 겪는 분들에게 도움이 되었길 바란다. 🚀
