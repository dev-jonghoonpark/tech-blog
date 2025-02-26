---
layout: "post"
title: "Feature Toggles (aka Feature Flags)"
description: "Feature Toggle(기능 플래그)는 개발 중인 기능을 고객에게 노출하지 않고도 배포할 수 있게 해주는 기법으로, 여\
  러 기능을 동시에 개발할 때 유용합니다. 이 글에서는 마틴 파울러의 글을 바탕으로 Feature Toggle의 필요성과 구현 방법을 설명하며,\
  \ 간단한 예시를 통해 초기 구현에서부터 복잡도를 낮추는 방법까지 단계별로 다룹니다. 특히, 제어 역전과 전략 패턴을 활용하여 코드의 유연성과\
  \ 유지보수성을 향상시키는 방법을 강조합니다."
categories:
- "스터디-개발"
tags:
- "배포"
- "기능 플래그"
- "feature flag"
- "flag"
- "기능 토글"
- "feature toggle"
- "toggle"
- "플래그 가드"
- "flag guard"
- "지속적인 배포"
- "Continuous Delivery"
- "릴리즈"
- "release"
- "마틴 파울러"
- "martin fowler"
- "제어 역전"
- "IoC"
- "Inversion of Control"
- "전략 패턴"
- "strategy pattern"
date: "2024-09-20 07:20:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-09-19-flag-toggle.jpg"
---

## 개요

최근에 [릴리즈 안정적으로 수행하기 - 플래그 가드(flag guard)로 보호하기](/2024/09/10/release-flag-guard) 라는 짧은 글을 쓴 적이 있다. 이 부분을 어떻게 실제로 수행할 수 있을까를 고민해보다가 당근 테크 블로그에서 비슷한 고민을 한 경험글을 발견하여 내용을 읽어보았다. (링크는 하단 '참고' chapter 에 정리해두었다.)

이 글에서는 마틴 파울러의 글을 참고하였다고 되어 있어서 해당 글을 나도 스터디 해보기로 마음먹었고, 스터디 하면서 이해한 부분을 정리해보기로 하였다.

## Feature Toggle 가 필요한 이유

개발을 하다보면 A 라는 기능을 개발하다가 B 라는 기능을 개발해야 하는 경우가 생긴다. 이 때 A 라는 기능은 고객한테 아직 보여서는 않되거나, 완성도가 낮은 상태일 수 있다. 이런 상황은 생각보다 자주 발생된다.

이런 경우에는 먼저 개발하고 있던 A 기능이 마무리 될 때까지 B 기능의 배포를 기다려 줄 수 있으면 좋겠지만, 그런것이 아니라 B기능을 바로 배포해야할 경우에는 상황이 복잡해진다. 코드를 revert 하거나 해서 필요한 부분 따로 분리하여 반영해야 한다.

이러한 상황을 개선하기 위해 Feature Toggle 을 사용한다.

## Feature Toggle 구현

마틴 파울러 블로그에 있던 예시 중 하나를 가져다가 발전시켜보겠다.

게임 엔진의 알고리즘을 개선하려고 하는데 이를 Feature Toggle 을 통해서 컨트롤 하는 시나리오이다.

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
const features = fetchFeatureTogglesFromSomewhere();

function reticulateSplines() {
  if (features.isEnabled("use-new-SR-algorithm")) {
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
    isEnabled(featureName) {
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

이미지로 봤을 때 ToggleRouter 가 추가되어 더 복잡한게 아닐까 생각이 들 수 있다.
하지만 ToggleRouter 를 통해서 일관된 방식으로 feature toggle 를 제공할 수 있게 되었기 때문에, 여러 feature에 대한 toggle을 제공하거나, 한가지 feature 에 대해서 여러 곳에서 분기를 해야할 때 훨씬 좋은 선택이 될것이다.

### v3 - 복잡도 낮추기

기능 플래그는 코드를 지저분하게 할 수 있으며, 토글 포인트는 코드베이스 전체에 확산되는 경향이 있다. 이러한 문제를 줄일 수 있는 개선 방향에 대해서 소개한다.

현재(v2)는 아래와 같은 구조이다. 합리적인 접근 방식처럼 보이지만 이 접근 방식에도 몇 가지 문제가 있다.

```js
const features = fetchFeatureTogglesFromSomewhere();

function reticulateSplines() {
  if (features.isEnabled("use-new-SR-algorithm")) {
    return enhancedSplineReticulation();
  } else {
    return oldFashionedSplineReticulation();
  }
}
```

v3에서는 이와 같은 문제를 피하기 위한 방법들을 소개한다.

#### 결정 논리에서 결정 지점 분리 (de-coupling)

현재(v2) 코드는 특정 기능(use-new-SR-algorithm)의 매우 구체적인 부분(새로운 스플라인 리티큘레이션 알고리즘)을 직접적으로 참조하고 있다.
이로인해 reticulateSplines 함수는 "새로운 알고리즘"이라는 기능 플래그가 어떤 기술적인 세부 사항을 포함하는지 알아야 한다. 이는 코드의 유연성을 떨어뜨리고, 특정 기능 플래그와 코드의 결합도를 높힌다.

만약 현재 코드에서 새로운 리티큘레이션 알고리즘의 일부 기능만 활성화하고 싶거나, 반대로 일부만 비활성화하고 싶다면 어떻게 될까? 또는 새로운 알고리즘을 특정 사용자 그룹에게만 롤아웃하고 싶다면 어떻게 처리해야 할까? 현재처럼 플래그가 하드코딩되어 있다면 이런 요구사항에 맞춰 코드를 수정하는 것이 매우 어려워진다.

더 나아가, 여러 곳에서 이와 유사한 플래그 사용 패턴이 반복된다면, 각 기능 플래그에 대한 로직을 모든 코드에서 찾아서 수정해야 하는 상황이 발생하게 된다. 즉, 기능 플래그를 확인하는 로직이 여러 군데에 흩어져 있고, 이로 인해 각각의 로직을 유지보수하는 데에 어려움이 따르게 된다.

기능 플래그와 비즈니스 로직을 좀 더 명확하게 분리하고, 플래그 관리와 비즈니스 결정이 각기 독립적으로 처리될 수 있는 구조를 도입하는 것이 필요하다. 간접 계층을 추가하여 결정 지점(decision point)을 다음과 같이 결정 논리(decision logic)에서 분리할 수 있다.

```js
function createFeatureDecisions(features) {
  return {
    useNewSplineReticulation() {
      // A/B 테스트 와 같은 추가적인 조건을 넣을 수 있다.
      return features.isEnabled("use-new-SR-algorithm");
    },
    // ... 추가적인 결정 기능들 ...
  };
}
```

```js
const features = fetchFeatureTogglesFromSomewhere();
const featureDecisions = createFeatureDecisions(features);

function reticulateSplines() {
  if (featureDecisions.useNewSplineReticulation()) {
    return enhancedSplineReticulation();
  } else {
    return oldFashionedSplineReticulation();
  }
}
```

새롭게 추가된 FeatureDecision 객체는 기능 토글 결정 로직들을 모으는 역할을 한다.

비록 예시로 사용된 결정 로직은 단순히 flag의 on/off만 체크하는 간단한 형태이지만 결정을 관리할 수 있는 단일 포인트가 생겼다는 것이 중요하다. 특정 토글 결정의 로직을 수정하고 싶을 때마다 한 곳에서 관리할 수 있게 된 것이다. 이로 인해 어떤 경우든 엔진은 토글 결정이 어떻게 또는 왜 이루어졌는지 알지 않아도 된다.

![v3-1](/assets/images/2024-09-19-flag-toggle/v3-1.png)

#### 제어 역전

방금 전 우리는 결정 논리에서 결정 지점을 분리하였다. 코드는 이전보다 개선되었지만 아직 아쉬운 부분이 있다.

이를 개선하기 위해 제어 역전을 적용한다.

> 제어 반전, 제어의 반전, 역제어는 프로그래머가 작성한 프로그램이 재사용 라이브러리의 흐름 제어를 받게 되는 소프트웨어 디자인 패턴을 말한다. 줄여서 IoC(Inversion of Control)이라고 부른다. 전통적인 프로그래밍에서 흐름은 프로그래머가 작성한 프로그램이 외부 라이브러리의 코드를 호출해 이용한다. 하지만 제어 반전이 적용된 구조에서는 외부 라이브러리의 코드가 프로그래머가 작성한 코드를 호출한다. - [위키피디아](https://ko.wikipedia.org/wiki/%EC%A0%9C%EC%96%B4_%EB%B0%98%EC%A0%84)

```js
function createSplineReticulater(config) {
  return {
    function reticulateSplines() {
      if (config.useNewSplineReticulation) {
        return enhancedSplineReticulation();
      } else {
        return oldFashionedSplineReticulation();
      }
    }

    // ... 다른 메소드들 ...
  };
}
```

```js
function createFeatureAwareFactoryBasedOn(featureDecisions) {
  return {
    splineReticulater() {
      return createSplineReticulater({
        useNewSplineReticulation: featureDecisions.useNewSplineReticulation(),
      });
    },

    // ... 다른 메소드들 ...
  };
}
```

FeatureDecision 이라는 복잡한 객체가 아니라 Config라는 상태값만 바라보게 되었다. 결합도가 낮아졌고, 유연성이 높아졌다. 테스트에도 용이하다. 테스트 하고자 하는 시나리오에 맞게 config 객체만 설정해주면 된다.

실제 사용은 다음과 같이 진행된다.

```js
describe("spline reticulation", function () {
  it("works correctly with old algorithm", function () {
    // Given
    const splineReticulater = createSplineReticulater({
      useNewSplineReticulation: false,
    });

    // When
    const result = splineReticulater.reticulateSplines();

    // Then
    verifySplineReticulation(result);
  });

  it("works correctly with new algorithm", function () {
    // Given
    const splineReticulater = createSplineReticulater({
      useNewSplineReticulation: true,
    });

    // When
    const result = splineReticulater.reticulateSplines();

    // Then
    verifySplineReticulation(result);
  });
});
```

splineReticulater는 config 객체만 바라보면 되기 때문에 테스트가 훨씬 단순해졌다. feature toggle과 분리하여 테스트를 진행 할 수 있게 되었다.

![v3-2](/assets/images/2024-09-19-flag-toggle/v3-2.png)

구조가 더 복잡해진 것으로 보이지만 바로 위에서 이야기 한 것처럼 splineReticulater 가 분리되었고, splineReticulater는 config 객체만 바라보면 된다는 것이 포인트이다.

#### 조건문 피하기

방금 전 우리는 제어 역전을 통해 결합도를 낮추고, 유연성을 높힐 수 있었다. 코드는 이전보다 개선되었지만 마지막으로 한번 더 개선을 해보겠다.

[전략 패턴(strategy pattern)](https://ko.wikipedia.org/wiki/%EC%A0%84%EB%9E%B5_%ED%8C%A8%ED%84%B4)을 이용하여 조건문을 숨겨볼 것이다.

> **전략 패턴(strategy pattern)** 은 실행 중에 알고리즘을 선택할 수 있게 하는 소프트웨어 디자인 패턴이다.

전략 패턴은 함수를 넘겨주는 방식으로 구현할 수 있다. (자바에서는 인터페이스를 통해서 구현할 수 있다.)

```js
function createSplineReticulater(splineReticulationExcutor) {
  return {
    function reticulateSplines() {
      return splineReticulationExcutor.execute();
    }

    // ... 다른 메소드들 ...
  };
}
```

```js
function createFeatureAwareFactoryBasedOn(featureDecisions) {
  return {
    splineReticulater() {
      if (featureDecisions.useNewSplineReticulation()) {
        createSplineReticulater(enhancedSplineReticulationExcutor);
      }
      return createSplineReticulater(oldFashionedSplineReticulationExcutor);
    },

    // ... 다른 메소드들 ...
  };
}
```

실제 사용은 다음과 같이 진행된다.

```js
describe("spline reticulation", function () {
  it("works correctly with old algorithm", function () {
    // Given
    const splineReticulater = createSplineReticulater(
      oldFashionedSplineReticulationExcutor
    );

    // When
    const result = splineReticulater.reticulateSplines();

    // Then
    verifySplineReticulation(result);
  });

  it("works correctly with new algorithm", function () {
    // Given
    const splineReticulater = createSplineReticulater(
      enhancedSplineReticulationExcutor
    );

    // When
    const result = splineReticulater.reticulateSplines();

    // Then
    verifySplineReticulation(result);
  });
});
```

전략 패턴을 사용하여 reticulateSplines 내의 분기가 사라졌다. 전달받은 splineReticulationExcutor 를 수행 하면 된다. 상세 구현이 어떻게 되어있는지는 알지 못해도 된다.

![v3-3](/assets/images/2024-09-19-flag-toggle/v3-3.png)

## 참고

- [Feature Toggles - 마틴 파울러 블로그](https://martinfowler.com/articles/feature-toggles.html)
  - [번역글 - 당근 개발자 Jeremy 님 블로그](https://sungjk.github.io/2022/10/15/feature-toggles.html)
- [매일 배포하는 팀이 되는 여정 - Feature Toggle 활용하기 - 당근 블로그](https://medium.com/daangn/%EB%A7%A4%EC%9D%BC-%EB%B0%B0%ED%8F%AC%ED%95%98%EB%8A%94-%ED%8C%80%EC%9D%B4-%EB%90%98%EB%8A%94-%EC%97%AC%EC%A0%95-2-feature-toggle-%ED%99%9C%EC%9A%A9%ED%95%98%EA%B8%B0-b52c4a1810cd)

## 기타

### 소프트웨어 공학의 기본 정리 (Fundamental theorem of software engineering)

아래 글은 마틴 파울러 블로그 글에서 인용된 글이다.

> 소프트웨어의 모든 문제는 간접 계층을 추가하면 해결할 수 있습니다. (We can solve any problem by introducing an extra level of indirection.)

[https://en.wikipedia.org/wiki/Fundamental_theorem_of_software_engineering](https://en.wikipedia.org/wiki/Fundamental_theorem_of_software_engineering)

### Spline Reticulation ?

책에서 나오는 Spline Reticulation 이 뭔가 싶어서 찾아보았는데 다음과 같은 레딧글을 찾아볼 수 있었다.

[What does Reticulating Splines actually mean?](https://www.reddit.com/r/programming/comments/8dfn4/what_does_reticulating_splines_actually_mean/)

정리해보면 컴퓨터는 실제로 곡선을 그리지는 못한다. 대신 곡선을 직선으로 나누어 근사하여 보여준다. 그 과정을 Spline Reticulation 이라고 하는 것 같다.
