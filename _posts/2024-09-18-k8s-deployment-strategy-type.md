---
layout: "post"
title: "[k8s, kubernetes] 배포 전략 (deployment starategy)"
description: "Kubernetes의 배포 전략인 Rolling Update, Canary, Blue-Green에 대해 설명합니다. Rolling\
  \ Update는 새 버전의 복제본을 점진적으로 추가하여 업데이트하며, Canary는 소규모 사용자에게 새 버전을 테스트하여 위험을 줄이는 방식\
  입니다. Blue-Green 배포는 새 버전이 완전히 배포된 후 로드 밸런서를 통해 트래픽을 전환하여 이전 버전과 새 버전이 공존하는 시간을 최\
  소화합니다. 각 전략의 YAML 예시를 통해 서비스와 포드 간의 연결 방식을 설명합니다."
categories:
- "스터디-인프라"
- "개발"
tags:
- "k8s"
- "kubernetes"
- "deploy"
- "deployment"
- "deployment strategy"
- "rolling update"
- "canary"
- "blue-green"
date: "2024-09-18 11:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-09-18-k8s-deployment-strategy-type.jpg"
---

이번에 [google cloud 에서 진행하는 study jam](https://sites.google.com/view/2024-study-jams/ai?pli=1)에 참여 하였다.

이번에는 이전과 같이 커리큘럼이 딱 정해져 있는 형태는 아니고, 주어진 목록에서 원하는 것을 일정 갯수 이상 듣는 방식으로 진행되는 것으로 보인다.

그 중 내가 가장 관심 있었던 코스는 [Manage Kubernetes in Google Cloud](https://www.cloudskillsboost.google/course_templates/783) 였다.

들으면서 내용을 정리해보고자 한다.

---

참고 링크 : [https://www.cloudskillsboost.google/course_templates/783/labs/408508](https://www.cloudskillsboost.google/course_templates/783/labs/408508)

뱃지를 얻는데는 크레딧이 필요하지만, 그냥 보는 것에는 비용이 들지 않는 것으로 알고 있다. 필요하면 참고하면 좋을 것 같다.

## 개요

K8S의 배포 전략 타입 3가지에 대해서 소개한다.

- Rolling Update
- Canary
- Blue-Green

## 기본 컨셉

deployment yaml을 작성할 때 service 가 어떤 pod를 참조하게 할 지 seletor를 잘 지정하는 것이다.

## Rolling Update

![rolling update](/assets/images/2024-09-18-k8s-deployment-strategy-type/rolling%20update.png)

K8S에서 기본적으로 사용되는 방식이다.

배포가 새 버전으로 업데이트되면 새 복제본 집합(replicaSet)이 생성되고 이전 복제본 집합의 복제본을 줄이면서 새 복제본 집합의 복제본 수를 서서히 증가시킨다.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: "hello"
spec:
  selector:
    app: "hello"
  ports:
    - protocol: "TCP"
      port: 80
      targetPort: 80
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
        track: stable
        version: 1.0.0
    spec:
      containers:
        - name: hello
          image: kelseyhightower/hello:1.0.0

    ...생략...
```

yaml 파일이 업데이트되면 그에 따라 rolling update가 진행된다.

## Canary

![canary](/assets/images/2024-09-18-k8s-deployment-strategy-type/canary.png)

카나리아 배포를 사용하면 일부 사용자를 대상으로 프로덕션 환경에서 새 배포를 테스트할 수 있다. 소규모 사용자에게 변경 사항을 릴리스하여 새 릴리스를 하면서 발생될 수 있는 위험을 완화할 수 있다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
        track: canary
        version: 2.0.0
    spec:
      containers:
        - name: hello
          image: kelseyhightower/hello:2.0.0

    ...생략...
```

별도의 이름(`hello-canary`)으로 deployment를 생성한다. 하지만 `hello` 라는 서비스에 함께 묶이게 된다. (참고로 track 은 pod 구분을 위해 정보를 입력해 둔 것이다.)

이 부분이 핵심이다.

```yaml
selector:
  matchLabels:
    app: hello
```

기존 3개의 pod replica (1.0.0 버전) 가 있었던 상태에서 하나의 pod replica (2.0.0 버전, canary)가 추가된다.

기본적으로 별도의 설정을 하지 않았다면 라운드로빈 방식으로 동작한다. 이 시나리오에서는 1/4 확률로 2.0.0 버전과 통신할 수 있다. istio 와 같은 도구를 사용한다면 더 정교한 트래픽 관리가 가능하다고 한다.

service yaml 에 `sessionAffinity: ClientIP` 를 추가해주면 하나의 IP에 대해 동일한 pod과 통신을 유지하도록 할 수 있다.

## Blue-Green

![Blue-Green](/assets/images/2024-09-18-k8s-deployment-strategy-type/blue-green.png)

롤링 업데이트는 오버헤드와 성능 영향을 최소화하고 다운타임을 최소화하면서 애플리케이션을 천천히 배포할 수 있기 때문에 이상적이다. 하지만 이전 버전과, 새 버전이 공존하는 시간이 발생하는 단점이 있다.
이와 다르게 blue-green 배포는 새 버전이 완전히 배포된 후, 로드 밸런서가 새 버전을 가리키도록 수정한다. (blue: 이전 버전, green: 새 버전)
쿠버네티스는 green 버전에 대해 별도로 배포를 진행하여 이를 달성할 수 있다. green 버전이 완전히 실행되면 해당 버전을 사용하도록 트래픽을 전환한다.

다음과 같은 service 를 사용한다. 여기서 핵심은 service의 selector에 버전도 명시해뒀다는 것이다.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: "hello"
spec:
  selector:
    app: "hello"
    version: 1.0.0
  ports:
    - protocol: "TCP"
      port: 80
      targetPort: 80
```

다음과 같이 hello-green 이라는 이름의 deployment를 만든다. (2.0.0 버전)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
        track: stable
        version: 2.0.0
    spec:
      containers:
        - name: hello
          image: kelseyhightower/hello:2.0.0

    ...생략...
```

deployment에 따라 pod이 생성된다. 하지만 서비스와는 아직 연결되지 못한 상태이다.
모든 pod이 정상적으로 실행이 되었다면 이제 service를 업데이트하여 트래픽을 전환한다.
service의 seletor의 버전을 2.0.0 으로 올린 것이 핵심이다.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: hello
spec:
  selector:
    app: hello
    version: 2.0.0
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```
