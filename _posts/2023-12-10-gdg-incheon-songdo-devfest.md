---
layout: post
title: GDG 송도 devfest 참여 후기
description: GDG 송도 DevFest에서 오픈소스 기여, 구글 엔지니어의 협업 방식, 안드로이드 모듈화, 개발자 커뮤니티 성장, Vector Database, Bun, 그리고 다양한 커리어 사례에 대한 발표가 진행되었습니다. 김인제님은 오픈소스 기여의 중요성을 강조하며 열정을 불어넣었고, 신지민님은 구글의 협업 문화를 소개했습니다. 안석용님은 안드로이드 모듈화의 기법을 설명하였으며, 한성민님은 성장형 마인드셋과 커뮤니티 운영의 중요성을 언급했습니다. 다양한 주제를 통해 개발자들이 서로의 경험을 공유하고 성장할 수 있는 기회를 제공한 행사였습니다.
categories: [행사]
tags: [GDG, devfest, Google, Google developer, GDG Songdo]
date: 2023-12-12 00:30:00 +0900
---

짧게 정리해서 남겨본다.

---

## 오픈소스 기여로 수억명에게 임팩트 만들기 (김인제님)

![김인제님](/assets//images/2023-12-10-gdg-incheon-songdo-devfest/2023-12-10-14-16-21-166.jpg)

인제님은 지난번 대전 행사때에도 오셔서 [오픈소스 기여에 대한 가이드](/2023/11/26/opensource-study)를 해주셨었다.

이번 발표에서는 더 다양한 사례를 자세히 소개해주셨다.

오픈소스에 기여해야겠다는 열정을 다시 불어넣어주신 발표였던 것 같다.  
하지만 현실은 쉽지 않다. 그래도 시간이 될 때마다 이 레포 저 레포 돌아다니면서 컨트리뷰트 할만한 이슈가 없을까 찾아보고 있다.

![오픈소스 기여를 통한 역량 성장](/assets//images/2023-12-10-gdg-incheon-songdo-devfest/2023-12-10-14-45-12-123.jpg)

---

[오픈소스 Armeria 업무 시간에 기여하기](https://www.youtube.com/watch?v=jYT98fxN6Ak)

<iframe width="560" height="315" src="https://www.youtube.com/embed/jYT98fxN6Ak?si=ZFqVJee-0h4znPhm" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

[armeria](https://github.com/line/armeria)

서킷 브레이커
[분산 서비스 환경에 대한 Circuit Breaker 적용](https://engineering.linecorp.com/ko/blog/circuit-breakers-for-distributed-services)

## 구글 엔지니어의 개발 및 협업 방식 (신지민님)

지민님께서는 지난번에도 구글의 문화를 소개해주셨었다. [GDG SUMMIT 2023](/2023/10/20/gdg-summit)
다시 들어도 재밌었어서 정리하면서 들었다.

끝나고 [구글 엔지니어는 이렇게 일한다](https://www.yes24.com/Product/Goods/109182479) 책을 구매하였다.

도서관에서 빌려서 테스트 관련 부분만 빠르게 읽어보았는데 전체를 읽어보면 좋겠다 싶었다.

---

서로 돕는 문화. 회사의 시스템이 그렇게 만든다.

플래닝 -> 딜리버리 -> 레트로스펙트 -> 플래닝(loop)

### 플래닝

: 시간을 굉장히 많이 사용함

OKR (Objective and Key Results)

- Org OKR Planning
  - Annually
- Team OKR
  - Annually, quarterly
  - Reviewed by leads
- Top down & bottom up

- individual OKR/expectation setting
  - Role profile
  - Quarterly check-in
- It's Okay to realign priorities/expectations
- It's not for blame, it's more to individual's career, to provide feedback/coaching

실패해도 괜찮아. -> 리뷰하는 것은 비난하려 함 아님 / 더 나은 방향으로 나아가기 위함

level 3,4,5,6 ?

개발은 프로덕트를 전세계가 함께함.
타임존으로 인한 어려움은 있음.

그럼 어떻게 처리하느냐

- 미팅 (시간과 아젠다를 정해놓고 함. 미팅을 효율적으로 하자.)
- 1on1
- 이메일 / 챗
- 디자인 doc
- Transparency
  - Google search for Googlers
  - Code share
- Code review
  - Code/readability owner
- Eng review

### 회고

왜 서로에게 답변을 해주는가.
보상 (reward) -> 서로가 윈윈

- team level
  - okr scoring; no-blame
- individual level
  - annual assessment : 여기에도 시간을 많이 씀.
  - promotion
    - contribution, challenges, Influence

#### build a culture which rewards effective collaboration

Assessment

- how well the person collaborated/communicated with others?
- how the person influence others beyond yourself?

Other merits

- Peer bonus
- Peer feedback

## 안드로이드 모듈화 (안석용님)

지금은 안드로이드를 주로 개발하고 있지는 않지만 한 때 안드로이드를 개발했었어서 그런지 석용님의 발표를 (어렵지만) 재밌게 들었다.

지난번에 서울에서 했던 행사에서도 다른 주제의 발표를 하신것을 들었었는데 기회가 되어서 이번에도 들었다.

<script defer class="speakerdeck-embed" data-id="1b4655d27012443e8ac180d05c1a7b9a" data-ratio="1.7777777777777777" src="//speakerdeck.com/assets/embed.js"></script>

단계적으로 모듈화 하기

gradle에서 compile only, runtime only를 잘 사용하자.

nonTransitiveRClass - 최신 버전들 에서는 true가 기본값

Convention Plugin
https://www.slideshare.net/YoungjikYoon/gradle-kotlin

모듈화의 함정 : 병렬로 빌드하지 않으면 줄어들지 않는다. (오히려 늘수도 있다.)
그런데 병렬로 빌드하려고 할 때 모듈별 의존성을 가지고 있으면 불가능하다. 그리고 의존성을 갖기 쉽다.

api와 impl로 분리
최근 공식 모듈화 가이드 업데이트 됨.

Dagger Hilt 의존성 주입

## 개발자 커뮤니티와 함께 성장하기 (한성민 님)

성민님의 발표는 늦게 도착하는 바람에 끝나갈때쯤부터 들어서 아쉬웠다.

성장형 마인드셋과 지속 가능한 커뮤니티 : 프로세스 도입 및 개선
에 대한 이야기를 해주셨는데

커뮤니티 운영을 하다보면 정말 프로세스가 중요하다는걸 느낀다.

항상 열심히 일하시는게 멋지신것 같다.

## Vector Database as a dedicated service (박진형님)

진형님은 개인적으로 느끼기에는 워낙 인싸이셔서 행사에 가면 잘 보이시는 편이다.

아쉽게도 이쪽 분야에는 크게 지식이 없어서 다 듣지는 못했다.

## What is Bun (서동민님)

![서동민님](/assets//images/2023-12-10-gdg-incheon-songdo-devfest/2023-12-10-16-39-46-109.jpg)

Bun에 대해서 가볍게만 알고 있었는데 접할 수 있어서 좋았다.
Bun 관련해서 찾아보면서 발표를 들었는데

Bun에는 자체적으로 test를 실행할 수 있도록 해 두었는데
이렇게 구성하기 위해 jest같은 외부 라이브러리를 가져다 썼을까? 라는 생각이 들어서 확인해보니
아예 자체적으로 구현을 해두었더라. (jest compatible 이다.)

## 세상에 꼬인 이력은 없다 (황혜경님)

혜경님의 발표도 재밌게 들었고 여러 커리어의 사례를 들을 수 있었어서 좋았다.

![날밤님 사례](/assets//images/2023-12-10-gdg-incheon-songdo-devfest/2023-12-10-17-45-30-569.jpg)

그 중 재밌었던것중 날밤님에 대한 사례였는데 실제적으로 동작하는 프로덕트를 운영해 보신게 큰 도움이 되셨다고 한다.
AWS 관련 행사가 있을 때 앞에서 보던분인데 갑자기 구글 행사에서도 이렇게 나오셔서 재밌었다.
