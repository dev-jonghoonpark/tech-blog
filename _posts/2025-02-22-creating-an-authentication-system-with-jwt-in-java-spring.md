---
layout: "post"
title: "[Spring] 스프링에서 jwt를 이용한 인증시스템 만들기"
description:
  "스프링에서 JWT(Json Web Token)를 이용한 인증 시스템 구축 방법을 소개합니다. 이 글에서는 세션 토큰 방식과\
  \ JWT의 차이점을 설명하고, JWT의 구조, 대칭 및 비대칭 키 암호화 방식, 그리고 실제 구현 방법을 다룹니다. 또한, Spring Security와\
  의 통합 방법을 통해 JWT 기반 인증을 설정하는 방법도 안내합니다. JWT는 효율적이고 확장 가능한 인증 방식이지만, 보안상의 고려가 필요하므\
  로 프로젝트 요구사항에 맞는 적절한 인증 방식을 선택하는 것이 중요합니다."
categories:
  - "스터디-자바"
tags:
  - "Java"
  - "Spring"
  - "Spring Boot"
  - "Spring security"
  - "login"
  - "access token"
  - "refresh token"
  - "jwt"
  - "jjwt"
  - "rsa"
  - "hmac"
  - "private key"
  - "public key"
  - "JwtAuthenticationFilter"
  - "SecurityFilterChain"
date: "2025-02-21 15:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring.jpg"
---

# 스프링에서 jwt를 이용한 인증시스템 만들기

지난 시간에 [스프링 부트 기반 간단한 로그인, 회원가입 예제 만들어보기](/2025/02/08/spring-boot-login-system-example) 라는 글을 작성했었다.

해당 글에서는 전통적인 세션 토큰 방식을 활용하여 인증을 구현했다.

이번 글에서는 먼저 세션 토큰 방식에 대해 간단히 정리한 뒤, **JWT(Json Web Token)**를 활용한 인증 방식에 대해 알아보고 구현해보겠다.

## session token

![session token](/assets/images/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring/session-token.png)

서버에서 클라이언트의 인증 상태를 관리한다.
클라이언트는 서버가 준 세션 ID 값을 보관하고 있다가, 서버에 요청할 때 함께 요청한다.

이미지 출처 : [bytebytego](https://blog.bytebytego.com/p/sessions-tokens-jwt-sso-and-oauth)

## jwt

jwt는 SPA(Single Page Application) 과 마이크로서비스가 활성화 되면서 사용이 증가하게 된 방식이다. stateless 한 것이 특징이다.
(stateless는 서버가 클라이언트의 상태를 유지하지 않는 설계를 뜻한다. 이를 통해 서버 간 확장성과 분산 시스템의 효율성이 올라간다.)

![jwt](/assets/images/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring/JWT.png)

서버가 서명한 인증 토큰을 클라이언트가 보관한다.
서버는 클라이언트에 대해 알고 있지 못하며, 서버에 요청할 때 인증 토큰을 확인하여 올바른 서명일 경우 통과시킨다.

이미지 출처 : [bytebytego](https://blog.bytebytego.com/p/sessions-tokens-jwt-sso-and-oauth)

## session token 과 jwt 의 비교

두 가지 방식은 각자 장단점이 있다.

세션 토큰은 서버에 상태를 저장하므로 보안이 강하고 실시간 토큰 무효화가 가능하지만, jwt에 비하면 확장성이 낮다.

반면, JWT는 상태를 서버가 아닌 토큰에 포함하여 분산 시스템에서 확장성이 뛰어나지만, 토큰 탈취 시 무효화가 어렵고, 세션 토큰 방식에 비해 보내야 하는 데이터 크기가 커 전송 비용이 늘어날 수 있어 주의가 필요하다.

세션은 단일 서버나 보안 중심 애플리케이션에 적합하고, JWT는 마이크로서비스나 분산 환경에서 유리하다.

## access token 과 refresh token

방금 전에 jwt는 토큰 탈취 시 무효화가 어렵다는 설명을 하였다. 서명된 토큰은 유효 기간 내에 계속 사용할 수 있으며, 이를 방지하려면 블랙리스트 형태로 관리해야 한다.
이러한 문제을 해결하기 위한 방법 중 하나로 access token 과 refresh token을 나누어 관리하는 전략을 사용한다.

사용자가 인증할 때, 서버는 access token 과 refresh token 을 함께 발급한다.
access token 은 짧은 만료 시간을 가지며, 클라이언트에서만 관리한다.
refresh token 은 긴 만료 시간을 가지며, 서버에서도 관리한다.

일반적인 api 호출시 에는 access token을 사용한다.
access token 이 만료되었을 때에는 refresh token 을 이용하여 새로운 access token을 발급 받을 수 있다.

이 방식을 통해 access token이 탈취되더라도, 서버에서 refresh token 을 만료 시키면 탈취된 access token 의 만료 이후 추가적인 사용을 방지할 수 있다. 이 전략이 완벽한 방어수단은 아님에 주의하자.

추가적으로 짧다는 것은 주관적인데, 서비스에 따라서 적절한 시간을 설정해줘야 한다. 만료 시간을 짧게 설정했을 경우에는 보안은 강화될 수 있겠지만, 클라이언트가 자주 refresh 를 해줘야 하므로 통신 횟수가 늘어나게 된다. 반대로 길게 설정했을 경우에는 사용자는 편리할 수 있겠지만, access token이 탈취 당했을 경우 만료 처리에 어려움이 발생된다.

## jwt 구조 알아보기

[jwt.io](https://jwt.io/) 에 들어가면 온라인으로 테스트 해볼 수 있는 디코더가 제공된다.

![jwt.io](/assets/images/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring/jwt.io.png)

다음과 같은 예시 jwt 가 있어 가져와 보았다.

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30
```

`jwt`는 `header`, `payload`, `signiture` 3가지 파트로 구성되며, 각 파트는 `.(dot)` 으로 구분된다.

파트를 나눠보면 다음과 같이 나눠진다.

- header: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
- payload: `eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0`
- signiture: `KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30`

각 파트에 대해서 설명하자면 다음과 같다.

- header 파트는 이 jwt 가 어떤 알고리즘으로 생성되었는지에 대해서 설명한다.
- payload 파트는 실제 데이터(예: 사용자 정보, 만료 시간 등)가 담겨있다.
  - payload 는 원하는 대로 정보를 구성하여 구현할 수 있다. 대표적인 값들은 다음과 같다.
    - sub (subject): 토큰이 참조하는 대상 (id 나 대상을 정의할 수 있는 unique 값)
    - iat (issued at): 발행 시점
    - exp (expired at): 만료 시점
- signiture 파트는 이 토큰이 정상적으로 서명된 토큰인지 검증할 수 있는 값이 들어가 있다.
  - signiture 파트를 검증하기 위해서는 키가 필요하다.

header 파트와 payload 파트는 Base64Url로 인코딩된 것이므로 누구나 열어볼 수 있다. 따라서 민감한 정보를 담지 않도록 주의해야 한다.
(`Base64Url` 는 URL과 파일 시스템에서 안전하게 사용할 수 있도록 설계된 Base64를 기반으로 하는 변형 인코딩 방식입니다.)

## 대칭 키 와 비대칭 키

> JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

JWT는 secret(대칭 키) 또는 public/private key pair(비대칭 키)를 사용하여 서명할 수 있다.

### 대칭 키 암호화

> 대표적인 알고리즘 : HMAC (HMAC SHA 를 줄여서 HS 로 표기함)

대칭 키는 비교적 단순합니다. 하나의 키를 사용해 서명과 검증을 모두 수행할 수 있습니다. 그러나 이 방식은 서명 및 검증을 수행하는 모든 주체가 동일한 키(secret)를 알고 있어야 합니다. 키가 노출될 경우 보안에 큰 위협이 될 수 있으므로, 키 관리에 특히 주의해야 합니다.

### 비대칭 키 암호화

> 대표적인 알고리즘 : RSA (줄여서 RS 로 표기), RSA-PSS (줄여서 PS 로 표기), ECDSA

비대칭 키는 대칭 키보다 더 복잡하지만, 보안과 유연성 면에서 장점이 있다. 두 개의 키로 구성되며, 하나는 private key(비공개 키), 다른 하나는 public key(공개 키)이다.

private key는 서명과 검증 모두에 사용할 수 있다. public key는 서명은 불가능하며, 검증만 수행할 수 있다.

이를 통해 private key는 서명이 필요한 곳에서만 관리하고, public key는 검증이 필요한 곳에만 배포하는 전략을 사용할 수 있다. 이는 키 노출 위험을 줄이고 보안을 강화하는 데 도움이 된다.

## 실제로 서명 / 검증 구현하기

jwt 처리를 위해 `jjwt` 라이브러리를 사용하였다.

`build.gradle` 에는 다음과 같이 추가하였다.

```groovy
implementation 'io.jsonwebtoken:jjwt-api:0.12.6'
runtimeOnly 'io.jsonwebtoken:jjwt-impl:0.12.6'
runtimeOnly 'io.jsonwebtoken:jjwt-jackson:0.12.6'
```

### 대칭 키 방식

아래의 예시는 `HS256` 방식을 사용하였다.

먼저는 SecretKey를 생성해야 한다. SecretKey 인스턴스는 `Keys.hmacShaKeyFor` 를 통해서 생성할 수 있다.
이때 입력값의 bit 값이 중요하다. `hmacShaKeyFor` 의 구현을 보면 다음과 작성되어있는 것을 확인할 수 있다.

> JWA Specification (RFC 7518, Section 3.2) states that keys used with HMAC-SHA algorithms MUST have a size >= 256 bits

따라서 적어도 256 bit 이상의 입력값을 넣어줘야 한다.

256 bit의 문자열은 다음 코드로 생성할 수 있다.

```java
SecureRandom random = new SecureRandom();
byte[] bytes = new byte[32]; // 256 bits = 32 bytes
random.nextBytes(bytes);

StringBuilder hexString = new StringBuilder();
for (byte b : bytes) {
    hexString.append(String.format("%02x", b));
}

System.out.println("Random 256-bit string: " + hexString.toString());
```

생성된 hexString을 적절한 곳에 보관하고 있다가, 필요할 때 꺼내서 사용하면 된다. 앞서 말한것과 같이 secret 키는 유출되지 않도록 주의하자.

token 은 아래와 같이 생성한다.

```java
private String generateToken(String subject, long expirationTime) {
    Jwts.builder()
        .subject(subject)
        .issuedAt(new Date())
        .expiration(new Date(System.currentTimeMillis() + expirationTime))
        .signWith(secretKey)
        .compact();
}
```

검증은 다음과 같이 한다. parse 중 토큰이 잘못되었을 경우 Exception 에 걸린다. 여기서는 Exception 으로 처리했지만, 세부 Exception 케이스에 따라 적절히 처리를 해주면 된다.

```java
public Claims parse(String token) {
    try {
        return Jwts.parser().verifyWith(secretKey).build()
                .parseSignedClaims(token)
                .getPayload();
    } catch (Exception e) {
        log.error("jwt parse failed", e);
        return null;
    }
}
```

발급과 검증 모두 동일하게 secretKey를 사용하였다.

### 비대칭 키 방식 예시

아래의 예시는 `RS256` 방식을 사용하였다.

먼저는 다음과 같이 KeyGenerator 를 구성하였다.

```java
public class KeyGenerator {

    public static void main(String[] args) throws Exception {
        KeyPair keyPair = generateKeyPair();
        PrivateKey privateKey = keyPair.getPrivate();
        PublicKey publicKey = keyPair.getPublic();

        savePrivateKeyToFile(privateKey, "private_key.pem");
        savePublicKeyToFile(publicKey, "public_key.pem");
    }

    public static KeyPair generateKeyPair() throws NoSuchAlgorithmException {
        KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
        keyPairGenerator.initialize(2048); // Key size
        return keyPairGenerator.generateKeyPair();
    }

    // Private Key 저장
    public static void savePrivateKeyToFile(PrivateKey privateKey, String filePath) throws IOException {
        String privateKeyPem = "-----BEGIN PRIVATE KEY-----\n" +
                Base64.getEncoder().encodeToString(privateKey.getEncoded()) +
                "\n-----END PRIVATE KEY-----";

        try (FileWriter fileWriter = new FileWriter(filePath)) {
            fileWriter.write(privateKeyPem);
        }
    }

    // Public Key 저장
    public static void savePublicKeyToFile(PublicKey publicKey, String filePath) throws IOException {
        String publicKeyPem = "-----BEGIN PUBLIC KEY-----\n" +
                Base64.getEncoder().encodeToString(publicKey.getEncoded()) +
                "\n-----END PUBLIC KEY-----";

        try (FileWriter fileWriter = new FileWriter(filePath)) {
            fileWriter.write(publicKeyPem);
        }
    }

}
```

수행하면 아래와 같이 파일이 생성된다.

![private_key.pem](/assets/images/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring/private_key.pem.png)
![public_key.pem](/assets/images/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring/public_key.pem.png)

이 key 파일(.pem) 을 읽어올 수 있도록 KeyLoader 도 구현해주었다.

```java
public class KeyFileLoader {

    public static PrivateKey loadPrivateKeyFromFile(String filePath) throws Exception {
        String privateKeyPem = new String(Files.readAllBytes(Paths.get(filePath)))
                .replace("-----BEGIN PRIVATE KEY-----", "")
                .replace("-----END PRIVATE KEY-----", "")
                .replaceAll("\\s", "");

        byte[] keyBytes = Base64.getDecoder().decode(privateKeyPem);
        PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        return keyFactory.generatePrivate(keySpec);
    }

    public static PublicKey loadPublicKeyFromFile(String filePath) throws Exception {
        String publicKeyPem = new String(Files.readAllBytes(Paths.get(filePath)))
                .replace("-----BEGIN PUBLIC KEY-----", "")
                .replace("-----END PUBLIC KEY-----", "")
                .replaceAll("\\s", "");

        byte[] keyBytes = Base64.getDecoder().decode(publicKeyPem);
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        return keyFactory.generatePublic(keySpec);
    }
}
```

token 은 아래와 같이 생성한다. 토큰 발급에는 privateKey를 사용하였다.

```java
private String generateToken(String subject, long expirationTime) {
    Jwts.builder()
        .subject(subject)
        .issuedAt(new Date())
        .expiration(new Date(System.currentTimeMillis() + expirationTime))
        .signWith(privateKey)
        .compact();
}
```

검증은 다음과 같이 한다. 검증에는 publicKey를 사용하였다. parse 중 토큰이 잘못되었을 경우 Exception 에 걸린다. 여기서는 Exception 으로 처리했지만, 세부 Exception 케이스에 따라 적절히 처리를 해주면 된다.

```java
public Claims parse(String token) {
    try {
        return Jwts.parser().verifyWith(publicKey).build()
                .parseSignedClaims(token)
                .getPayload();
    } catch (Exception e) {
        log.error("jwt parse failed", e);
        return null;
    }
}
```

### Spring 에 적용하기

다음과 같이 `JwtAuthenticationFilter` 를 구현하였다. 빈으로 등록할 경우 전역적으로 필터가 걸려서 bean 으로 등록하지는 않았다.

```java
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private JwtService jwtService;

    public JwtAuthenticationFilter(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String token = extractToken(request);
        if (token != null) {
            Claims claims = jwtService.parse(token);
            if (claims != null) {
                UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(claims.getSubject(), null, List.of(new SimpleGrantedAuthority("ROLE_USER")));
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        }
        filterChain.doFilter(request, response);
    }

    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

다음과 같이 `SecurityFilterChain` 를 2개로 나누어 빈으로 등록하였다.

- `/api/public/**` 으로 접근하는 경우에는 `JwtAuthenticationFilter` 를 거치지 않도록 하였다.
- `/api/v1/**` 으로 접근하는 경우에는 `JwtAuthenticationFilter` 를 거쳐 헤더의 값을 검증하도록 하였다.

```java
@Bean
public SecurityFilterChain publicApiFilterChain(HttpSecurity http) throws Exception {
    http
        .securityMatcher("/api/public/**")
        .authorizeHttpRequests((authorize) -> authorize.anyRequest().permitAll())
        .httpBasic(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable);

    return http.build();
}

@Bean
public SecurityFilterChain apiFilterChain(HttpSecurity http) throws Exception {
    http
        .securityMatcher("/api/v1/**")
        .authorizeHttpRequests((authorize) -> authorize.anyRequest().authenticated())
        .addFilterBefore(new JwtAuthenticationFilter(jwtService), UsernamePasswordAuthenticationFilter.class)
        .httpBasic(Customizer.withDefaults())
        .csrf(AbstractHttpConfigurer::disable);

    return http.build();
}
```

## 마무리

지금까지 자바/스프링에서 jwt 를 통해 인증하는 방법에 대해서 알아보았다. JWT는 효율적이고 확장 가능한 인증 방식이지만, 단점도 존재한다. 따라서 프로젝트 요구사항에 맞게 인증 방식을 선택하는 것이 중요하겠다.
