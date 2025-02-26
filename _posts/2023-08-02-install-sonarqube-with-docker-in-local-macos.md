---
layout: "post"
title: "소나큐브 설치하기 (with Docker, macOS)"
description: "macOS에서 Docker를 이용해 SonarQube를 설치하는 방법을 설명합니다. SonarQube는 정적 코드 분석을\
  \ 통해 코드 품질을 지속적으로 검토하는 오픈 소스 플랫폼입니다. 이 글에서는 Docker 이미지를 pull하고 실행한 후, 웹 콘솔에 접속하여\
  \ 기본 설정을 진행하고 Bitbucket과 연동하는 과정을 다룹니다. 또한, 프로젝트 분석을 위한 SonarScanner 설치와 환경 변수 설\
  정 방법도 안내합니다. 마지막으로, 기본 데이터베이스로 H2를 사용하며, 필요에 따라 다른 데이터베이스로 변경할 수 있는 옵션도 소개합니다."
categories:
- "개발"
- "스터디-테스트"
tags:
- "테스트"
- "testing"
- "macos"
- "sonarqube"
- "정적 테스트"
- "docker"
- "bitbucket"
- "소나큐브"
date: "2023-08-01 16:32:14 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-08-02-install-sonarqube-with-docker-in-local-macos.jpg"
---

## 개요

최근에 devops 님께 3개의 sonarqube 프로젝트를 생성해달라는 요청을 드렸었다.  
devops 님께는 항상 감사한 마음을 가지고 있다. 참 수고가 많으신 것 같다.

요청 드린것은 요청 드린 것이고 한번쯤은 직접 어떤 과정을 통해 진행되는지 확인해보고 싶었다.

참고로 소나큐브는

> 20개 이상의 프로그래밍 언어에서 버그, 코드 스멜, 보안 취약점을 발견할 목적으로 **정적 코드 분석**으로 자동 리뷰를 수행하기 위한 지속적인 코드 품질 검사용 오픈 소스 플랫폼이다

라고 위키피디아에 소개되어있다.

## 본문

### 설치 환경

이 글에서는 Docker를 이용해서 설치하며, 로컬에 설치하기 때문에 macOS 를 기반으로 설명을 진행한다.

### 진행 순서

#### 1. 도커 이미지 pull & run

공식홈페이지에 이미지에 따른 pull 명령어가 정리되어 있다.  
[https://www.sonarsource.com/products/sonarqube/deployment/](https://www.sonarsource.com/products/sonarqube/deployment/)

나는 커뮤니티 버전을 사용할 예정이기 때문에 아래와 같은 명령어로 이미지를 받아왔다.

```
docker pull sonarqube:10.1.0-community
```

다운로드(pull)가 다 되었으면 실행시키면 된다.

소나 큐브는 웹 콘솔이 있는데 9000 포트를 기본적으로 사용하는 것으로 확인되었다.  
[https://github.com/SonarSource/sonar-.net-documentation/blob/master/doc/installation-and-configuration.md](https://github.com/SonarSource/sonar-.net-documentation/blob/master/doc/installation-and-configuration.md)  
그래서 port forwarding 옵션과 함께 실행시켜 주었다.

```
docker run -d --name sonarqube -p 9000:9000 sonarqube
```

참고로 d 옵션은 아래와 같은 의미이다.

\-d : detached

> **\[Note\]**
> Docker가 실행되지 않고 있다면 아래와 같은 에러가 발생된다.  
> Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?  
> App 에 들어가서 도커(데스크탑)을 gui로 실행 해줘도 되겠지만 이미 cli에 들어와 있는 상태이니 명령어로 실행시켜주자.  
> open -a Docker

#### 2. 웹 콘솔 접속하기

아무튼 성공적으로 실행이 되면 브라우저에서 localhost:9000 로 접속해주면 된다.

처음 접속하면 세팅을 진행하는데 기다리면 로딩 후 로그인 화면이 나온다.  
기본 계정 정보는 admin/admin 이다. (document 도 안찾아보고 그냥 때려봤는데 맞았다.)

섬세하게 기본 비밀번호를 변경하도록 유도해주니 적당히 변경해주자.

#### 3. Git 서비스 계정 연동하기

로그인 이후의 메인 화면은 다음과 같다.

아직 연결된 프로젝트가 하나도 없는 첫 접속상태라 그런지 친절하게 어떤 서비스 연결할것인지 물어본다.

![choose-how-to-setup](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/choose-how-to-setup.png)

우리 회사는 bitbucket을 쓰고 있기 때문에 bitbucket을 기준으로 설명을 한다.  
repository와 굳이 연결하지 않아도 된다 싶으면 Manually 을 선택하면 되는 것으로 보인다.

중간중간에 필요한 설명들을 잘 적어두었기 때문에 놓치지 않고 꼼꼼히 잘 읽으면 한번에 진행할 수 있다.

![config-with-bitbucket-cloud](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/config-with-bitbucket-cloud.png)

OAuth Key 발급과 관련해서는 파란색 부분에 잘 적혀있다.  
[https://support.atlassian.com/bitbucket-cloud/docs/use-oauth-on-bitbucket-cloud/](https://support.atlassian.com/bitbucket-cloud/docs/use-oauth-on-bitbucket-cloud/)

bit bucket 페이지에서 우측 상단의 프로필 버튼을 누르면 아래와 같은 드롭다운 메뉴가 나오게 된다.

여기서 All workspaces 를 클릭하자.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image3.png)

그러면 내가 접근 가능한 워크스페이스 목록을 볼 수 있다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image4.png)

여기서 회사 워크스페이스의 경우에는 내가 수정할 권한이 없기 때문에 Manage 버튼이 보이지 않았다.  
그래서 진행 가능한 개인 계정으로 진행하였다.

Manage 버튼을 누르면 아래같은 화면이 나오게 되는데 좌측 메뉴에서 아래로 내려가 OAuth consumers 메뉴를 클릭한다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image5.png)

Add Consumer 를 해준다.

![choose-how-to-setup](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/choose-how-to-setup.png)

![bitbucket-oauth-consumer-list](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/bitbucket-oauth-consumer.png)

아래와 같은 입력폼이 나오는데 위에서 본 설명을 참고해서 작성하면 된다.

![bitbucket-add-oauth-consumer](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/bitbucket-add-oauth-consumer.png)

![permissions](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/permissions.png)

- Name 체크

- Callback URL 입력 (sonarqube에서 callback을 사용하지는 않지만 입력해야 한다고 명시되어 있다. 입력하지 않으면 중간 과정에서 막히기 때문에 아무 주소나 입력하면 된다. 작성자의 경우에는 그냥 블로그 주소를 적었다. [https://jonghoonpark.com](https://jonghoonpark.com))

- This is private consumer 체크

권한은 Pull Requests: Read 만 체크 하면 된다.  
Repositories: Read 도 필요하지 않을까 했는데 Pull Requests: Read 를 하면 자동으로 선택 되었다.

이후 저장을 하면 아래와 같이 키 값과 시크릿 값이 생성이 된다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image9.png)

이 키 값과 시크릿 값을 다시 소나큐브로 돌아가서 입력하면 된다.

> \[Note\]
>
> Callback을 입력하지 않으면 이렇게 에러가 나서 진행이 막히게 된다.
>
> ![no-callback-url](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/no-callback-url.png)

다음 단계로 넘어왔는데 또 뭘 입력하라고 한다.

![onboarding](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/onboarding.png)

여기서 주의할 점은 app password다. 일반적인 password가 아니다.

우측에 힌트를 참고해서 생성해주면 된다.  
[https://bitbucket.org/account/settings/app-passwords/new](https://bitbucket.org/account/settings/app-passwords/new)

이번에는 Repositories: Read 권한이 있으면 된다.

![add-app-password](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/add-app-password.png)

Create 하면 아래와 같이 app password 가 생성된다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image13.png)

한번만 볼 수 있다니 잘 저장해두자.

생성된 app password로 로그인을 하면 프로젝트 목록이 가져와진다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image14.png)

(회사랑 관련된 프로젝트들이라 이름을 가렸다)

원하는 프로젝트에 Set up 버튼을 클릭하자.

#### 4\. 프로젝트 분석하기

프로젝트 Set up 버튼을 누르면 아래와 같이 프로젝트 페이지가 생성되고

마찬가지로 생성후 첫 접속이기 때문에 어떻게 분석을 처리할지에 대해서 물어본다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image15.png)

우리 회사는 Jenkins를 사용한다.

다만 개인적인 테스트 용도로 하는 것이기 때문에 Locally를 선택하였다.

![create-sonarqube-project](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/create-sonarqube-project.png)

토큰을 생성해주라고 해서 대충 생성해주었다.

Generate를 누르면 아래와 같이 토큰이 생성되는데 굳이 기억하거나 어디에 옮겨 적을 필요는 없다. 바로 다음에 나온다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image17.png)

이후에 어떻게 수동으로 분석을 할지에 대해서 환경에 따라 설명을 해주니 본인의 환경에 맞게 선택하면된다.

작성자의 경우에는 TS, macOS 여서 그렇게 선택하였다.

![](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/image18.png)

로컬에서 실행하려면 SonarScanner 라는걸 설치해야 하는 모양이다.

![download-sonar-scanner-binary](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/download-sonar-scanner-binary.png)

다운로드 해서 적당한 위치에 풀어주고 환경변수에 추가해주면 된다.

작성자의 경우에는

vim .zshrc 에  
export PATH="$PATH:/Users/dev-jonghoonpark/dev/sonar-scanner/bin"  
추가 후  
source ~/.zshrc  로 적용하였다.

환경변수 설정이 정상적으로 되었다면 이후 위에서 나온 명령어를 입력해주면 분석이 진행 된다.

명령어를 입력할 때는 아무데서나 실행하면 안되고 **해당 프로젝트의 경로에서 실행**시켜줘야 했다.  
나는 repository와도 연동 했으니깐 그냥 아무데서나 실행해도 될꺼라고 생각해서 막 했는데 착오였다.

> \[Note\]
>
> 분석을 실행하였는데 “개발자를 확인할 수 없기 때문에 ‘java’을(를) 열 수 없습니다.” 라고 나와서
>
> 설정 - 보안 및 개인 정보 보호 로 가서
>
> ![apple-security-setting](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/apple-security-setting.png)
>
> “확인 없이 허용” 을 눌러 허용 해주었다.
>
> TMI : Java는 asdf 로 세팅되어있다.

![sonarqube-project-main](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/sonarqube-project-main.png)

따로 설정 없이 기본 값으로 분석해본 것 이기에 일단은 별 문제 없는 것으로 나왔다.

제대로 된 코드와 제대로 된 sonaqube 설정을 해주면 제대로된 결과가 나올 것이다.

일단 여기까지 알아보는 것이 목적이였기 때문에 여기 까지만 작성해본다.

> **\[Note\]**
>
> ![database-warning](/assets/images/2023-08-02-install-sonarqube-with-docker-in-local-macos/database-warning.png)
> 추가적으로 진행을 하다보면 하단에 임베디드 데이터베이스에 대한 워닝이 나온다.
>
> [https://hub.docker.com/\_/sonarqube](https://hub.docker.com/_/sonarqube)  
> 도커 문서를 보니 기본 값으로 H2 database를 embedded database로 사용하고 있다는것 같다.  
> 설치 가능한 Database로는 MSSQL 과 Oracle 과 PostgreSQL을 제공한다.
>
> [https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/](https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/)  
> 본인의 인프라 환경에 따라 세팅하면 될 것 같고  
> Supabase 에서 PostgreSQL을 무료로 제공 받을 수 있는것으로 알고 있어서 궁금하면 연결해봐도 좋을 것 같다.  
> 여기서는 Sonarqube를 실행시켜보는것이 주 목적이기 때문에 Embedded Database로 그냥 진행하였다.

끝.
