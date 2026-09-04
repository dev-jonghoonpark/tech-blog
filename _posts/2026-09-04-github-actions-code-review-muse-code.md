---
layout: "post"
title: "GitHub PR 코드리뷰를 Muse Code로 바꿔보았다"
description: "Gemini Code Assist 컨슈머 버전이 종료돼 Claude Code로 옮겼는데, 이번엔 코드리뷰가 구독 사용량을 갉아먹었다. Meta의 Muse Code로 갈아타며 정리한 것들 — Opus 5와의 단가·벤치마크 비교, 학습에 코드가 쓰이는 contributor 티어를 고른 이유, 만료되는 OAuth 토큰 대신 정적 API 키를 쓰게 된 점, 그리고 실측 비용."
categories:
  - "개발"
tags:
  - "GitHub Actions"
  - "코드리뷰"
  - "Muse Code"
  - "Muse Spark"
  - "Claude Code"
  - "Opus 5"
  - "Gemini Code Assist"
  - "K-DEVCON"
  - "LLM"
  - "CI"
date: "2026-09-04 21:10:00 +0900"
toc: true
image:
  path: "/assets/thumbnails/2026-09-04-github-actions-code-review-muse-code.jpg"
---

## 들어가며

K-DEVCON 프로젝트들에 원래는 GitHub Gemini Code Review를 쓰고 있었다. 앱만 붙여두면 알아서 리뷰를 달아줬고 무료라 신경 쓸 일도 없었다. 그런데 어느 날 PR에 리뷰 대신 이런 코멘트가 달렸다.

![Gemini Code Assist 봇이 남긴 서비스 종료 안내 코멘트](/assets/images/2026-09-04-github-actions-code-review-muse-code/gemini-code-assist-sunset.png)

> The consumer version of Gemini Code Assist on GitHub has been sunset. All code review activity has officially ceased.

찾아보니 컨슈머(무료) 버전은 2026년 6월 18일에 deprecated 됐고 7월 17일에 완전히 종료됐고 엔터프라이즈 버전만 남았다. 잘 사용하던 리뷰어가 하루아침에 사라져버렸다.

임시로 `anthropics/claude-code-action`에 Claude Opus 5를 물려서 리뷰가 돌도록 액션을 구성해뒀다. 리뷰 품질 자체는 만족스러웠다. 그렇게 쓰다 보니 코드리뷰에서도 토큰이 꽤 많이 나가는 것처럼 느껴졌다.

개인적으로 월 $100짜리 Claude 플랜을 쓰고 있다. 평일에는 회사 일을 하느라 거의 못 쓰는 게 좀 아깝긴 한데 또 막상 붙잡고 앉으면 사용량 한도를 다 쓴다. 정작 내가 쓰려고 할 때 한도에 걸리는 상황이 반복되니 코드리뷰가 조용히 갉아먹고 있는 사용량부터 줄이고 싶었다.

싼 모델을 찾다 보니 GLM이 눈에 들어왔다. 단가만 놓고 보면 후보로 충분했다. 중국 쪽 모델이라는 점에서 선뜻 손이 가지 않아 결정을 못 하고 미뤄두고 있었다.

그러던 차에 Muse Code 소식을 들었다. 이거다 싶었다. Meta가 내놓은 터미널 코딩 에이전트인데 백엔드 모델인 Muse Spark 1.3에는 토큰 단가가 확 낮은 contributor 티어가 있었다. 고민할 것 없이 바로 붙여봤다.

## Muse Code가 뭔가

Meta가 내놓은 터미널용 코딩 에이전트다. Claude Code와 포지션이 거의 같다. 대화형 TUI로도 쓰고 CI에서는 헤드리스로 한 번만 실행하는 `muse exec` 모드를 쓴다.

설치는 이렇다.

```bash
curl -fsSL https://dev.meta.ai/install.sh | bash
```

`~/.local/bin/muse`에 바이너리를 떨어뜨린다. 헤드리스 실행은 이런 형태다.

```bash
muse exec \
  --provider meta \
  --model muse-spark-1.3-contributor \
  --reasoning-effort medium \
  --max-model-steps 30 \
  --prompt-file ./prompt.md
```

Claude Code를 써봤다면 옵션 대응은 금방 감이 온다.

| 하려는 것          | Claude Code                   | Muse Code                               |
| ------------------ | ----------------------------- | --------------------------------------- |
| 턴 수 제한         | `--max-turns`                 | `--max-model-steps`                     |
| 추론 깊이 조절     | `--model` 선택 / effort       | `--reasoning-effort`                    |
| 툴 권한            | `--allowedTools` 화이트리스트 | `--approval-mode` / `--sandbox-network` |
| 결과를 기계가 읽기 | stream-json                   | `--json` (JSONL)                        |

눈에 띄는 차이는 툴 권한 모델이다. Claude Code는 "이 툴만 허용"이라고 나열하는 방식인데 Muse Code는 승인 모드(`untrusted` / `on-request` / `never`)와 샌드박스 설정으로 제어한다. 세밀한 화이트리스트를 짜던 사람이라면 그대로 옮기긴 어렵고 승인 정책 + 샌드박스 조합으로 다시 생각해야 한다.

## 비용: Opus 5와 얼마나 차이 나나

먼저 단가부터. 백만 토큰당 가격이다.

| 모델                         | 입력  | 캐시된 입력 | 출력   | 컨텍스트 |
| ---------------------------- | ----- | ----------- | ------ | -------- |
| `claude-opus-5`              | $5.00 | —           | $25.00 | 1M       |
| `muse-spark-1.3` (표준)      | $1.25 | $0.15       | $4.25  | 1M       |
| `muse-spark-1.3-contributor` | $0.10 | $0.002      | $0.20  | 1M       |

단가 출처는 [Meta Model API 요금·레이트리밋 문서](https://dev.meta.ai/docs/pricing-rate-limits)와 [Anthropic 요금 문서](https://platform.claude.com/docs/en/pricing)다. Muse 쪽은 [OpenRouter의 contributor 모델 페이지](https://openrouter.ai/meta/muse-spark-1.3-contributor)에서도 같은 숫자를 확인할 수 있다.

표준 티어만 해도 Opus 5 대비 입력 1/4, 출력 약 1/6이다. contributor는 자릿수가 달라진다. 입력 1/50, 출력 1/125.

PR 리뷰 한 번에 입력 5만 토큰, 출력 5천 토큰을 쓴다고 가정하면 이렇게 된다. (어디까지나 가정 계산이다. 실측은 아래에서 따로 이야기한다.)

기존 Claude 액션은 구독 토큰으로 붙여둔 거라 이 금액이 실제로 청구되던 건 아니다. 대신 구독 사용량을 깎아먹었다. 아래 Opus 5 열은 "같은 리뷰를 API로 돌렸다면" 기준의 환산값으로 보면 된다.

| 모델                         | 리뷰 1회 비용 | 월 200회 |
| ---------------------------- | ------------- | -------- |
| `claude-opus-5`              | 약 $0.375     | 약 $75   |
| `muse-spark-1.3`             | 약 $0.084     | 약 $17   |
| `muse-spark-1.3-contributor` | 약 $0.006     | 약 $1.2  |

리뷰는 diff 전체를 컨텍스트에 넣기 때문에 입력 토큰 비중이 크고 출력은 코멘트 몇 개라 상대적으로 적다. 입력 단가가 50배 차이 나는 게 그대로 총액에 반영된다. 캐시된 입력 단가($5.00 → $0.002)까지 보면 차이는 더 벌어진다.

## 성능: 싼 만큼 못 하나

여기가 궁금했던 부분이다. 아래 두 표는 Meta가 [Muse Spark 1.3 발표 글](https://research.meta.ai/blog/introducing-muse-spark-1-3)에서 직접 공개한 숫자다. **모델을 만든 쪽이 낸 자체 측정치**라는 점을 감안하고 봐야 한다.

벤치마크 숫자만 보면 코딩 쪽에서는 Muse Spark 1.3이 오히려 앞선다.

| 벤치마크              | Muse Spark 1.3 | Claude Opus 5 |
| --------------------- | -------------- | ------------- |
| DeepSWE v1.1          | 75.4           | 74.0          |
| SWEAtlas CodeBase QnA | 59.4           | 52.7          |
| Terminal-Bench 2.1    | 88.8           | 86.7          |

반대로 에이전트 계열 태스크에서는 Opus 5가 일관되게 앞선다.

| 벤치마크         | Muse Spark 1.3 | Claude Opus 5 |
| ---------------- | -------------- | ------------- |
| GDPVal-AA v2     | 1754           | 1824          |
| JobBench         | 64.9           | 65.7          |
| OSWorld 2.0      | 66.9           | 68.3          |
| DeepSearchQA     | 89.4           | 90.4          |
| Agentic IF Index | 57.8           | 59.1          |

### 그런데 함정이 있다

위 표의 Muse Spark 1.3 숫자는 **max 추론 구성**에서 나온 것인데 max 구성은 아직 널리 열려 있지 않다. Meta는 추가 안전성 테스트 중이고 "곧" 풀겠다고 하는 상태다. 지금 Muse Code와 Model API로 실제로 쓸 수 있는 건 그 아래인 **xhigh** 구성이다.

같은 모델의 두 구성 차이가 꽤 난다. 이 비교는 [VentureBeat 기사](https://venturebeat.com/technology/meta-says-muse-spark-1-3-has-frontier-performance-but-its-best-results-come-from-a-model-developers-cant-broadly-use-yet)가 정리해둔 것을 옮겼다.

| 벤치마크     | max (제한 공개) | xhigh (실제 사용 가능) |
| ------------ | --------------- | ---------------------- |
| GDPval-AA v2 | 1,754 Elo       | 1,709 Elo              |
| OSWorld 2.0  | 66.9            | 57.2                   |
| JobBench     | 64.9            | 61.2                   |

[Artificial Analysis의 Muse Spark 1.3 분석](https://artificialanalysis.ai/articles/muse-spark-1-3) 기준으로 보면 Muse Spark 1.3 xhigh는 Intelligence Index 61로 Claude Opus 5 high와 같은 수준이고 Opus 5는 max에서 63까지 간다(Muse Spark 1.3 max는 62). 모델별 점수와 태스크당 비용은 [Artificial Analysis 모델 비교 페이지](https://artificialanalysis.ai/models)에서 직접 볼 수 있다.

Artificial Analysis는 자체 측정도 하는데 여기서 숫자가 갈리는 항목이 있다. Terminal-Bench 2.1이 대표적이다. Meta 자체 발표는 88.8인데 Artificial Analysis 측정은 xhigh 85 / max 86이다. 벤더 발표와 제3자 측정을 같은 표에 섞어 놓으면 이런 차이가 묻히니 숫자를 인용할 때는 어느 쪽인지 같이 적어두는 게 낫다.

"코딩 벤치마크에서 Opus 5를 이겼다"는 헤드라인은 지금 당장 내가 쓸 수 있는 구성의 이야기가 아니다. 실사용 기준으로는 **비슷하거나 약간 아래, 대신 훨씬 싸다** 정도로 보는 게 맞다. PR 리뷰라는 용도에서는 그 정도면 충분하다고 판단했다.

## contributor 티어를 고른 이유

contributor 티어가 싼 데는 이유가 있다. 입력과 출력이 **Meta의 모델 학습에 사용된다**. 표준 티어는 학습에 쓰지 않는 대신 비싸다. 단순히 "싼 요금제"가 아니라 데이터 거버넌스 문제다.

배수는 토큰 종류마다 다르다. 위 단가표를 표준 티어 기준으로 다시 보면 **입력 12.5배, 출력 21.25배, 캐시된 입력 75배**($0.15 → $0.002)다. 코드리뷰는 diff를 읽는 입력 비중이 크니 이 글에서는 입력 기준인 12.5배로 이야기한다. 가장 보수적인 숫자다.

코드리뷰 워크플로는 PR diff 전체를 모델에 넘긴다. 저장소 코드가 통째로 학습 데이터로 들어간다는 뜻이다. 회사 코드였다면 고민할 것도 없이 표준 티어를 썼을 것이다.

이 프로젝트는 그렇지 않았다.

- 커뮤니티 프로젝트다. 비공개 저장소이긴 하지만 그렇게 보안이 필요한 코드를 다루지는 않는다
- 인증 토큰이나 키는 전부 GitHub Secrets와 환경변수로 빠져 있어서 코드에 남아 있지 않다
- 비즈니스 로직에 영업 비밀이라 할 만한 게 없다. 게시글 CRUD, 이미지 업로드, OAuth 로그인 정도다

학습에 들어가서 곤란할 게 없는 코드라면, 최소 12.5배인 요금을 데이터 보호 명목으로 낼 이유가 없다. 그래서 contributor를 골랐다.

## 워크플로 구성

클로드의 코드를 받아 아래와 같이 구성했다.

### .github/workflows/muse-review.yml

{% raw %}

```yaml
name: Muse Code Review

on:
  # PR 최초 생성 시에만 자동 실행. 이후 추가 커밋(synchronize)에는 반응하지 않습니다.
  pull_request:
    types: [opened]
  # 이후 재리뷰는 PR 에 `/review` 코멘트를 달아 수동으로 트리거합니다.
  issue_comment:
    types: [created]

concurrency:
  group: muse-review-${{ github.event.pull_request.number || github.event.issue.number }}
  cancel-in-progress: true

jobs:
  review:
    name: Muse Review
    # issue_comment 는 이슈에도 발생하므로 PR 코멘트인지 확인하고,
    # 쓰기 권한이 있는 사람의 `/review` 코멘트만 허용합니다.
    if: >-
      github.event_name == 'pull_request' ||
      (github.event.issue.pull_request &&
       startsWith(github.event.comment.body, '/review') &&
       contains(fromJSON('["OWNER", "MEMBER", "COLLABORATOR"]'), github.event.comment.author_association))
    runs-on: self-hosted
    # 모델 단계가 멈췄을 때 self-hosted 러너를 무한 점유하지 않도록 상한을 둡니다.
    # 실측 리뷰 소요는 5~6분 수준입니다.
    timeout-minutes: 20
    permissions:
      contents: read
      pull-requests: write
      issues: write

    steps:
      - name: Resolve PR context
        id: pr
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPO: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number || github.event.issue.number }}
        run: |
          head_sha=$(gh pr view "$PR_NUMBER" --repo "$REPO" --json headRefOid --jq .headRefOid)
          echo "number=$PR_NUMBER" >> "$GITHUB_OUTPUT"
          echo "head_sha=$head_sha" >> "$GITHUB_OUTPUT"

      - name: Checkout PR head
        uses: actions/checkout@v4
        with:
          ref: refs/pull/${{ steps.pr.outputs.number }}/head
          fetch-depth: 0

      - name: Install Muse Code CLI
        run: |
          set -euo pipefail
          if ! command -v muse >/dev/null 2>&1; then
            curl -fsSL https://dev.meta.ai/install.sh | bash
            # 설치 위치(~/.local/bin)가 PATH 에 없을 수 있으므로 이후 스텝을 위해 등록
            echo "$HOME/.local/bin" >> "$GITHUB_PATH"
            export PATH="$HOME/.local/bin:$PATH"
          fi
          muse --version

      - name: Render review prompt
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPO: ${{ github.repository }}
          DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
          PR_NUMBER: ${{ steps.pr.outputs.number }}
          HEAD_SHA: ${{ steps.pr.outputs.head_sha }}
          PROMPT_PATH: .github/muse-review-prompt.md
        run: |
          set -euo pipefail
          mkdir -p "$RUNNER_TEMP/muse"
          raw="$RUNNER_TEMP/muse/prompt.raw.md"

          # 프롬프트는 가능하면 기본 브랜치에서 가져옵니다. issue_comment 경로에서는
          # 워크플로만 기본 브랜치 기준이고 체크아웃은 PR head 이므로, PR 쪽에서
          # 프롬프트를 수정해 리뷰어 동작을 바꾸는 것을 막기 위함입니다.
          if gh api "repos/$REPO/contents/$PROMPT_PATH?ref=$DEFAULT_BRANCH" \
               -H "Accept: application/vnd.github.raw" > "$raw" 2>/dev/null && [ -s "$raw" ]; then
            echo "prompt source: $DEFAULT_BRANCH"
          else
            # 기본 브랜치에 프롬프트가 아직 없는 경우(= 이 워크플로를 도입하는 PR)
            # 체크아웃본으로 폴백합니다. 머지 후에는 이 경로를 타지 않습니다.
            echo "::warning::기본 브랜치($DEFAULT_BRANCH)에 $PROMPT_PATH 가 없어 PR 체크아웃본을 사용합니다."
            cp "$PROMPT_PATH" "$raw"
          fi

          sed -e "s|__REPO__|$REPO|g" \
              -e "s|__PR_NUMBER__|$PR_NUMBER|g" \
              -e "s|__HEAD_SHA__|$HEAD_SHA|g" \
              "$raw" > "$RUNNER_TEMP/muse/prompt.md"
          [ -s "$RUNNER_TEMP/muse/prompt.md" ] || { echo "::error::렌더링된 프롬프트가 비어 있습니다."; exit 1; }

      - name: Muse Code Review
        env:
          # 시크릿에는 Model API 대시보드에서 발급한 API 키가 들어 있습니다.
          # META_API_KEY: Muse Code CLI 가 읽는 변수. 저장된 로그인 세션보다 우선합니다.
          # MODEL_API_KEY: Model API / 공식 SDK 가 읽는 변수. 같은 키를 사용합니다.
          META_API_KEY: ${{ secrets.META_API_KEY }}
          MODEL_API_KEY: ${{ secrets.META_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          muse exec \
            --provider meta \
            --model muse-spark-1.3-contributor \
            --reasoning-effort medium \
            --approval-mode never \
            --sandbox-network enabled \
            --max-model-steps 30 \
            --prompt-file "$RUNNER_TEMP/muse/prompt.md"
```

{% endraw %}

#### 만료되는 토큰 vs 정적 키

Claude Code를 액션에서 쓰려면 OAuth 토큰에 만료가 있어서 주기적으로 갱신해줘야 한다. 어느 날 리뷰가 안 도는 걸 보고 "아 토큰 만료됐구나" 하고 다시 발급받아 시크릿에 넣는 일이 반복된다. Muse는 대시보드에서 발급한 정적 API 키를 그대로 계속 쓴다. 넣어두고 잊어버리면 된다.

물론 만료가 있는 쪽이 보안상으로는 낫다. 키가 유출돼도 수명이 있으니깐. 다만 개인이 사이드로 굴리는 워크플로에서 그것을 주기적으로 갱신해줘야 하는 것은 꽤 성가시다.

### .github/muse-review-prompt.md

`__REPO__`, `__PR_NUMBER__`, `__HEAD_SHA__` 세 자리는 워크플로의 `sed`가 채운다. 프롬프트의 리뷰 관점과 심각도 배지 규칙도 Claude Code 가 작성해준 것이다.

```markdown
REPO: **REPO**
PR NUMBER: **PR_NUMBER**

이 Pull Request의 변경 사항을 코드 리뷰해 주세요. 리뷰는 한국어로 작성합니다.

**이 PR의 변경된 파일(diff)만** 리뷰 대상입니다. 변경과 무관한 코드베이스
탐색은 최소화하고, 간결하게 진행하세요.

먼저 `gh pr diff __PR_NUMBER__`로 변경된 코드를 확인한 뒤, 아래 관점으로 검토하세요:

- 버그 및 로직 오류, 엣지 케이스 누락
- 보안 취약점 (입력 검증, 인증/인가, 시크릿 노출 등)
- 코드 품질 / 가독성 / 유지보수성, 프로젝트 컨벤션 준수
- 성능 및 리소스 관리 이슈
- 테스트 커버리지

리뷰 방식:

- **반드시** 마지막에 `gh pr comment __PR_NUMBER__ --body "..."` 를 실행해 총평
  코멘트를 1개 남기세요. 이것은 필수이며, 코멘트를 남기지 않고 종료하면 안 됩니다.
  리뷰 내용을 응답 텍스트로만 쓰고 끝내지 마세요.
- 총평 코멘트의 **맨 첫 줄**에는 이번 리뷰의 전체 심각도/중요도를 나타내는
  배지를 반드시 넣으세요. 발견된 이슈 중 **가장 높은 심각도**를 기준으로
  아래 4개 중 하나를 그대로 복사해 사용합니다(어떤 것이 필수 수정인지 한눈에
  보이도록 하는 것이 목적입니다):
  - 머지 전 반드시 고쳐야 하는 버그/보안/장애 위험:
    `![review](https://img.shields.io/badge/review-MUST_FIX-critical) 🔴 **필수 수정 — 머지 전 반드시 수정이 필요합니다.**`
  - 고치는 것이 좋으나 머지를 막지는 않는 문제:
    `![review](https://img.shields.io/badge/review-SHOULD_FIX-orange) 🟠 **권장 수정 — 수정을 권장합니다.**`
  - 사소한 개선/취향 수준의 제안:
    `![review](https://img.shields.io/badge/review-NITPICK-yellow) 🟡 **개선 제안 — 가벼운 제안 사항입니다.**`
  - 특이사항 없음:
    `![review](https://img.shields.io/badge/review-LGTM-brightgreen) 🟢 **특이사항 없음.**`
    배지 다음 줄부터 심각도별로 이슈를 그룹핑해 요약하세요.
- 지적할 문제가 전혀 없더라도 위 🟢 LGTM 배지와 함께 간단한 승인 코멘트를
  반드시 남기세요.
- 특정 코드 라인에 대한 지적은 아래 명령 형태로 인라인 코멘트를 남기되, 각 코멘트
  맨 앞에 심각도 이모지(🔴 필수 / 🟠 권장 / 🟡 제안)를 붙여 어떤 것이 필수 수정인지
  바로 구분되게 하세요:
  `gh api repos/__REPO__/pulls/__PR_NUMBER__/comments -f body="..." -f commit_id="__HEAD_SHA__" -f path="<파일경로>" -F line=<줄번호> -f side=RIGHT`
- 실제로 문제가 되는 부분만 지적하고, 사소한 취향 문제는 최소화하세요.
```

그대로 가져다 쓸 거라면 `runs-on`(self-hosted를 쓰고 있다), 모델 ID(학습에 코드가 들어가도 되는지), 시크릿 이름 세 가지는 각자 환경에 맞게 바꿔야 한다.

## 결과

워크플로가 붙었으니 실제로 도는지 봐야 했다. 실제 PR에 사용하기 전, 테스트용 PR을 하나 만들었다.

리뷰가 뭔가는 잡아내야 확인이 되니 문자열을 자르는 `truncate` 유틸을 하나 만들어 넣었다. 입력이 `null`일 때 그대로 `.length`를 읽는, 티 나게 잘못된 코드였다. 리뷰 하면서 이걸 짚어내는지 보려는 미끼였다.

5분 27초 만에 리뷰가 완료됐다. 미끼로 넣어둔 null 가드 누락을 잡아냈고 심각도 배지가 붙은 총평 코멘트 1개와 인라인 코멘트 3개를 남겼다.

### 그래서 얼마 나왔나

첫 리뷰를 돌리고 나서 대시보드를 봤을 때 누적 사용액은 15원이었다. 몇 번 더 돌린 뒤 100회 요청분의 통계를 다시 보니 이렇다.

![Meta Model API 대시보드 100회 사용량](/assets/images/2026-09-04-github-actions-code-review-muse-code/meta-model-api-dashboard.png)

| 항목      | 값      |
| --------- | ------- |
| Requests  | 100     |
| 입력 토큰 | 2.5M    |
| 출력 토큰 | 68.6k   |
| Spend     | **₩94** |

여기서 Requests는 리뷰 횟수가 아니라 **모델 호출 횟수**다. `muse exec`는 diff를 읽고 파일을 열어보고 코멘트를 다는 동안 여러 스텝을 밟는다. 워크플로에 `--max-model-steps 30`을 걸어뒀으니 리뷰 한 번이 수십 번의 요청으로 쪼개진다. 100 requests는 리뷰 대여섯 번쯤이고, 앞서 나온 리뷰 1회 15원과도 얼추 맞는다.

호출 하나당 평균을 내보면 입력 2만 5천 토큰, 출력 686 토큰, 0.94원이다. 리뷰 한 번이 diff와 파일 내용을 반복해서 컨텍스트에 싣는다는 게 입력 토큰 비중에 그대로 드러난다.

재미있는 건 총액이다. 입력 2.5M을 contributor 정가($0.10/1M)로 계산하면 $0.25, 출력까지 더해 **350원 안팎**이 나와야 한다. 실제 청구는 94원이다. 차이는 캐시된 입력이다. 에이전트 루프는 매 스텝마다 같은 프롬프트 앞부분을 다시 보내는데, 이 구간이 $0.002/1M로 읽힌다. 역산해보면 입력의 80% 정도가 캐시에서 나왔다는 계산이다. 앞의 단가표에서 캐시된 입력 열을 눈여겨봐야 하는 이유가 여기 있다.

물론 표본이 크지 않고 diff 크기에 따라 편차도 있을 것이다.

## 마무리

단가가 자릿수 단위로 내려갔다. 만료되는 OAuth 토큰을 주기적으로 갱신하던 일도 없어졌다.

앞으로도 Muse는 코드리뷰 말고 종종 사용해 볼 생각이다. 쓸 만하다는 확신이 들면 Claude 쪽을 줄이거나 아예 구독을 접는 것까지 고려하고 있다. 월 $100은 매일 붙잡고 있으면 아깝지 않은 금액인데 월~금은 회사 일 때문에 거의 손을 못 댄다. 실제로 쓰는 건 평일 늦은 밤과 주말 이틀인 셈이고 그렇게 보면 단가가 꽤 비싸진다.

당장 결론을 내릴 생각은 없다. 몇 주 더 써보고 결정하려고 한다.

## 참고

벤치마크와 가격 출처

- [Introducing Muse Spark 1.3 (Meta 공식 발표)](https://research.meta.ai/blog/introducing-muse-spark-1-3) — 본문 코딩·에이전트 벤치마크 표의 출처. Meta 자체 측정치다
- [Muse Spark 1.3: Meta reaches the frontier (Artificial Analysis)](https://artificialanalysis.ai/articles/muse-spark-1-3) — Intelligence Index, 태스크당 비용, max/xhigh 독립 측정
- [Artificial Analysis 모델 비교](https://artificialanalysis.ai/models) — 모델별 점수를 직접 비교해볼 수 있는 곳
- [Meta says Muse Spark 1.3 has frontier performance — but its best results come from a model developers can't broadly use yet (VentureBeat)](https://venturebeat.com/technology/meta-says-muse-spark-1-3-has-frontier-performance-but-its-best-results-come-from-a-model-developers-cant-broadly-use-yet) — max/xhigh 구성 차이 정리
- [Meta Model API 요금·레이트리밋](https://dev.meta.ai/docs/pricing-rate-limits) — Muse Spark 단가와 contributor 티어
- [Anthropic 요금 문서](https://platform.claude.com/docs/en/pricing) — Claude Opus 5 단가
- [Muse Spark 1.3 Contributor (OpenRouter)](https://openrouter.ai/meta/muse-spark-1.3-contributor) — contributor 단가 교차 확인용

문서·기타

- [Muse Code 문서](https://ai.developer.meta.com/docs)
- [Meta Model API](https://developer.meta.com/ai/products/meta-model-api/)
- [Muse Spark 1.3: Features, Benchmarks, and Pricing (DataCamp)](https://www.datacamp.com/blog/muse-spark-1-3)
- [Getting Started with Muse Code: CLI Commands, Syntax and Purpose (QAInsights)](https://qainsights.com/getting-started-with-muse-code-cli-commands-syntax-and-purpose/)
