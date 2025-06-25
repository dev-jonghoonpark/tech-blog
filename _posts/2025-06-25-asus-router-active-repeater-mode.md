---
layout: "post"
title: "ASUS 공유기에서 리피터 모드(repeater mode) 강제 활성화하기"
description:
  "ASUS 공유기에서 리피터 모드(repeater mode)를 강제로 활성화하는 방법을 안내합니다. \
  ZenWiFi AX Mini 제품에서 리피터 모드를 선택할 수 없는 경우, 개발자 도구를 활용해 JavaScript 코드 `goTo.rpMode();`를 실행하여 \
  설정 페이지에 접근할 수 있습니다. 이후 2.4G Wi-Fi만 보일 경우, 수동 설정을 통해 5G를 확장할 수 있으며, \
  네트워크 이름(SSID)을 정확히 입력해야 합니다. 이 방법으로 안정적인 인터넷 환경을 구축할 수 있습니다."
categories:
  - "개인"
tags:
  - "ASUS"
  - "ROUTER"
  - "아수스"
  - "공유기"
  - "리피터"
  - "repeater"
  - "extend"
  - "extender"
  - "확장"
  - "확장기"
date: "2025-06-25 09:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-06-25-asus-router-active-repeater-mode.jpg"
---

# ASUS 공유기에서 리피터 모드(repeater mode) 강제 활성화하기

리피터 모드를 활성화 하는 방법에 대해서는 공식 사이트의 FAQ로도 제공된다.

[[Wireless Router] How to set up repeater mode?](https://www.asus.com/support/faq/1036082/)

그럼에도 내가 이 글을 쓰기 시작한 이유는 다음과 같다.

나는 현재 **ZenWiFi AX Mini** 제품을 사용하는 중인데 해당 제품의 환경설정에는 리피터 모드를 선택할 수 없게 되어있다는 것을 알게 되었기 때문이다. 나의 경우에는 웹 개발 경험이 있어 쉽게 우회할 수 있었겠지만, 그렇지 않은 사람이라면 좌절하였을 것이다. 그래서 어떻게 강제로 활성화 하였는지 가이드를 남겨보고자 한다.

## 방법 안내

![no repeater mode in config](/assets/images/2025-06-25-asus-router-active-repeater-mode/no-repeater-mode-in-config.png)

보다시피 설정 화면에 repeater mode가 존재하지 않는다. 그럼에도 우회하여 repeater mode를 사용할 수 있다.

![quick internet setup](/assets/images/2025-06-25-asus-router-active-repeater-mode/quick-internet-setup.png)

좌측 메뉴에서 **빠른 인터넷 설정** 을 클릭한다.

![quick internet setup main](/assets/images/2025-06-25-asus-router-active-repeater-mode/quick-internet-setup-main.png)

빠른 인터넷 설정의 메인 페이지에서 하단의 **고급 설정** 을 클릭한다.

![select Choose operation mode](/assets/images/2025-06-25-asus-router-active-repeater-mode/select-choose-operation-mode.png)

**Choose operation mode** 를 선택한다.

![mode list](/assets/images/2025-06-25-asus-router-active-repeater-mode/mode-list.png)

그러면 선택할 수 있는 mode 의 목록이 나오는데, 여기에는 **repeater mode** 가 없다. 따라서 우회해야한다.

이를 위해서는 **개발자 도구** 를 열어야 한다.

아래의 단축키를 사용하여 열 수 있다.

| OS               | 단축키                           |
| ---------------- | -------------------------------- |
| Windows or Linux | `F12` or `Ctrl + Shift + I`      |
| Mac              | `Fn + F12` or `Cmd + Option + I` |

또는

`우측 상단의 메뉴 버튼` → `도구 더보기` → `개발자 도구` 를 통해서도 열 수 있다.

![manual open devtools](/assets/images/2025-06-25-asus-router-active-repeater-mode/manual-open-devtools.png)

열었으면 상단 탭에서 console을 선택한 후 다음과 같이 입력후 실행한다. (엔터를 누르면 실행된다.)

```javascript
goTo.rpMode();
```

![execute script](/assets/images/2025-06-25-asus-router-active-repeater-mode/execute-script.png)

그러면 다음과 같이 repeater mode 설정을 위한 페이지로 진입하게 된다.

![enter to repeater mode page](/assets/images/2025-06-25-asus-router-active-repeater-mode/enter-to-repeater-mode-page.png)

잠시 기다리면 검색이 완료되어 리스트에 근처의 wifi 들을 볼 수 있다.

![search completed](/assets/images/2025-06-25-asus-router-active-repeater-mode/search-completed.png)

이후로는 동일하게 설정을 진행하면 된다.

## repeater mode 설정 화면에서 2.4G만 나오는 이슈

이렇게 해서 설정을 마쳤는데 아쉬운점이 wifi 목록에 2.4G 만 있고 5G는 없었다는 것이다.

이때는 수동 설정을 통해서 5G를 확장할 수 있다. 와이파이 목록 하단에서 **수동 설정** 버튼을 눌러 수동 설정을 진행할 수 있다.

![manual config](/assets/images/2025-06-25-asus-router-active-repeater-mode/manual-config.png)

이 때 주의해야하는 부분은 **네트워크 이름(SSID)** 을 수동으로 작성해줘야 한다는 것이다. 오타가 없도록 이름을 잘 확인하여 적어주자.

## 마무리

이렇게 해서 repeater mode 를 우회하여 설정하는 방법에 대해서 알아보았다. 하루정도 사용해보았는데 문제 없이 안정적으로 잘 동작한다. 불안정한 인터넷으로 고생하는 사람에게 도움이 되는 글이길 바란다.
