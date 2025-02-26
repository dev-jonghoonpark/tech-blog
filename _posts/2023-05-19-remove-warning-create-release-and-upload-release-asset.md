---
layout: "post"
title: "Github Action - create-release, upload-release-asset warning 제거하기"
description: "Github Action에서 deprecated 경고를 제거하기 위해, 기존의 `actions/create-release@v1`\
  \ 및 `actions/upload-release-asset@v1.0.1` 대신 `softprops/action-gh-release`를 사용하여\
  \ 워크플로우를 수정하는 방법을 설명합니다. 이를 통해 APK 빌드 및 릴리즈 과정을 단일 job으로 통합하고, 경고 없이 성공적으로 릴리즈할\
  \ 수 있습니다."
categories:
- "개발"
tags:
- "Github Action"
- "create-release"
- "upload-release-asset"
- "workflow"
- "release"
- "artifacts"
- "deprecated"
- "warning"
date: "2023-05-19 04:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-05-19-remove-warning-create-release-and-upload-release-asset.jpg"
---

어제 workflow를 구축하고 잘 릴리즈가 되고 있었다.
(관련글 : [안드로이드 - Github Action을 이용하여 Signed APK 빌드하기](/2023/05/19/build-signed-apk-using-github-action))

그런데 아쉬운 것이 빌드 과정중에 warning이 나오고 있었다.
deprecated 관련 warning이였는데 평소에 deprecated 된 걸 최대한 안쓰려 하는 편이라 저걸 제거해 봐야 겠다는 생각이 들었다.

warning은 아래와 같이 나오고 있었다.

> Node.js 12 actions are deprecated. Please update the following actions to use Node.js 16: actions/create-release@v1, actions/upload-release-asset@v1.0.1.

![warnings in github action build](/assets/images/2023-05-19-remove-warning-create-release-and-upload-release-asset/image1.png)

우선 [actions/create-release@v1](https://github.com/actions/create-release), [actions/upload-release-asset@v1.0.1](https://github.com/actions/upload-release-asset) 는 현재 repository가 readonly 상태이다.

그러면 어떻게 대체할 수 있을까를 확인해봐야 하는데 repository의 readme를 보면 대체 할 수 있는 레포지토리들을 소개해 주고 있다는 것을 확인할 수 있다.

![readme of release api](/assets/images/2023-05-19-remove-warning-create-release-and-upload-release-asset/image2.png)

이 중 [softprops/action-gh-release](https://github.com/softprops/action-gh-release) 를 선택하였는데 그 이유는 create-release의 기능과 upload-release-asset의 기능 두 가지를 모두 대체 가능하며 가장 많은 사람들이 사용하고 있었기 때문이다.

이에 따라 바뀐 release-apk.yml 은 다음과 같다.

```yml
name: release apk

on:
  push:
    branches:
      - main

jobs:
  apk:
    name: Generate and Release APK
    runs-on: ubuntu-latest
    permissions: write-all
    steps:
      - name: Checkout
        uses: actions/checkout@v1
      - name: Setup JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: "17"
          distribution: "temurin"
      - name: Generate Keystore file from Github Secrets
        run: |
          echo "${{ secrets.APP_KEYSTORE_BASE64 }}" > ./keystore.b64
          base64 -d -i ./keystore.b64 > ./${{ secrets.KEYFILE }}
          cp ./${{ secrets.KEYFILE }} ./app/${{ secrets.KEYFILE }}
      - name: Build Signed APK
        run: |
          bash ./gradlew assembleRelease \
            -Pandroid.injected.signing.store.file=${{ secrets.KEYFILE }} \
            -Pandroid.injected.signing.store.password=${{ secrets.STORE_PASSWORD }} \
            -Pandroid.injected.signing.key.alias=${{ secrets.KEY_ALIAS }} \
            -Pandroid.injected.signing.key.password=${{ secrets.KEY_PASSWORD }} \
            --stacktrace
      - name: set now
        run: |
          echo "now=v$(date +'%Y.%m.%d.%H%M')" >> $GITHUB_ENV
      - name: Create Release
        id: create_release
        uses: softprops/action-gh-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ env.now }}
          files: |
            app/build/outputs/apk/release/app-release.apk
```

job을 하나로 통일해서 처리해 주었다.

---

이렇게 수정하면 아래 아무런 warning 없이 깔끔하게 성공하는 것을 확인 할 수 있다.

![result with new workflow](/assets/images/2023-05-19-remove-warning-create-release-and-upload-release-asset/image3.png)
