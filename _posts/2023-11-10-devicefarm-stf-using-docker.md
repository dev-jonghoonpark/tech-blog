---
layout: post
title: 디바이스팜 STF 설치해보기 (with docker)
categories: [개발, 스터디-테스트]
tags: [테스트, 디바이스팜, 안드로이드, stf, iOS, MacOS, 아이폰, 모바일]
date: 2023-11-10 21:30:00 +0900
---

QA 업무를 하면서 디바이스팜 이라는 단어를 알게 되었다.  
디바이스 팜은 테스트를 수행할 디바이스를 관리하고 디바이스 자원 활용을 효율화하는 플랫폼이다.

내가 관심있던 프로젝트는 stf 프로젝트인데 line 블로그에서 해당 프로젝트와 관련해서 다룬글이 있다.  
[코로나 시대 원격 QA! 오픈소스 디바이스팜 STF 도입기](https://engineering.linecorp.com/ko/blog/remote-qa-devicefarm-stf)

예전부터 기회가 되면 설치해봐야지 하고 있다가 이번에 개발 서버를 구성해서 이것저것 해보는 김에 한 번 설치를 해보았다.

> 참고로 dogu 라는 팀에서 만드는 [자동화 플랫폼](https://dogutech.io/ko/features/device-farm)에서도 디바이스팜을 제공한다. (이 프로젝트는 올해부터 시작하신 것으로 알고 있다.)

stf의 Requirements 는 다음과 같다.

- Node.js up to 20.x required (some dependencies don't support newer versions)
- ADB properly set up
- RethinkDB >= 2.2
- CMake >= 3.9 (for node-jpeg-turbo)
- GraphicsMagick (for resizing screenshots)
- ZeroMQ libraries installed
- Protocol Buffers libraries installed
- yasm installed (for compiling embedded libjpeg-turbo)
- pkg-config so that Node.js can find the libraries

굉장히 복잡하다.

docker를 사용하면 더 편하게 구축할 수 있다. stf 프로젝트는 standalone 으로 실행 가능하도록 docker-compose 제공한다.
따라서 이 글에서는 docker를 이용하여 스마트팜을 설치한다.

## 설치 및 구성

먼저 curl로 docker-compose 파일을 다운로드 한다.

```
curl -o docker-compose.yaml https://raw.githubusercontent.com/DeviceFarmer/stf/master/docker-compose.yaml
```

다운로드를 마쳤으면 docker-compose.yaml 에서 `YOUR_EMAIL`, `YOUR_NAME`, `YOUR_IP` 를 수정해야 한다. 본인의 상황에 맞게 변경하자.

설정을 마쳤으면 up 하면 된다.

```
docker-compose -f docker-compose.yaml up --detach
```

> `--detach` 옵션을 붙이면 백그라운드에서 실행된다.

정상적으로 띄워졌으면 7100 포트로 접근할 수 있다.

![stf-login-page](/assets/images/2023-11-10-devicefarm-stf-using-docker/stf-login-page.png)

방금 전 docker-compose 에서 설정한 email과 name 으로 로그인을 할 수 있다.

아직 기기를 연결하지 않아 처음에 들어갔을떄는 아무것도 보이지 않았다.

![stf-main-page](/assets/images/2023-11-10-devicefarm-stf-using-docker/stf-main-page.png)

하지만 기기를 연결한 후에도 기기가 stf console에서 보이지 않았다.

이럴 경우에는 기기가 정상적으로 adb server에 연결되었는지 확인해보면 된다.  
host 의 adb가 아닌 docker compose를 통해 띄워진 adb container 에 붙어야 한다.
host의 adb 서버가 실행되어 있을 경우 `adb kill-server` 명령어를 통해 adb 서버를 종료해주면 된다.

정상적으로 adb container의 adb server에 연결되면 기기가 연결된 것을 볼 수 있다.

![stf-main-page-with-device](/assets/images/2023-11-10-devicefarm-stf-using-docker/stf-main-page-with-device.png)

왼쪽 화면에서 기기를 직접 컨트롤 할 수도 있다. 오른쪽 화면에서도 각종 기능들을 제공한다.

![device-control-page](/assets/images/2023-11-10-devicefarm-stf-using-docker/device-control-page.png)

기기를 사용중 일 경우 대시보드에서 busy device로 표시되고 기기목록에서는 사용중으로 표시된다.  
따라서 사용을 한 후에는 사용 해제를 해주면 될 것 같다. 그래도 오래 사용하지 않으면 자동으로 해제되는 것으로 보인다.

![stf-main-page-with-busy-device](/assets/images/2023-11-10-devicefarm-stf-using-docker/stf-main-page-with-busy-device.png)

![device-stop-using](/assets/images/2023-11-10-devicefarm-stf-using-docker/device-stop-using.png)

## 마무리

구축하는 것 자체는 그렇게 어렵지 않았다.  
얼마나 잘 활용하냐가 문제일 것 같다.

어디서나 기기를 확인해서 테스트를 할 수 있다는 것이 장점일 것 같다.

다만 아쉬운 점은 화면이 꺼지면 이후 연결 안된다. 따라서 폰이 계속 켜져있는 상태여야 한다.
개발자 옵션에서 "화면 켜짐 상태 유지" 활성화를 하고 밝기를 최소로 낮춰주는 것이 좋을 것 같다.
![screen-always-on](/assets/images/2023-11-10-devicefarm-stf-using-docker/screen-always-on.png)

실제 기기의 밝기를 낮게 해둬도 stf console 상에서는 영향을 받지 않는다.

추가적으로 기기 컨트롤 페이지에서 adb connect 명령어가 있길래 해봤더니
adb connect 시도를 할 경우 다음과 같이 key를 추가할 것인지 확인하는 팝업이 나왔다.

![adb-connect-key-check.png](/assets/images/2023-11-10-devicefarm-stf-using-docker/adb-connect-key-check.png)

add key 를 하면 사용할 수 있다.

아 그리고 아이폰은 사용이 어렵다는게 아쉬운 점인것 같다. 근데 그 부분은 복잡하긴하지만 되는것으로 보이긴 한다.  
[stf ios support](https://github.com/dryark/stf_ios_support)  
하지만 내용을 보면 알겠지만 MacOS 가 필요하다. 그래서 따로 시도해보지는 않았다. 추후에 필요하다면 시도해 보는 것으로 해야겠다.

끝.
