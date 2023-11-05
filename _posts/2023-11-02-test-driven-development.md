---
layout: post
title: Test-Driven Development
categories: [스터디-테스트]
tags: [테스트, TDD, agile]
date: 2023-11-06 23:00:00 +0900
published: false
---

원문 : [Test-Driven Development](https://www.jamesshore.com/v2/books/aoad1/test_driven_development)  
James Shored의 Art of Agile Development의 TDD장

[마틴 파울러의 블로그 글](https://martinfowler.com/bliki/TestDrivenDevelopment.html)에 Kent Beck의 Test-Driven Development 책과 함께 소개되어 있는 글이다.

Kent Beck의 Test-Driven Development 도 조만간 읽어나가기 시작할 예정이지만
이 글도 소개되어 있어 번역하며 읽어 나가고자 한다.

이 글은 TDD를 적용하고 싶은 사람들을 위해 어떤 방식으로 작업을 해나가야 하는지에 대한 예시를 제공해준다.

---

## 테스트 주도 개발

우리는 작고 검증 가능한 단계들을 통해 잘 설계되고 잘 테스트되고 잘 구성된 코드를 생성합니다.

"프로그래밍 언어에 필요한 명령어는 'DWIM (do what I mean)'이라는 농담도 있습니다, '내가 작성 코드 대로가 아니라 내가 의도한대로 동작 해줘'"

프로그래밍을 하는 것은 까다롭습니다. 꾸준하게 완벽함을 유지해야 합니다. 몇달이든 몇년이든 끝없이 노력해야 합니다.
실수를 하면 적어도 컴파일 에러를 일으킵니다. 최악의 경우에는 알지 못하고 있다가 어느 순간 큰 문제를 일으키는 버그가 되기도 합니다.

---

Replace Method with Method Object는 1판에만 있음.
(2판에서는 일단 목차에서 사라짐.)

https://archive.org/details/RefactoringImprovingTheDesignOfExistingCode1stEditionByMartinFowlerKentBeckJohnB/page/n109/mode/2up
110 페이지

https://refactoring.guru/replace-method-with-method-object
아니면 여기서
