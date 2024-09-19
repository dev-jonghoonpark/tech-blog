---
layout: post
title: "[마틴 파울러] Feature Toggles (aka Feature Flags)"
categories: [스터디-개발]
tags:
  [
    배포,
    기능 플래그,
    feature flag,
    flag,
    기능 토글,
    feature toggle,
    toggle,
    플래그 가드,
    flag guard,
    지속적인 배포,
    Continuous Delivery,
    릴리즈,
    release,
    마틴 파울러,
    martin fowler,
  ]
date: 2024-09-10 16:30:00 +0900
toc: true
---

## 개요

최근에 [릴리즈 안정적으로 수행하기 - 플래그 가드(flag guard)로 보호하기](/2024/09/10/release-flag-guard) 라는 짧은 글을 쓴 적이 있다. 이 부분을 어떻게 실제로 수행할 수 있을까를 고민해보다가 당근 테크 블로그에서 비슷한 고민을 한 경험글을 발견하여 내용을 읽어보았다. (링크는 하단 '참고' chapter 에 정리해두었다.)

이 글에서는 마틴 파울러의 글을 참고하였다고 되어 있어서 해당 글을 나도 스터디 해보기로 마음먹었고, 스터디 하면서 이해한 부분을 정리해보기로 하였다.

## Feature Toggle 가 필요한 이유

개발을 하다보면 A 라는 기능을 개발하다가 B 라는 기능을 개발해야 하는 경우가 생긴다. 이 때 A 라는 기능은 고객한테 아직 보여서는 않되거나, 완성도가 낮은 상태일 수 있다. 이런 상황은 생각보다 자주 발생된다.

이런 경우에는 먼저 개발하고 있던 A 기능이 마무리 될 때까지 B 기능의 배포를 기다려 줄 수 있으면 좋겠지만, 그런것이 아니라 B기능을 바로 배포해야할 경우에는 상황이 복잡해진다. 코드를 revert 하거나 해서 필요한 부분 따로 분리하여 반영해야 한다.

이러한 상황을 개선하기 위해 Feature Toggle 을 사용한다.

## Feature Toggle 구현

### v0 - 초기 상태

```js
function reticulateSplines() {
  // current implementation lives here
}
```

아직 feature toggle 이 구현되지 않은 상태이다.
여기서 기존 알고리즘을 유지한 상태에서 새 알고리즘을 구현해야 하는 상황을 가정하여 구현해나가본다.

![v0](/assets/images/2024-09-19-flag-toggle/v0.png)

### v1 - 가장 심플한 구현

가장 심플한 형태이다. 코드의 value 값을 직접 수정해야 한다.

```js
function reticulateSplines() {
  var useNewAlgorithm = false;
  // useNewAlgorithm = true; // UNCOMMENT IF YOU ARE WORKING ON THE NEW SR ALGORITHM

  if (useNewAlgorithm) {
    return enhancedSplineReticulation();
  } else {
    return oldFashionedSplineReticulation();
  }
}

function oldFashionedSplineReticulation() {
  // current implementation lives here
}

function enhancedSplineReticulation() {
  // TODO: implement better SR algorithm
}
```

![v1](/assets/images/2024-09-19-flag-toggle/v1.png)

### v2 - 동적으로 값을 할당 가능한 구조로 변경

v1의 경우 직접 코드에 들어가서 true인지, false인지 지정을 해주어야 했다.
이러한 문제를 아래와 같은 구조로 수정하여 개선한다.

```js
function reticulateSplines() {
  if (featureIsEnabled("use-new-SR-algorithm")) {
    return enhancedSplineReticulation();
  } else {
    return oldFashionedSplineReticulation();
  }
}
```

```js
function createToggleRouter(featureConfig) {
  return {
    setFeature(featureName, isEnabled) {
      featureConfig[featureName] = isEnabled;
    },
    featureIsEnabled(featureName) {
      return featureConfig[featureName];
    },
  };
}
```

실제 사용은 다음과 같이 진행된다.

```js
describe("spline reticulation", function () {
  let toggleRouter;
  let simulationEngine;

  beforeEach(function () {
    toggleRouter = createToggleRouter();
    simulationEngine = createSimulationEngine({ toggleRouter: toggleRouter });
  });

  it("works correctly with old algorithm", function () {
    // Given
    toggleRouter.setFeature("use-new-SR-algorithm", false);

    // When
    const result =
      simulationEngine.doSomethingWhichInvolvesSplineReticulation();

    // Then
    verifySplineReticulation(result);
  });

  it("works correctly with new algorithm", function () {
    // Given
    toggleRouter.setFeature("use-new-SR-algorithm", true);

    // When
    const result =
      simulationEngine.doSomethingWhichInvolvesSplineReticulation();

    // Then
    verifySplineReticulation(result);
  });
});
```

ToggleRouter 를 SimulationEngine 을 생성하는 시점에 주입하고
ToggleRouter 에 feature 에 대한 flag 값을 설정하여 실제 수행 로직을 분기한다.

![v2](/assets/images/2024-09-19-flag-toggle/v2.png)

이미지로 봤을 때

## 참고

- [Feature Toggles - 마틴 파울러 블로그](https://martinfowler.com/articles/feature-toggles.html)
  - [번역글 - 당근 개발자 Jeremy 님 블로그](https://sungjk.github.io/2022/10/15/feature-toggles.html)
- [매일 배포하는 팀이 되는 여정 - Feature Toggle 활용하기 - 당근 블로그](https://medium.com/daangn/%EB%A7%A4%EC%9D%BC-%EB%B0%B0%ED%8F%AC%ED%95%98%EB%8A%94-%ED%8C%80%EC%9D%B4-%EB%90%98%EB%8A%94-%EC%97%AC%EC%A0%95-2-feature-toggle-%ED%99%9C%EC%9A%A9%ED%95%98%EA%B8%B0-b52c4a1810cd)

## 기타

책에서 나오는 Spline Reticulation 이 뭔가 싶어서 찾아보았는데 다음과 같은 레딧글을 찾아볼 수 있었다.

[What does Reticulating Splines actually mean?](https://www.reddit.com/r/programming/comments/8dfn4/what_does_reticulating_splines_actually_mean/)

정리해보면 컴퓨터는 실제로 곡선을 그리지는 못한다. 대신 곡선을 직선으로 나누어 근사하여 보여준다. 그 과정을 Spline Reticulation 이라고 하는 것 같다.

```

```
