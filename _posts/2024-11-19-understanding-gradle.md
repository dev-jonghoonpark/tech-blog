---
layout: post
title: "gradle 톺아보기 (plugin, dependency, source set, module)"
categories: [스터디-자바, 개발]
tags:
  [
    java,
    gradle,
    plugin,
    api,
    published api,
    implementation,
    runtime,
    compile,
    dependency,
    dependencies,
    source set,
    module,
    project,
  ]
date: 2024-11-19 18:00:00 +0900
toc: true
---

최근에 회사에서 프로젝트를 진행하며 프로젝트 구조를 어떻게 잡야할 할지 고민하면서 이것 저것 시도하다보니 gradle 의 구조에 대해 기존보다 더 알게된 부분들이 있어 내용으로 정리해보고 공유해보고자 한다.

# Gradle

Gradle은 오픈소스 빌드 도구로, 유연성과 강력한 성능을 통해 대규모 프로젝트부터 간단한 애플리케이션까지 다양한 소프트웨어 빌드를 지원한다.
Gradle 은 Maven 과 함께 JVM 계열에서 가장 많이 사용되는 빌드 시스템이다.

![build-system-percentage](/assets/images/2024-11-19-understanding-gradle/build-system-percentage.png)

## plugin

Gradle의 많은 기능은 [plugin](https://docs.gradle.org/current/userguide/plugins.html)을 통해 제공되며, 여기에는 Gradle과 함께 배포되는 핵심 플러그인, 타사 플러그인, 빌드 내에 정의된 스크립트 플러그인이 포함된다.

### java plugin

기본적으로 사용되는 plugin이다. gradle 로 프로젝트를 초기화 하면 `java` plugin 이 적용되어 있다. ([java plugin documentation](https://docs.gradle.org/current/userguide/java_plugin.html))

```groovy
plugins {
    id 'java'
}
```

java plugin 가 적용되어 우리가 gradle 에서 사용하는 기본적인 task 들(compileJava, clean, build 등)을 사용할 수 있게 된다.

![init-with-gradle](/assets/images/2024-11-19-understanding-gradle/init-with-gradle.png)

java plugin 을 빼게 되면 사용 가능한 task 들도 사라지고 dependency 영역과 test 영역도 사용하지 못하게 된다.

![without-java-plugin](/assets/images/2024-11-19-understanding-gradle/without-java-plugin.png)

### java-library plugin

라이브러리 개발을 한다면 `java-library` plugin 를 사용할 수도 있다. java-library 는 java plugin 을 확장하며, 공개 의존성 관리 config를 추가한 plugin 이다.

## dependency

### 의존성 설정 (Dependendcy Configuration)

java / java-library plugin 은 다음과 같은 의존성 설정을 제공한다. ([자료 링크](https://docs.gradle.org/current/userguide/dependency_configurations.html))

| 의존성 설정 종류   | 설명                                                                             |
| ------------------ | -------------------------------------------------------------------------------- |
| implementation     | 컴파일과 런타임 모두에 필요한 의존성. 공개 API x.                                |
| api                | 컴파일과 런타임 모두에 필요한 의존성, 공개 API. (java-library 에서 사용 가능)    |
| compileOnly        | 컴파일에만 필요한 의존성, 런타임 포함 x. 공개 API x.                             |
| compileOnlyApi     | 컴파일에만 필요한 의존성, 런타임 포함 x. 공개 API. (java-library 에서 사용 가능) |
| runtimeOnly        | 클래스 경로에 포함되지 않고 런타임에만 필요한 의존성.                            |
| testImplementation | 테스트를 컴파일하고 실행하는 데 필요한 의존성.                                   |
| testCompileOnly    | 테스트를 컴파일하는데만 필요한 의존성.                                           |
| testRuntimeOnly    | 테스트 실행에만 필요한 의존성.                                                   |

### api 와 implementation 의 차이, 공개 API(published api)

- `api` 로 선언된 의존성은 외부에서도 직접 접근 가능하도록 공개된다.
- `implementation` 는 의존성을 "구현의 일부"로 취급하여 캡슐화한다. 외부 프로젝트에서는 해당 프로젝트 내부의 의존성에 직접 접근할 수 없다.

**공개 API** 는 프로젝트에 추가한 의존성이 다른 프로젝트에서 접근 가능한 것을 의미한다.

### compileOnly 와 runtimeOnly

compileOnly는 컴파일에만 사용하고, runtimeOnly은 런타임에만 사용된다. 이름 그대로 해석되고 이해할 수 있다. 하지만 그래서 어떨때 사용되어야 하는건지는 알기 어려운 부분이 있다. 그래서 각 케이스를 정리해보았다.

#### compileOnly 가 사용되는 경우

compileOnly 의 경우 일반적으로 인터페이스를 제공할 때 사용한다. 실제 runtime에는 구현체 클래스가 사용되기 때문에 컴파일 시에만 있으면 된다.

예시 : 웹 애플리케이션 개발 시 javax.servlet-api를 사용하여 컴파일할 때 서블릿 인터페이스를 참조하지만, 실행 시에는 Tomcat 같은 서블릿 컨테이너가 이를 제공해주기 때문에 필요하지 않다. 따라서 compileOnly 를 통해 컴파일 시에만 포함되면 된다.

#### runtimeOnly 가 사용되는 경우

runtimeOnly 의 경우 일반적으로 구현체를 제공하는데 사용된다. 실제 compile 시에는 인터페이스가 사용되기 때문에 런타임 에만 있으면 된다.

예시 : MySQL 데이터베이스를 연결하려고 할 때, 컴파일 시은 JDBC API 를 통해 진행된다. 하지만 런타임에서는 MySQL 드라이버 구현체가 필요하다. 따라서 runtimeOnly 를 통해 런타임 시에만 포함되면 된다.

#### compileOnly 와 runtimeOnly 를 제공하여 얻은 것

프로젝트의 빌드 시간을 단축하고, 배포 파일의 크기를 줄이며, 의존성 관리를 효율적으로 할 수 있게 되었다.

#### 왜 runtimeOnlyApi 는 없을까?

runtimeOnly 는 런타임 시에만 포함되는 의존성이다. 따라서 코드 작성에 영향을 주지 않는다. 또한 굳이 구현 세부 사항이 드러날 필요는 없다.

## Project layout

Java plugin 은 아래의 Project Layout 을 가정한다.

| 경로                      | 설명                                    |
| ------------------------- | --------------------------------------- |
| src/main/java             | 프로덕션 자바 코드                      |
| src/main/resources        | 프로덕션 리소스 (xml, property 파일 등) |
| src/test/java             | 테스트 코드                             |
| src/test/resources        | 테스트 리소스                           |
| src/{sourceSet}/java      | 추가적인 소스셋 자바 코드               |
| src/{sourceSet}/resources | 추가적인 소스셋 리소스                  |

[source set](https://docs.gradle.org/current/dsl/org.gradle.api.tasks.SourceSet.html) 은 Java 소스 코드와 리소스 파일들의 논리적인 그룹이다. main 과 test 는 기본적으로 사용되는 source set이다.

`{sourceSet}` 부분에 본인의 필요에 따라 추가 레이아웃을 구성해주면 gradle 에서는 sourceSet 으로 인식하여 관리한다. `build.gradle` 에서 설정을 통해 소스셋들간에 서로 코드를 공유할 수 있다. 예시는 다음과 같다.

```groovy
sourceSets {
  datagen {
    java {
      "src/main/java",
      "src/datagen/java"
    }
    resources {
      "src/main/resources",
      "src/datagen/resources"
    }
  }
}

dependencies {
    datagenImplementation sourceSets.main.output
    // ...
}
```

## module

![multi-module-proejct](/assets/images/2024-11-19-understanding-gradle/multi-module-project.png)

gradle을 통해 멀티 모듈 프로젝트를 구성할 수 있다. ([관련 문서](https://docs.gradle.org/current/userguide/intro_multi_project_builds.html))

> \* 참고로 Gradle 문서에서 모듈은 하위 프로젝트(subprojects) 라는 표현으로 사용한다.

멀티 모듈 프로젝트를 구성할 때는 settings.gradle 파일을 통해 어떤 모듈이 어떻게 결합되는 구조인지 명시한다.

멀티 모듈 프로젝트를 구성하면 다음과 같은 장점을 보인다.

- 코드베이스를 기능별로 나눠 관리할 수 있다.
  - 특정 모듈만 별도로 빌드하거나 테스트하여 빌드 시간을 단축할 수 있다
  - 프로젝트 구조를 체계적 관리 할 수 있으며 확장 가능한 구조를 가지게 된다.
  - 모듈 간 의존성을 명확히 정의하고, 코드의 재사용성을 높힌다.
  - 변경 사항의 영향을 최소화하여 안정적인 소프트웨어 개발이 가능하다.

참고로 자식에서 부모 모듈에 접근하는 것은 일반적인 패턴이 아니다. 공통으로 사용해야할 부분이 있다면 별도의 모듈로 분리하는 것이 좋다.

## 기타 : gradle 파일 분리하기

build.gradle 파일이 너무 길어지게 되는 경우가 있다.

이럴 경우에는 분리 파일을 만들어 분리할 부분들을 분리한 후에 build.gradle 에 아래와 같이 내용을 추가해주면 된다.
(여기서는 datagen.gradle 이라는 파일을 만들었다.)

```groovy
apply from: 'datagen.gradle'
```

## 참고

- [gradle user guide - learning basics](https://docs.gradle.org/current/userguide/gradle_directories.html)
- intellij java survey
  - [2023 report](https://www.jetbrains.com/ko-kr/lp/devecosystem-2023/java/)
  - [2022 report](https://www.jetbrains.com/ko-kr/lp/devecosystem-2022/java/)
  - [2021 report](https://www.jetbrains.com/ko-kr/lp/devecosystem-2021/java/)
