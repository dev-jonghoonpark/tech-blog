---
layout: "post"
title: "[Spring] HandlerMethodArgumentResolver 를 이용하여 client 버전에 따른 기능 분기 구현하기"
description: "Spring의 `HandlerMethodArgumentResolver`를 활용하여 클라이언트 버전에 따라 API 기능을 분\
  기하는 방법을 설명합니다. `AppVersionFlag` 어노테이션을 통해 HTTP 요청 헤더의 버전을 확인하고, 이를 기반으로 컨트롤러의 매개\
  변수를 설정하여 새로운 기능을 활성화하거나 기존 로직을 수행하도록 합니다. 이 과정에서 구현의 복잡성을 줄이고, 버전 비교를 간편하게 처리할 수\
  \ 있습니다."
categories:
- "스터디-자바"
tags:
- "Spring"
- "HandlerMethodArgumentResolver"
- "annotation"
- "WebMvcConfig"
- "feature flag"
- "feature toggle"
- "version"
- "header"
date: "2025-03-31 15:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-04-11-spring-handler-method-argument-resolver.jpg"
---

# client 버전에 따른 기능 분기 구현

서비스에서 API를 분기할 때, 같은 endpoint를 바라보면서 client 버전에 따라 기능이 분기 되면 좋겠다는 니즈가 있었다. 그래서 개발을 시작하게 되었다. 어떻게 구현해볼까 고민 하다가 `HandlerMethodArgumentResolver` 를 활용하여 간결하게 처리할 수 있겠다 싶어 해당 방향으로 설계 후 진행하였다.

## HandlerMethodArgumentResolver

HandlerMethodArgumentResolver 는 Spring MVC에서 컨트롤러 메서드의 매개변수를 처리하고 값으로 변환하는 데 사용되는 인터페이스 이다. 이 인터페이스를 상속하여 Config 에 설정해준다면, client 버전에 따라 기능 분기를 해줄 수 있다.

### 사용 설계

참고로 client 에서는 http request header 에 `x-app-version=aa.bb.cc` 이런식으로 넘겨주고 있다.

`AppVersionFlag` 라는 annotation 을 사용하여 request 가 들어올 경우, 사용자의 버전에 따라 컨트롤러의 매개 변수가 `true` 또는 `false` 로 반환하도록 할 것이다. 그리고 해당 값을 사용하여 기능 분기를 진행할 것이다.

예시로 들면 다음과 같은 구조가 될 것이다.

```java
@GetMapping("/api/v1/something")
public void method(
  ...
  @AppVersionFlag(from="1.0.0") boolean newFeatureRequired,
  ...
) {
  ...
  if (newFeatureRequired) {
    // 버전 1.0.0 이상일 경우 로직 실행
  } else {
    // 버전이 낮으면 기존 로직 수행
  }
  ...
}
```

클라이언트가 전달해준 x-app-version 값을 통해 분기 로직을 처리한다. header 처리와 관련된 직접적인 구현을 숨겨 간단히 처리할 수 있을 것이다.

### HandlerMethodArgumentResolver 구현

실제 코드는 조금 더 복잡하지만 핵심 부분만 정리해보면 다음과 같다.

우선 Annotation interface 를 만든다. `from` 은 어떤 버전부터 분기할 것인지를 결정하는데 사용된다.

```java
@Target(ElementType.PARAMETER)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface AppVersionFlag {
  String from();
}
```

실제적으로 분기를 담당하는 부분은 `HandlerMethodArgumentResolver` 를 상속한 `AppVersionFlagResolver` 클래스가 담당한다.

```java
@Component
public class AppVersionFlagResolver implements HandlerMethodArgumentResolver {

  private static final String APP_VERSION_KEY = "x-app-verion";

  @Override
  public boolean supportsParameter(MethodParameter parameter) {
    return parameter.hasParameterAnnotation(AppVersionFlag.class) && parameter.getParameterType().equals(boolean.class);
  }

  @Override
  public Object resolveArgument(MethodParameter parameter, ModelAndViewContainer mavContainer,
                                org.springframework.web.context.request.NativeWebRequest webRequest,
                                org.springframework.web.bind.support.WebDataBinderFactory binderFactory) {
    HttpServletRequest request = (HttpServletRequest) webRequest.getNativeRequest();
    String appVersion = request.getHeader(APP_VERSION_KEY);

    if (appVersion == null) {
      return true; // app version 이 명시되지 않았을 경우 최신 버전으로 가정한다.
    }

    AppVersionFlag annotation = parameter.getParameterAnnotation(AppVersionFlag.class);
    assert annotation != null;
    String requiredVersion = annotation.from();

    return isVersionGreaterOrEqual(appVersion, requiredVersion);
  }

  protected boolean isVersionGreaterOrEqual(String current, String required) {
    if (required == null) {
      return true;
    }

    try {
      String[] currentParts = current.split("\\.");
      String[] requiredParts = required.split("\\.");

      for (int i = 0; i < Math.max(currentParts.length, requiredParts.length); i++) {
        int currentVal = i < currentParts.length ? Integer.parseInt(currentParts[i]) : 0;
        int requiredVal = i < requiredParts.length ? Integer.parseInt(requiredParts[i]) : 0;

        if (currentVal > requiredVal) return true;
        if (currentVal < requiredVal) return false;
      }
    } catch (Exception e) {
      log.warn("failed compare version");
    }

    return true;
  }
}
```

마지막으로 `AppVersionFlagResolver` 를 `WebMvcConfig` 에 등록해주면 마무리된다. (구체적인 코드는 버전에 따라 차이가 있을 수 있다.)

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

  @Bean
  public WebMvcRegistrations webMvcRegistrationsHandlerMapping() {
    return new WebMvcRegistrations() {
      @Override
      public RequestMappingHandlerAdapter getRequestMappingHandlerAdapter() {
        return new RequestMappingHandlerAdapter() {
          @Override
          public void afterPropertiesSet() {
            super.afterPropertiesSet();
            List<HandlerMethodArgumentResolver> resolvers = new ArrayList<>();
            resolvers.add(new AppVersionFlagResolver());
            resolvers.addAll(getArgumentResolvers());
            setArgumentResolvers(resolvers);
          }
        };
      }
    };
  }
}
```

## 마무리

이번 글에서는 `HandlerMethodArgumentResolver`를 활용하여 클라이언트 버전에 따라 API 동작을 분기해본 경험에 대해서 기록해보았습니다. 어노테이션을 통해서, 직접적인 기능 구현은 숨기면서 간단하게 버전 분기를 위한 변수를 설정할 수 있었습니다.
