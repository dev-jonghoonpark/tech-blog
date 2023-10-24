---
layout: post
title: jekyll URL Redirect 처리하기 - 블로그 이동 준비하기 (wordpress to jekyll)
categories: [블로그]
tags:
  [
    블로그,
    워드프레스,
    깃헙,
    깃헙페이지,
    지킬,
    리다이렉트,
    Blog,
    Wordpress,
    Github,
    Github Pages,
    Jekyll,
    Redirect,
    301 Moved Permanently,
    github action,
  ]
date: 2023-09-29 1:00:00 +0900
---

추석이 되어서 미뤄뒀던 블로그 이동 작업을 진행해보려고 하고 있습니다.

9월 15일날 작성하였던 [깃헙 블로그 세팅](/2023/09/15/깃헙-블로그-세팅) 글에서도 작성하였지만 현재는 블로그로 워드프레스를 사용하고 있습니다.

잘 사용중인데, 문제는 oracle cloud의 무료 인스턴스에 자체적으로 호스팅을 하고 있다보니
간혹가다가 서버가 shutdown 되어 있거나, 알 수 없는 이유로 접속이 되지 않는 문제가 발생되었습니다.
추가적으로 지금은 무료 인스턴스를 유지해주고 있다지만 언젠가 끝나면 어쩌지 싶은 마음도 있기 때문에
더 안전한 곳으로 이동을 하고 싶었습니다.

# 이사 계획

현재 github 블로그는 github.jonghoonpark.com 을 사용중에 있고
워드프레스 블로그는 jonghoonpark.com 을 사용중에 있습니다.
(2023.10.24 기준 jonghoonpark.com 으로 마이그레이션 진행함.)

기존 게시글에 대한 이동을 마치면 github 블로그를 jonghoonpark.com 으로 연결하고
워드프레스 블로그를 wordpress.jonghoonpark.com 과 같은 링크로 (당분간) 연결을 하는 것으로 계획을 세웠습니다.

하지만 여기서 문제가 발생됩니다.

# 문제

문제는 다음과 같습니다.

- 기존(wordpress)의 링크 구조와 github page에 사용하는 지킬(jekyll)의 페이지 구조가 다릅니다. 예시는 다음과 같습니다.
  - wordpress 구조 : /mocks-and-test-fragility-1
  - jekyll 구조 : /2023/05/11/테스트-대역-목-과-스텁
- 그리고 워드프레스의 301 리다이렉트 플러그인 기능을 사용해서 2개의 외부 링크를 301 처리 하고 있었습니다.
  - /resume : 이력서 페이지(노션)로 이동
  - /linkedin : 링크드인 프로필 페이지로 이동

# 해결 방법

각 post에 permalinks 만들어주는 것으로도 방법이 될 수 있겠지만 이번에 블로그를 이동하면서 지킬에 설정되어 있는 URL 구조를 따르고 싶었습니다.

그렇게 하기 위해서 이전 경로로 페이지에 접근했을 때 새 경로로 사용자를 이동시켜줄 수 있는 방법을 찾아야 했습니다.

## Redirect 시켜주기

일단 jekyll의 경우 정적 페이지를 사용합니다. 따라서 http 헤더에 301을 담아준다든지 할 수는 없습니다.

그래서 메타테그의 refresh 을 이용하는 방법을 사용했습니다.

예시로 들었던 링크들을 그대로 사용하겠습니다.

- wordpress 구조 : /mocks-and-test-fragility-1
- jekyll 구조 : /2023/05/11/테스트-대역-목-과-스텁

jekyll 프로젝트의 루트 폴더에 `/mocks-and-test-fragility-1.html` 파일을 생성한 뒤 아래와 같이 html을 작성해 줍니다.

```html
<!DOCTYPE html>
<html>
  <head>
    <meta
      http-equiv="refresh"
      content="0; url=/2023/05/11/테스트-대역-목-과-스텁"
    />
  </head>
</html>
```

그러면 이제 사용자는 `/mocks-and-test-fragility-1` 경로로 들어왔을 때
`/2023/05/11/테스트-대역-목-과-스텁` 링크로 이동되게 됩니다.

외부 링크도 가능하기 때문에 `/linkedin` 링크로 들어왔을 때 프로필 링크로 리다이렉트를 시키고 싶다면

```html
<meta
  http-equiv="refresh"
  content="0; url=https://linkedin.com/in/dev-jonghoonpark"
/>
```

이렇게 meta tag를 구성하면 되겠습니다.

설명을 위해서 그냥 한글인 상태로 URL을 적어두었는데 실제 사용시에는 URL Encode 된 주소를 사용하는 것이 더 좋지 않을까 생각됩니다.

## 개선하기 (Github Action 으로 파일 옮기기)

근데 이 구조의 단점은 프로젝트 루트에 html 파일들이 생기게 된다는 것이였습니다.
기존에 블로그에서 옮겨야 하는 글이 80개 조금 넘어가는 것을 감안하였을 때 프로젝트 루트가 메우 지저분 해질 것은 당연했습니다.

그래서 생각한 방식이 `_redirects` 폴더를 만들어 여기서 Redirect html 을 관리하고 github action으로 빌드 및 배포하는 과정에서 해당 폴더 내에 있는 redirect용 html들을 빌드 경로에 적절하게 넣어주면 되겠다는 생각이 들었습니다.
(참고로 jekyll의 경우 `_` 가 들어간 폴더를 특수 폴더로 인식해서 build시에 복사하지 않는다고 합니다.)

빌드와 업로드 사이에 `Copy redirects` 단계를 추가하였습니다.

```yml
- name: Build with Jekyll
  # Outputs to the './_site' directory by default
  run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
  env:
    JEKYLL_ENV: production
- name: Copy redirects
  run: cp ./_redirects/* ./_site/
- name: Upload artifact
  # Automatically uploads an artifact from the './_site' directory by default
  uses: actions/upload-pages-artifact@v2
```

이렇게 해서 깔끔한 프로젝트 루트를 구성하면서도 리다이렉트를 시켜줄 수 있게 되었습니다.

# 마무리

블로그 이동에 대한 준비는 어느정도 마친것 같습니다.
(이제 나머지는 노가다 작업...)

이 글 작성하면서 카테고리도 만들어두면 좋겠다 싶어서 카테고리 기능도 추가하였습니다.

마지막 걱정되는 문제라면
워드프레스에서는 요스트 SEO 와 같은 플러그인들을 설치해서 사용했었는데
github pages 에서는 어떻게 이 문제를 개선할 수 있을지를 잘 모르겠습니다.
(사이트맵은 등록 해두었습니다만...)
더 고민 해봐야 할 부분인 것 같습니다.
