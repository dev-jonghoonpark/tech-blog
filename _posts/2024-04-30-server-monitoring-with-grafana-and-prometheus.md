---
layout: post
title: "[Grafana, Prometheus] 서버 상태 모니터링 하기"
categories: [개발]
tags:
  [
    grafana,
    그라파나,
    Prometheus,
    프로메테우스,
    docker,
    도커,
    호스트,
    host,
    모니터링,
    monitoring,
  ]
date: 2024-04-30 22:00:00 +0900
toc: true
---

## 개요

점점 더 많은 도커 컨테이너들이 추가되어 가고 있다.

![portainer summary](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/portainer-summary.png)

portainer를 통해서 도커 컨테이너들을 관리하고 있는데 현재 26개의 컨테이너가 활성화 되어있는 것을 확인할 수 있었다.

슬슬 메모리가 부족하거나 하는 이슈가 발생할 때가 되지 않았을까 싶었던지라 상태 모니터링을 할 수 있으면 좋겠다 생각이 들었다.

서버 모니터링에 대해서 찾다보니 그라파나와 프로메테우스 조합을 소개하는 글들을 볼 수 있었는데, 마침 지난번에 로그 시스템을 구축하면서 그라파나를 설치한 상태였기 때문에 프로메테우스를 추가하여 모니터링을 해보면 어떨까 생각이 들었다. (프로메테우스에 대한 이름은 들어보았지만, 사용해본적은 없기에 맘에 드는 조합이였다고 할 수 있다.)

- [[Java] spring boot 프로젝트에 loki 추가해서 로그 수집하기](https://jonghoonpark.com/2024/04/22/java-loki-grafana-with-spring-boot)

## 본문

- [Server Monitoring using Prometheus and Grafana](https://sahsumit.medium.com/server-monitoring-using-prometheus-and-grafana-a041b3333fa7)

위 글을 주로 참고하였고, 나의 상황에 맞게 수정하였다.

### Prometheus docker compose 구성하기

나의 경우에는 grafana 와 관련된 부분은 이미 구성이 되어있기 때문에 prometheus 와 관련된 부분만 추가적으로 구성하였다. grafana의 docker-compose.yaml 구성이 궁금하면 위의 링크를 참조하면 된다.

```yaml
version: "3"

volumes:
  prometheus-data:
    driver: local

networks:
  prometheus:
    driver: bridge

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./config:/etc/prometheus/
      - prometheus-data:/prometheus
    networks:
      - prometheus
    ports:
      - "9090:9090"
  node_exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: node_exporter
    command:
      - "--path.rootfs=/host"
    pid: host
    ports:
      - "9100:9100"
    restart: unless-stopped
    volumes:
      - "/:/host:ro,rslave"
    networks:
      - prometheus
```

참고로 [Node Exporter](https://github.com/prometheus/node_exporter)는 하드웨어 와 운영체제 메트릭을 수집하는 프로메테우스 수집기라고 한다.

이후, 안내에 따라 `config/prometheus.yml` 을 생성하여 아래 내용을 추가하였다.

```yml
global:
  scrape_interval: 15s

  external_labels:
    monitor: "codelab-monitor"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]
  - job_name: "node_exporter"
    static_configs:
      - targets: ["node_exporter:9100"]
```

이후 docker compose 를 재실행 한다.

### Grafana DataSource 등록하기

우선 구성한 Prometheus를 Grafana DataSource로 등록해줘야 한다.

`Connections` - `Data sources` 에서 등록할 수 있다.

![add datasource](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/add-datasource.png)

연결 주소는 본인의 주소로 해주면 되고 포트는 `docker-compose.yaml` 에서 정한 포트를 사용하면 된다. 저장하면서 연결이 정상적으로 되는지 테스트 해볼 수 있다.

### Grafana Dashboard 구성하기

Grafana에는 다양한 Dashboard를 구성할 수 있다.

그리고 다른 사람들이 미리 구성해둔 구성을 사용할 수도 있다.

- [그라파나 공식 대시보드 공유 게시판](https://grafana.com/grafana/dashboards/)

왼쪽 사이드 메뉴에서 Datasource 로 필터링을 할 수 있다. 우리는 Prometheus 를 사용할 것이기 때문에 해당 필터로 적용하였고 첫번째 템플릿을 다운로드 하였다.

![dashboard template list](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/dashboard-template-list.png)

먼저 나는 등록해둔 대시보드가 없었기 때문에 아래와 같이 나왔다.

![create dashboard](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/create-dashboard.png)

create dashboard 버튼을 누르면 직접 대시보드를 구성할수도, 미리 구성된 대시보드를 적용할 수도 있다. 나는 미리 구성된 대시보드를 적용할 예정이기 때문에 import dashboard를 눌러 진행하였다.

![import dashboard](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/import-dashboard.png)

## 마무리

다음과 같이 grafana 에서 내 서버상태를 확인할 수 있었다.

![my dashboard](/assets/images/2024-04-30-server-monitoring-with-grafana-and-prometheus/my-dashboard.png)

메모리와 저장소 공간을 늘려주면 좋을 것 같다.

요즘에는 종종 llama3 를 쓰기 때문에 GPU 현황도 확인할 수 있도록 대시보드를 개선하면 좋을 것 같다는 생각도 들었다.
