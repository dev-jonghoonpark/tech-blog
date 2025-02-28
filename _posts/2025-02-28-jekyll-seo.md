---
layout: "post"
title: "[Spring] Jekyll SEO 개선해보기 (description, thumbnail 자동 생성)"
description:
  "Spring Boot를 활용하여 Jekyll 블로그의 SEO를 개선하기 위해 description과 썸네일을 자동 생성하는\
  \ 프로그램을 개발한 경험을 공유합니다. Open Graph 메타데이터를 활용하여 링크 미리보기를 개선하고, AI를 통해 본문 요약 및 썸네일\
  \ 이미지를 생성하여 블로그의 시각적 매력을 높였습니다. 이 과정에서 Java와 Spring Boot를 사용하여 CLI 환경에서 실행 가능한 애\
  플리케이션을 구현하였으며, 최종적으로 자동 생성된 description과 썸네일을 확인할 수 있습니다."
categories:
  - "개발"
tags:
  - "Jekyll"
  - "SEO"
  - "Java"
  - "Spring"
  - "og"
  - "Open Graph"
  - "og:description"
  - "og:image"
  - "thumbnail"
  - "Spring AI"
  - "Spring Boot"
  - "CommandLineRunner"
  - "awt"
date: "2025-02-28 14:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-02-28-jekyll-seo.jpg"
---

# Jekyll SEO 개선해보기 (description, thumbnail 자동 생성)

이 글에서는 Spring Boot를 활용해 description과 썸네일을 자동 생성하는 프로그램을 만든 경험을 공유한다.
Jekyll 기반 블로그를 운영하며 SEO 개선 필요성을 느꼈고, 이를 개선하기 위해 application 을 개발하여 보았다.

## 동기

평소에 [geeknews](https://news.hada.io/) 를 잘 보고 있는 편이다. geeknews 의 경우 링크를 공유할 경우 다음과 같이 해당 글과 관련된 썸네일이 함께 나오게 된다.

![geek news](/assets/images/2025-02-28-jekyll-seo/geeknews-thumbnail-example.png)

geeknew 를 예시로 들었지만 다른 사이트들도 내용에 따라 동적으로 썸네일이 생성되곤 한다. 그런 사이트들처럼 내 블로그에서도 썸네일이 나오면 좋겠다는 생각을 하였다.

그렇다고 썸네일을 수동으로 만드는건 번거로운 일이다. 디자인 작업할 재주도 딱히 없다. 따라서 자동으로 되게 하고 싶었다.

처음에는 jekyll 이 ruby로 구현되어 있기 때문에, ruby 기반의 플러그인 형태로 만들어보려고 했다.
하지만 ruby 를 알지 못하다보니 꽤나 진입장벽이 있어서 금새 흥미를 잃어버렸었다.

최근에 다시 흥미가 생겨 다시 시도해보았고, 이번에는 반드시 개발하겠다는 생각으로 java 로 개발하였다.
하는김에 LLM(AI)을 이용하여 description 도 자동으로 생성되게 하면 좋겠다 생각되어 함께 구현하였다.

## 개념

### Open graph

우선 Open Graph에 대해서 간단하게 설명해보겠다.

Open Graph(OG)는 웹페이지의 메타데이터를 표준화하기 위해 페이스북에서 개발한 프로토콜이다.

Open Graph를 적절히 사용하면 링크 미리보기에서 제목(og:title), 설명(og:description), 이미지(og:image)를 제공하여 사용자가 콘텐츠를 더 매력적으로 볼 수 있다.

여러 property 중 `og:image` property 는 소셜 미디어 플랫폼이나 메신저에서 웹페이지 링크가 공유될 때, 그 링크를 설명하는 미리보기(preview)를 생성하는 데 사용된다.

더 자세한 내용은 [Open Graph](https://ogp.me/) 페이지에서 확인할 수 있다.

### jekyll markdown 구조

jekyll 의 post 에 사용되는 markdown 파일은 다음과 같은 구조를 가지고 있다.

```yaml
---
layout: "post"
title: "[Spring] 스프링에서 jwt를 이용한 인증시스템 만들기"
categories: ["스터디-자바"]
tags:
  - "Java"
  - "Spring"
  - "Spring Boot"
  - "Spring security"
  - ...
date: "2025-02-21 15:00:00 +0000"
toc: true
---
본문 시작
```

두 번재 `---` 를 기준으로 위에는 yaml 을 통해 메타데이터를 기록하고 아래에는 본문 내용을 markdown 으로 작성한다.

## 구현

### 구상

구현은 다음과 같이 구상하였다.

1. Spring AI 를 통해 LLM 을 사용하여 본문을 한문단으로 요약한다.
2. 썸네일 이미지를 생성하여 `/assets/thumbnails` 에 썸네일을 저장한다.
3. markdown 상단의 메타데이터 영역을 업데이트 한다.

### description 생성하기

```java
public class DescriptionService {

    private ChatModel chatModel;

    public String createDescription(String postAbsoluteFilePath) throws IOException {
        Path filepath = Paths.get(postAbsoluteFilePath);
        String content = Files.readString(filepath);
        String prompt = "SEO 를 위한 description 내용을 작성하려고합니다. `---` 아래 내용을 한문단으로 요약해주세요.\n" +
                "바로 description 으로 적용할 수 있도록 불필요한 말은 하지 말아주세요.\n" +
                "기본적으로 한글로 요약해주세요. 다만 본문이 영어일 경우에는 영어로 요약해주세요. \n" +
                "---\n" +
                content;

        ChatResponse response = chatModel.call(
                new Prompt(prompt,
                        OpenAiChatOptions.builder()
                                .model(OpenAiApi.ChatModel.GPT_4_O_MINI)
                                .temperature(0.4)
                                .build()
                ));

        return response.getResult().getOutput().getText();
    }
}
```

적절히 prompt 를 작성한 후, `.md` 파일에서 내용을 가져와 미리 작성된 prompt 에 포함시켜 api 를 호출하였다.

ChatModel 이 자동 구성 될 수 있도록 다음과 같이 `application.yaml` 을 작성해준다.

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
```

`${}`는 Spring의 Property Placeholder 기능이다. 환경 변수나 외부 설정 값을 가져와 연결시킨다.

### thumbnail 생성하기

#### 배경 이미지 다운로드 하기

배경 이미지를 어떻게 할까 리서치를 하다가 [picsum](https://picsum.photos/) 이라는 서비스를 발견하였다. 이미지를 랜덤하게 반환해준다.

여기서 반환해 주는 이미지는 Unsplash 에 등록된 이미지를 가져오는데 다음과 같은 정책을 따른다고 한다.

- 모든 이미지는 무료로 다운로드 및 사용 가능
- 상업적 및 비상업적 목적 으로 사용 가능
- 허가 불필요(저작자 표시를 할 경우 감사하게 생각함!)

그래서 맘놓고 사용하였다.

1200 x 630 사이즈의 미미지가 필요해서 `https://picsum.photos/1200/630` 를 GET 호출한 후, 나오는 랜덤한 이미지를 다운로드 하였다.

#### 썸네일 이미지 생성하기

`awt` 패키지의 `Graphics2D` 를 사용하여 원하는 구성으로 리소스들을 배치한 후 저장한다.

바로 전에서 다운로드한 이미지를 배경으로 깔고 투명도를 조절 해 준 후, 중앙에 텍스트로 제목을 배치하도록 하였다.

코드가 꽤 기므로 링크 첨부로 대체한다.

[DrawUtil.java](https://github.com/dev-jonghoonpark/jekyll-seo-helper/blob/main/src/main/java/org/example/jekyllseohelper/util/DrawUtil.java)

사용해보니 web의 canvas 와 비슷한 느낌이 들었다. 생각보다 사용이 쉽지만은 않다. 생각보다 많은 시간이 소요되었다.

### yaml 파서

우리가 오늘 생성할 description 과 thumbnail 은 윗 부분(메타데이터)에 업데이트 되어야 한다.
그래서 yaml 부분을 쉽게 파싱할수 있도록 파서를 도입하였다.

Java 에서 사용할 수 있는 yaml 파서를 찾아보니 SnakeYAML 이라는 애가 먼저 검색에 나왔으나,
spring boot 의 경우 기본적으로 `jackson` 을 이미 포함하고 있으므로 jackson 을 사용하기로 결정하였다.

spring boot 에 jackson 은 포함되어 있으므로, 거기에 추가적으로 `jackson-dataformat-yaml` 의존성을 추가한다.

```groovy
implementation 'com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:2.18.2'
```

yaml을 read, write 하기 위한 메소드를 `YamlUtil` 이라는 클래스에 구현하였다. ObjectMapper의 생성자에 `YAMLFactory` 인스턴스를 전달한게 포인트 이다.

```java
public class YamlUtil {

    private static final ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

    static {
        mapper.findAndRegisterModules();
    }

    public static PostInfo getPostInfo(String filename) throws IOException {
        return mapper.readValue(new File(filename), PostInfo.class);
    }

    public static String toYamlString(PostInfo postInfo) throws IOException {
        return mapper.writeValueAsString(postInfo);
    }

}
```

markdown 파일 상단의 메타데이터를 파싱 할 수 있도록 다음과 같이 클래스를 작성하였다.
record 의 경우 java 14 부터 지원하는 기능인데, 만약 그것보다 낮은 버전을 쓰고 있다면 직접 객체를 구현해도 된다.

```java
@Data
@JsonIgnoreProperties
public class PostInfo {
    private String layout;
    private String title;
    private String description;
    private String[] categories;
    private String[] tags;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss Z")
    private ZonedDateTime date;
    private Boolean toc;
    private Image image;

    public record Image(String path) {}

    // ...
}
```

### 외부에서 실행시키기

rest api 가 아닌 cli 에서 호출이 되었다는 생각이 들어서 찾아보니 `CommandLineRunner` 라는 것이 있어 적용해보았다.

`CommandLineRunner` 는 spring boot application 을 cli 환경에서 실행시킬 수 있도록 돕는다. 해당 인터페이스에 있는 `run(String... args)` 메소드를 구현시켜 주면 된다.

```java
@Slf4j
@AllArgsConstructor
@SpringBootApplication
public class JekyllSEOHelperApplication implements CommandLineRunner {

    private final ApplicationContext applicationContext;
    private final DescriptionService descriptionService;
    private final ThumbnailService thumbnailService;

    public static void main(String[] args) {
        SpringApplication.run(JekyllSEOHelperApplication.class, args);
    }

    @Override
    public void run(String... args) throws Exception {
        log.debug(Arrays.toString(args));
        Arrays.stream(args).filter((filename) -> filename.startsWith("/_posts/"))
                .map((filename) -> filename.substring(1))
                .forEach((filename) -> {
                    try {
                        PostInfo postInfo = YamlUtil.getPostInfo(filename);
                        log.debug(postInfo.toString());

                        String description;
                        if (postInfo.getDescription() == null) {
                            description = descriptionService.createDescription(filename);
                        } else {
                            description = postInfo.getDescription();
                        }

                        if (postInfo.getImage() == null) {
                            thumbnailService.createThumbnail(filename, postInfo.getTitle());
                        }

                        postInfo.update(filename, description);

                        JekyllUtil.updatePost(filename, postInfo);
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                });

        SpringApplication.exit(applicationContext, () -> 0);
    }

}
```

`ApplicationContext`을 넣은 이유는 `SpringApplication.exit` 명령어를 통해 필요한 로직 수행이 종료되었다면 SpringApplication 을 종료시키기 위해서이다.

### spring boot 어플리케이션 jar 파일로 빌드하기

빌드시 jar 파일이 생성되게 하기 위해 `build.gradle` 에 다음과 같은 영역을 추가해주었다.

```groovy
jar {
    manifest {
        attributes 'Main-Class': 'org.example.jekyllseohelper.JekyllSEOHelperApplication'
    }
}
```

## 실행

최종적으로 생성된 jar 파일로 다음과 같이 명령어를 작성하여 cli에서 실행시킬 수 있다.

```sh
OPENAI_API_KEY=YOUR_OPENAI_API_KEY java -jar jekyll-seo-helper-0.0.1-SNAPSHOT.jar "/_posts/post1.md" "/_posts/post2.md" ...
```

`YOUR_OPENAI_API_KEY` 는 본인의 API KEY 값으로 대체하면 된다.

## 최종 결과물

먼저 결과물은 여기서 확인할 수 있다.

[https://github.com/dev-jonghoonpark/jekyll-seo-helper](https://github.com/dev-jonghoonpark/jekyll-seo-helper)

### 테스트 입력

입력글: [[Spring] 스프링에서 jwt를 이용한 인증시스템 만들기](/2025/02/22/creating-an-authentication-system-with-jwt-in-java-spring)

### 생성된 description

> 스프링에서 JWT(Json Web Token)를 이용한 인증 시스템 구축 방법을 소개합니다. 이 글에서는 세션 토큰 방식과 JWT의 차이점을 설명하고, JWT의 구조, 대칭 및 비대칭 키 암호화 방식, 그리고 실제 구현 방법을 다룹니다. 또한, Spring Security와 의 통합 방법을 통해 JWT 기반 인증을 설정하는 방법도 안내합니다. JWT는 효율적이고 확장 가능한 인증 방식이지만, 보안상의 고려가 필요하므로 프로젝트 요구사항에 맞는 적절한 인증 방식을 선택하는 것이 중요합니다.

### 생성된 thumbnail

![thumbnail example](/assets/thumbnails/2025-02-22-creating-an-authentication-system-with-jwt-in-java-spring.jpg)

## 마무리

![my blog thumbnail example](/assets/images/2025-02-28-jekyll-seo/myblog-thumbnail-example.png)

이제 내 블로그도 썸네일이 잘 보인다. 이번 시간을 통해 평소에 해보고 싶었던 프로젝트를 마무리 하였다. Spring 을 이용하여 간단한 프로그램을 만들어 볼 수 있어서 재밌었다.

## 기타

github action 과 연동하면 좋을 것 같아서 graal vm 을 이용한 native image 를 생성해보려고 했는데 아쉽게도 native image 에서 awt 에 대한 문제를 해결하지 못한 것으로 보인다.

[no awt in java.library.path](https://github.com/oracle/graal/issues/4124)

그래서 그냥 jar 를 만들어서 실행시키는 것으로 스스로 합의를 보았다.
