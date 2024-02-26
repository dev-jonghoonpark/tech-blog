---
layout: post
title: "Jekyll 실행시 `level': undefined method `[]' for nil (NoMethodError) 에러 해결법"
categories: [블로그]
tags: [루비, ruby, bundle, jekyll, level, fiber, NoMethodError]
date: 2024-02-26 22:00:00 +0900
image:
  path: /assets/images/2024-02-26-jekyll-serve-error-level-undefined-method/error.png
---

최근에 맥북을 구매하면서 환경을 새로 구성하였다.

mac 기본 버전인 2.6.x 에서 ruby 버전을 올리고  
평소대로 `bundle exec jekyll serve` 를 수행하려 했는데 아래와 같은 에러가 발생되었다.

```rb
jekyll 4.3.2 | Error:  undefined method `[]' for nil
/opt/homebrew/Cellar/ruby/3.3.0/lib/ruby/3.3.0/logger.rb:384:in `level': undefined method `[]' for nil (NoMethodError)

    @level_override[Fiber.current] || @level
                   ^^^^^^^^^^^^^^^
```

- ruby 3.3.0 
- bundler 2.5.4
- jekyll 4.3.2

인 상황에서 발생한 이슈이다.

## 해결방법

jekyll 를 4.3.3 으로 올리면 해결된다.

`Gemfile` 에서 `jekyll` 에 대한 버전 명시를 해준 뒤 

```rb
...
gem 'jekyll', "= 4.3.3"
...
```

`bundle install` 을 진행하여 `Gemfile.lock` 파일내 버전 정보를 업데이트 한 후 `Gemfile` 에서는 다시 버전 명시를 지워주었다.

## 참고

[https://talk.jekyllrb.com/t/error-when-executing-bundle-install/8822](https://talk.jekyllrb.com/t/error-when-executing-bundle-install/8822)