---
layout: post
title: "[ios 개발] pod install 시 ruby path가 2.6.x일 경우 해결방법"
categories: [개발]
tags: [아이폰, ios, 애플, apple, pod, cocoa]
date: 2024-02-27 13:00:00 +0900
---

mac에는 기본적으로 ruby가 설치되어 있다.  
하지만 2.6.0 버전이기 때문에 최신버전인 3 버전이랑은 호환 문제가 발생된다.

그래서 보통 개발을 위해 brew로 3버전을 설치한다.

그런데 오늘 발생된 문제는 설치 후 `ruby --version`을 실행 해보았을 때 3버전이 문제없이 나오고 있는 상태인데  
막상 `pod install`을 수행 해보면 2.6.0 버전을 사용하고 있는 이슈가 있었다

이로 인해서 ffi 관련 이슈가 발생하였고
```
sudo gem uninstall ffi && sudo gem install ffi -- --enable-libffi-alloc
```
을 수행해보라는 로그가 친절하게 나왔지만 해당 명령을 수행하면 3 버전의 ruby에 설치가 진행되는 것이기 때문에 의미가 없었다.

## 해결방법

pod 파일은
/usr/local/bin/pod 에 위치해 있는데

맨 윗줄을 보면

```sh
#!/System/Library/Frameworks/Ruby.framework/Versions/2.6/usr/bin/ruby
```

로 되어있다.

이 부분을 brew로 통해 받은 ruby 경로로 바꿔주면 해결된다.

```sh
#!/usr/local/opt/ruby/bin/ruby
```
