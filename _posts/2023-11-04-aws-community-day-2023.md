---
layout: post
title: AWS Community day 2023 참여 기록 (with AWSKRUG)
description: AWS Community Day 2023에 참여한 기록으로, AWSKRUG 주최 행사에서 쿠버네티스 관련 핸즈온랩 세션에 참석하였습니다. 기차를 놓치는 해프닝이 있었지만 무사히 행사에 도착했으며, 다양한 트랙 중 컨테이너 세션을 선택했습니다. 실습은 자율적으로 진행되었고, 네트워킹 기회도 있었으나 제한적이었습니다. 앞으로 architecture 소모임에 참여할 계획이며, 핸즈온 세션 관련 내용을 별도로 정리할 예정입니다.
categories: [행사, 커뮤니티]
tags:
  [
    AWS,
    AWSKRUG,
    핸즈온,
    실습,
    EKS,
    쿠버네티스,
    컨테이너,
    Docker,
    Kubernetes,
    K8s,
    커뮤니티,
    행사,
    굿즈,
  ]
date: 2023-11-05 22:00:00 +0900
---

AWSKRUG 주최 행사(소모임 포함)에 3번째 참여이다.

![web-banner](/assets/images/2023-11-04-aws-community-day-2023/web-banner.jpeg)

AWS Community Day 2023 에 대한 정보는 [https://event-us.kr/awskrug/event/71783](https://event-us.kr/awskrug/event/71783) 에서 볼 수 있다.

주변에 같이 갈 사람은 없어서 혼자 당일치기로 다녀왔다.

아침부터 기차를 놓치게 되어서 살짝 멘붕이 되긴 했지만(태어나서 처음으로 기차를 놓쳤다), 다행히도 바로 취소표를 잡아서 늦지않게 행사장에 도착할 수 있었다.

행사는 아래와 같이 2일로 나눠졌다.

- 10월 28일 강연행사
- 11월 4일 핸즈온랩

나는 그 중 11월 4일의 행사에 참여하였다.

또 핸즈온랩은 4개의 트랙으로 나눠졌다.

- 데브옵스 (CI/CD 구축, Observability 구축 )
- 컨테이너 (Amazon EKS)
- 서버리스
- DeepRacer

이 중 나는 컨테이너 세션에 참여하였다.

![timetable](/assets/images/2023-11-04-aws-community-day-2023/timetable.png)

평소에도 쿠버네티스에 관심이 있었고, GDG에서 운영하는 쿠버네티스 잼도 참여했었지만 실제 업무에서는 사용하지 않다보니 가물가물 하기도 하고 그렇다고 혼자서 해보자니 아무래도 비용이 많이 들 것 같았기 때문에 이번 세션에 참여해서 접해봐야겠다 라고 생각하고 참여하였다.

행사 소개 때 해주시는 이야기를 들어보니 요즘은 무료 워크샵도 잘 되어 있고, Skill Builder 를 사용하면 적은 비용으로 실제 인프라 구성을 해보며 경험할 수 있다고 소개해주셔서 다음에는 그걸 이용해 봐야겠다는 생각이 들었다.

---

**aws 입구**  
![aws-entrance](/assets/images/2023-11-04-aws-community-day-2023/aws-entrance.jpg)

**받은 굿즈들**
![goods](/assets/images/2023-11-04-aws-community-day-2023/goods.jpg)
![badge](/assets/images/2023-11-04-aws-community-day-2023/goods-badge.jpg)
![detail](/assets/images/2023-11-04-aws-community-day-2023/goods-detail.jpg)

**핸즈온랩 진행 장소**
![track-info](/assets/images/2023-11-04-aws-community-day-2023/track-info.jpg)

![hands-on-lab-ready](/assets/images/2023-11-04-aws-community-day-2023/hands-on-lab-ready.jpg)

![hands-on-lab-start](/assets/images/2023-11-04-aws-community-day-2023/hands-on-lab-start.jpg)

---

이름을 적을 수 있는 뱃지를 주셨지만 네트워킹할 시간은 없었기 때문에 쓸 일은 없었다.

개발자 전투 식량은 끝나고 더 가져가도 된다고 했는데 손이 부족해서 많이는 못챙겨왔다. 회사 사람들한테 보여나 주려고 조금 가져왔다.

실습은 수업/강의 형태가 아닌 잘 만들어진 워크샵 자료를 참고하여 자율적으로 진행하는 방식이였다.
(이 부분은 살짝 아쉽긴 했지만 사실 실습이란게 예외상황도 많이 나오고 사람마다 실력도 다르기 때문에...)
모르는 것은 스탭 분들께 질문드리면 답변해주셨다.

한 테이블에는 3-4명 정도씩 앉았는데 옆에 계신분이 계속 살갑게 말을 걸어주셔서 그나마 다른 사람과 이야기 할 수 있었던것 같다.  
링크드인 1촌 신청도 걸어주셨다. 파워 e 이신 것 같았다.

---

소모임의 경우 architecture 소모임에 참여하려고 하고 있고, 마지막 모임이였던 8월 모임에도 참여했는데 최근에 운영진 분들이 바쁘시기도 하고 10월도 행사와 맞물려서 모임이 미루어졌다.

오늘 행사를 참여하면서 architecture 소모임 운영자분을 만났는데 다행히도 이번달(11월)은 진행 예정이라고 하셔서 기대하는 마음으로 다시 대전으로 돌아왔다.

---

참여했던 핸즈온 세션 관련된 내용은 기회가 된다면 조만간에 정리해서 별도의 포스트로 올려볼 예정이다. (요즘에는 정리하고 공부할게 끝이 없는 것 같다.)

11월, 12월에는 행사도 업무도 많다. 공부할 것도 많다. 일정 관리를 잘 해야겠다.
