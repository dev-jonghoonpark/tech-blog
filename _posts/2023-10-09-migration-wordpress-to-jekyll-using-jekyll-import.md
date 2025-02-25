---
layout: post
title: jekyll import 를 이용하여 wordpress에서 jekyll로 글 옮기기 (마이그레이션)
description: 워드프레스에서 Jekyll로 블로그 글을 마이그레이션하기 위해 jekyll-import 도구를 설치하고 사용하는 방법을 설명합니다. 설치는 간단하며, 필요한 의존성을 추가한 후 명령어를 통해 데이터를 가져올 수 있습니다. 마이그레이션 후에는 이미지 URL 변경, 포스트 URL 구조 수정, HTML을 Markdown으로 변환하는 추가 작업이 필요합니다. 이 과정에서 발생할 수 있는 문제와 해결 방법도 함께 안내합니다.
categories: [블로그]
tags: [블로그, wordpress, 워드프레스, jekyll, 지킬, 마이그레이션, migration]
date: 2023-10-09 23:30:00 +0900
---

블로그에 여러 번 글을 남겼지만 시간이 날 때 글들을 수동으로 옮기는 중이다.

- [깃헙 블로그 세팅](/2023/09/15/깃헙-블로그-세팅)
- [jekyll url redirect 처리하기](/2023/09/28/jekyll-url-redirect-처리하기)

계속 옮기고 있는 중이지만 너무 많은 시간이 소요되고 있어 jekyll에서 제공해주는 마이그레이션 도구를 사용해보기로 했다.

[https://import.jekyllrb.com/docs/installation/](https://import.jekyllrb.com/docs/installation/)

이 마이그레이션 도도구는 다양한 플랫폼을 지원한다.

![support platforms](/assets/images/2023-10-09-migration-wordpress-to-jekyll-using-jekyll-import/support-platforms.png)

# 설치방법

설치와 사용은 간단하다.
위 사이트에 있는 안내를 따르면 되는데

```
gem install jekyll-import
```

우선 gem 명령어로 jekyll import를 설치하면 된다.

설치를 하면 바로 사용할 수 있는 것은 아니고 몇 가지를 수동으로 추가 설치해줘야 한다.

![require-dependencies](/assets/images/2023-10-09-migration-wordpress-to-jekyll-using-jekyll-import/require-dependencies.png)

어떤 dependency가 필요한지는 해당 플랫폼에서 마이그레이션 하는 법을 설명해주는 상세페이지에서 설명을 해준다.

나는 워드프레스에서 옮기는 것이기 때문에 [wordpress 에서 마이그레이션 하는 법](https://import.jekyllrb.com/docs/wordpress/) 페이지를 참고하였다.

![wordpress-require-dependencies](/assets/images/2023-10-09-migration-wordpress-to-jekyll-using-jekyll-import/wordpress-require-dependencies.png)

나의 경우에는 아래 3가지를 추가해주면 되었다.

```
gem install sequel unidecode mysql2
```

---

mysql2의 경우 설치 중 아래와 같은 에러가 발생되었는데

```
`block in find_library': undefined method `split' for nil:NilClass (NoMethodError)
```

brew를 통해 mysql 을 설치해주니 해결되었다.

```
brew install mysql
```

동일한 맥 유저의 경우에는 참고하면 좋을 것 같다.

참고 : https://discuss.rubyonrails.org/t/error-occurred-while-installing-mysql2/76210/4

# migration 진행하기

페이지에서 소개해주는 명령어 샘플은 아래와 같다.

```
jekyll import wordpress --dbname DB --socket SOCKET --user USER --password PW --host HOST --port PORT --table_prefix PREFIX --site_prefix PREFIX --clean_entities --comments --categories --tags --more_excerpt --more_anchor --status STATUS,STATUS2
```

다 쓸 필요는 없고 문서을 확인해가면서 필요에 따라 수정하면 된다.  
나의 경우에는 아래와 같이 수정하여 사용하였다.

```
jekyll import wordpress --dbname {DB_NAME} --user {USER} --password {PASSWORD} --host {HOST} --port {PORT} --table_prefix {TABLE_PREFIX}
```

참고로 host에는 localhost(로컬호스트)를 쓰면 정상적으로 동작하지 않는다. 127.0.0.1 로 작성하자.

실행을 하면 아래와같이 \_posts 폴더가 생성이 된다.

![migrated images](/assets/images/2023-10-09-migration-wordpress-to-jekyll-using-jekyll-import/migrated-posts.png)

생성된 폴더를 내 jekyll 블로그로 옮기면 작업이 마무리된다.

# 글 마무리

마이그레이션 도구가 있는건 알고 있었다.  
하지만 마이그레이션 도구가 내 상황에 딱 맞는 것도 아닌지라 옮기고 나서도 어처피 추가 작업을 해야할 것이라 판단해서 수동으로 하고 있었다.

해줘야 하는 작업은

- 이미지 url 변경
- post url 구조 변경에 따른 migration 파일 생성
- html 에서 markdown 으로 변경

정도가 되겠다.

3번의 경우에는 마이그레이션 도구를 통해 html으로 post들이 추출되었는데 생각보다 문제가 크게 깨지는 부분들이 없는 것 같아서 이 부분은 그냥 사용해도 되지 않을까 싶다.

이미지들은 github으로 옮기고 상대주소로 변경해주기는 해야할 것 같다.
(현재는 wordpress 서버를 바라보고 있다.)

`post url 구조 변경에 따른 migration 파일 생성`은 검색엔진이나 기타 다른 채널을 통해 기본 url로 들어왔을 때 새로 변경된 url 구조로 redirect 해줄 수 있도록 처리해주는 부분을 이야기 하는 것인데 이 부분은 위에서도 언급한 [jekyll url redirect 처리하기](/2023/09/28/jekyll-url-redirect-처리하기) 글에서 다루고 있다.

시간날 때 이어서 계속 처리해야 겠다.
