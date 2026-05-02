---
layout: "post"
title: "OpenJDK PR 전 테스트 진행하기"
description: "OpenJDK에 기여할 때 내 아키텍처 외의 플랫폼에서도 테스트하는 방법을 정리합니다. GitHub Actions 기반 pre-submit 테스트와 Skara 봇의 활용법을 소개합니다."
categories:
  - "개발"
tags:
  - "JDK"
  - "OpenJDK"
  - "오픈소스 기여"
  - "테스트"
  - "GitHub Actions"
date: "2026-05-01 00:00:00 +0900"
toc: true
---

## 내 아키텍처 외의 플랫폼은 어떻게 테스트하지?

OpenJDK에 기여하면서 항상 어려웠던 부분이 있었다. 내가 사용하는 머신들(예: macOS arm, linux x86-64)에서는 빌드하고 테스트를 돌릴 수 있지만, 그 외의 다른 플랫폼에서도 내 변경이 문제 없이 제대로 동작하는지는 어떻게 확인하는지에 대한 부분이였다.

이 고민에 답을 찾게 된 건 리뷰어의 한마디 덕분이었다.

[JDK-8379867](https://bugs.openjdk.org/browse/JDK-8379867) PR을 올렸을 때, 리뷰어인 eme64가 이런 코멘트를 남겼다.

> "변경사항은 좋다. 다시 직접 테스트를 돌리고 싶진 않고, GitHub Actions의 pre-submit 테스트에 맡기고 싶다. 지금 보니 비활성화되어 있으니, pre-submit 테스트가 돌도록 해달라."

이 말을 보고 처음으로 fork 저장소의 GitHub Actions를 통한 크로스 플랫폼 테스트 방법을 알게 되었다.

## GitHub Actions 기반 Pre-submit 테스트

OpenJDK는 [Skara](https://wiki.openjdk.org/display/SKARA) 프로젝트를 통해 GitHub 기반 개발 워크플로우를 제공하고 있다. 그 중 하나가 fork 저장소에서의 GitHub Actions를 활용한 pre-submit 테스트다.

원리는 단순하다. 기여자가 자신의 fork에서 GitHub Actions를 활성화하면, 브랜치에 커밋을 push할 때마다 Linux, macOS, Windows 세 플랫폼에서 자동으로 빌드와 테스트가 실행된다. 즉, 내가 직접 Linux 머신이나 Windows 머신을 갖고 있지 않아도, GitHub의 인프라를 통해 크로스 플랫폼 검증이 가능한 것이다.

## Skara Testing 문서 정리

OpenJDK의 [Skara Testing 문서](https://wiki.openjdk.org/display/SKARA/Testing)에서는 GitHub Actions를 이용한 테스트 방법을 다음과 같이 안내하고 있다.

### 워크플로우 활성화

fork 저장소를 새로 만들면 GitHub Actions가 기본적으로 비활성화되어 있다. fork의 Actions 탭에 가면 "Workflows aren't being run on this forked repository"라는 메시지가 표시된다. 여기서 **"I understand my workflows, go ahead and enable them"** 버튼을 클릭하면 활성화된다.

### 테스트 트리거

GitHub Actions가 활성화된 상태에서 fork의 브랜치에 커밋을 push하면 자동으로 빌드와 테스트가 실행된다. 수동으로 특정 커밋에 대해 재실행하는 것도 가능하다.

### 결과 분석

테스트가 실행되면 Skara 봇이 PR의 checks 영역에 빌드/테스트 결과 요약을 자동으로 표시해준다. 각 빌드/테스트 실행의 로그는 GitHub Actions 탭에서 확인할 수 있고, 테스트 실행의 추가 출력은 artifact로 다운로드할 수도 있다.

### 선택적 활성화/비활성화

모든 push마다 테스트가 도는 것이 부담스러울 수 있다. 이를 위해 두 가지 옵션이 제공된다.

- **`JDK_SUBMIT_FILTER`**: GitHub Secret으로 설정하면 `submit/` prefix가 붙은 브랜치에 push할 때만 테스트가 트리거된다. 테스트를 돌리고 싶을 때만 아래처럼 push하면 된다.

```bash
git push origin <브랜치명>:submit/<브랜치명>
```

- **`JDK_SUBMIT_PLATFORMS`**: GitHub Secret으로 설정하면 특정 플랫폼에서만 테스트를 실행할 수 있다. 사용 가능한 플랫폼은 `Linux x64`, `Linux x86`, `Linux additional (hotspot only)`, `Windows x64`, `macOS x64`이다.

### 빌드 및 테스트 범위

GitHub Actions에서 실행되는 빌드와 테스트 범위는 다음과 같다.

**빌드:**

| 플랫폼         | Release | Debug | 비고                         |
| -------------- | ------- | ----- | ---------------------------- |
| Linux x86-64   | O       | O     | PCH 없는 Release 빌드도 포함 |
| macOS x86-64   | O       | O     |                              |
| Windows x86-64 | O       | O     |                              |

**테스트:**

- tier1 테스트를 Linux x86-64, macOS x86-64, Windows x86-64 세 플랫폼에서 실행한다.

### 로컬 실행

GitHub Actions에서 도는 것과 동일한 테스트를 로컬에서 실행하려면 다음 명령어를 사용하면 된다.

```bash
make test-tier1
```

GitHub Actions에서는 release와 debug 빌드 모두에서 테스트를 실행한다는 점을 참고하자. 더 자세한 테스트 실행 방법은 JDK 저장소의 `doc/testing.md`에서 확인할 수 있다.

## 실제 적용 과정

실제로 내가 했던 과정은 다음과 같다.

1. fork 저장소([dev-jonghoonpark/jdk-forked](https://github.com/dev-jonghoonpark/jdk-forked))의 Actions 탭에서 GitHub Actions를 활성화했다.
2. 최신 master를 머지한 뒤, PR 브랜치에 push했다.
3. Actions 탭에서 여러 플랫폼의 빌드와 tier1 테스트가 돌기 시작하는 것을 확인했다.
4. 모든 테스트가 통과한 후 리뷰어에게 완료를 알렸다.

빌드와 테스트는 여러 플랫폼에서 동시에 실행되기 때문에 보통 몇 시간 정도 소요된다. 시간이 걸리는 만큼 push 전에 로컬에서 `make test-tier1`로 먼저 확인하고, GitHub Actions는 크로스 플랫폼 검증용으로 활용하는 것이 효율적이다.

## 비용은?

GitHub Actions는 public 저장소에 대해 무제한 무료 실행 시간을 제공한다. OpenJDK의 jdk 저장소는 public이고, fork도 기본적으로 public으로 생성되므로 비용 걱정 없이 사용할 수 있다. 참고로 private 저장소의 경우에는 무료 플랜 기준 월 2,000분의 제한이 있다.

## 마무리

이 방식은 OpenJDK에만 국한되지 않을 것이다. 다른 오픈소스 프로젝트에서도 GitHub Actions를 사용하는 오픈소스 프로젝트라면 대부분 동일한 방식으로 fork에서 CI를 활성화할 수 있다. `.github/workflows` 디렉토리에 워크플로우 정의가 있는 프로젝트라면, fork의 Actions 탭에서 활성화하고 push하면 해당 워크플로우가 실행된다.

기여자 입장에서 이것이 의미하는 바는 크다. 내가 직접 여러 OS 환경을 갖추지 않아도, PR을 올리기 전에 프로젝트가 지원하는 모든 환경에서 내 변경사항을 검증할 수 있다는 뜻이다. 리뷰어에게도 "테스트 다 통과했습니다"라고 자신 있게 말할 수 있고, 리뷰 과정도 그만큼 수월해진다.
