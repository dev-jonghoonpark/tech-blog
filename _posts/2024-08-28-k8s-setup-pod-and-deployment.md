---
layout: "post"
title: "[k8s, kubernetes] deployment 설정하기 - k8s에서 mysql 실행하기"
description: "Kubernetes에서 MySQL을 실행하기 위한 deployment 설정 방법을 다룹니다. 기존 Docker Compose\
  \ 구성을 k8s로 이전하며, MySQL 서버를 위한 deployment, persistent volume, 및 persistent volume\
  \ claim을 설정하는 과정을 설명합니다. 설정 완료 후, kubectl 명령어를 통해 적용하고, pod 생성 및 데이터베이스 연결 테스트를\
  \ 수행하여 정상 작동을 확인합니다."
categories:
- "스터디-인프라"
- "개발"
tags:
- "k8s"
- "kubernetes"
- "microk8s"
- "on-premises"
- "pod"
- "deployment"
- "pv"
- "pvc"
- "persistent volume"
date: "2024-08-27 20:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2024-08-28-k8s-setup-pod-and-deployment.jpg"
---

기존의 테스트 환경에 구성해뒀던 컨테이너 구성을 k8s 위에서 동작하도록 옮겨보는것을 목표로 진행해보도록 한다.

대략 아래와 같이 docker-compose 파일을 작성하여 mysql 서버들을 띄워두고 있다.

```yaml
services:
  mysql:
    image: mysql:8.0.33
    container_name: test-mysql
    ports:
      - 3306:3306 # HOST:CONTAINER
    environment:
      MYSQL_ROOT_PASSWORD: mysqlrootpassword
      MYSQL_DATABASE: test
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    volumes:
      - test-mysql-data:/var/lib/mysql
    healthcheck:
      test: "/usr/bin/mysql --user=root --password=mysqlrootpassword --execute=\"SHOW DATABASES;\""
      timeout: 60s
      retries: 30
      interval: 1s

volumes:
  test-mysql-data:
```

## 생성 및 적용하기

[공식홈페이지의 deployment 문서](https://kubernetes.io/ko/docs/concepts/workloads/controllers/deployment/)를 참고하여 아래와 같이 구성하였다.

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-mysql-deployment
spec:
  replicas: 1 # Adjust the number of replicas as needed
  selector:
    matchLabels:
      app: test-mysql
  template:
    metadata:
      labels:
        app: test-mysql
    spec:
      containers:
        - name: test-mysql
          image: mysql:8.0.33   
          env:
          - name: MYSQL_ROOT_PASSWORD
            value: mysqlrootpassword
          - name: MYSQL_DATABASE
            value: test
          command:
          - "--character-set-server=utf8mb4"
          - "--collation-server=utf8mb4_unicode_ci"
          ports:
          - containerPort: 3306
          volumeMounts:
          - name: test-mysql-data
            mountPath: /var/lib/mysql
          livenessProbe:
            exec:
              command:
              - mysqladmin
              - ping
              - "-h"
              - "127.0.0.1"
            initialDelaySeconds: 60
            timeoutSeconds: 1
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            exec:
              command:
              - mysqladmin
              - ping
              - "-h"
              - "127.0.0.1"
            initialDelaySeconds: 60
            timeoutSeconds: 1
            periodSeconds: 10
            failureThreshold: 3
        volumes:
        - name: test-mysql-data
          persistentVolumeClaim:
          claimName: test-mysql-pvc
```

데이터를 저장하기 위한 볼륨도 설정해준다.

[퍼시스턴트볼륨](https://kubernetes.io/ko/docs/concepts/storage/persistent-volumes/)은 사용자 및 관리자에게 스토리지 사용 방법에서부터 스토리지가 제공되는 방법에 대한 세부 사항을 추상화하는 API를 제공한다.

```yml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: test-mysql-pv
spec:
  volumeMode: Filesystem
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /home/jonghoonpark/k8s/pv/test-mysql
```

```yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  volumeName: test-mysql-pv
```

설정이 완료되었으면 apply 명령을 통해 적용한다.

```sh
$ kubectl apply -f test-mysql-pv
$ kubectl apply -f test-mysql-pvc
$ kubectl apply -f test-mysql-deployment
```

## 결과

deployment 가 정상적으로 적용되면 pod이 생성된다.

![pod-property](/assets/images/2024-08-28-k8s-setup-pod-and-deployment/pod-property.png)

포트포워딩을 해서 db 연결을 테스트해보면 정상적으로 연결되는 것을 확인할 수 있다.

![connect-test](/assets/images/2024-08-28-k8s-setup-pod-and-deployment/connect-test.png)