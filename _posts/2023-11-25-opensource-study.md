---
layout: post
title: 오픈소스 스터디 진행 가이드
categories: [오픈소스, 개발]
tags:
  [
    오픈소스,
    오픈소스 스터디,
    스터디,
    GDG,
    Playwright,
    PR,
    Pull Request,
    issue,
    maintainer,
    contributor,
    contribute,
  ]
date: 2023-11-26 01:00:00 +0900
---

전 세계의 GDG 에서는 연말에 DevFest 라는 행사를 개최한다.  
내가 오거나이저로 활동하고 있는 GDG 대전 에서도 행사를 진행하게 되었다.  
[2023 GDG Devfest Daejeon](https://festa.io/events/4318)

이번 행사의 컨셉은 오픈소스와 스터디로 잡았다.  
이를 통해 한 번의 이벤트성 행사 보다는 지속적인 교류가 이뤄질 수 있었으면 좋겠다는 기대를 하였다.

그 과정에서 GDG 송도의 오거나이저 이신 [김인제](https://www.linkedin.com/in/injae-kim-dev/)님께 도움을 요청드리게 되었다.

김인제님은 GDG 송도에서 오픈소스 스터디를 운영하고 계신다.  
GDG 오거나이저 채널을 통해서 종종 스터디 사진과 소식을 볼 수 있었는데, 보기만 해도 너무 재밌어 보였다.  
[GDG 송도 - 오픈소스 스터디 2기 멤버 별 진행사항 정리](https://chip-bream-9d5.notion.site/2-459f46f1dbe048ffbb7ef04fd9dcc6a6?pvs=4)

그래서 혹시 온라인으로라도 좋으니 경험을 공유해주실 수 있을지를 요청드렸었는데 대전 까지 오시기에는 먼 거리임에도 불구하고, 흔쾌히 도움을 주시겠다고 대전까지 와주셨다.  
이 글을 통해 다시 한 번 감사를 드린다.

일단 행사는 23일날 잘 마무리 되었고, 인제님께서 앞으로 대전에서도 스터디 진행하는데 도움이 되었으면 하시는 마음으로 짧은 시간동안 속성으로 스터디를 진행해주셨다.

스터디 과정에서 진행된 부분도 위 notion 링크에 정리해서 등록해주셨다.

![gdg-songdo-x-daejeon.png](/assets/images/2023-11-25-opensource-study/gdg-songdo-x-daejeon.png)

이 글을 통해서는 어떤 단계를 통해서 스터디가 진행이 되었는지를 정리해본다.  
아래 적는 것의 경우에는 풀리퀘스트를 해보는 것으로 스터디 방향이 잡혔지만, 오픈소스 코드 분석이나 문서화에 참여하는 것도 스터디 활동으로 하신다고 하신다.

## 0. 스터디 목표

누구나 오픈소스에 관심을 가지고, 기여를 한다면 좋다는 것을 알고 있다.  
하지만 심리적인 부담으로 인해 쉽게 시작하지 못한다.

오픈소스에 기여를 해 본 사람이 도와준다면 누구나 PR을 열어볼 수 있다. (의지가 있다면)  
스터디를 통해 커뮤니티 구성원들에게 오픈소스에 기여할 수 있는 경험을 제공한다.

## 1. 진행해보고 싶은 오픈소스 고르기

먼저 기여를 하고 싶은 오픈소스를 고르는 것이 첫번째이다.  
본인이 관심 있어하고 평소에 사용하는 프로젝트를 선택하는 것이 좋다고 설명해주셨다.

그래서 나는 **[Playwright](https://github.com/microsoft/playwright)**를 선택하였다.

Playwright는 다음과 같은 도구이다.

> Playwright is a framework for Web Testing and Automation. It allows testing Chromium, Firefox and WebKit with a single API.

현 시점 기준으로 스타수 56.8K 를 가진 큰 프로젝트이다.

비슷한 프로젝트로는 Cypress가 있는데 나는 Playwright가 좀 더 나에게는 맞다고 생각을 하고 있다.
Mail이 정상적으로 도착했는지 확인하는 기능을 Cypress와 Playwright로 모두 구현을 해보았는데 Playwright가 더 간단하고 직관적이였다.

## 2. 그 프로젝트를 고른 이유

이후 단계에서 나오겠지만 스터디 리드는 스터디원이 오픈소스에 기여할 수 있도록 많은 부분을 도와주어야 한다.  
처음은 어렵다. 하지만 첫 PR을 하는 경험을 마친다면 이 사람은 스스로 PR을 할 수 있게 될 것이다.

따라서 이 프로젝트를 고른 이유와 어떤 부분에 관심이 있는지, 어떤 부분을 수정해보고 싶었는지에 대해서 파악이 되어야 한다.  
적절한 이슈를 선택하는데 도움이 될 수 있다.

나는 Playwright를 선택한 이유에 대해서 아래와 같이 설명드렸다.

> 저는 E2E 테스트를 할 때 Playwright라는 도구를 가장 좋아하다보니 이 도구에 기여를 하고 싶었습니다.  
> 기여해보고 싶던 부분은 저도 크게 생각하지 못하고 있어서 고민을 좀 해보았는데  
> 도구 수동 빌드시에 진행하는 테스트 중에 몇가지 fail 케이스가 발생되는것으로 보여서  
> 해당 이슈를 분석하고 다뤄보면 어떨까 생각이 들었습니다...!

## 3. 기여할만한 이슈 찾아보기

사실 처음부터 직접 풀리퀘스트를 만드는 것은 어려울 수 있다.  
그래서 스터디 리더는 스터디원이 처음으로 기여하기에 적절한 이슈를 찾아주어야 한다.

적절한 이슈는 아래와 같다. (하나하나 찾아보기는 해야한다.)

- 댓글 수 5개 정도. 댓글이 너무 많으면 문제나 해결책이 명확하지 않다는 것일 수 있다.
- 컨트리뷰터가 해당 이슈에 대해서 인지하고 있음.
- 첫 컨트리뷰트를 하는 사람들을 위해 라벨로 할만한 이슈들을 정리해주는 경우도 있으나, 그런 이슈들은 빠르게 마무리 된다.

적절한 이슈를 찾았다면, 그 이슈를 어떻게 해결할 수 있는지, 코드 레벨에서 분석까지 해준다. (디테일한 부분까지는 아니더라도 틀은 잡을 수 있도록)

나의 경우 [Setup default timeout to expect.toPass assertion](https://github.com/microsoft/playwright/issues/23937) 이라는 일감을 선택해주셨다.

스터디 리더는 이슈와 그 해결방법에 대해서 설명을 해준다.

## 4. 코드 분석하고 수정하기

스터디 리더는 틀까지만 잡아주는 것이고 더 디테일한 부분은 스터디원이 분석해서 만들어 나가야 한다.  
(틀까지 잡아주는데도 정말 많은 노력과 시간을 사용해주신 것이다. 감사해하자.)

나는 이슈에 대한 이야기를 스터디 리더와 나누고 난 후,  
밤 사이에 해당 이슈에 대한 처리를 마치고 커밋을 하였고 아침에 다음과 같이 상황을 공유 드렸다.

> 좋은 아침입니다 인제님 :)
>
> toPass를 이해하기 위해 실제로 동작시켜보니깐 0 으로 들어가도 무한은 아니더라고요
>
> 이 프로젝트에서 toPass를 사용할 경우
> 관련된 타임아웃 값이 3개가 있는데 아래와 같았습니다.
>
> - global timeout
> - expect 의 timeout
> - toPass 의 timeout
>
> 0으로 될 경우 이론상 무한이 맞는것 같으나
> global timeout에 잡혀서 toPass가 종료되도록 되어있었습니다.
>
> expect의 timeout은 expect 블록의 검증문이 timeout이 되는 시간이고
> toPass의 timeout은 expect 블록이 성공할 때까지 최대 언제까지 retry 할지에 대한 시간이였습니다.
>
> 둘은 다르기 때문에 메인테이너가 toPass 설정을 따로 추가하자 제안 한 것으로 이해하였습니다.
>
> 그래서 아래와 같이 작업되었습니다…!  
> [https://github.com/dev-jonghoonpark/playwright/commit/041785faa775861d6b9c49dc65fbcb9af0e0908a](https://github.com/dev-jonghoonpark/playwright/commit/041785faa775861d6b9c49dc65fbcb9af0e0908a)
>
> 작업 중에 특이하였던 점은  
> 빌드 과정중에 test.d.ts 파일이 생성되는데 md 파일을 기반으로 해서 구현이 되도록 해두었더라고요  
> (그래서 이 커밋에서 class-testconfig.md, class-testproject.md 파일도 수정하게 되었습니다)
>
> md는 단순히 문서라고 생각해서 코드를 이해하는 과정에서 배제하고 있었는데  
> 그래서 이 부분에서 많이 헤맸었습니다.

상황을 정확하게 공유해줘야 스터디 리더가 도움을 주시기 편할 것이다.

이후 스터디 리더의 피드백까지 반영하면 PR을 올릴 준비가 마무리된다.
(나의 경우에는 더 적절한 commit 메시지와, 테스트 케이스 추가를 제안해주셨고 그에 따라 추가적으로 수정을 진행하였다.)

## 5. PR 올려보기

코드를 다 수정하였다면 PR을 올릴 차례이다. 프로젝트들에서는 PR을 올리는 법에 대해서도 문서화를 해둔다.

Playwright도 [CONTRIBUTING.md](https://github.com/microsoft/playwright/blob/main/CONTRIBUTING.md) 가 있다.

이 문서를 읽고 준수하여 PR을 올리면 된다.

내가 한 PR은 다음과 같다.
[feat(expect): Make toPass's option configurable by TestConfig #28231](https://github.com/microsoft/playwright/pull/28231)

Playwright의 경우 PR에 대한 Template 는 없는데, 이런식으로 Template가 경우에는 아래의 Template로 작성해주면 좋다고 설명해주셨다.

> related issue:
>
> Motivation:
>
> Modification:
>
> Result:

이 템플릿을 따라 다음과 같이 작성되었다.

![My-PR.png](/assets/images/2023-11-25-opensource-study/My-PR.png)

## 6. 기타

이제 컨트리뷰터가 반응해주기를 기다리면 된다.

컨트리뷰터들은 돈을 받고 일하는 것이 아니다. 따라서 반영이 되는데 많은 시간이 소요될 수 있다.

# 마무리

너무 재밌는 경험이였고, 다른 사람에게도 추천해주고 싶은 경험이였다.

실제로 그래도 바로 오늘 있었던 [K-DEVCON 대전 스터디](https://k-devcon.tistory.com/entry/Review-2023-11-25-K-DEVCON-DAEJEON-%EC%8A%A4%ED%84%B0%EB%94%94-%ED%9B%84%EA%B8%B0)에서도 내가 했던 경험을 간단하게나마 공유를 해 주었다.
(기존 발표자분께서 사정이 있으셔서 불참하게 되어서 급하게 준비한 것은 아쉽지만 그것이 아니더라도 공유하고 함께 해보고 싶었다.)

실제로 PR을 해보면서 문서화와 테스트에 신경을 많이 썼다는 것이 느껴졌다.

이제 스스로 이슈를 찾아서 PR을 올릴 차례인 것 같다. 더 많은 PR을 해볼 수 있기를 기대한다.
