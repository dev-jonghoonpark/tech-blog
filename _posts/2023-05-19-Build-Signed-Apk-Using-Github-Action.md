---
layout: post
title: 안드로이드 - Github Action을 이용하여 Signed APK 빌드하기
categories: [개발]
tags:
  [
    안드로이드,
    Android,
    Github Action,
    Sign APK,
    env,
    workflow,
    release,
    keystore,
  ]
date: 2023-05-19 12:00:00 +0900
---

# 개요

저는 3개의 핸드폰을 가지고 있습니다.

용도에 따라서 핸드폰과 번호를 분리해서 사용중인데요

사실 3개의 폰을 항상 들고 다니는 일은 어렵기 때문에 필요에 따라 핸드폰을 1~2개 를 들고 다니고 있습니다.  
그러다보니 3개의 핸드폰에서 오는 알림들을 공유해서 볼 수 있는 앱이 있으면 좋겠다 싶어서 시간이 날때마다 만들고 있습니다.

아무래도 현재 QA 엔지니어로 일하고 있기 때문에 추후에는 알림 수집 기능을 푸시 알림 기능 테스트에 활용할 수 있도록 구조를 조금씩 개선해 볼 예정입니다.

# 구현

workflow 코드는 다음과 같습니다.

해당 파일을 push 하려면 workflow 권한이 있는 token으로 push를 해야합니다.

.github/workflows/release-apk.yml

```yml
name: release apk

on:
  push:
    branches:
      - main

jobs:
  apk:
    name: Generate APK
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v1
      - name: Setup JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: "17"
          distribution: "temurin"
      #      - name: Build APK
      #        run: bash ./gradlew assembleDebug --stacktrace
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
      - name: Upload APK
        uses: actions/upload-artifact@v1
        with:
          name: apk
          path: app/build/outputs/apk/release/app-release.apk
  release:
    permissions: write-all
    name: Release APK
    needs: apk
    runs-on: ubuntu-latest
    steps:
      - name: set now
        run: |
          echo "now=v$(date +'%Y.%m.%d.%H%M')" >> $GITHUB_ENV
      - name: Download APK from build
        uses: actions/download-artifact@v1
        with:
          name: apk
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ env.now }}
          release_name: Release ${{ env.now }}
      - name: Upload Release APK
        id: upload_release_asset
        uses: actions/upload-release-asset@v1.0.1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: apk/app-release.apk
          asset_name: ${{ github.event.repository.name }}.apk
          asset_content_type: application/zip
```

workflow를 작성하면서 좀 해맸던 것이  
github action에 생소한 것도 있지만 인터넷에 있는 정보들이 부분적으로 있거나 옛날 정보가 섞여있어서 겪는 부분들이 많았습니다.

위의 코드는 제가 사용한 실제로 동작한 코드이기에 secret 변수 값을 잘 설정한다면 별 문제 없이 동작할 것이지만  
왜 이렇게 작성을 하였을까 에 대한 부분을 남겨보고자 작성 중 겪은 부분들에 대해서 정리합니다.

## 구현 상세

### 1. gradle jdk 버전

gradle 8.0 은 비교적 최근에 나온 버전이기 때문에 jdk 버전도 최근 것으로 맞춰줘야 했다.

jdk 17로 설정하도록 하였다.

### 2. secrets 값

위에 작성된 yml 에서는 5개의 값을 사용한다.

![env variables](/assets/images/2023-05-19-Build-Signed-Apk-Using-Github-Action/image1.png)

먼저 KEYSTORE의 BASE64 값은 openssl을 통해서 얻을 수 있다.

```bash
openssl base64 -in [키스토어 파일명] -out [저장될텍스트파일명]
```

KEYFILE에는 정확하게 확장자를 포함한 파일명(ex. xxx.jks)만 넣어주면 동작하게 작성 해두었다.  
(사실, KEYFILE의 경우 yml에 하드코딩해도 문제는 없을 것 같다.)

왜인지 모르겠는데 project root와 app root 경로에 모두 keyfile이 있어야 빌드과정에서 에러없이 처리가 되었다. 그래서 cp 를 통해서 두 위치에 모두 들어갈 수 있도록 처리하였다. (지금 생각해보니 심볼릭 링크를 사용해도 좋았을 것 같다.)

### 3. app-release.apk 생성위치

./gradlew assembleRelease 명령어를 통해서 생성된 apk는 app/release/app-release.apk 에 있지 않다.  
(안드로이드 스튜디오를 통해서 생성하면 저 경로에 생성되기 때문에 당연히 저 경로에 생성될 줄 알았다.)

app/build/outputs/apk/release/app-release.apk 에 있다.

### 4. github에 릴리즈 하기

릴리즈하는 workflow job에 permissions: write-all 를 추가해줘야 정상적으로 릴리즈 할 수 있다.

### 5. set-env, set-output deprecated

릴리즈를 하려면 tag_name과 release_name이 무조건 설정되어야 한다.  
시간 기반으로 자동으로 생성되도록 처리하기를 원했고 그 과정에서 변수를 생성해야 했는데 사용 방법이 변경되었다.

[https://github.blog/changelog/2020-10-01-github-actions-deprecating-set-env-and-add-path-commands/](https://github.blog/changelog/2020-10-01-github-actions-deprecating-set-env-and-add-path-commands/)

[https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/](https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/)

# 결과

릴리즈 workflow가 정상적으로 종료되면 다음과 같이 등록된 것을 확인 할 수 있습니다.

![release result](/assets/images/2023-05-19-Build-Signed-Apk-Using-Github-Action/image2.png)

개인 프로젝트에 github action 이용해서 signed apk 빌드 자동화를 해보았는데 일단 private repositorty 여도 무료로 사용가능하다는게 좋았습니다.
시간은 당연하게 맥에서 직접 빌드하는것보다는 느렸지만 그래도 자동화 되어서 빌드 결과물이 나온다는게 좋았습니다.

# 참고

[Github에서 Keystore를 Secret Key로 반영하기(feat. Android)](https://blog.soobinpark.com/232)

이 코드는 다음글에서 조금 더 개선되었습니다.
[Github Action - create-release, upload-release-asset warning 제거하기](/2023/05/19/remove-warning-create-release-and-upload-release-asset)
