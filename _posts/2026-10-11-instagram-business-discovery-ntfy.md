---
layout: "post"
title: "인스타그램 게시물, 약관 어기지 않고 수집하기"
description: "좋아하는 브랜드의 콜라보 공지를 자꾸 놓쳐서 인스타그램 새 글을 ntfy로 받아보기로 했다. 비로그인 요청은 막혀 있고 로그인 쿠키를 쓰는 건 약관 위반이다. Meta 공식 Graph API의 Business Discovery로 해결할 수 있었다."
categories:
  - "개발"
tags:
  - "Instagram"
  - "Instagram Graph API"
  - "Business Discovery"
  - "Meta"
  - "ntfy"
  - "Python"
  - "크롤링"
date: "2026-10-11 15:00:00 +0900"
toc: true
---

## 들어가며

유튜브 쇼츠를 보다가 개인적으로 진짜 마음에 드는 옷을 찾았다.

![IAB Studio x Yonex Woven Pullover Blue](/assets/images/2026-10-11-instagram-business-discovery-ntfy/iab-studio-x-yonex-woven-pullover-blue.png)

몇 년 전 제품이라 현재는 아쉽게도 팔지 않고 크림에서나 살 수 있다.

IAB STUDIO 콜라보 옷들은 참 이쁜 것 같은데 나는 패알못이다 보니 소식을 알 방법이 없다. 인스타그램 앱이 깔려 있긴 하지만 그렇게 자주 들어가보지는 않는 편이라 더 그럴 것이다. 개인적으로 원치 않는 알림을 싫어하는 편이라 인스타 알림도 거의 꺼두고 살아간다. 그래서 내가 원하는 템포로 `@iabstudio`와 `@worksout_official` 두 계정에 새 글이 올라오면 알림이 오도록 수집기를 만들어보기로 했다.

알림은 자체 호스팅하고 있는 [ntfy](https://ntfy.sh)로 받는다. ntfy를 통해서는 이미 다양한 것들을 받고 있다. 알림을 보낼 곳은 텔레그램 봇이든 슬랙이나 디스코드 웹훅이든 상관없다. 나는 이미 ntfy를 잘 쓰고 있어서 알림 받는 곳을 한군데로 모으려고 ntfy를 골랐다. 다른 곳으로 받고 싶다면 알림 보내는 부분만 바꾸면 된다.

개발 자체는 Claude가 잘 해줬다. 하지만 Meta 개발자 콘솔에서 이것저것 세팅하는 데 20분 정도 걸렸고 헷갈리는 부분도 많았다. 그래서 그 구성 과정을 정리해본다. 참고로 이 방법은 조회하려는 인스타그램 계정이 비즈니스 계정이거나 크리에이터 계정일 때만 쓸 수 있다.

## 인스타그램 내부 API는 막혀 있다

instagram.com 웹 클라이언트는 프로필을 그릴 때 내부 API를 호출한다. 이 API를 그대로 따라 호출해보면 다음과 같은 결과가 나온다.

```bash
curl -H "x-ig-app-id: 936619743392459" \
  "https://www.instagram.com/api/v1/users/web_profile_info/?username=iabstudio"
```

```json
{
  "message": "Please wait a few minutes before you try again.",
  "require_login": true,
  "status": "fail"
}
```

401이 왔다. `require_login: true`가 붙어 있다. 프로필 HTML도 받아와 봤는데 게시물 데이터는 들어 있지 않았다. 로그인하지 않으면 공개 계정이라도 데이터를 주지 않는다.

로그인한 브라우저의 `sessionid` 쿠키를 헤더에 넣으면 이 API는 동작한다. 실제로 이 방식으로 만든 도구가 많다. 하지만 인스타그램 이용약관은 자동화된 수단으로 데이터를 수집하는 것을 금지한다. 걸리면 쿠키를 제공한 계정이 제재를 받는다. 부계정을 쓰면 위험은 줄지만 약관을 어기는 건 그대로다. 게다가 내부 API는 인스타그램이 언제든 바꿀 수 있다.

알림 하나 받자고 약관을 어기고 싶지는 않았다. 공식적인 방법을 찾아보기로 했다.

## 공식 API로 남의 게시물을 볼 수 있을까

인스타그램 공식 API는 기본적으로 로그인한 자기 계정의 데이터만 다룬다. 예전에 있던 Instagram Basic Display API도 본인 프로필과 게시물만 조회할 수 있었고 그마저도 2024년 12월 4일에 종료됐다.

그럼 방법이 없을까?

재미있는 게 남의 인스타 계정을 볼 수 있는 기능이 Facebook 로그인을 통한 Instagram API 쪽에 있었다.

이름은 [Business Discovery](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery)다.

이 API로 인스타그램의 다른 비즈니스·크리에이터 계정의 프로필 정보와 공개 게시물을 조회할 수 있다. 브랜드 계정은 대부분 여기에 해당하고 IAB STUDIO와 WORKSOUT도 마찬가지였다.

## 준비하기

크게 준비해야 하는 것은 다음과 같다.

1. 내 인스타그램 계정을 프로페셔널 계정으로 전환한다.
2. 페이스북 페이지를 만들고 그 계정을 연결한다.
3. Meta 개발자 앱을 만든다. 앱은 [메타 개발자 콘솔](https://developers.facebook.com/apps)에서 만들 수 있다.

프로페셔널 계정 전환은 무료이고 언제든 되돌릴 수 있다. 다만 공개 계정만 전환할 수 있어서 비공개 계정이라면 먼저 공개로 바꿔야 한다. 본 계정을 공개로 돌리는 게 신경 쓰이면 부계정을 하나 만들어서 사용하면 될 것 같다.

개발자 앱은 개발 모드 그대로 두면 된다. 내 계정에만 쓰는 용도라 앱 검수도, 비즈니스 인증도 필요 없다.

### 개발자 앱 권한 설정하기

개발자 앱에서 토큰을 발급할 때 아래 권한을 넣어야 한다.

나는 직접 시도하면서 필요 권한을 찾아야 했는데 이 글을 보고 있는 사람은 굳이 그럴 필요가 없다.

| 권한                        | 용도                                                                |
| --------------------------- | ------------------------------------------------------------------- |
| `instagram_basic`           | 인스타그램 계정 정보와 게시물 조회                                  |
| `instagram_manage_insights` | Business Discovery 호출에 필요                                      |
| `pages_show_list`           | `me/accounts`로 내 페이지 목록 조회                                 |
| `pages_read_engagement`     | 페이지와 연결된 데이터 읽기. Business Discovery 호출에 필요         |
| `business_management`       | 비즈니스 관리자로 관리하는 페이지 접근                              |
| `ads_read`                  | 페이지 권한을 비즈니스 관리자로 받은 경우 Business Discovery에 필요 |

권한은 이용 사례 메뉴를 통해 설정할 수 있다.

![meta-app-use-cases](/assets/images/2026-10-11-instagram-business-discovery-ntfy/meta-app-use-cases.png)
앱 대시보드의 이용 사례 화면. 오른쪽 위 **이용 사례 추가**로 Instagram 이용 사례를 넣는다.

![meta-use-case-customize](/assets/images/2026-10-11-instagram-business-discovery-ntfy/meta-use-case-customize.png)
이용 사례 맞춤 설정 화면. 여기서 위에서 언급한 6개의 권한을 추가하면 된다.

## 토큰 발급 받기

### 단기 토큰 발급 받기

[Graph API 탐색기](https://developers.facebook.com/tools/explorer/)에서 단기 액세스 토큰을 발급받을 수 있다.

![graph-api-explorer](/assets/images/2026-10-11-instagram-business-discovery-ntfy/graph-api-explorer.png)

우리는 페이스북 API를 통해 인스타에 접근하는 것이기 때문에 호스트를 `graph.facebook.com`으로 두면 된다.

인스타그램 데이터를 가져오는데 로그인 및 API Base URL 설정은 페이스북으로 해야 한다는 게 이 API 사용에서 가장 헷갈리는 부분이다. 인스타로 바꾸면 오히려 에러를 반환하니 주의한다.

위에서 말한 권한 6개를 추가한 후 "Generate Access Token"을 누르면 액세스 토큰을 발급받을 수 있다.

### 내 instagram_business_account 조회하기

장기 토큰으로 바꾸기 전에, 탐색기에서 방금 받은 단기 토큰으로 아래 API를 요청해 페이지와 인스타그램 계정이 제대로 연결됐는지 확인한다.

```
me/accounts?fields=name,instagram_business_account{id,username}
```

![graph-api-explorer-me-accounts](/assets/images/2026-10-11-instagram-business-discovery-ntfy/graph-api-explorer-me-accounts.png)
페이지에 연결된 인스타그램 계정의 `id`와 `username`이 `instagram_business_account` 아래에 나온다.

이 중 `instagram_business_account.id`가 원하는 값이다.

### 장기 토큰 발급 받기

탐색기에서 받은 토큰은 1시간짜리 단기 토큰이다. 매일 도는 알림에 쓰려면 수명이 길어야 한다. Meta 토큰은 이렇게 바꿀 수 있다.

1. 단기 사용자 토큰(약 1시간)을 장기 사용자 토큰(약 60일)으로 교환한다.
2. **장기 사용자 토큰으로 페이지 토큰을 받으면, 그 페이지 토큰은 만료되지 않는다.**

```python
# 1) 단기 → 장기 사용자 토큰
long_user = graph(
    "oauth/access_token",
    grant_type="fb_exchange_token",
    client_id=app_id,
    client_secret=app_secret,
    fb_exchange_token=short_token,
)["access_token"]

# 2) 장기 사용자 토큰으로 받은 페이지 토큰은 만료되지 않는다
pages = graph(
    "me/accounts",
    fields="name,access_token,instagram_business_account{id,username}",
    access_token=long_user,
)["data"]
```

`debug_token`으로 확인하면 `type: PAGE`, `expires_at: 0`이 나온다. 0이 만료 없음이다. 페이스북 비밀번호를 바꾸거나 앱 권한을 해제하면 무효가 되지만 그 전까지는 갱신할 필요가 없다.

Business Discovery는 페이지 토큰으로도 호출된다.

## Business Discovery API 조회하기

토큰과 인스타그램 계정 ID가 준비되면 요청은 한 번이면 된다.

```
GET https://graph.facebook.com/v26.0/{내 IG 계정 ID}
  ?fields=business_discovery.username(iabstudio){
      username,name,followers_count,media_count,
      media.limit(50){id,caption,media_type,media_url,thumbnail_url,permalink,timestamp}
    }
  &access_token={페이지 토큰}
```

`media.limit(...)`로 최근 게시물을 원하는 만큼 받을 수 있다. 50과 100 모두 그대로 돌아왔다.

```json
{
  "business_discovery": {
    "username": "iabstudio",
    "name": "IAB-STUDIO ®",
    "followers_count": 251451,
    "media_count": 466,
    "media": {
      "data": [
        {
          "caption": "New for fall\n\nAvailable in store tomorrow 10.03 (Sat) ...\n\nOnline raffle 10.05 (Mon) 3PM\nat WORKSOUT (APP)",
          "media_type": "CAROUSEL_ALBUM",
          "permalink": "https://www.instagram.com/p/Dd_HN0yj4Id/",
          "timestamp": "2026-10-02T09:00:20+0000",
          ...
        }
      ]
    }
  }
}
```

본문, 썸네일, 게시물 링크, 작성 시각까지 알림에 필요한 건 다 들어 있다.

## 알림 만들기

나머지는 평범한 폴링이다. 의존성 없이 Python 표준 라이브러리만 썼다.

나는 아래와 같이 구성했다.

- 매일 오전 9시에 두 계정의 최근 게시물 50개를 가져온다.
- 이미 본 게시물 목록과 비교해서 새 글만 ntfy로 보낸다.
- 처음 실행할 때는 기존 게시물을 기록만 하고 알림은 보내지 않는다.

ntfy 에 대한 글은 아니기 때문에, 이 글에서 ntfy 에 대해서는 자세히 설명하지는 않는다.

## 결과

새 게시물이 올라오면 ntfy를 통해 휴대폰 알림 센터에 이렇게 뜬다.

![ntfy-notification](/assets/images/2026-10-11-instagram-business-discovery-ntfy/ntfy-notification.png)
제목에는 계정 이름이, 본문에는 캡션 앞부분이 들어가고 썸네일이 첨부 이미지로 보인다.

알림을 누르면 바로 해당 게시물이 열린다.

![instagram-post](/assets/images/2026-10-11-instagram-business-discovery-ntfy/instagram-post.jpg)
알림을 눌러 열린 실제 인스타그램 게시물. 부산국제영화제를 맞아 나온 p!tt X IAB STUDIO 콜라보 공지다.

딱 이런 콜라보 소식을 받고 싶어서 만든 거라 만족스러웠다.

## 한계

- **비즈니스·크리에이터 계정만 볼 수 있다.** 개인 계정은 공식 API로 볼 방법이 없다.
- **스토리는 볼 수 없다.** Business Discovery는 피드 게시물만 준다.
- **처음 세팅이 번거롭다.** 프로페셔널 계정 전환, 페이지 연결, 개발자 앱, 권한, 토큰 교환까지 한 번은 거쳐야 한다. 대신 한 번 해두면 토큰 갱신 없이 계속 돈다.

## 마무리

로그인 쿠키를 쓰는 비공식 방식이었다면 금방 끝났을 일이다. 공식 API로 하느라 20분 정도를 Meta 개발자 콘솔에서 보냈다. 그래도 약관을 신경 쓸 필요가 없고, 계정이 막힐 걱정도 없고, 인스타그램이 내부 API를 바꿔도 영향을 받지 않는다. 만료 없는 토큰까지 받았으니 정말 넣어두고 잊어버리면 된다.

인스타그램 알림은 여전히 꺼두었다. 보고 싶은 소식만 내가 정한 시간에 받아볼 수 있게 되었다.

## 결과물 확인

전체 코드는 GitHub에 올려두었다.

- [dev-jonghoonpark/insta-ntfy](https://github.com/dev-jonghoonpark/insta-ntfy)

## 참고

- [Business Discovery - Instagram Platform](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery)
