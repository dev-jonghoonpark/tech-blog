---
layout: "post"
title: "Blue-Green 배포 구현하기 (Nginx + Podman + Spring Boot)"
description: "Podman과 Nginx를 활용하여 Blue-Green 무중단 배포를 구현하는 과정을 다룹니다. YAML anchor를 활용한 podman-compose 설정, Nginx upstream 전환을 통한 트래픽 스위칭, 헬스체크와 drain 대기를 포함한 배포 스크립트 작성까지 실제 적용 과정에서 겪은 문제와 해결 방법을 정리합니다."
categories:
  - "개발"
tags:
  - "podman"
  - "blue-green"
  - "deploy"
  - "nginx"
  - "Spring Boot"
  - "무중단 배포"
date: "2026-03-23 02:30:00 +0900"
toc: true
---

## 배경

K8S 를 사용할 때는 쉽게 무중단 배포를 구현할 수 있다. 하지만 Kubernetes(K8S)를 작은 프로젝트에 도입할 수는 없다. 과도한 엔지니어링이 되어버리기 때문이다. K8S 를 사용하지 않는 경우에는 어떻게 무중단 배포를 할 수 있을까?

현재는 Podman 을 이용하여 K-DEVCON 서비스를 운영하고 있다. Spring Boot 서버는 Nginx Proxy 를 거쳐 운영되고 있다.
현재 구성은 컨테이너를 재생성하는 동안 순단이 발생한다. 서비스 규모가 작아서 큰 문제는 아니었지만, 항상 아쉬움이 있었기 때문에, K8S 없이 Blue-Green 배포 방식으로 무중단 배포를 구현해보기로 했다.

### 기존 구조

```
Nginx (Podman 컨테이너) → host.containers.internal:8080 → App 컨테이너
```

- Nginx도 Podman 컨테이너로 운영 중
- 단일 슬롯(8080)으로 운영
- `podman-compose up --force-recreate`로 배포 → 컨테이너 재시작 동안 순단 발생

### 목표 구조

```
Nginx → upstream (8080 or 8081) → Blue 또는 Green 컨테이너
```

- Blue(8080)와 Green(8081) 두 슬롯을 두고
- 비활성 슬롯에 새 버전을 배포하고 헬스체크 통과 후
- Nginx upstream 전환으로 트래픽을 무중단 전환

## 1. Nginx 설정 변경

기존 conf 파일에서 `upstream` 블록을 추가하고, `proxy_pass`가 upstream을 참조하도록 변경한다.

```nginx
upstream k_devcon_backend {
    server host.containers.internal:8080;  # blue
    # server host.containers.internal:8081;  # green (전환 시 주석 교체)
    keepalive 8;
}

server {
    listen 443 ssl;
    http2 on;
    server_name api.k-devcon.com;

    # SSL, 보안 헤더 등 기존 설정은 그대로 유지

    location / {
        proxy_pass http://k_devcon_backend;  # 직접 IP 대신 upstream 참조
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # ... 기타 프록시 설정
    }
}
```

기존 설정에서 `proxy_pass` 부분만 upstream 블록으로 빼면 되기 때문에 SSL, 보안 헤더, WebSocket 설정 등은 건드리지 않아도 된다.

`keepalive 8`은 Nginx worker 프로세스 1개당 upstream과 유지할 최대 유휴 연결 수다. 이 설정이 있으면 Nginx가 upstream과의 연결을 재사용하므로 매 요청마다 TCP 핸드셰이크를 하지 않아도 된다. reload 시에는 기존 keepalive 연결이 정리되면서 새 upstream으로 자연스럽게 전환되기 때문에 Blue-Green 전환이 더 깔끔해진다. 소규모 서비스 기준으로 8 정도면 충분하다고 하여 일단 8으로 잡았다.

배포 스크립트에서 `sed`로 upstream의 주석을 교체하는 방식으로 트래픽을 전환한다. 배포 스크립트는 아래에서 다시 이야기 한다.

## 2. podman-compose.yml 구성

Blue와 Green 두 서비스를 정의할 때, 환경변수/볼륨/로깅 같은 공통 설정이 중복된다. YAML anchor(`&`)와 alias(`*`)를 활용하면 한 곳에서 관리할 수 있다.

```yaml
x-server-common: &server-common
  image: k-devcon-server:latest
  environment:
    - SPRING_DATASOURCE_URL=jdbc:mysql://...
    - SPRING_DATASOURCE_USERNAME=...
    - SPRING_DATASOURCE_PASSWORD=...
    - SPRING_JPA_SHOW_SQL=false
    - SPRING_PROFILES_ACTIVE=...
  volumes:
    - ./logs:/var/log/app:U
    - ./og-html:/app/og-html:U
    - ./resolv.conf:/etc/resolv.conf:ro
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "10"

services:
  k-devcon-server-blue:
    <<: *server-common
    container_name: k-devcon-server-blue
    ports:
      - "8080:8080"
    restart: "unless-stopped"

  k-devcon-server-green:
    <<: *server-common
    container_name: k-devcon-server-green
    ports:
      - "8081:8080"  # 호스트 8081 → 컨테이너 내부 8080 (내부 포트는 Blue와 동일)
    restart: "no"
```

### x- prefix

`x-` prefix는 Docker/Podman Compose 스펙에서 **사용자 정의 확장 필드**를 나타낸다. Compose 파서는 `services`, `volumes`, `networks` 같은 예약 키워드 외의 최상위 키를 만나면 오류를 내는데, `x-` prefix가 붙으면 "커스텀 필드"로 인식하고 무시한다.

- `x-` → Compose 스펙 (파싱 오류 방지)
- `&` → YAML 자체 기능 (anchor 선언, `<<: *`로 참조)

### container_name 주의

Blue와 Green에 동일한 `container_name`을 쓰면 이름 충돌로 두 번째 컨테이너가 실행되지 않는다. 반드시 `k-devcon-server-blue`, `k-devcon-server-green`으로 구분해야 한다.

### Green의 restart 정책

Green 슬롯은 평소에 중지 상태로 유지되므로 `restart: "no"`로 설정한다. 자동 재시작이 필요 없다.

## 3. 배포 스크립트

```bash
#!/bin/bash
# deploy-all.sh
set -e

echo "🌟 [ALL] Blue-Green 배포를 시작합니다..."

NGINX_CONTAINER="k-devcon-nginx"
NGINX_CONF="/etc/nginx/conf.d/api.k-devcon.com.conf"
ACTIVE_FILE="$HOME/k-devcon/.active_slot"

# 현재 활성 슬롯 확인
if [ -f "$ACTIVE_FILE" ]; then
    ACTIVE=$(cat "$ACTIVE_FILE")
else
    ACTIVE="blue"
fi

if [ "$ACTIVE" = "blue" ]; then
    NEXT="green"
    NEXT_PORT=8081
    NEXT_SERVICE="k-devcon-server-green"
    PREV_SERVICE="k-devcon-server-blue"
else
    NEXT="blue"
    NEXT_PORT=8080
    NEXT_SERVICE="k-devcon-server-blue"
    PREV_SERVICE="k-devcon-server-green"
fi

echo "▶ 현재 활성: $ACTIVE  →  배포 대상: $NEXT (:$NEXT_PORT)"

# 1. 비활성 슬롯에 새 버전 띄우기
echo "--- [DEPLOY TO $NEXT] ---"
podman-compose up -d --force-recreate $NEXT_SERVICE

# 2. 헬스체크 (최대 60초)
echo "⏳ 헬스체크 중... (http://localhost:$NEXT_PORT/actuator/health)"
for i in $(seq 1 20); do
    STATUS=$(curl -sf "http://localhost:$NEXT_PORT/actuator/health" \
             | grep -o '"status":"UP"' || true)
    if [ -n "$STATUS" ]; then
        echo "✔ 헬스체크 통과!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "✘ 헬스체크 실패 — 배포 중단 (기존 $ACTIVE 유지)"
        podman-compose stop $NEXT_SERVICE
        exit 1
    fi
    echo "  대기 중... ($i/20)"
    sleep 3
done

# 3. Nginx upstream 전환
echo "--- [SWITCH TRAFFIC → $NEXT] ---"
if [ "$NEXT" = "green" ]; then
    podman exec $NGINX_CONTAINER sed -i \
        -e 's|server host.containers.internal:8080;.*# blue|# server host.containers.internal:8080;  # blue|' \
        -e 's|# server host.containers.internal:8081;.*# green|server host.containers.internal:8081;  # green|' \
        "$NGINX_CONF"
else
    podman exec $NGINX_CONTAINER sed -i \
        -e 's|# server host.containers.internal:8080;.*# blue|server host.containers.internal:8080;  # blue|' \
        -e 's|server host.containers.internal:8081;.*# green|# server host.containers.internal:8081;  # green|' \
        "$NGINX_CONF"
fi

podman exec $NGINX_CONTAINER nginx -t && podman exec $NGINX_CONTAINER nginx -s reload
echo "✔ 트래픽이 $NEXT (:$NEXT_PORT)로 전환됨"

# 4. 기존 연결 drain 대기 후 이전 슬롯 중지
echo "--- [STOP $ACTIVE] ---"
for i in $(seq 10 -1 1); do
    echo -ne "기존 연결 drain 대기... ${i}초\r"
    sleep 1
done
echo ""

podman-compose stop $PREV_SERVICE
echo "$NEXT" > "$ACTIVE_FILE"

echo ""
echo "✨ 배포 완료! 활성 슬롯: $NEXT"
```

### 마지막에 10초 대기가 필요했던 이유

Nginx reload 후 바로 이전 슬롯을 중지하면, 아직 처리 중이던 요청이 강제 종료되어 순단이 발생한다. 10초 대기로 기존 연결이 처리 완료될 시간을 확보하여 이 문제를 줄이고자 하였다.

## 전체 배포 흐름 요약

```
1. deploy-all.sh      → 비활성 슬롯에 새 버전 배포 + 헬스체크
2. 헬스체크 통과       → Nginx upstream 전환 (nginx -s reload)
3. drain 대기          → 기존 연결 처리 완료 대기
4. 이전 슬롯 중지
```

Nginx reload는 기존 연결을 끊지 않고 새 연결만 새 upstream으로 보내기 때문에 무중단 전환이 가능하다.

## 마무리

Kubernetes 없이도 Podman + Nginx 조합으로 충분히 Blue-Green 무중단 배포를 구현할 수 있었다. 핵심은 간단하다. 두 개의 슬롯을 두고, Nginx upstream 전환으로 트래픽을 넘기는 것이다.

실제로 적용해보니 배포 중 순단이 완전히 사라지지는 않았다. 아주 약간의 오류 응답이 발생되었다. 가능한 원인으로는 Nginx reload 시점에 기존 keep-alive 커넥션이 이전 슬롯으로 계속 유지되는 경우나, Spring Boot의 graceful shutdown이 설정되지 않아 컨테이너 중지 시 처리 중인 요청이 끊기는 경우 등을 의심하고 있다. 이 부분은 조금 더 파악해 봐야겠다. 하지만 그럼에도 다운타임을 줄일 수 있었다는 것에 일단은 만족해보고자 한다.

작은 프로젝트에 K8S를 도입하는 건 과하다고 생각되지만, 무중단 배포를 시도하고 싶다는 비슷한 고민을 하고 있다면 이 방식을 참고해 보면 좋겠다.
