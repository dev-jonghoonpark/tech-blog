---
layout: post
title: Playwright PR 마무리
description: Playwright에 올린 PR이 머지되었으며, 이를 기록하기 위해 블로그에 글을 남깁니다. GDG Daejeon Devfest에서 Injae Kim님의 발표를 통해 오픈소스 기여의 중요성을 배우고, Microsoft의 Playwright 프로젝트에 기여하게 되었습니다. PR 내용은 toPass() 함수의 기본 timeout을 사용자 설정으로 변경하는 것으로, 2개월 만에 머지되었습니다. 오픈소스 기여 경험을 통해 많은 것을 배우고, 앞으로도 기여할 기회를 갖고 싶습니다.
categories: [개발]
tags: [github, pr, pull requests, contribute, playwright]
date: 2024-01-16 23:00:00 +0900
---

![Playwright logo](/assets/images/2024-01-16-playwright-pr-merged/Playwright_Logo.png)

최근에 Playwright 에 올린 PR이 merge 되었다. 링크드인에 남긴 글을 기록용으로 블로그에도 올려본다.

<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7153026591256629248" height="1013" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>

---

지난번 GDG Daejeon Devfest 행사에서  
GDG Songdo의 Injae Kim 님께서 "오픈소스 기여로 수억명에게 임팩트 만들기" 라는 주제로 발표를 해주셨습니다.

그 당시에 오픈소스 기여에 대해서 발표를 준비 해주시면서 동시에 GDG Songdo 에서 진행하시는 오픈소스 스터디를 압축해서 경험할 수 있도록 도와주셨는데 덕분에 아래의 PR을 하게 되었습니다.

\[microsoft/playwright] feat(expect): Make toPass's option configurable by TestConfig

- Merged PR: [https://github.com/microsoft/playwright/pull/28231](https://github.com/microsoft/playwright/pull/28231)
- Microsoft에서 개발한 웹 브라우저 UI를 코드기반으로 테스트 할 수 있는 오픈소스 (현재 스타수 58.2k)
- toPass() 라는 함수로 원하는 상태를 만족할때까지 테스트도중 기다릴 수 있는데 toPass()의 default timeout을 유저가 global config로 편하게 한번에 설정할 수 있게 변경

PR을 올린 후 2달 정도 지났고, 드디어 머지가 되었습니다.

내가 평소에 좋아하던 프레임워크에 기여를 하게 되어서 너무 좋기도 하고 신기한것 같습니다.  
계속 관심 가져 주신 김인제님께 다시 한 번 감사드립니다...!  
발표 해주셨던 내용 너무 좋았어서 주변 개발자들에게도 오픈소스 기여와 관련해서 배웠던 것들을 공유해드렸었네요

앞으로도 기여할 기회가 있다면 또 하고 싶은 경험인것 같습니다

---

참고로 위에 나온 오픈소스 스터디와 관련해서는 [오픈소스 스터디 진행 가이드](2023/11/26/opensource-study) 라는 글로 정리해두었다.
