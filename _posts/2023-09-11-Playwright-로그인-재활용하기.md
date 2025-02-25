---
layout: post
title: Playwright 로그인 재활용하기 - 세션 관리 (cookie, local storage, session storage)
description: Playwright를 사용하여 로그인 인증정보를 관리하고 재활용하는 방법에 대해 설명합니다. 이 글에서는 cookie, local storage, session storage를 활용하여 테스트 속도를 단축시키는 방법을 다루며, 파이썬과 node.js에서의 접근 방식을 비교합니다. 수동으로 cookie 값을 가져오고 저장하는 방법, local storage 및 session storage에 접근하는 방법, Playwright의 저장소 상태를 활용하는 방법을 소개하며, 인증정보 유출 방지를 위한 주의사항도 안내합니다.
categories: [개발, Playwright]
tags: [Playwright, token, session, cookie, local storage, session storage, state, python, login, auth]
date: 2023-09-11 12:00:00 +0900
---

이 글은 인증정보에 접근하고 보관하고 재사용하는 방법에 대해 다룹니다. (cookie, local storage, session storage)

![auth](/assets/images/2023-09-11-Playwright-로그인-재활용하기/image1.jpg)

일반적으로 로그인을 하였을 때 cookie나 local storage나 session storage를 통해 클라이언트의 브라우저에 인증정보(혹은 세션에 해당하는 키 값)를 보관합니다.

이러한 특성을 이용하여 테스트시에 인증정보를 보관하고 있다가 다시 로드하게 된다면, 각각의 테스트에서 인증할 필요가 없어지기 때문에 테스트 실행 속도를 단축시킬 수 있습니다.

이 글은 파이썬 playwright를 기반으로 작성되었으나. 기본적으로 node.js와 크게 다르지 않기 때문에 참고해주시면 감사하겠습니다.

# 방법 1 : 수동으로 값 가져오기
page 객체를 중심으로 각각의 저장소에 접근할 수 있는 방법에 대해 설명함.

## cookie
cookie 값은 `page.context.cookies()` 함수를 통해 조회 가능하고 `page.context.add_cookies(cookies)` 함수를 통해 입력 가능하다.

이를 아래와 같이 응용할 수 있다.

```
# 저장하기
with open("{0}/{1}".format(pathlib.Path(__file__).parent.resolve(), "cookies.json"), "w") as json_file:
    json.dump(await page.context.cookies(), json_file)
```

```
# 불러오기
with open("{0}/{1}".format(pathlib.Path(__file__).parent.resolve(), "cookies.json")) as json_file:
    await page.context.add_cookies(json.load(json_file))
```



## local storage 및 session storage
evaluate를 통해 아래와 같이 local storage 및 session storage 값에 접근 가능하다.
```
import os

# Get session storage and store as env variable
session_storage = await page.evaluate("() => JSON.stringify(sessionStorage)")
os.environ["SESSION_STORAGE"] = session_storage

# Set session storage in a new context
session_storage = os.environ["SESSION_STORAGE"]
```

# 방법 2 : Playwright에서 제공하는 storage
```
# Save storage state into the file.
storage = context.storage_state(path="state.json")

# Create a new context with the saved storage state.
context = browser.new_context(storage_state="state.json")
```

playwright에서 cookie와 local storage 데이터를 관리한다.

단 이 방법으로는 session storage는 관리되지 않음.

# 주의사항
인증정보를 별도로 관리할때는 해당 정보가 유출되지 않을 수 있도록 유의하자 (ex. git을 통한 버전관리에 포함되지 않도록 처리해야 함)

# 참고
[https://playwright.dev/python/docs/auth](https://playwright.dev/python/docs/auth "https://playwright.dev/python/docs/auth")
