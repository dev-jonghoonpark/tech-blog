---
layout: "post"
title: "Google Colab에서 Playwright 사용하기"
description: "Google Colab에서 Playwright를 사용하여 자동화를 구현하는 방법을 소개합니다. 무료로 GPU를 활용할 수\
  \ 있는 Colab에서 Playwright의 기본 코드를 실행하며, Chrome 설치 및 필요한 라이브러리 설치 과정을 포함합니다. 스케줄링 기\
  능은 Pro+에서만 지원되며, 다른 서버에서 실행할 수 있는 방법을 추가로 탐색할 예정입니다."
categories:
- "개발"
- "Playwright"
tags:
- "Google Colab"
- "Colab"
- "Playwright"
- "E2E"
- "End to End"
- "Python"
date: "2023-05-26 03:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-05-26-Google-Colab에서-Playwright-사용하기.jpg"
---

어제 밤에 뭔가를 자동화 하고 싶다는 생각이 들었고  
이를 위해 Playwright가 적합할 것이라는 생각이 들었다.

그리고 그 과정에서 코랩을 사용하면 좋겠다는 생각이 들었다.

일단 무료이기도 하고 머신러닝용으로 그래픽 카드가 좋으니까라는 판단에서 였다. (영향이 있을지는 모르겠지만...)

작성은 Playwright공식 홈페이지에 있는 Getting Started 코드를 기반으로 작성하였다.  
(일단 동작이 되는것을 확인하는 것이 주된 목표였기 때문에 아직은 뭘 더 작성하거나 한 건 없다.)

```python
!wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt install ./google-chrome-stable_current_amd64.deb

!pip install nest_asyncio
!pip install pytest-playwright

import nest_asyncio
nest_asyncio.apply()

import asyncio
from playwright.async_api import async_playwright, expect

import re

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            executable_path="/usr/bin/google-chrome-stable",
            user_data_dir="/content/random-user"
        )
        page = await browser.new_page()
        await page.goto("https://playwright.dev/")

        # Expect a title "to contain" a substring.
        await expect(page).to_have_title(re.compile("Playwright"))

        # create a locator
        get_started = page.get_by_role("link", name="Get started")

        # Expect an attribute "to be strictly equal" to the value.
        await expect(get_started).to_have_attribute("href", "/docs/intro")

        # Click the get started link.
        await get_started.click()

        # Expects the URL to contain intro.
        await expect(page).to_have_url(re.compile(".*intro"))

asyncio.run(main())
```

위와 같이 작성해서 동작시키면 문제 없이 잘 동작한다.

다만 원래 나는 기능을 만든 뒤 특정 시간에 실행되도록 스케쥴링을 하고 싶었는데  
그 기능은 Pro+ 에서만 된다는 것 같다.  
[https://github.com/googlecolab/colabtools/wiki/Scheduled-notebooks](https://github.com/googlecolab/colabtools/wiki/Scheduled-notebooks)

스케쥴링은 다른 서버에서 하더라도 실행만 시킬 수 있으면 좋을 것 같은데 방법은 더 찾아봐야 할 것 같다.

# 참고

- [https://stackoverflow.com/questions/73084593/running-playwright-on-google-colab-gives-error-asyncio-run-cannot-be-called](https://stackoverflow.com/questions/73084593/running-playwright-on-google-colab-gives-error-asyncio-run-cannot-be-called)
- [https://askubuntu.com/questions/1204571/how-to-install-chromium-without-snap](https://askubuntu.com/questions/1204571/how-to-install-chromium-without-snap)
