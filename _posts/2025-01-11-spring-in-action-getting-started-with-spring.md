---
layout: post
title: "[Spring] Spring In Action - 스프링 시작하기 (1-2장)"
categories: [스터디-자바]
tags:
  [
    Java,
    Spring,
    Spring In Action,
    Servlet,
    DispatcherServlet,
    Spring MVC,
    Front Controller,
    Model,
    View,
    Controller,
    MVC Pattern,
    Spring MVC,
    Spring Boot,
    SpringApplication,
    SpringBootTest,
  ]
date: 2025-01-12 22:59:59 +0900
toc: true
---

최근에 K-DEVCON 에서 Spring 스터디를 시작하였다.
Spring In Action 이라는 책을 함께 공부하기로 하였다.
책에 있는 내용들도 다루지만, 그 외에도 관련된 다양한 내용들을 함께 다뤄보고자 한다.

[https://k-devcon.web.app/spring2025](https://k-devcon.web.app/spring2025)

---

# 스프링 시작하기

## Spring Framework

Spring 프레임워크는 최신 Java 기반 엔터프라이스 애플리케이션을 위한 종합적인 프로그래밍 및 설정 모델을 제공한다.

### Architecture

현재 Spring 공식 doc 에서는 Architecture 이미지를 제공하지 않는다.

인터넷에서 돌아다니는 것들은 대부분 5.0 혹은 그 이하 버전의 doc에서 제공되었던 architecture 이미지이다.

그래서 이번 기회에 [현재 버전의 doc](https://docs.spring.io/spring-framework/reference/)을 기준으로 새로 그려보았다.

![spring architecture](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring%20architecture.png)

이전 버전과 크게 바뀌지는 않았다.

개인적으로 생각하는 주요 변경사항은 아래의 두 가지 라고 생각된다.

1. 반응형(reative) 프로그래밍 지원 확대
2. AoT(Ahead of Time) 기능 도입

> AoT 와 관련된 부분은 [Graal VM 알아보기 (차세대 Java VM)](/2024/12/09/graal-vm) 글에서도 다뤘었다.

## IoC, DI

스프링 을 배울때 가장 먼저 접하는 개념이 아닐까 싶다. (스프링에만 있는 개념은 아니다.) 하지만, 막상 설명하라고 하면 쉽지만은 않다. 이번 기회에 잘 정리해보자.

- IoC : Inversion of Control (제어의 역전)
  - 프로그램의 제어 흐름을 개발자가 아닌 프레임워크나 컨테이너가 담당하도록 하는 디자인 원칙
- DI : Dependency injection (의존성 주입)
  - IoC를 실현하는 방법 중 하나 (스프링은 이 방식을 사용)
  - 객체나 기능을 내가 직접 만들지 않고, 외부에서 받아서 사용하는 방법

### IoC 의 장점

- 더 모듈화되고 유연하며 테스트하기 쉬운 코드를 작성할 수 있습니다.
- 자원을 효율적으로 사용할 수 있습니다.

## Spring Application Context

Spring은 Spring Application Context 라는 Container 를 제공한다.
Container는 애플리케이션의 구성 요소(Bean)들을 관리하고 이들의 생명 주기를 제어한다.

![spring application context](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring-application-context.png)

## Bean

Spring IoC(Container)에 의해 관리되는 객체를 빈(Bean) 이라고 부른다.

## Servlet

Jakarta Servlet(구, Java Servlet)은 자바에서 서버 기능을 구현하는 데 사용되는 인터페이스이다.

서버에서 클라이언트의 요청을 처리하고 응답을 생성하는 데 필요한 기본 동작이 정의되어 있다.
다양한 유형의 요청에 응답할 수 있지만, 주로 웹 서버에서 서버 측 로직을 처리하기 위해 사용된다.

PHP나 ASP.NET과 같은 동적 웹 콘텐츠 기술에 대응하는 Java 기반의 표준 API이다.

## Spring MVC가 나오게 된 배경

### 초기 웹 서버 (정적 리소스 제공)

초기의 웹 서버는 미리 만들어 둔 컨텐츠를 제공할 수 있었다.

![static server](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/static-server.png)

### Servlet 등장 (동적 컨텐츠 제공)

사용자의 요청에 따라 상호작용하여 컨텐츠를 제공할 수 있게 되었다.

![web application server using servlet](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/web-application-server-using-servlet.png)

이전보다 더 다양한 니즈를 충족할 수 있게 되었지만, 곧 두 가지 아쉬움에 부딪히게 된다.

#### 아쉬움 1: URL 별로 별도의 클래스로 구현 및 매핑 관리 필요

![servlet-class-per-url](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/servlet-class-per-url.png)

각 URL 에 대해 별도의 클래스를 작성하고 이를 직접 매핑을 관리 해야했다.
URL 수가 늘어날 수록 처리하는데 어려움이 있으며, 유사한 코드가 반복 작성되어 코드 중복이 많이 발생하였다.

#### 아쉬움 2: 컨텐츠를 Java 로직 내에서 직접 관리

클라이언트에게 제공할 컨텐츠(HTML, JSON 등)를 Java 로직 내에서 직접 관리 해야했다.
이로 인해 비즈니스 로직과 컨텐츠 생성 코드가 섞여 가독성이 떨어졌고, 개발자가 비즈니스 로직에만 집중하기 어려웠다.
개발 생산성이 떨어질 뿐만 아니라 유지보수에도 어려움이 있었다.

Servlet으로 컨텐츠를 관리하는 예시 코드는 다음과 같다.

```java
@Override
protected void doGet(HttpServletRequest request, HttpServletResponse response)
	    throws ServletException, IOException {
    response.setContentType("text/html");
    PrintWriter out = response.getWriter();

    String name = request.getParameter("name");
    if (name == null || name.isEmpty()) {
        name = "Guest";
    }

    out.println("<!DOCTYPE html>");
    out.println("<html>");
    out.println("<head>");
    out.println("<title>Dynamic HTML Example</title>");
    out.println("</head>");
    out.println("<body>");
    out.println("<h1>Welcome, " + name + "!</h1>");
    out.println("<p>This page is dynamically generated using Java.</p>");
    out.println("<p>Current Time: " + new java.util.Date() + "</p>");
    out.println("</body>");
    out.println("</html>");
    out.close();
}
```

### 아쉬움 개선하기

위에서 설명한 아쉬움을 개선하고자 2가지 컨셉이 사용된다.

#### Front Controller Pattern

![front controller pattern, 출처: https://en.wikipedia.org/wiki/Front_controller](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/front-controller-pattern.png)

URL에 대한 모든 요청을 한 곳에서 처리하도록 한다.
요청에 대한 처리를 한 곳에서 처리하여 공통적으로 처리되는 로직에 대한 코드 중복을 줄인다.

세부 로직은 구현체로 위임한다.

#### MVC Pattern

![MVC Pattern, 출처: https://en.wikipedia.org/wiki/Model-view-controller](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/mvc-pattern.png)

MVC는 Model, View, Controller 의 앞자리를 딴 것이다.

각각 다음의 역할을 수행한다.

- 모델: 정보의 내부 표현
- 뷰: 사용자에게 정보를 제공하고 사용자로부터 정보를 받아들이는 인터페이스
- 컨트롤러: 이 둘을 연결하는 소프트웨어

### Spring MVC

Spring MVC는 위에어 업급된 2가지 패턴을 도입한 프레임워크이다.

Spring 문서에서는 Spring Web MVC 에 대해 다음과 같이 소개하고 있다.

> Spring Web MVC는 Servlet API를 기반으로 구축된 **최초**의 웹 프레임워크로, Spring 프레임워크의 시작부터 포함되어 왔습니다.

### Spring MVC 동작 단계별로 알아보기

이 내용은 Spring MVC의 내부 로직에 대해 알아보는 내용이다. 알지 않아도 Spring MVC를 사용하는데에는 문제는 없다. 개발자는 Handler만 개발하면 된다. 하단에서 설명하겠지만 대표적으로 Controller에서 RequestMapping을 사용하는 메소드들이 Handler 메소드에 해당하게 된다.

#### step1: DispatcherServlet 에서 모든 요청을 받아온다.

![step1](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring-mvc-step1.png)

Spring MVC의 핵심인 DispatcherServlet은 모든 클라이언트 요청을 받아서 적절한 핸들러로 라우팅하고, 최종적으로 응답을 전달하는 Front Controller 역할을 한다.

#### step2: 받아온 요청을 처리할 대상(Handler)을 찾는다.

![step2](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring-mvc-step2.png)

```java
// Determine handler for the current request.
mappedHandler = getHandler(processedRequest);
if (mappedHandler == null) {
    noHandlerFound(processedRequest, response);
    return;
}
```

요청을 기반으로 가장 적합한 핸들러를 찾는다.

#### step3: Handler에 적합한 Adapter를 찾아 Handler 로직 호출

![step3](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring-mvc-step3.png)

```java
// Determine handler adapter for the current request.
HandlerAdapter ha = getHandlerAdapter(mappedHandler.getHandler());
```

Handler에 맞는 HandlerAdaper를 찾는다.

```java
// Actually invoke the handler.
mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
```

HandlerAdapter를 이용하여 핸들러 메소드의 로직을 수행한다. 로직 수행의 결과로 ModelAndView를 반환한다

#### step4: View Render 하여 사용자에게 전달.

![step4](/assets/images/2025-01-11-spring-in-action-getting-started-with-spring/spring-mvc-step4.png)

step3에서 전달한은 View Name (View의 논리적 이름) 으로 View를 찾는다.

```java
@Nullable
private View resolveViewNameInternal(String viewName, Locale locale) throws Exception {
    if (this.viewResolvers != null) {
       for (ViewResolver viewResolver : this.viewResolvers) {
          View view = viewResolver.resolveViewName(viewName, locale);
          if (view != null) {
             return view;
          }
       }
    }
    return null;
}
```

이후 View를 Render 하여 reponse에 담아 사용자에게 전달한다.

```java
view.render(mv.getModelInternal(), request, response);
```

#### 추가설명

Spring MVC에서 가장 일반적으로 사용되는 Adapter는 RequestMappingHandlerAdapter 이다.
RequestMappingHandlerAdapter 는 HTTP 요청을 처리하는데 사용되는 @RequestMapping, @GetMapping, @PostMapping 등이 붙은 메서드를 호출하는데 사용된다.
HandlerAdapter 는 RequestMappingHandlerAdapter 뿐 아니라 WebSocketHandlerAdapter, ReactorHttpHandlerAdapter 등 다양한 요청 방식에 대응할 수 있도록 설계 및 구현되어 있다.

## Spring Boot

Spring Boot는 Spring Framework 기반의 어플리케이션을 빠르고 효율적으로 개발할 수 있도록 도와주는 프레임워크이다

다음과 같은 특징을 가지고 있다.

- 독립 실행형 애플리케이션: 내장 웹 서버를 이용하여 애플리케이션을 쉽게 실행하고 배포할 수 있다.
- 스타터 의존성: 필요한 다양한 라이브러리나 모듈을 한 번에 쉽게 추가할 수 있도록 도와주는 그룹화 하여 제공한다.
- 자동 구성: Spring 및 관련 라이브러리들을 감지하여 자동으로 구성한다.

### Spring Boot 구동(bootstrap) 클래스

```java
@SpringBootApplication
public class TacoCloudApplication {
  public static void main(String[] args) {
    SpringApplication.run(TacoCloudApplication.class, args);
  }
}
```

어플리케이션을 구동하기위한 최소한의 스프링 구성이다.

#### @SpringBootApplication 어노테이션

@SpringBootApplication 어노테이션은 3가지 어노테이션을 합친 어노테이션 이다.

- @SpringBootConfiguration
  - Configuration의 특수한 형태. 기능상 차이가 있지는 않는다.
  - Spring Boot Application 의 진입점을 나타내는데 사용된다.
  - Spring Boot Application 내에서 1번만 사용되어야 함. 일반적으로 직접 쓰지는 않는다.
- @EnableAutoConfiguration
  - 스프링 부트 자동 구성을 활성화 한다.
  - 스프링 부트의 자동 구성을 통해 불필요한 설정 작업이 극적으로 줄어들었다. (생산성 향상)
- @ComponentScan : 컴포넌트 검색을 활성화 한다.
  - 특정 패키지가 정의되지 않은 경우, 이 주석을 선언하는 클래스의 패키지부터 재귀적으로 스캔 수행한다.

### Controller 클래스

```java
@Controller
public class HomeController {
  @GetMapping("/")
  public String home() {
    return "home";
  }
}
```

@Controller와 함께 @Component, @Service, @Repository와 같은 어노테이션은 클래스를 빈으로 등록되어 관리되도록 한다. 기능상은 차이보다는 역할을 더 잘 설명해주는 어노테이션으로 설정한다.

'/' 경로에 Http Get 요청이 수신되면 매핑된 메서드에서 요청을 처리한다.

return 하는 문자열은 뷰의 논리적인 이름이다.

#### @RestController 와 @ResponseBody

@RestController 는 @Controller 에 @ResponseBody 가 추가된 어노테이션이다.

@ResponseBody 를 사용하면 ViewResolver 대신 HttpMessageConverter 를 사용하여 동작한다. 반환 데이터를 직렬화 하여 HTTP 응답 본문에 직접 전달한다.

## Spring Test

### @SpringBootTest

```java
@SpringBootTest
public class TacoCloudApplicationTests {
  @Test
  public void contextLoads() {
  }
}
```

@SpringBootTest 은 테스트가 Spring Boot 기반으로 진행한다는걸 나타낸다. Context 를 불러와서 테스트를 진행한다.

contxtLoads 메소드: 별도의 테스트 코드가 없는것이 특징이다. 정상적으로 스프링 애플리케이션 컨텍스트가 로드될 수 있는지 확인하는데 사용된다.

### @WebMvcTest

컨트롤러를 테스트 할 떄 사용한다. 응답 코드, 뷰, 내용 등 다양한 부분을 테스트 할 수 있다.

```java
@WebMvcTest(HomeController.class) public class HomeControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testHomePage() throws Exception {
        mockMvc.perform(get("/"))
            .andExpect(status().isOk())
            .andExpect(view().name("home"))
            .andExpect(content().string(
                containsString("Welcome to...")));
    }
}
```
