---
layout: "post"
title: "Visual Studio Code, Extension 만들어서 등록까지 해보기 (with mocha)"
description: "Visual Studio Code에서 한영타 변환기를 확장 프로그램으로 개발하고 등록하는 과정을 다룹니다. 블로그 작성 중\
  \ 발생하는 한글과 영어 키보드 입력 문제를 해결하기 위해 TypeScript 기반의 변환기를 모듈화하고, Mocha를 사용하여 BDD 방식으로\
  \ 테스트 코드를 작성했습니다. 이후 VS Code API를 활용해 선택된 텍스트를 변환하는 기능을 구현하였고, 최종적으로 Azure DevOps와\
  \ Visual Studio Marketplace에 등록하여 성공적으로 배포했습니다. [GitHub](https://github.com/dev-jonghoonpark/ettk-vscode-extention)\
  \ 및 [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=dev-jonghoonpark.ettk)에\
  서 확인할 수 있습니다."
categories:
- "개발"
- "블로그"
tags:
- "Visual Studio Code"
- "vscode"
- "Extension"
- "converter"
- "marketplace"
- "확장 프로그램"
- "테스트 코드"
- "mocha"
- "tdd"
- "bdd"
date: "2023-10-19 11:40:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-10-19-how-to-create-vscode-extension.jpg"
---

# 개요

올해 5월 부터 블로그를 계속 작성하고 있다.
이것 저것 작성하고 있지만 보통 읽었던 책을 정리하고 있다.

책을 보면서 정리하다보니 화면이 아닌 책을 본 상태로 타이핑을 하는 경우가 많았고 그러다보니 종종 영어 키보드인 상태로 한글을 입력하는 경우가 생겼다. (물론 종종 반대의 경우도 발생하였다.)
이런 상황이 발생되면, 해당 문제가 발생된 시점에서 작성했던 글을 지우고 다시 작성해야 하기 때문에 쌓이면 은근 번거롭고 스트레스가 되었다.

그 때 마다 YT 님의 [한영타 변환기](https://www.theyt.net/wiki/%ED%95%9C%EC%98%81%ED%83%80%EB%B3%80%ED%99%98%EA%B8%B0)를 정말 잘 사용하였다.

최근에는 Wordpress에서 Jekyll로 블로그 도구를 옮기면서 VS Code로 글을 작성하기 시작하였다.
물론 VS Code 에서도 동일한 이슈는 계속 발생하였고 이 문제를 해결하기 위해 VS Code의 Extension (확장 프로그램) 으로 개발을 하면 좋겠다는 생각이 들어 바로 실행에 옮겼다.

기능적으로는 아쉬운 점이 없었지만 이 변환기는 웹 상에서 동작하였기 때문에 필요할 때마다 들어가야 한다는 것이 아쉬웠고 Extension으로 개발하면 이러한 과정을 줄일 수 있을 것이라 생각하였다.

# 개발 과정

먼저 공식 문서를 확인해보기 위해 검색을 해보았다.

[your-first-extension](https://code.visualstudio.com/api/get-started/your-first-extension)

기본적인 것은 가이드를 따라서 하면 되는데 나는 나는 pnpm을 좋아하기 때문에 pnpm으로 진행하였다.

yo 와 generator-code 라이브러리를 다운로드 하면 된다.

```
pnpm install -g yo generator-code
```

그 다음에는 yo 를 통해서 프로젝트를 초기화 한다.

```
yo code
```

초기화 과정중에 있는 질문들에 대한 답변도 가이드에 나와있는 것을 그대로 참고하면 되는데
package manager 선택 부분에서 pnpm도 있어 나는 pnpm을 선택하였다.

```
# ? Which package manager to use? pnpm
```

---

프로젝트 초기화가 되었으면 실행을 하면 된다. 에디터에서는 `src/extension.ts` 을 열고 `F5` 키를 누르라고 하는데 익숙하지 않다면 좌측 사이드바 에서 run 메뉴를 눌러도 된다.

![sidebar run](/assets/images/2023-10-19-how-to-create-vscode-extension/sidebar-run.png)

Run Extension 과 Extension Tests 를 제공해주는 것을 볼 수 있다  
나의 경우에는 Tests 코드도 간단하게 작성해보았다. 테스트 코드는 mocha를 기본 도구로 사용한다.

---

우선 한영타 변환기의 코드를 typescript 기반으로 정리하고 모듈화 하였다. (크게 바꾼건 없고 문법상 걸리는 부분만 조금씩 수정하였다.)
그리고 그 변경이 정상적으로 이뤄진 것인지 확인하기 위해서 테스트 코드를 작성하기로 맘을 먹었다.

[mocha](https://mochajs.org/)는 처음 사용해 보았는데 대부분의 테스트 도구가 비슷한 형태를 가지고 있기 때문에 그렇게 문제될 부분은 없었다.

공식 문서를 보면 TDD 방식과 BDD 방식을 지원한다고 되어 있는데 나는 BDD를 사용하기로 결정을 하였다.
BDD 테스트 작성 방법에 대해서는 "[JUnit5로 계층 구조의 테스트 코드 작성하기](https://johngrib.github.io/wiki/junit5-nested/)" 이 글을 정말 좋아한다. BDD 테스트 작성 방법에 대해 궁금한 사람이 있다면 봐보는것을 추천한다.

`yo code`로 설정한 프로젝트에서는 기본값으로 TDD가 설정이 되어있다.
BDD 로 변경하려면 `src/test/suite/index.ts` 에서

```ts
// Create the mocha test
const mocha = new Mocha({
  ui: "bdd",
  color: true,
});
```

`tdd` 라고 되어 있던 부분을 `bdd` 로 변경해주면 된다.

테스트 코드는 변환기가 정상적으로 동작하는지만 확인하면 되었기 때문에 매우 간단하게 작성하였다.
`src/test/suite/extension.test.ts`에 기존에 작성되어 있던 테스트 코드 예제를 지우고 작성하였다.

```ts
describe("converter 유틸", () => {
  describe("영어 입력을 변환기에 입력하면", () => {
    it("한글 키보드로 입력했을 때의 결과를 출력한다.", () => {
      assert.equal(
        ETTKConverter.engTypeToKor("gksrmfdmf duddj zlqhemfh dlqfurgoTdmf Eo"),
        "한글을 영어 키보드로 입력했을 때"
      );
    });
  });

  describe("한글 입력을 변환기에 입력하면", () => {
    it("영어 키보드로 입력했을 때의 결과를 출력한다.", () => {
      assert.equal(
        ETTKConverter.korTypeToEng("조두 쇼ㅔㄷ 두히ㅑ노 ㅑㅜ ㅏㅐㄱㄷ무 ㅏ됴ㅠㅐㅁㄱㅇ"),
        "when type english in korean keyboard"
      );
    });
  });
});
```

Sidebar의 Run 메뉴에서 테스트를 선택한 후 시작하면 테스트가 진행되고 결과를 바로 보여준다.

---

핵심 로직이 TS로 변환한 후에도 잘 동작하고 있다는 것은 확인을 하였다.
이제 확장 프로그램을 본격적으로 구현을 해야 하는데 이 부분은 vs code의 api 영역이다.
따라서 나는 이 부분은 처음 접한 것이며, 구글 검색과 ChatGPT의 도움을 통해서 찾아나가면서 구현하였다.
또한 기본으로 생성된 예제의 구조를 최대한 활용하였다.

내가 기대했던 기능 구현 방향은

1. 잘 못 입력된 부분을 drag로 선택하고
2. 오른쪽 마우스를 눌러
3. 메뉴를 선택하면
4. 해당 선택 영역이 제대로 입력했을 때의 값으로 변환되는 것이였다.

우선은 내가 사용할 기능을 json에 등록해야 한다.
기존에 있던 내용들을 지우고 아래와 같이 입력해주었다.

```json
"contributes": {
  "commands": [
    {
      "command": "ettk.engTypeToKor",
      "title": "영어 키보드 입력을 한글로"
    },
    {
      "command": "ettk.korTypeToEng",
      "title": "한글 키보드 입력을 영어로"
    }
  ],
  "menus": {
    "editor/context": [
      {
        "command": "ettk.engTypeToKor",
        "when": "editorTextFocus"
      },
      {
        "command": "ettk.korTypeToEng",
        "when": "editorTextFocus"
      }
    ]
  }
}
```

command를 등록해주었고, 내가 등록한 command가 어떤 상황에서 메뉴에 떠야하는지를 명시를 해주었다.

이후 등록한 command를 src/extension.ts 에서 구현해주면 된다.
아래와 같이 구현해주었다.

```ts
const engTypeToKorCommand = vscode.commands.registerCommand(
  "ettk.engTypeToKor",
  () => {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      const selectedText = editor.document.getText(editor.selection);
      editor.edit((builder) => {
        builder.replace(
          editor.selection,
          ETTKConverter.engTypeToKor(selectedText)
        );
      });
    }
  }
);
context.subscriptions.push(engTypeToKorCommand);

const korTypeToEngCommand = vscode.commands.registerCommand(
  "ettk.korTypeToEng",
  () => {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      const selectedText = editor.document.getText(editor.selection);
      editor.edit((builder) => {
        builder.replace(
          editor.selection,
          ETTKConverter.korTypeToEng(selectedText)
        );
      });
    }
  }
);
context.subscriptions.push(korTypeToEngCommand);
```

코드는 별거 없이 심플하다.
앞서 계획한 시나리오 대로 현재 선택된 영역의 text값을 가져와서 converter를 통해 변환을 해주고, 해당 값을 치환(replace) 해준다.

Extension run 을 통해 정상적으로 동작하는지 확인하면 구현은 마무리 된다.

---

이제 등록이 남아있다.
등록도 마찬가지로 공식문서를 참고하면 된다.

@vscode/vsce 를 아래와 같이 설치해주고

```
pnpm install -g @vscode/vsce
```

안내에 따라 package 과정과 publish 과정을 거치면 되는데 pnpm을 사용할 경우 그냥 vsce package 나 vsce publish 를 사용하면 에러가 발생하였다.  
[vsce의 깃헙 이슈 페이지](https://github.com/microsoft/vscode-vsce/issues/421#issuecomment-1038911725)를 찾아보니 pnpm을 거쳐 아래와 같이 명령어를 입력하면 문제없이 된다는 팁이 있었다.

```
"package": "pnpm vsce package --no-dependencies"
"publish": "pnpm vsce publish --no-dependencies"
```

위 명령어 대로 하니 문제없이 잘 진행되었다.

---

publish를 위해서는 준비해줘야 하는 것들이 꽤 있다. 가이드에 설명이 있으니 요약해서만 적는다.

- [Azure DevOps](https://azure.microsoft.com/services/devops/)에 가입하여 Personal Access Token을 발급받아야 한다.  
  `vsce login` 을 통해 발급받은 토큰을 등록할 수 있다.
- [Market Place](https://marketplace.visualstudio.com/manage) 에도 등록을 해줘야 한다.
- **package.json**에 이것저것 추가를 해줘야 한다.

  - "icon" : 아이콘 이미지를 등록해줘야 한다. 이미지 크기는 128x128 이면 된다고 한다.  
    참고 : [https://stackoverflow.com/a/42877217](https://stackoverflow.com/a/42877217)
  - "repository" : 해당 프로젝트의 repository 주소를 등록해줘야 한다. 등록하지 않으면 아래와 같이 워닝이 계속 발생된다.

    > A 'repository' field is missing from the 'package.json' manifest file.
    > Do you want to continue? [y/N] N

    ```
    "repository": {
      "type": "git",
      "url": "https://github.com/dev-jonghoonpark/ettk-vscode-extention"
    },
    ```

    나는 이렇게 추가해주었다.

  - "publisher": Market Place 에 등록한 publisher id를 입력하면 되는것으로 보인다. 입력하지 않으면 아래와 같이 에러가 발생한다.

    > Missing publisher name.

    ```
    "publisher": "dev-jonghoonpark"
    ```

    이렇게 추가해주었다.

# 결과

성공적으로 등록을 마쳤다. 무료로 등록이 가능하니 아이디어가 있는 개발자라면 본인의 extension을 등록해봐도 좋을 것 같다.

[github](https://github.com/dev-jonghoonpark/ettk-vscode-extention) , [visual studio marketplace](https://marketplace.visualstudio.com/items?itemName=dev-jonghoonpark.ettk)

데모 영상
![demo](/assets/images/2023-10-19-how-to-create-vscode-extension/demo.gif)
