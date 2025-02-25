---
layout: post
title: jekyll 에 PWA 적용하기
description: Jekyll에 PWA를 적용하는 방법을 설명하며, jekyll-pwa 플러그인을 설치하고 설정하는 과정을 다룹니다. manifest.json과 service-worker.js 파일을 수동으로 설정하여 PWA 기능을 활성화하고, 최종적으로 Lighthouse에서 PWA 관련 만점을 받을 수 있는 방법을 안내합니다.
categories: [개발, 블로그]
tags:
  [
    블로그,
    깃헙,
    깃헙페이지,
    지킬,
    Jekyll,
    PWA,
    Lighthouse,
    Cache,
    workbox,
    플러그인,
  ]
date: 2023-10-01 17:30:00 +0900
---

# PWA plugin 설치하기

수동으로 직접 세팅하는 것보다는 플러그인을 사용하는게 편할 것이기 때문에
[jekyll-pwa](https://github.com/lavas-project/jekyll-pwa)를 사용한다.

jekyll 프로젝트의 Gemfile에 `gem 'jekyll-pwa-plugin'` 을 추가한다.
이후 `bundle` 명령어를 실행시키면 플러그인을 설치할 수 있다.

> 설치 후 빌드시 아래 이슈와 같은 증상이 있었어서 나는 그냥 낮은 버전을 사용했다.  
> [block in <module:Jekyll>](https://github.com/lavas-project/jekyll-pwa/issues/39)  
> (이슈는 클로즈 된 것 같은데 버전을 낮추는 것 외에는 딱히 해결방법은 보이지 않았다. pwa 사용에는 문제가 없으므로 깊게 파지는 않았다. workbox 라이브러리를 업데이트 하면서 충돌이 있는것으로 보인다.)
>
> 진행중에 동일한 증상이 있다면 아래와 같이 버전 명시를 추가해주고  
> `gem 'jekyll-pwa-plugin', "= 2.2.3"`  
> 다시 `bundle` 명령어를 통해 해당 라이브러리를 재설치 해주자.

\_config 의 plugins 에 설치된 jekyll-pwa-plugin을 추가해주자.

```yml
plugins:
  - ...
  - jekyll-pwa-plugin
```

# 수동 설정

수동으로 설정해 줘야 하는 부분들이 꽤 있다.

## manifest.json 설정해주기

manifest의 각 항목에 대해서 궁금하다면

- [mdn](https://developer.mozilla.org/ko/docs/Mozilla/Add-ons/WebExtensions/manifest.json)
- [web.dev](https://web.dev/add-manifest/)

를 참고하자

나의 경우에는 다음과 같이 만들었다.  
이 코드는 최소한으로 필요한 부분들만 설정한 것이며 해당 파일은 프로젝트 루트에 둬야 한다.

```json
{
  "short_name": "박종훈 기술블로그",
  "name": "박종훈 기술블로그",
  "id": "/",
  "start_url": "/",
  "description": "박종훈 기술블로그 - 공부하고 경험한 것을 기록합니다",
  "icons": [
    {
      "src": "/assets/icons/icons-192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "/assets/icons/icons-192-maskable.png",
      "type": "image/png",
      "sizes": "192x192",
      "purpose": "maskable"
    },
    {
      "src": "/assets/icons/icons-512.png",
      "type": "image/png",
      "sizes": "512x512"
    },
    {
      "src": "/assets/icons/icons-512-maskable.png",
      "type": "image/png",
      "sizes": "512x512",
      "purpose": "maskable"
    }
  ],
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#070707"
}
```

### id, start_url

처음 접속했을 때 나와야 하는 경로를 지정해주면 됩니다.
저의 경우 '/' 이기 때문에 '/'로 지정해줬으며, query param이나 hash를 추가해야 한다면 추가하시면 됩니다.

참고 : [https://developer.chrome.com/blog/pwa-manifest-id/](https://developer.chrome.com/blog/pwa-manifest-id/)

### 아이콘 생성하기

아이콘은 보통 192, 512 사이즈를 준비하는 것 같고 maskable 이미지도 준비해주는 것이 좋다.
maskable 이미지가 있으면 앱 형태로 설치시에 더 깔끔하게 나온다.
(없어도 문제가 되는것은 아니지만, 개발자 콘솔에서 워닝을 띄운다)

두 이미지의 차이는 다음과 같다.

- 일반 이미지  
  ![normal](/assets/images/2023-10-01-jekyll에-PWA-적용하기/icons-192.png)

- maskable 이미지  
  ![maskable](/assets/images/2023-10-01-jekyll에-PWA-적용하기/icons-192-maskable.png)

나의 경우에는 아래 링크에서 maskable 용 asset 을 만들었다.
[https://maskable.app/editor](https://maskable.app/editor)

### color 설정하기

- [background_color](https://developer.mozilla.org/en-US/docs/Web/Manifest/background_color)  
  앱 형태로 설치하면 스플레시 화면을 거쳐 앱이 실행된다.
  스플레시 화면에서 사용될 background color를 지정하는 용도이다.

- theme_color
  상단 툴바의 색상을 결정한다. head 태그에 `<meta name="theme-color" content="#070707" />` 도 추가 해주었다.
  (둘을 색상을 동일하게 맞춰주라고 한다.)

## service-worker.js 설정해주기

레포지토리의 README에 예시가 있으니 참고해서 본인에 맞게 수정을 하면 된다.

나의 경우에는 image path에 대해 수정을 진행하였고
github을 통해서 모든 리소스를 관리하기 때문에 외부 리소스에 대한 처리가 없지만 필요하면 추가하면 된다.

해당 파일은 프로젝트 루트에 둬야 한다.

```js
// service-worker.js

// set names for both precache & runtime cache
workbox.core.setCacheNameDetails({
  prefix: "dev-jonghoonpark",
  suffix: "v1.0",
  precache: "precache",
  runtime: "runtime-cache",
});

// let Service Worker take control of pages ASAP
workbox.skipWaiting();
workbox.clientsClaim();

// let Workbox handle our precache list
workbox.precaching.precacheAndRoute(self.__precacheManifest);

// use `NetworkFirst` strategy for html
workbox.routing.registerRoute(/\.html$/, new workbox.strategies.NetworkFirst());

// use `NetworkFirst` strategy for css and js
workbox.routing.registerRoute(
  /\.(?:js|css)$/,
  new workbox.strategies.NetworkFirst()
);

// use `CacheFirst` strategy for images
workbox.routing.registerRoute(
  /assets\/(images|icons)/,
  new workbox.strategies.CacheFirst()
);
```

> 2.2.3 버전을 사용했다면 workbox.core 가 아닌 위 코드 예시처럼 workbox를 통해 직접 함수를 호출해야 한다. 반대로 2.2.3 버전이 아니라면 workbox.core를 통해 함수를 호출해야 한다.(라이브러리 README 참고)

# 마무리

위 단계를 따라왔으면 Lighthouse에서 PWA 관련해서 만점을 받을 수 있다.
(참고로 만점이 아니여도 부분적으로는 PWA의 기능들이 사용 가능하다. 만점을 받으면 중간의 W 부분이 파란색으로 나온다.)

![lighthouse result](/assets/images/2023-10-01-jekyll에-PWA-적용하기/lighthouse-result.png)

앱으로도 설치 가능하다

![install as app](/assets/images/2023-10-01-jekyll에-PWA-적용하기/install-as-app.jpeg)

블로그를 앱으로 쓸 경우는 많지 않겠지만, 서비스 워커를 통해서 리소스 캐시가 가능해 지는 것에 의의가 있지 않을까 생각된다.
