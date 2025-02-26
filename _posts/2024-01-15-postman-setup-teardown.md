---
layout: "post"
title: "postman - setup, teardown 처리하기 (using newman)"
description: "Postman을 사용한 테스트 자동화에서 데이터 초기화와 정리에 대한 고민을 해결하기 위해 Newman을 활용하는 방법을\
  \ 소개합니다. Newman은 Postman 컬렉션을 CLI 환경에서 실행할 수 있게 해주며, 특정 이벤트(예: beforeTest, test)를\
  \ 통해 setup과 teardown 처리를 할 수 있습니다. 이 글에서는 Newman의 사용법과 간단한 테스트 예제를 통해 데이터 셋팅과 정리\
  를 어떻게 효율적으로 수행할 수 있는지 설명합니다."
categories:
- "스터디-테스트"
tags:
- "테스트"
- "Testing"
- "Postman"
- "Newman"
- "Event"
- "Setup"
- "Teardown"
- "external library"
- "api test"
date: "2024-01-15 04:30:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-01-15-postman-setup-teardown.jpg"
---

어떻게 보면 별거 아닌 이야기 인데 그래도 비슷한 고민을 하고 있으신 분이 있으실까 싶어서 글로 정리를 해본다.

최근에 커피챗을 하면서 어떤 회사에서 Postman을 통한 테스트 자동화를 진행하고 있다는 이야기를 들었다.

그래서 postman으로 데이터를 어떻게 초기화 하고 어떻게 정리할지에 대한 의문이 들었다.
아쉽게도 아무리 찾아봐도 속 시원한 방법은 보이지 않았다.

테스트는 서로 독립적으로 동작할 수 있어야 한다고 이야기 한다. 그렇기 때문에 테스트를 한 후 데이터를 깔끔하게 정리하는 것도 중요하다고 생각한다. 테스트를 할 때 항상 이 부분이 어려운 것 같다.

api를 통해서 데이터를 삭제하는 경우에는 데이터가 soft-delete 되어 있는 경우도 있어 아쉬움이 있었는데, 그렇다고 데이터베이스에 직접 접근하자니 내 범위를 벗어나는게 아닐까 싶은 마음도 들게된다.

그렇기 때문에 데이터를 초기화 할 수 있는 기능을 개발자에게 부탁해야할지, 내가 처리해야할지도 고민해야한다.

---

우선 postman에서 외부 라이브러리를 사용 할 수 있는지 찾아보았다.

찾아보니 postman에서 외부 라이브러리를 사용하는 것은 제약이 있었다.
[Adding External Libraries in Postman](https://blog.postman.com/adding-external-libraries-in-postman/)

---

그 이후로 newman이 떠올라서 newman의 documentation을 확인해보기로 하였다.
[https://github.com/postmanlabs/newman](https://github.com/postmanlabs/newman)

newman은 postman collection을 cli 환경에서 실행할수 있도록 도와주는 실행 도구이다.
문서를 보면 알겠지만 newman은 cli 기능도 제공하지만 node 라이브러리로 사용하는 방식도 지원하고 있다.

그리고 라이브러리 형태로 사용하면, 특정 이벤트가 발생하였을 때 어떤 처리를 해줄지를 정해놓을 수 있다.

여기서 관심을 가지고 본 이벤트가 beforeTest, test 이다.
beforeTest에서 setup을 test에서 teardown을 해주면 될 것 같다는 생각이 들었다.

| Event      | Description                              |
| ---------- | ---------------------------------------- |
| beforeTest | Before `test` script is execution starts |
| test       | After `test` script execution completes  |

일단 아래와 같이 코드를 작성해보았다.

```ts
import newman from "newman";

newman
  .run({
    collection: require("./postman_collection.json"),
    reporters: "cli",
  })
  .on("beforeTest", function (err, args) {
    console.log("before test");
  });
```

그리고 postman에서 autuator health api를 호출하는 request를 만들어 200이 정상적으로 나오는지 확인하는 간단한 테스트를 작성하였다.

http://{{BASE_URL}}/actuator/health

```
pm.test("Status test", function () {
    pm.response.to.have.status(200);
});
```

해당 request에 대한 부분을 json으로 export하여 테스트를 진행해보았더니 예상했던대로 테스트가 진행되기 전 "before test" 로그가 출력되는 것을 확인할 수 있었다.

![output](/assets/images/2024-01-15-postman-setup-teardown/output.png)

node 단으로 끌고 나왔기 때문에 이제 내가 원하는대로 다양한 라이브러리를 이용하여 데이터 셋팅(setup)과 정리(teardown)를 할 수 있게 되었다.

나의 경우에는 별도의 테스트용 환경에서 테스트 할 것이기 때문에 개발자에게 요청 없이 그냥 내가 처리해도 문제는 없을 것이라고 판단해서 내가 처음으로 끝까지 세팅해봐야 겠다 싶다.
