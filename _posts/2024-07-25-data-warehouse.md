---
layout: "post"
title: "[한빛앤] 데이터웨어하우스로 효율적인 분석 시스템 만들기 - 후기"
description: "한빛앤에서 진행한 세미나 \"데이터웨어하우스로 효율적인 분석 시스템 만들기\"에서는 데이터 웨어하우스의 개념과 OLTP,\
  \ OLAP의 차이, 데이터 웨어하우스와 데이터 레이크의 특징을 설명하며, 효과적인 데이터 분석을 위한 ETL 과정과 스타 스키마, 스노우플레이\
  크 스키마, 데이터 마트 구축 방법 등을 다루었습니다. 또한, 데이터 품질의 중요성과 분석 시 패턴을 찾아보는 접근법에 대한 팁도 공유되었습니다\
  ."
categories:
- "행사"
tags:
- "데이터웨어하우스"
- "Data Warehouse"
- "DW"
- "한빛앤"
- "분석"
- "analytics"
- "분석 시스템"
- "analytics system"
- "DDIA"
- "Data Driven"
- "Database"
- "DB"
date: "2024-07-25 10:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-07-25-data-warehouse.jpg"
---

[데이터웨어하우스로 효율적인 분석 시스템 만들기](https://festa.io/events/5501)

- 발표자: 강성욱([@LinkedIn](https://www.linkedin.com/in/sungwook-kang/)) / NOWCOM Sr.DBOps Engineer / [K-DEVCON](https://k-devcon.com) 파운더

![cardnews](/assets/images/2024-07-25-data-warehouse/cardnews.jpg)

[한빛앤](https://www.hanbitn.com/)에서 진행한 세미나에 참여하였다.

데이터 웨어하우스의 경우에는 책에서 종종 봤긴 했지만(아마 DDIA 에서 봤던것 같다), 간단하게 언급만 나오고 실제로 경험해볼 경험은 없었기에 이번 세미나에서 제대로 배울 수 있으면 좋겠다는 마음으로 행사에 참여하였다.

들으면서 메모한 것들을 정리해본다.

---

## 데이터웨어하우스?

- 데이터웨어하우스 : 데이터를 모아둔다.
- 최근에는 "데이터 웨어하우스" 라는 단어를 잘 사용하지 않는다. 하지만 이름이 바뀌었을 뿐 계속 사용되는 기술이다.
- 데이터 분석의 8할은 데이터 가공이다. 가장 중요한 것은 데이터의 품질이다. (GIGO, Garbage in garbage out)

## 빅 데이터 시스템이 꼭 필요한가?

- 어떠한 목적으로 데이터를 수집하는가? (비즈니스 목표 정의)
- 데이터가 목표와 일치하는지 정기적 확인

## OLTP, OLAP

- OLTP (트랜잭션), OLAP (분석)

## 데이터 웨어하우스 와 데이터 레이크

### 데이터 웨어하우스

- OLTP의 한계를 극복하기 위해 등장. 양질의 데이터를 쓸 수 있게 만들어 준다.
- 스키마를 미리 정해놓고 스키마에 맞게 정제 (schema-on-write)
- 분석 관점의 스키마

### 데이터 레이크

- 데이터를 있는 그대로 저장 (일단 수집하고 보자., raw data)
- 데이터를 캡처할 때 스키마의 구조가 정의되지 않음.
- 분석 당시 작성(schema-on-read)
- 용량이 부담될 수 있음.

## 구축해보기

### 서버 스펙

- rdb 그대로 사용해도 됨. 단 분리된 환경에서 진행할 것
- 큰 용량의 디스크
- CPU 코어가 많은 것이 유리
- 메모리는 많을 수록 좋음.

### ETL

data warehouse 에 넣기 전 처리

#### 부분 추출, 전체 추출

초기 로딩(전체 데이터를 가져옴)과 주기적 갱신
어느 주기로 가져올 것인가

##### 주기적 갱신시 고려사항

변경하는 데이터가 있으면 어떻게 할 것인가 (updated_at 이 없다면?)

- 전체데이터를 긁어와서 아우터 조인으로 찾음.
- CDC(capture data change), DML 트리거 통해서 변경 사항이 있을 때마다 별도 테이블에 기록하여 로딩

## 스타 스키마

다차원 데이터를 효과적으로 저장, 조회하기 위한 RDB 설계 기법

- 팩트 : 분석하고자 하는 대상 항목
- 디멘젼 : 사실을 보는 관점 (e.g. 월별, 날씨별, 상품별 ...)
- 하나의 모델에는 하나의 팩트 테이블이 존재한다.
- 비정규화 데이터를 사용하여 데이터 검색을 용이하게 한다. (테이블이 커지는 것을 무서워하면 안됨.)

팩트 테이블은 실제 데이터가 들어가면 안됨. 키로만 가지고 있어야 함. (중복데이터가 있으면 손해임)

## 스노우플레이크 스키마

약간의 정규화된 스키마를 사용함.
확장이 좋음.
바꾸는게 쉽지 않음.

## 데이터 마트

- 목적에 맞게 재집계 해둠
- 사용자에게 친절하지 않다.

### 데이터 마트 구축 방법

매일 쓰는걸 저장해둠.

## 차원

차원 : 분석하고자 하는 관점. 큐브를 구성하는 축

셀 단위로 데이터가 저장됨.

차원이 늘어나면 희박성(Sparsity)가 발생됨. (e.g. 날짜는 있는데 데이터가 없다면?)
희박성을 줄여야 함.

하이퍼 큐브 : 팽창해서 터짐? 팽창 계수?

차원을 어떻게 만들지 고민을 많이 해야함.

드릴 스루, 드릴 다운, - 한단계 내려가서 디테일한 데이터를 다룸.

## 데이터 웨어하우스 운영 팁

raw 데이터도 함께 보관 (과거 데이터를 얼마만큼 어떻게 보관할 것인가도 고민해야 함.)

대량의 데이터를 집계할 때에는 부분 집합으로 나누어 처리한 다음 상위 처리 과정으로 집계하여 리소스를 효율적으로 운영

## 분석 팁

처음부터 너무 디테일하게 보려고 하지 말고 패턴을 먼저 찾아봐라. (하나의 기준으로 데이터를 보려하지 말라. 여러 차원에서 보라. -> 안보이던 인사이트가 보일 수 있음.)
