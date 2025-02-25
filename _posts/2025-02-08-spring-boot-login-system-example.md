---
layout: post
title: "[Spring] 스프링 부트 기반 간단한 로그인, 회원가입 예제 만들어보기"
description: 스프링 부트와 스프링 시큐리티를 활용하여 간단한 로그인 및 회원가입 시스템을 구축하는 방법을 설명합니다. 프로젝트 초기화부터 필요한 의존성 설정, 자동 구성, 로그인 및 회원가입 처리, 비밀번호 암호화, 사용자 인증 기능까지 단계별로 안내합니다. 이 예제는 스프링 부트의 생산성 향상 기능을 활용하여 간편하게 구현할 수 있으며, CSRF 보호 및 사용자 정보 관리를 포함합니다.
categories: [스터디-자바]
tags:
  [
    Java,
    Spring In Action,
    Spring,
    Spring Boot,
    Spring Security,
    Auto Configuration,
    Configuration,
    JPA,
    User,
    Login,
    Signup,
    csrf,
    UserDetails,
    UserDetailService,
    loadUserByUsername,
    password,
    password encoder,
    argon2,
    bouncycastle,
  ]
date: 2025-02-08 23:59:59 +0900
toc: true
---

최근에 K-DEVCON 에서 Spring 스터디를 시작하였다.
Spring In Action 이라는 책을 함께 공부하기로 하였다.
책에 있는 내용들도 다루지만, 그 외에도 관련된 다양한 내용들을 함께 다뤄보고자 한다.

[https://k-devcon.web.app/spring2025](https://k-devcon.web.app/spring2025)

---

# 스프링 부트 기반 간단한 로그인, 회원가입 예제 만들어보기

이 글은 Spring Boot와 Spring Security를 활용하여 간단한 로그인 및 회원가입 시스템을 구축하는 방법을 설명한다. 프로젝트 초기화부터 구현까지의 과정을 단계별로 알아보자.

## 프로젝트 세팅

대표적인 IDE에서는 Spring Initializr 를 제공해주니 해당 기능을 사용하여 프로젝트를 초기화 하면 되고
그 외의 경우에도 [https://start.spring.io/](https://start.spring.io/) 를 통해서 쉽게 프로젝트를 시작할 수 있다.

### 선택한 dependency

- lombok
- spring boot devtools
- spring web
- spring data jpa
- spring security
- mysql driver
- thymeleaf (타임리프)

## Spring Boot Auto Configuration

스프링 부트는 자동 구성(Auto Configuration)을 통해 기존 대비 불필요한 설정 작업을 극적으로 줄였다. (생산성 향상)

런타임에 의존성 라이브러리를 classpath 에서 찾아 사용할 수 있다면, 해당 빈을 자동으로 찾아 스프링 애플리케이션 컨텍스트에 생성한다.

### Bean 세부 설정

Bean 을 설정하는 방법은 크게 2가지로 나누어 진다.

- 빈 연결 (Bean wiring)
  - 빈을 직접 구성하여 **스프링 애플리케이션 컨텍스트**에 등록한다.
- 속성 주입 (Property injection)
  - 사전에 정의된 속성을 활용하여 빈을 구성한다.
  - 빈을 반드시 명시적으로 직접 구성하지 않고도 빈을 설정할 수 있다.

Spring 3.0 이전에는 XML을 통해 빈을 직접 다 정의해줬아야 했다. 현재는 자바에서 구성하는 방법이 대중적으로 사용되고 있다.

## 스프링 환경 추상화 (Environment abstraction)

![spring-environment-abstraction](/assets/images/2025-02-08-spring-boot-login-system-example/spring-environment-abstraction.png)

스프링 환경 추상화를 통해 다양한 방법으로 속성값을 제공할 수 있다.
각 빈(Bean)이 속성을 필요로 하는 속성을 스프링 환경에서 가져와 사용한다.

## 로그인 해보기

위에서 언급한 dependency 대로 설정을 하였다면, 추가 세팅 없이 어플리케이션을 실행한 후 `localhost:8080` 으로 접근해보면 로그인 화면으로 연결된다.

![default-login-form](/assets/images/2025-02-08-spring-boot-login-system-example/default-login-form.png)

### 어떻게 동작한걸까?

우리는 아직 별도의 controller 도 service 도 config 도 생성하지 않았다.
그럼에도 불구하고 로그인 화면을 볼 수 있었던 이유는 spring boot의 auto configuration 덕분이다.
classpath 에 spring security 가 있었기 때문에 빈을 찾아 컨텍스트에 등록하였다.

### 기본 보안 구성

자동으로 생성된 스프링 스큐리티의 보안 구성은 대략 다음과 같다.

- 모든 HTTP 요청 경로는 인증 되어야 한다.
- 특정 역할이나 권한 설정은 없다.
- 간단한 로그인 페이지(/login)로 인증 할 수 있다.
- 간단한 로그아웃 페이지(/logout)로 인증 해제 할 수 있다.
- 사용자는 ‘user’ 단 한 명뿐이다.

### user 의 비밀번호

기본 생성된 user 의 비밀번호는 log를 통해서 확인할 수 있다. (테스트 용으로만 사용하자.)

![test-user-password](/assets/images/2025-02-08-spring-boot-login-system-example/test-user-password.png)

이제 username 과 password를 찾았으니 로그인을 할 수 있다.

### 로그인 결과

로그인을 해보면 잘 수행된다. 하지만 에러 페이지로 이동된다.

![404-no-static-resources](/assets/images/2025-02-08-spring-boot-login-system-example/404-no-static-resources.png)

당연한 결과이다. 아직 우리가 어떤것도 설정해주지 않았기 때문이다. 이제부터 하나씩 해나가보자.

## URL 설계

대략적으로 어떤 URL이 필요한지만 구상해두었다.

- GET / : 메인 페이지
- GET /login : 로그인 페이지
- GET /signup : 회원가입 페이지
- Post /signup : 회원가입 처리

## 메인 컨트롤러

메인 컨트롤러를 만들어준다. 아직 크게 하는건 없고 main view만 반환해주면 된다.

```java
@Controller
public class MainController {

    @GetMapping("/")
    public String main(Model model) {
        return "main";
    }
}
```

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">
  <head>
    <title>Spring Boot Demo</title>
  </head>
  <body>
    <h1>Welcome to...</h1>
  </body>
</html>
```

![main-page-1](/assets/images/2025-02-08-spring-boot-login-system-example/main-page-1.png)

## 회원가입 컨트롤러

스프링 시큐리티에서는 보안의 많은 관점을 알아서 처리해 준다.
하지만 사용자 등록 절차에는 직접 개입하지 않기 때문에 직접 처리 방법을 구현해줘야 한다.

- GET /signup : 회원가입 페이지
- Post /signup : 회원가입

앞 서 말한대로 spring security의 기본 보안 구성에서는 모든 HTTP 요청 경로는 인증 되어야 한다.
하지만 signup 페이지는 로그인(인증) 전에도 접근 가능해야만 한다. 따라서 별도의 Config가 필요하다.

### SecurityConfig 생성

다음과 같이 SecurityConfig 클래스를 생성해준다.

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .authorizeHttpRequests((authorize) -> authorize
                        .requestMatchers("/login").permitAll()
                        .requestMatchers("/signup").permitAll()
                        .anyRequest().authenticated()
                )
                .httpBasic(Customizer.withDefaults())
                .formLogin(Customizer.withDefaults());

        return http.build();
    }
}
```

WebSecurityConfigurerAdapter는 Deprecated 되어 최신버전에는 사용할 수 없다. 대신 위와같이 SecurityFilterChain를 구성하여 bean으로 등록해주면 된다.
로그인 페이지와 회원가입 페이지외의 나머지 페이지는 로그인 필요하다고 가정하고 설정하였다.
permitAll 은 모든 요청을 허용한다. authenticated는 인증된 사용자에 대한 요청만 허가한다.

이제 회원가입 페이지에 로그인 없이 접근할 수 있게 되었다.

### view 구현

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">
  <head>
    <title>Sign up</title>
  </head>
  <body>
    <h1>Sign up</h1>
    <form method="POST" th:action="@{/signup}" id="signupForm">
      <label for="email">Email: </label>
      <input id="email" type="email" name="email" /><br />

      <label for="username">Password: </label>
      <input id="username" type="password" name="password" /><br />

      <label for="name">Name: </label>
      <input id="name" type="text" name="name" /><br />

      <input type="submit" value="Register" />
    </form>
  </body>
</html>
```

![signup-form](/assets/images/2025-02-08-spring-boot-login-system-example/signup-form.png)

#### th:action

왜 th:action을 사용하였을까? 여기서는 그냥 action을 사용했어도 큰 차이가 없었지만, th:action 을 사용하면 url을 동적으로 생성할 수 있다. (context 경로에 대한 prefix를 붙힌다든지, value 를 중간에 mapping 한다든지)
그리고 중요한 이유가 하나가 더 있는데 아래에서 추가로 설명한다.

### 회원가입 시도해보기

만든 form으로 회원가입을 시도해보면 다음과 같은 결과가 나온다.

![signup-form-submit-result](/assets/images/2025-02-08-spring-boot-login-system-example/signup-form-submit-result.png)

우선 우리가 signup form submit을 처리하기 위한 post mapping을 추가해주지 않았다. 따라서 다음 단계에서는 post mapping 처리를 추가해 줄 것이다. 그런데 그 전에 개발자 콘솔을 보게되면 우리가 정의하지 않은 \_csrf 라는 값이 form data에 추가되어 있는 것을 볼 수 있다. 이게 th:action을 사용한 또 다른 이유이다.

Spring Security에는 CSRF 보호 기능이 기본적으로 활성화되어 있다. 그리고 th:action을 사용하면 html을 렌더링 하면서 token 값을 form에 추가한다.

### csrf

[spring security doc - csrf](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html)

Cross-Site Request Forgery 의 약자이다. CSRF는 사용자 몰래 특정 요청을 보내는 공격 기법이다. 공격자는 사용자가 인증된 세션을 악용해 원하지 않는 작업(예: 비밀번호 변경, 데이터 전송)을 수행하도록 한다.

#### cors 와의 차이

csrf 와 cors와 종종 헷갈리는 경우가 있는것 같아 정리해보았다.

- csrf 의 경우 동일한 사이트나 다른 사이트에서 보내는 요청이 유효한지 확인하기 위해 CSRF 토큰을 통해서 요청을 검증한다. 요청에서 token이 없거나 올바르지 않다면 요청을 거부한다.

  - CSRF 토큰 뿐 아니라 SameSite 쿠키 옵션을 통해 쿠키 허용 범위를 조절하는 방법도 함께 사용된다.

- cors 의 경우 다른 오리진(도메인, 프로토콜, 포트가 다른 경우)을 통해서 온 요청을 제한하거나 허용하는 메커니즘이다.

### user entity 생성하기

다음과 같이 user entity 클래스를 만들어준다.

```java
@Data
@Entity
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique=true)
    private String email;

    private String name;

    private String password;

    @CreationTimestamp
    private LocalDateTime createdAt;

}
```

@CreationTimestamp 는 엔티티가 처음 저장될 때 해당 필드 값을 현재 VM의 타임스탬프로 설정한다.

### mysql config

application.yaml 에 다음과 같이 설정해주었다.

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/test
    username: root
    password: mysqlrootpassword
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        show_sql: true
        format_sql: true
```

#### mysql docker-compose

mysql 이 따로 없다면 docker를 이용하면 간단하게 mysql 서버를 실행시킬 수 있다.
사용한 docker-compose 파일은 다음과 같다.

```yaml
services:
  mysql:
    image: mysql:8.0.33
    container_name: test-mysql
    ports:
      - "3306:3306" # HOST:CONTAINER
    environment:
      MYSQL_ROOT_PASSWORD: mysqlrootpassword
      MYSQL_DATABASE: test
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    volumes:
      - test-mysql-data:/var/lib/mysql
    healthcheck:
      test: '/usr/bin/mysql --user=root --password=mysqlrootpassword --execute="SHOW DATABASES;"'
      timeout: 60s
      retries: 30
      interval: 1s

volumes:
  test-mysql-data:
```

#### spring.jpa.hibernate.ddl-auto 속성

이 속성은 개발시에 사용하면 편리하게 개발할 수 있다. 다만 production 환경에서 잘못 사용되었을 경우 큰 문제가 발생될 수 있으니 주의가 필요하다.

- create - 먼저 기존 테이블을 삭제한 다음 새 테이블을 생성.
- update - entity 기반으로 생성된 모델을 기존 스키마와 비교한 후 변경된 부분을 업데이트. (애플리케이션에서 더 이상 필요하지 않더라도 기존 테이블이나 열은 삭제하지 않음)
- create-drop - create + 모든 작업이 완료된 후 데이터베이스를 삭제.
- validate - 필요한 테이블과 열의 존재 여부만 확인, 없을 경우 예외 발생.
- none - DDL 생성 안함.

production 환경에서는 liquibase 와 같은 db 버전 관리 도구를 사용하는 것이 좋다.

update로 두고 어플리케이션을 실행할 경우 테이블이 없으므로 다음과 같이 ddl을 수행한다.

![ddl-auto-result](/assets/images/2025-02-08-spring-boot-login-system-example/ddl-auto-result.png)

데이터베이스 에서 조회해봐도 정상적으로 설정된 것을 확인해볼 수 있다.

![ddl-auto-result-datagrip](/assets/images/2025-02-08-spring-boot-login-system-example/ddl-auto-result-datagrip.png)

## userRepository 만들기

[JpaRepository](https://docs.spring.io/spring-data/jpa/docs/current/api/org/springframework/data/jpa/repository/JpaRepository.html)를 상속하면 기본적으로 제공되는 메소드들이 있다. 일단은 추가 구현 메소드 없이 바로 사용하도록 하겠다.

```java
public interface UserRepository extends JpaRepository<User, Long> {
}
```

## post 요청 mapping 하기

Form을 통해 User 정보가 들어오는 것을 가정하고 userRepository를 통해 save를 한다.
이후 login 페이지로 리다이렉트하여 로그인을 진행할 수 있도록 한다.

```java
@PostMapping("/signup")
public String processSignup(User user) {
    userRepository.save(user);
    return "redirect:/login";
}
```

save 하면 다음과 같이 query가 처리된다.

![entity-save-result](/assets/images/2025-02-08-spring-boot-login-system-example/entity-save-result.png)

데이터베이스 에서 조회한 결과는 다음과 같다.

![entity-save-result-datagrip](/assets/images/2025-02-08-spring-boot-login-system-example/entity-save-result-datagrip.png)

## Password Encoder 사용하기

위에서 repository를 통해 entity를 database 로 저장하였다.
하지만 이 과정에서 아쉬운 점이 있다면 비밀번호가 평문으로 저장되어 그대로 노출되어 있다는 것이다.

Spring Security에서는 Password 에 대한 처리를 돕기 위해 Password Encoder를 제공하고 있다.

- NoOpPasswordEncoder
- StandardPasswordEncoder(sha-256)
- BCryptPasswordEncoder
- Pbkdf2PasswordEncoder
- SCryptPasswordEncoder
- Argon2PasswordEncoder

우리는 이 중 Argon2PasswordEncoder 를 사용할 것이다. (간단하게 사용할 것이라면 BCrypt도 나쁘지 않은 선택이라고 생각한다.)

SecurityConfig 클래스에 PasswordEncoder bean을 등록한다.

```java
@Bean
public PasswordEncoder encoder() {
    return Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8();
}
```

참고로 Argon2 를 사용하려면 bouncycastle 의존성을 추가해줘야한다. `implementation 'org.bouncycastle:bcprov-jdk18on:1.80'`

데이터 처리 단계를 2단계로 나눈다. 기존에는 Form 을 통해 온 데이터를 바로 User로 담았지만, 이제는 SignupRequestDto를 중간에 두어 원문으로 데이터를 받은 뒤, 암호화 하여 User 데이터를 생성한다.

```java
@Data
public class SignupRequestDto {

    private String email;

    private String name;

    private String password;

    private LocalDateTime createdAt;

    public User toUser(PasswordEncoder passwordEncoder) {
        return new User.UserBuilder()
                .email(email)
                .name(name)
                .password(passwordEncoder.encode(password))
                .build();
    }
}
```

롬복의 builder 어노테이션을 사용하였다. User 클래스는 다음과 같이 수정되었다.

```java
@Data
@Entity
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
```

최종적으로 SignController 의 processSignup 메소드는 다음과 같이 변경되었다.

```java
@PostMapping("/signup")
public String processSignup(SignupRequestDto signupRequestDto) {
    userRepository.save(signupRequestDto.toUser(passwordEncoder));
    return "redirect:/login";
}
```

이제 평문이 아닌 해시 처리가 된 상태인 것을 확인할 수 있다.

![entity-save-result-after-password-encoder](/assets/images/2025-02-08-spring-boot-login-system-example/entity-save-result-after-password-encoder.png)

## 로그인 처리하기

스프링 시큐리티를 이용하여 로그인을 처리하기 위해서는 UserDetails 과 UserDetailService를 구현해야 한다.

### UserDetails 구현하기

UserDetails를 사용하면 스프링 프레임워크 내에서 사용자 정보를 사용할 수 있다.
이전에 만들었던 User 클래스에 UserDetails 를 상속하여 구현한다.
UserDetails 에는 다음과 같은 메소드가 있다.

- Collection<? extends GrantedAuthority> getAuthorities(); - 필수
- String getPassword(); - 필수
- String getUsername(); - 필수
- boolean isAccountNonExpired()
- boolean isAccountNonLocked()
- boolean isCredentialsNonExpired()
- boolean isEnabled()

이에 따라 User 클래스를 최종적으로 다음과 같이 구현하였다.

```java
@Data
@Entity
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique=true)
    private String email;

    private String name;

    private String password;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of();
    }

    @Override
    public String getUsername() {
        return email;
    }

}
```

참고로 여기서 username은 단순히 user 의 name 을 반환하는것이 아니다. 이후에 UserDetailService 를 구현해보면 알수 있겠지만 사용자를 특정할 수 있는 값이여야 한다. 그래서 여기서는 username 으로 email을 지정하였다.

### 구조 개선하기

UserDetailService 를 구현하기에 앞서 현재의 코드 구조를 개선해보자.

SignupController 가 UserRepostiroy와 PasswordEncoder를 가지고 있기 때문에
UserService를 만들어서 SignupController 는 UserService 만을 바라보도록 한다.

```java
@Controller
@AllArgsConstructor
public class SignupController {

    private UserService userService;

    @GetMapping("/signup")
    public String signup() {
        return "signup";
    }

    @PostMapping("/signup")
    public String processSignup(SignupRequestDto signupRequestDto) {
        userService.processSignup(signupRequestDto);
        return "redirect:/login";
    }
}
```

```java
@Service
@AllArgsConstructor
public class UserService {

    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;

    public void processSignup(SignupRequestDto signupRequestDto) {
        userRepository.save(signupRequestDto.toUser(passwordEncoder));
    }
}
```

### userRepository에 findByEmail 추가

아까 설명에서 다음과 같은 이야기를 하였다.

> 이후에 UserDetailService 를 구현해보면 알수 있겠지만 사용자를 특정할 수 있는 값이여야 합니다. 그래서 여기서는 username 으로 email을 지정하였습니다.

마찬가지로 UserDetailService 에서 username을 통해 사용자를 검색해야하므로 미리 findByEmail 를 구현해준다.

```java
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

}
```

### UserDetailService 구현하기

이전에 만들었던 UserService 클래스에 UserDetailsService 를 상속하여 구현한다.
UserDetailsService 에는 loadUserByUsername 메소드가 있다.

```java
@Service
@AllArgsConstructor
public class UserService implements UserDetailsService {

    private UserRepository userRepository;
    private PasswordEncoder passwordEncoder;

    public void processSignup(SignupRequestDto signupRequestDto) {
        userRepository.save(signupRequestDto.toUser(passwordEncoder));
    }

    @Override
    public UserDetails loadUserByUsername(String username)
            throws UsernameNotFoundException {
        return userRepository.findByEmail(username)
                .orElseThrow(() ->
                        new UsernameNotFoundException("username '" + username + "' not found"));
    }
}
```

loadUserByUsername 메서드는 사용자 정보를 로드한다.

UserDetails 를 상속한 사용자 정보가 반환되면 이후에는 AuthenticationManager 에서 비밀번호 검증을 진행한다.
이 떄 bean으로 등록한 PasswordEncoder를 사용하여 검증을 하게 된다.

사용자가 별도의 검증 로직을 작성할 필요 없이 검증이 진행된다.

이제 로그인을 할 수 있다.

## 로그인한 사용자 인지하기

세션을 통해 사용자 인지하는 방법은 여러가지가 있다. 대표적으로는 다음과 같다.

- Principal 객체 활용
- Authentication 객체 활용
- SecurityContextHolder 사용
- @AuthenticationPrincipal 어노테이션 활용

여기서는 메인페이지에서 Principal을 사용하여 메인페이지에 로그인한 사용자의 이메일을 보여주도록 개선해본다.

```java
@GetMapping("/")
public String main(Model model, Principal principal) {
    String email = principal.getName();
    model.addAttribute("email", email);
    return "main";
}
```

```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:th="http://www.thymeleaf.org">
  <head>
    <title>Spring Boot Demo</title>
  </head>
  <body>
    <h1>Welcome [[${email}]]</h1>
  </body>
</html>
```

principal 객체를 통해 model 으로 로그인한 사용자의 email을 받아와서 view에서 보여주고 있다.
![main-page-2](/assets/images/2025-02-08-spring-boot-login-system-example/main-page-2.png)

## 로그아웃 하기

로그아웃의 경우에도 기본적으로 설정되어있다. `/logout` 경로로 접근하면 확인할 수 있다.

![logout-page](/assets/images/2025-02-08-spring-boot-login-system-example/logout-page.png)

## 마무리

이번 시간에는 스프링 부트의 Auto Configuration 및 Spring Security 기본 동작을 활용해 로그인과 회원가입 기능을 구현해보았다.

관심이 있다면 다음과 같은 내용을 추가적으로 다뤄보면 좋을 것 같다.

- Role 에 따른 인증 규칙
- 커스텀 로그인, 로그아웃 상세 설정
- Property 설정 (ConfigurationProperties)
- Profile 설정
- 로깅 구성하기 (logback)
