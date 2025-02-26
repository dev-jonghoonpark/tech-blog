---
layout: "post"
title: "슬랙봇을 이용하여 슬랙 대화 내역 PostgreSQL 데이터베이스에 기록하기"
description: "슬랙봇을 사용하여 슬랙 대화 내역을 PostgreSQL 데이터베이스에 기록하는 방법을 소개합니다. 무료 플랜의 제한으로 메\
  시지가 사라지는 문제를 해결하기 위해, supabase의 PostgreSQL을 선택하여 데이터베이스를 구성하고, node.js 서버에서 봇을 실\
  행하여 메시지를 자동으로 저장하도록 설정했습니다. 이 과정에서 데이터베이스와 서버 간의 연결을 설정하고, 슬랙에서 발생하는 메시지를 데이터베이스\
  에 삽입하는 코드를 구현했습니다. 최종적으로 데이터가 정상적으로 저장되는 것을 확인하였으며, 향후 사용자 친화적으로 데이터를 재구성할 계획입니다\
  ."
categories:
- "개발"
- "스터디-테스트"
tags:
- "slack"
- "bot"
- "PostgreSQL"
- "pg"
- "socket mode"
- "app level token"
- "bot token"
- "socket mode"
date: "2023-12-17 11:40:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2023-12-17-archive-slack-messages-to-postgresql-database.jpg"
---

오랜만에 시간이 나서 개발을 진행해보았다.

시간이 있을 때 커뮤니티 운영과 관련된 도구들을 만들어 보려고 하고 있다.

K-DEVCON 슬랙방에는 링크드인 프로필 공유부터 시작해서 질문/답변 등 다양한 것들이 올라오는데 무료 플랜(free plan)이다 보니 메시지들이 90일이 지나면 보이지 않는것이 너무 아쉬웠다.

메시지를 다시 볼 수 있으면 좋을 것 같았기 때문에 일단은 데이터들을 DB에다 쌓아놓는 것 까지 구현해본 후 시간이 있을 때 데이터를 가공해서 보기 쉽게 해보자고 생각을 하였다.

데이터 수집은 봇에 권한을 주어서 진행하기로 생각하였고  
기존부터 봇을 node.js 서버에서 실행하고 있었기 때문에 [해당 레포지토리](https://github.com/k-devcon/k-devcon-slack-bot)에 이어서 작업을 하였다.

먼저 데이터를 저장하기 위해서 데이터베이스를 선택해야 했다.  
처음에는 nosql로 간단하게 구현해볼까 생각을 하였고, 그 중에서도 firebase의 firestore를 사용해볼까 생각을 하였지만, 항상 firebase 에서 데이터베이스를 쓰다가 아쉬운점이 많았던 기억이 떠올라서 이번에는 supabase에서 제공해주는 PostgreSQL을 사용해 보기로 결정하였다.

처음 생성해보는데 한국 리전의 인스턴스도 제공해줘서 좋았던 것 같다.

# 슬랙봇을 이용하여 슬랙 대화 내역 PostgreSQL 데이터베이스에 기록하기

## Database 구성하기

Database 접속 정보는 supabase에서 제공해준다. 제공해주는 정보대로 datagrip에 입력하니 바로 잘 연결되었다.

우선은 Table을 만들건데, 그렇게 거창한 것은 만들 생각이 없었고, 자동으로 생성되는 id (auto-increment)와 json 데이터만 저장할 수 있는 테이블이면 됐다.

그래서 먼저 auto-increment primary key를 만드는 방법에 대해서 검색해보니 SERIAL 타입을 사용하면 된다는 답변을 볼 수 있었다.
정보대로 SERIAL 타입으로 지정해주니 `default nextval('slack_messages_id_seq'::regclass)` 로 자동으로 변경되었다.

최종적으로 slack_message_events 테이블은 다음과 같은 DDL을 가지게 되었다.

```
create table slack_message_events
(
    id   integer default nextval('slack_messages_id_seq'::regclass) not null
        constraint slack_message_events_pk
            primary key,
    data jsonb
);
```

json와 jonsb(json binary)의 차이는 [공식 홈페이지 문서](https://www.postgresql.org/docs/current/datatype-json.html)에 잘 나와 있다.

> The json data type stores an exact copy of the input text, which processing functions must reparse on each execution; while jsonb data is stored in a decomposed binary format that makes it slightly slower to input due to added conversion overhead, but significantly faster to process, since no reparsing is needed.

번역해보면 다음과 같다.

> json 데이터 유형은 입력 텍스트의 정확한 사본을 저장하므로 처리 함수가 실행할 때마다 다시 구문 분석해야 하는 반면, jsonb 데이터는 분해된 바이너리 형식으로 저장되므로 변환 오버헤드가 추가되어 입력 속도가 약간 느리지만 다시 구문 분석할 필요가 없으므로 처리 속도가 훨씬 빠릅니다.

## 서버 구성하기

이제 데이터베이스는 생성이 완료가 되었으니 서버에도 접속정보를 구성해주면 된다.

찾아보니 PostgreSQL과 연결하기 위한 [pg 라이브러리](https://node-postgres.com/)가 있었다. 설치후 사용하면 된다.

bot은 계속 띄워져 있는 상태로 동작하기 때문에 안내문서를 따라 다음과 같이 pool을 생성하였다.

```js
import dotenv from "dotenv";
dotenv.config();

import pkg from "pg";
const { Pool } = pkg;

const pool = new Pool({
  host: process.env.DATABASE_HOST,
  user: process.env.DATABASE_USER,
  database: process.env.DATABASE_NAME,
  password: process.env.DATABASE_PASSWORD,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

export { pool };
```

위에서 작성한 pool을 bot의 동작 코드에서 받아다 쓰면 된다.

```js
import dotenv from "dotenv";
dotenv.config();

import { pool } from "../../database/pool.js";

import pkg from "@slack/bolt";

const { App } = pkg;
const app = new App({
  token: process.env.ARCHIVE_BOT_TOKEN,
  appToken: process.env.ARCHIVE_APP_TOKEN,
  socketMode: true,
});

app.event("message", async ({ event, context, client, say }) => {
  await pool.query("insert into slack_message_events(data) values($1)", [
    event,
  ]);
});

export { app };
```

코드는 짧지만 bot 설정 페이지에서 작업 해줘야 하는 것이 꽤 된다. 필요한 범위의 permission을 선택하고 bot token과 app token 발급이 필요하며 socket mode를 활성화해야한다.

# 결과

이렇게 구성한 후 바로 배포 해보았다.

배포가 된 후 테스트를 위해 챗봇과 이야기를 진행해보았고, 확인 결과 슬랙에서 새로운 메시지가 작성되었을 때 정상적으로 데이터베이스에 insert 하는 것을 확인할 수 있었다.

![messages-in-slack](/assets/images/2023-12-17-use-postgresql-in-nodejs/messages-in-slack.png)

![messages-in-database](/assets/images/2023-12-17-use-postgresql-in-nodejs/messages-in-database.png)

supabase 의 DB를 사용하였기 때문에 웹 콘솔을 통해서도 database를 확인할 수 있었다.

![](/assets/images/2023-12-17-use-postgresql-in-nodejs/messages-in-supabase.png)

앞서 이야기 한 대로 추후에 시간이 있을 때 이 데이터들을 사용자 입장에서 보기 편하도록 재구성 해볼 예정이다.
