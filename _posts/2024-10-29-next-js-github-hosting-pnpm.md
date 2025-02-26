---
layout: "post"
title: "[pnpm] github action 을 이용하여 github pages 에 next.js 프로젝트 배포하기"
description: "Next.js 프로젝트를 GitHub Action을 이용해 GitHub Pages에 배포하는 방법을 소개합니다. 기본 YAML\
  \ 템플릿을 참고하여 pnpm을 사용한 설정을 추가하고, 성공적으로 배포하는 과정을 설명합니다. 이 글에서는 GitHub Pages에 배포하기\
  \ 위한 YAML 파일 구성과 필요한 단계들을 자세히 안내합니다."
categories:
- "개발"
tags:
- "github"
- "github action"
- "github pages"
- "pnpm"
- "배포"
- "deploy"
- "hosting"
- "호스팅"
- "nextjs"
- "next"
- "react"
date: "2024-10-29 14:59:59 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-10-29-next-js-github-hosting-pnpm.jpg"
---

개인 프로젝트로 next.js 를 선택하였다.
그래서 next.js 를 github action을 이용해서 github pages로 바로 배포할 수 있으면 좋겠다는 생각이 들었다.

next.js 프로젝트로 github pages 세팅을 하면 github 에서 자동으로 기본 yaml 템플릿을 제안해주는데
이 제안을 선택하면 yarn 과 npm 에서 사용할 수 있는 yaml 파일이 생성된다.

나의 경우에는 node 기반 프로젝트를 진행할 때에는 pnpm을 사용하는걸 좋아하다 보니 기본 npm 보다 조금 더 세팅이 필요한 편이다.
그래서 관련된 정보를 구글에 검색해 보았는데 나도 기억 못했던 내 블로그글이 상단에 떠서 오랜만에 확인해보았다.

[[pnpm] firebase hosting과 github action 연결하기](https://jonghoonpark.com/2023/08/26/firebase-hosting-deploy-via-github-aciton-with-pnpm)

위 글의 내용과 기본 yaml 템플릿을 참고하여 아래와 같이 구성하였고 성공적으로 배포되었기 때문에 공유해본다.

이번에는 github action을 통해 firebase hosting 이 아닌 github pages 에 배포하는 것을 목표로 한다. 참고로 기본 템플릿에서 npm과 yaml을 위해 작성되어 있던 부분은 그냥 제거하였다.

```yaml
# Sample workflow for building and deploying a Next.js site to GitHub Pages
#
# To get started with Next.js see: https://nextjs.org/docs/getting-started
#
name: Deploy Next.js site to Pages

on:
  # Runs on pushes targeting the default branch
  push:
    branches: ["main"]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment, skipping runs queued between the run in-progress and latest queued.
# However, do NOT cancel in-progress runs as we want to allow these production deployments to complete.
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  # Build job
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: pnpm/action-setup@v4
        with:
          version: 9
          run_install: false

      - name: Setup Pages
        uses: actions/configure-pages@v5
        with:
          # Automatically inject basePath in your Next.js configuration file and disable
          # server side image optimization (https://nextjs.org/docs/api-reference/next/image#unoptimized).
          #
          # You may remove this line if you want to manage the configuration yourself.
          static_site_generator: next

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: "pnpm"

      - name: Install dependencies
        run: pnpm install

      - name: Build with Next.js
        run: pnpm next build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./out

  # Deployment job
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

해당 파일을 `/.github/workflows/nextjs.yml` 에 추가하면 성공적으로 빌드되어 github pages 에 배포까지 진행되는것을 확인할 수 있다.

![github-action-success](/assets/images/2024-10-29-next-js-github-hosting-pnpm/github-action-success.png)
