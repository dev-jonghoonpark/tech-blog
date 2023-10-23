---
layout: post
title: jekyll 에서 page 파일들의 계층 구조 표현하기 (with jekyll plugin)
categories: [블로그, 개발]
tags:
  [계층 구조, page, jekyll, 블로그, plugin, logseq, obsidian, ruby, markdown]
date: 2023-10-23 21:30:00 +0900
---

\* 회사 업무와 관련된 것들이라서 혹시 몰라 이미지들에 블러 처리를 하였습니다.

# 서론

최근 회사에서 신규 서비스를 위한 테스트 케이스들을 작성하기 위해 어떤 도구를 사용할지 고민하다가 logseq 이라는 프로그램을 짧게 사용해보았다.
가장 관심있는 도구는 obsidian 이였으나 obsidian 의 경우 회사에서 사용하면 유료였어서 obsidian 의 대체제 같은 느낌으로 logseq 으로 결정하였다.
(사실 근데 obsidian도 잘 쓰지는 않는 편이다. 개인 컴퓨터에서 간단한 내용을 정리할떄 가끔 사용하는 정도다.)

한달 정도 사용한 것 같은데 쓰면 쓸수록 생각보다 너무 불편한 부분이 많아서 logseq의 사용을 멈추기로 하였다.

일단 내가 느낀 logseq 의 단점은 크게 아래와 같았다.

1. 전체 구조를 파악하기 힘들다. (작업이 얼마나 된 건지 파악하기 어려움.)
2. 검색이 어렵다. (파일 간 이동이 직관적이지 않음.)

전반적으로 제품의 마무리가 아쉬웠다. 계속 돼야 하는게 안되는 느낌이였다.

아무튼 logseq은 더 이상 사용하지 않기로 하였기 때문에  
그 다음 도구로 무엇을 쓸까 하다가 요즘 블로그 작성하는데 잘 쓰고 있는 jekyll을 사용해보기로 하였다.

jekyll은 정적 호스팅을 통해 다른 사람과 공유도 할 수 있을 뿐더러 그냥 에디터를 사용하면 되기 때문에 작성에도 훨씬 편리할 것이라 기대하였다.

> 애초에 문서 관리라는 본연의 기능에서 불편함을 느꼈기에 다른 도구로 옮기고자 결정이 든 것이지만
> 초기에 obsidian이나 logseq을 고려했던 이유 중 하나는 문서간의 연관성을 보여주는 기능이 있었기 때문이기도 하였다.
>
> ![interactive-graph](/assets/images/2023-10-23-jekyll-plugin-for-page-structure-view/interactive-graph.png)
>
> 처음 했던 기대는 문서간의 관계를 효과적으로 볼 수 있을 줄 알았다.
> 근데 막상 사용해면 의문이 드는 기능이다. '이게 꼭 필요할까?' 라는 생각이 사용하면서 계속 들었다.
> 내 맘대로 노트들의 위치를 고정해 놓을 수도 없을 뿐더러 나갔다 들어오면 다시 초기화가 되기 때문에 개인적으로는 그저 시각적으로 이뻐보일 뿐이며 가치가 없는 데이터라는 생각이 들었다.

---

# 본론

남들에게 public 하게 보여줄 용도는 아니기 때문에 지킬 템플릿을 새로 생성하여 깨끗한 상태에서 시작하였고 필요한 최소의 세팅만 이 블로그에 있던 세팅을 참고하여 진행하였다.

jekyll의 경우 커스텀이 비교적 가능하기 때문에 메인페이지에서 페이지들의 목록이 구조적으로 보였으면 좋겠다고 생각하였다.

그래서 아래 이미지와 같은 페이지를 만들었다. 프로젝트에서 사용되는 컴포넌트들과 기능들을 구조에 따라 묶어서 관리하기 위해 목록화 해둔 모습이다.

![page-structure-view](/assets/images/2023-10-23-jekyll-plugin-for-page-structure-view/page-structure-view.png)

index.html에서 jekyll 에서 기본제공하는 site.posts 변수를 이용하면 현재 프로젝트에 생성되어 있는 페이지 파일들에 대한 정보들을 받아올 수 있다.

## 문제

근데 이 변수를 사용해서 메인 페이지를 구성하였을 때의 단점은 시각적으로 계층구조를 깔끔하게 보여주기 위해서는 불필요한 파일들도 넣어줘야 한다는 것이였다.

예를 들어 메인 페이지에서

> - Blog
>   - Page
>     - Resume

이런 느낌의 계층 구조를 표현하려고 한다면

> - \_posts
>   - Blog.md
>   - Blog
>     - Page.md
>     - Page
>       - Resume.md

이런식으로 만들어야 한다.
여기서 Blog.md 와 Page.md 는 실제로 사용하지도 않는 페이지인데 단지 구조만을 위해서 생성할 수 밖에 없었다.

## 해결과정

그래서 이 문제를 어떻게 해결할 수 있을까 고민하다가 플러그인를 만들어보게 되었다.

### 플러그인 만들기

플러그인을 만드는 방법은 공식 블로그에 나와있다.
나는 커스텀한 데이터를 삽입하는게 주된 목적이였기 때문에 Plugin 관련 문서 중에서도 [Generators 문서](https://jekyllrb.com/docs/plugins/generators/)를 참고하였다.
ruby는 익숙하지 않은 언어이기 때문에 각종 온라인 문서와 chatgpt를 적극 활용하였다.

결론적으로 만들어진 플러그인 파일은 다음과 같다.
find_files를 통해 경로의 모든 파일을 1차원 array로 받아온 후
데이터들을 전처리 하고 계층 구조로 변환한다.

/\_plugins/page_structure.rb

```ruby
require 'json'

require_relative "util/file_util.rb"

module Jekyll
  class PageStructureGenerator < Generator
    safe true
    def generate(site)
      projectRoot = Dir.pwd

      full_filenames = []
      find_files(full_filenames, projectRoot + '/_pages')

      basepath_length = projectRoot.length + 8

      root = {name: 'root', children: []}

      full_filenames.each do |str|
        current_level = root
        filename = str.slice(basepath_length..-1).gsub(/\.md$/, '')
        segments = filename.split('/')

        segments.each_with_index do |segment, index|
          existing_node = current_level[:children].find { |node| node[:name] == segment }
          if existing_node
            current_level = existing_node
          else
            new_node = { name: segment, children: [] }
            if index == segments.length - 1
              new_node[:url] = '/' + filename
            end
            current_level[:children] << new_node
            current_level = new_node
          end
        end
      end

      site.data['page_structure'] = root.to_json
    end
  end
end
```

/\_plugins/util/file_util.rb

```ruby
def find_files(filenames, base_dir)
  Dir.foreach(base_dir) do |entry|
    next if entry == '.' || entry == '..'

    entry_path = File.join(base_dir, entry)
    if File.directory?(entry_path)
      find_files(filenames, entry_path)
    else
      filenames.push(entry_path)
    end
  end
end
```

### index.html에 적용하기

위에서 변환한 데이터는 index.html 에서 아래와 같이 사용하였다.

```html
---
layout: default
---

<section class="pages">
  <ul></ul>
</section>

<script>
  const structure = JSON.parse(
    decodeURIComponent("{{ site.data.page_structure | uri_escape  }}")
  );
  console.log(structure);

  const pages = document.querySelector("section.pages ul");

  createStructure(structure.children, 1);

  function createStructure(children, level) {
    children.forEach((item) => {
      const li = document.createElement("li");
      if (item.url) {
        li.innerHTML = `<a href="${item.url}" data-level="${level}" class="level-${level}">${item.name}</a>`;
      } else {
        li.innerHTML = `<div class="level-${level}">${item.name}</div>`;
      }
      pages.append(li);

      if (item.children.length > 0) {
        createStructure(item.children, level + 1);
      }
    });
  }
</script>
```

jekyll은 liquid template 을 사용한고 한다.
liquid template을 이용하면 template대로 적용된 정적 html이 나온다.

하지만 liquid template에 대한 지식이 부족하여 ruby에서 넘겨준 계층화된 데이터를 어떻게 처리해야할지 감이 오지 않았다.
결국 json으로 변환하여 js 단에서 처리하는 방향으로 진행하였다.

# 결론

시각적으로는 이전과 동일하다. 하지만 개선된 점이라면 이전에는 시각적으로 구조화된 모습을 보여주기 위해 불필요한 파일을 생성해야 했다면 이제는 더 이상 생성해주지 않아도 구조화된 모습을 볼 수 있게 되었다.

파일이 많으면 관리하기 힘들어진다. 어떤 파일이 실제로 가치있는 데이터가 있는지 덜 고민해도 되게 개선되었다고 생각한다.
