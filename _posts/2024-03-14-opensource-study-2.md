---
layout: post
title: 오픈소스 스터디 3기 참여 후기 (오픈소스 PR 해보기, github 후원(sponsor) 해보기)
categories: [개발, 오픈소스]
tags:
  [
    개발,
    오픈소스,
    기여,
    컨트리뷰트,
    opensource,
    contribute,
    pull request,
    풀리퀘스트,
    issue,
    이슈,
    github,
    깃헙,
    스폰서,
    sponsor,
    후원,
    playwright,
    querydsl,
  ]
date: 2024-03-14 21:00:00 +0900
---

요즘 회사 일이 많아져서 정신이 없지만. 공부는 여전히 열심히 하고 있고, 활동도 여전히 열심히 하고 있다.

최근에 진행했던 오픈소스 스터디 3기에 대해서 회고 및 소개해보고자 시간을 내서 글을 작성해본다.

## 오픈소스 스터디 참여 후기

### 오픈소스 스터디 2기

[오픈소스 스터디 진행 가이드](https://jonghoonpark.com/2023/11/26/opensource-study)

작년 11월에 운좋게 인제님의 오픈소스 스터디 2기(특별반)에 참여해서 playwright에 기여해보는 경험을 했었다.
많이 도와주신 덕분에 Playwright 라는 대규모 오픈소스에 기여해볼 수 있었다.

이후에도 종종 '내가 기여할만한 이슈가 없을까?' 라는 생각을 가지고 playwright에 눈팅을 해보았지만 내가 할만한 이슈를 찾는 것은 쉽지만은 않았다.

### 오픈소스 스터디 3기

인제님께서는 오픈소스 스터디 오픈채팅방을 운영하고 계신다.

해당 방에서 오픈소스 스터디 3기에 대한 소식이 조금씩 들려오기 시작하였기 때문에 나는 기회가 된다면 3기에 지원해야겠다 마음을 먹고 있었다. 지난 스터디에서 경험이 너무 좋았었기 때문일 것이다.

이번 스터디를 통해서는 동기를 부여받고 싶었다. 혼자하면 아무래도 동기부여가 떨어지는 측면이 있었기 때문이다.

#### 신청

시간이 되어서 오픈소스 스터디 3기의 신청이 시작되었다.

최근 회사 업무가 일시적으로 많아졌다. 그래서 3기에 신청을 해도 될까, 내가 많은 시간을 투자하지 못해서 폐가 되면 어떻게하지 라는 걱정을 가지면서도 오픈소스에 기여할 수 있는 정말 좋은 기회라고 생각하였기 때문에 조금 무리일수도 있겠지만 지원하였다.

내가 먼저 신청을 하였고, 주변의 다른 분들도 신청하셨으면 좋ㅎ겠다는 생각이 들어서 내가 운영자로 활동하고 있는 `K-DEVCON 대전`에도 홍보를 하였다.

![share-info-about-study](/assets/images/2024-03-14-opensource-study-2/share-info-about-study.jpeg)

다행히도 관심을 가지시는 분들이 있으셨다.

### 이슈 찾아서 PR 해보기

다행히 다시 한 번 기회를 받아 3기에도 참여할 수 있었다.

이번 3기에 참여하신 참가자분들이 기여해보고자 선정한 프로젝트는 다음과 같았다.

![opensource-project-list](/assets/images/2024-03-14-opensource-study-2/opensource-project-list.png)

나는 이번에도 테스트 도구들에 기여를 해보기로 마음을 먹었고, playwright에 기여를 하기로 결정하였다.

나는 지난번에도 한 번 해보았기 때문에 스스로 기여할 수 있을만한 이슈를 찾아서 선정을 하였다.
혼자 종종 찾아볼때는 할만한게 잘 안보였는데, 그래도 확실히 동기가 부여된 상태라 그런지 수월하게 적절한 이슈를 찾을 수 있었다.

![left-comment-in-issue](/assets/images/2024-03-14-opensource-study-2/left-comment-in-issue.png)

맘에 드는 이슈를 발견하였다면 코멘트를 남겨 내가 해결하여 PR 해보겠다는 것을 나타내면 된다.
(물론 모든 이슈가 Accept 되는 것은 아니다. 내가 찾은 이슈의 경우 메인테이너가 PR 하고 싶으면 열려있다는 라벨을 달아놓았다)

![issue-labels](/assets/images/2024-03-14-opensource-study-2/issue-labels.png)

처음 컨트리뷰트를 해보는 사람이라면 어떤 이슈로 시작해야할지 어려울 수 있다.
하지만 걱정하지는 않아도 된다. 처음 해보는 분들에게는 **인제님**께서 옆에서 친절하게 도움을 주신다.

#### 내가 올린 PR

[microsoft/playwright](https://github.com/microsoft/playwright)

- pr 주소 : [https://github.com/microsoft/playwright/pull/29868](https://github.com/microsoft/playwright/pull/29868)
- ui mode에서 단축키 추가

#### 이번 스터디에서 좋았던 점

이번 스터디에서 좋았던 부분은
첫째는 당연히 오픈소스에 기여할 수 있는 경험을 할 수 있었다는 것이고,
둘째는 나 말고도 열심히 하는 분들이 많구나 느낄 수 있었다. 자극을 얻어갈 수 있는 시간이였다고 생각한다.

#### 참가비 : 오픈소스에 $50 후원해보기

이번 3기의 참가비는 **오픈소스에 $50 후원해보기** 였다.

github에서는 오픈소스 프로젝트에 혹은 개인(오픈소스 메인테이너) 에게 후원을 할 수 있는 기능이 있다.

기능이 있다는 것은 알고 있었지만 처음으로 github 오픈소스 후원 기능을 사용해보게 되었고 나는 playwright의 메인 멤버에게 후원을 하게 되었다.

![sponsor-done](/assets/images/2024-03-14-opensource-study-2/sponsor-done.png)

스폰서 후원를 할 때 공개(public)으로 설정 하면 프로필에 누구를 후원중인지에 대한 정보가 추가되며, 뱃지도 추가되게 된다.

![public-sponsor](/assets/images/2024-03-14-opensource-study-2/public-sponsor.png)
![public-sponsor-badge](/assets/images/2024-03-14-opensource-study-2/public-sponsor-badge.png)

## 그 후

스터디가 끝난 이후로 자신감이 생겼는지 나는 한가지 또 할만한 것을 발견하였고, 이어서 PR을 해보았다.
요즘 java를 공부해야겠다 마음을 먹고있는 상태인데 그래서 그랬나 마침 querydsl 프로젝트가 눈에 띄였다.
querydsl의 경우 예전부터 종종 잘 쓰던 라이브러리 인데 java 21 이 아직 지원되지 않는것으로 보여 테스트를 통과하도록 수정하여 PR 하였다.

[querydsl](https://github.com/querydsl/querydsl)

- pr 주소 : [https://github.com/querydsl/querydsl/pull/3705](https://github.com/querydsl/querydsl/pull/3705)
- java 21 호환 처리

PR 준비를 하면서 cglib, byte buddy, asm 같은 애들을 사용하는 것을 볼 수 있었는데
이런 애들이 뭐하는 라이브러리인지 간단하게 알아보고 정리를 해봐야 겠다는 생각이 들었다.
wellgrounded java developer 를 읽을 떄도 중간에 나왔던 기억이 있다.

다음에는 spring, 특히 spring-data 쪽에 기여를 해보고 싶다 라는 생각이 들었다.

## 마무리

다시 한 번 좋은 경험을 할 수 있도록 기회를 주신 인제님께 감사드리고,
인제님께서 계획하시는 방향을 들어보니 나중에는 오픈소스 컨트리뷰터들 끼리 만날 수 있는 행사도 만들려고 하시는 것으로 보이셨다. (시간과 기회가 된다면)
그 날이 온다면 꼭 참여하고 싶고 참여해야겠다.
