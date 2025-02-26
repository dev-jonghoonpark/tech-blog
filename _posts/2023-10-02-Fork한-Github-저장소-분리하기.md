---
layout: "post"
title: "잔디심기 안되는 문제 해결 - Fork한 Github 저장소 분리하기"
description: "GitHub에서 잔디심기 문제를 해결하기 위해 Fork된 저장소를 독립형으로 분리하는 방법을 소개합니다. 커밋이 프로필에\
  \ 표시되지 않는 이유는 커밋이 포크된 저장소에서 이루어졌기 때문이며, 이를 해결하기 위해 GitHub에 티켓을 제출하여 저장소를 분리하는 절차\
  를 설명합니다. 티켓 제출 후, 빠른 시간 내에 Fork 정보가 제거되고 커밋이 정상적으로 프로필에 나타나는 결과를 확인할 수 있습니다."
categories:
- "개발"
- "블로그"
tags:
- "블로그"
- "깃헙"
- "Fork"
- "Github"
- "잔디심기"
- "Commit"
- "저장소 분리"
- "Ticket"
- "깃헙 프로필"
date: "2023-10-02 12:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-10-02-Fork한-Github-저장소-분리하기.jpg"
---

블로그를 jekyll을 이용해서 github pages로 이동하려고 시간날때 조금씩 준비하고 있다.
이번 추석에도 열심히 준비했는데 생각보다 해야할 양이 많더라...

일괄적으로 옮기면 좋겠지만 이전 글들은 마크다운이 아니라 형태도 조정해줘야 하기도 해서 손으로 옮기면서 내용도 다시 보고있다.

---

# 원인 찾기

그 와중에 작업하면서 궁금했던게 **'왜 커밋을 해도 프로필 커밋 영역에 표시가 안되는거지?'** 였다.
딱히 크게 의의를 두지는 않았기 때문에 '블로그는 안쳐주나?' 라고 생각하고 넘어갔는데

생각해보니 1일 1커밋 하시는 분들이 있다는데
'그럼 그 분들은 코드로 1일 1커밋 이상 하시는건가? 쉽지 않을텐데?' 라는 생각이 갑자기 들어
안되는 이유를 검색해보기 시작했다.

검색 해보면 **git config 에 등록된 이메일 주소가 github 계정으로 등록된 이메일 주소와 일치하지 않는 경우**에 대해서 가장 많이 나오는데 내 경우에는 일치했기 때문에 이 케이스는 아니였다.

'그러면 왜 안되는거지?' 하며 더 찾아보니 나 같은 사람이 많았는지 Github 공식 문서에도 commit이 보이는 기준에 대해서 정리해 둔 글이 있었다.

[Why are my contributions not showing up on my profile?](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/managing-contribution-settings-on-your-profile/why-are-my-contributions-not-showing-up-on-my-profile)

여기서 핵심 부분만 가져와 보자면 아래 부분이다.

> Commits will appear on your contributions graph if they meet **all** of the following conditions:
>
> - The email address used for the commits is associated with your account on GitHub.com.
> - The commits were made in a standalone repository, not a fork.
> - The commits were made:
>   - In the repository's default branch
>   - In the gh-pages branch (for repositories with project sites)

번역해보면 다음과 같다.

> 다음 조건을 **모두** 충족하는 경우 커밋이 기여 그래프에 표시됩니다.
>
> - 커밋에 사용된 이메일 주소는 GitHub.com의 계정과 연결되어 있습니다.
> - 커밋은 포크가 아닌 독립형 저장소에서 이루어졌습니다.
> - 아래의 조건에서 커밋이 이루어졌습니다.
>   - 저장소의 기본 브랜치에서
>   - (프로젝트 사이트가 있는 저장소의 경우) gh-pages 브랜치에서

나의 경우에는 2번째 케이스에 해당하였다. 마음에 드는 jekyll 테마를 고르고 해당 레포지토리를 fork 해서 블로그를 구성하고 있었기 때문에 거기서 오는 문제였다.

# 해결방법

기존의 레포지토리를 옮기고 새 레포지토리를 생성하여 해결하는 것도 가능한 방법일 수 있겠으나, 기존의 데이터를 최대한 유지하고 싶었다.

그래서 찾아보니 Github 에 Ticket을 제출하여 Fork 된 레포지토리를 독립된 레포지토리로 분리할 수 있는 방법이 있었다.

원문을 확인하고 싶으면 하단의 참고 링크를 보면 된다.

## chatbot-virtual-assistant을 사용해서 Fork된 레포지토리 분리 Ticket 제출하기

[https://support.github.com/contact?tags=rr-forks&subject=Detach%20Fork&flow=detach_fork](https://support.github.com/contact?tags=rr-forks&subject=Detach%20Fork&flow=detach_fork)

위 링크를 눌러 들어간다. 들어가면 미리 세팅되어 있는 상태이기 때문에 진행에 따르면 된다.

![image1](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image1.png)

스크린 샷에는 담겨있지 않지만 위 채팅의 바로 아래 `Delete` 와 `Detach/Extract` 버튼이 나온다.

`Detach/Extract` 버튼을 선택한다. (Detach/Extract 가 하나로 묶여서 가기 때문에 Detach 와 Extract 중에 어떤걸 골라야 하는지에 대한 걱정은 하지 않아도 된다.)

![image2](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image2.png)

그러면 어떤 레포지토리를 분리할 것인지에 대한 질문을 한다.
분리를 원하는 레포지토리를 형태에 맞게 입력해준다.

![image3](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image3.png)

포크한 레포지토리에 내가 한 커밋이 있냐고 해서 있다고 했다.

![image4](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image4.png)

왜 레포지토리를 분리하고 싶냐고 물어보는데 당황할 필요는 없다. 셀렉트 박스를 통해 선택지를 제공해준다. `Contributions to the repository aren't visible`이 첫번째 선택지였다.

![image5](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image5.png)

답을 마치면 티켓을 생성해준다.

![email about ticket](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image6.png)

티켓이 생성되엇으면 email로도 안내가 온다.

이제 기다리면 된다.

# 결과

Ticket을 사람이 직접 처리해주는 것으로 보인다.
걸리는 시간은 글에는 5분에서 1시간 정도로 나와있었지만, 나는 한국 시간으로 밤에 신청을 해서 아침에 일어나보니 처리되어 있었다.

![fork info removed](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image7.png)

repository에 들어가면 Fork 했던 원본 Repository에 대한 정보가 사라져 있는걸 볼 수 있다.

![commit visible in profile](/assets/images/2023-10-02-Fork한-Github-저장소-분리하기/image8.png)

프로필에서도 Commit이 정상적으로 보이기 시작하였다.

# 참고

- [https://stackoverflow.com/a/16052845](https://stackoverflow.com/a/16052845)
