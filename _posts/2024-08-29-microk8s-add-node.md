---
layout: post
title: "[k8s, kubernetes] microk8s node 추가 하기"
description: MicroK8s 환경에 노드를 추가하는 방법과 발생한 문제를 해결한 과정을 다룹니다. K8S의 Worker Node와 Master Node의 역할을 이해하고, 고가용성(HA) 설정을 고려하여 노드를 추가하는 방법을 설명합니다. 노드 연결 후 통신 문제와 API 서버 엔드포인트 설정, INTERNAL-IP 수정 과정을 통해 정상적인 클러스터 구성을 완료하는 방법을 안내합니다. 추가적으로 kubectl alias 설정과 MicroK8s 재시작 방법도 제공합니다.
categories: [스터디-인프라, 개발]
tags:
  [
    k8s,
    kubernetes,
    node,
    master,
    worker,
    add-node,
    ha,
    high availability,
    apiserver,
    advertise address,
    node ip,
    internal ip,
  ]
date: 2024-08-31 08:30:00 +0900
toc: true
---

microk8s 로 구성한 k8s 환경에 추가적으로 노드를 구성하고자 하였다. 더 다양한 시나리오를 실습/테스트할 수 있을 것이라 기대했다.

오늘 구성하려고 하였던 모습은 이런 모습이였다.
![architecture](/assets/images/2024-08-29-microk8s-add-node/architecture.png)

단일 노드로도 테스트 환경을 구성할 수 있지만, 가능하면 실제 환경과 최대한 비슷하게 해보고 싶어 노드를 추가하기로 마음 먹고 시작하였다.

---

노드를 추가하는 작업 자체는 [공식 문서](https://microk8s.io/docs/clustering#adding-a-node)를 참고하면 쉽게 따라할 수 있다.

노드 연결 작업까지는 분명 잘 되었다. 그런데 여기서 부터 문제가 발생되었다.

- 분명 cluster 에 노드로 추가되었다는 문구는 나오는데, 막상 노드를 조회하면 추가된 노드가 보이지 않는다거나 노드간의 통신이 정상적으로 되지 않는 이슈가 있었다.
- 아래와 같은 에러들도 발생되었다.
  - Get "https://127.0.0.1:16443/api/v1/nodes?limit=500": dial tcp 127.0.0.1:16443: connect: connection refused - error from a previous attempt: read tcp 127.0.0.1:37782->127.0.0.1:16443: read: connection reset by peer
  - Unable to connect to the server: net/http: TLS handshake timeout

뭔가 네트워크에서 충돌이 나고 있는 듯한 느낌이 들었는데 인터넷에 이슈를 검색해봐도 상황이 쉽게 해결되지는 않았다.

여러번의 시도 끝에 정상적으로 클러스터 구성에 성공하였고 이 글에서는 어떻게 해결하였는지와 문제를 해결하면서 알게된 내용들을 정리해보고자 한다.

## 1. 노드 추가하기

### K8S 노드 종류 이해하기

K8S 에는 두가지 노드가 있다. 한 가지는 Worker Node이고, 또 다른 한 가지는 Master Node 이다.

![components-of-kubernetes](/assets/images/2024-08-29-microk8s-add-node/components-of-kubernetes.svg)

#### Worker Node

컨테이너가 배치되는 노드이다.

- kubelet
- kube-proxy
- container runtime

이 포함되어 있다.

#### Master Node (Control Plane)

마스터 노드는 워커 노드를 제어하고 관리하는 노드이다.

- api server
- etcd
- scheduler
- contoller manager

같은게 이 노드에서 포함되어 있다.

### MicroK8s HA (High Availability, 고가용성)

나중에서야 알았는데 **MicroK8s은 3개 이상의 노드가 있는 클러스터의 경우 고가용성이 자동으로 활성화** 된다고 한다.

3개 번째의 노드가 추가되었을 때 동작이 이상하게 되던 것의 원인이 아닐까 생각하고 있다.

노드가 추가된다고 무조건 좋은 것은 아니다. 아직 컨트롤 플레인이 여러개인 상황까지 고려하고 있지는 않기 때문에, HA에 대한 부분은 추후에 기회가 되면 추가적으로 시도해보고 정리해보도록 한다.

### 문제 해결하기

그냥 `add-node`를 통해 `join`을 할 경우에는 master 노드로 추가가 된다.

나의 경우에는 컨테이너가 여러곳에 배치되는 상황을 구현하고 싶은것이였기 때문에 master 노드가 아닌 worker 노드로 추가를 했어야 했었다.
worker 노드로 추가를 하려면 add-node 명령어를 입력해서 나온 join 명령어에다가 `--worker` 옵션을 추가해주면 된다.

예를 들어보면 다음과 같다.

```sh
jonghoonpark@jonghoonpark:~$ microk8s add-node
From the node you wish to join to this cluster, run the following:
microk8s join 192.168.88.193:25000/3a791cde34e41f8cb035e06999a9d653/1ea97a1ecc9a

Use the '--worker' flag to join a node as a worker not running the control plane, eg:
microk8s join 192.168.88.193:25000/3a791cde34e41f8cb035e06999a9d653/1ea97a1ecc9a --worker

If the node you are adding is not reachable through the default interface you can use one of the following:
microk8s join 192.168.88.193:25000/3a791cde34e41f8cb035e06999a9d653/1ea97a1ecc9a
microk8s join 10.8.0.4:25000/3a791cde34e41f8cb035e06999a9d653/1ea97a1ecc9a
(생략)
jonghoonpark@jonghoonpark:~$ microk8s join 10.8.0.4:25000/3a791cde34e41f8cb035e06999a9d653/1ea97a1ecc9a --worker
```

worker 노드로 추가해주니, 기존과 같은 문제 없이 정상적으로 node가 연결된 것을 확인할 수 있었다.

```sh
jonghoonpark@jonghoonpark:~$ kubectl get nodes -o wide
NAME           STATUS   ROLES    AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
node1          Ready    <none>   68m   v1.31.0   192.168.88.193   <none>        Ubuntu 22.04.3 LTS   5.15.0-119-generic   containerd://1.6.28
node2          Ready    <none>   68m   v1.31.0   10.0.0.192       <none>        Ubuntu 22.04.2 LTS   6.5.0-1026-oracle    containerd://1.6.28
node3          Ready    <none>   68m   v1.31.0   10.0.0.58        <none>        Ubuntu 22.04.4 LTS   6.5.0-1027-oracle    containerd://1.6.28
```

## 2. api server endpoints 설정하기

add-node 명령어로 join 을 하는 과정을 자세히 봤다면 아래와 같은 문구가 스쳐지나가는 것을 봤을 것이다.

```sh
replace the API server endpoints with the one provided by the loadbalancer in:
    /var/snap/microk8s/current/args/traefik/provider.yaml
```

API server endpoint를 replace 를 해줘야 한다는 내용이다.

join 된 노드들에 api server의 endpoint를 설정되었는지 확인해보고 정상적으로 설정이 되지 않았다면 설정이 필요하다.

추가된 worker node(node2 or node3) 에서 문구에 있는 대로 `/var/snap/microk8s/current/args/traefik/provider.yaml` 파일의 내용을 살펴보았다.

아래와 같은 내용을 가지고 있었다.

```yaml
tcp:
  routers:
    Router-1:
      rule: HostSNI(`*`)
      service: kube-apiserver
      tls:
        passthrough: true
  services:
    kube-apiserver:
      loadBalancer:
        servers:
        - address: 192.168.88.193:16443
```

`192.168.88.193` 는 node1 의 내부 아이피인데 node2, node3 노드의 입장에서는 접근할 수 없는 아이피이다. 따라서 수정이 필요하다.

### 문제 해결하기

문제 해결을 위해 node1(마스터 노드)에서 다음과 같이 args 설정을 추가해준다.

```sh
vim /var/snap/microk8s/current/args/kube-apiserver
```

로 파일을 열어서 맨 아래줄에 다음과 같이 추가해준다.

```sh
--advertise-address=10.8.0.4
```

`10.8.0.4` 는 oc1, oc2 노드에서 접근할 수 있는 master node(node1)의 내부 아이피이다.

이후 microk8s 를 재시작한다.

## 3. INTERNAL-IP 설정하기

문제 설명을 위해 위에서 사용한 get nodes 명령어 결과를 다시 가져와 본다.

```sh
jonghoonpark@jonghoonpark:~$ kubectl get nodes -o wide
NAME           STATUS   ROLES    AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
node1          Ready    <none>   68m   v1.31.0   192.168.88.193   <none>        Ubuntu 22.04.3 LTS   5.15.0-119-generic   containerd://1.6.28
node2          Ready    <none>   68m   v1.31.0   10.0.0.192       <none>        Ubuntu 22.04.2 LTS   6.5.0-1026-oracle    containerd://1.6.28
node3          Ready    <none>   68m   v1.31.0   10.0.0.58        <none>        Ubuntu 22.04.4 LTS   6.5.0-1027-oracle    containerd://1.6.28
```

눈치가 빠른 분이시라면 바로 위의 `get nodes` 의 결과가 이상한 것을 눈치채셨을 수도 있으실 것 같다.

node1 은 192.168.88.193 이라는 내부 아이피로, node2 는 10.0.0.192 를 내부 아이피로, node3 은 10.0.0.58 를 내부 아이피로 표시되는 것을 볼 수 있다.

이로 인해 add-node 명령어를 통해 각 노드가 클러스터로 구성은 되었지만, 서로 통신은 하지 못하는 상황이 되어버린다.

예를 들어보면 다음과 같다.

- node1 노드 입장에서는 node1(10.0.0.192) 과 node2(10.0.0.58)에 접근할수가 없다.
- node2, node3 노드 입장에서는 node1(192.168.88.193)에 접근할수가 없다.

따라서 서로 통신할 수 있는 ip로 변경을 해주어야 한다.

### 문제 해결하기

각 노드에서 다음과 같이 args를 수정한다.

```sh
vim /var/snap/microk8s/current/args/kubelet
```

로 파일을 열어서 맨 아래줄에 다음과 같이 추가해준다.

```sh
--node-ip={NODE_IP}
```

나의 경우에는 vpn 에서 할당한 ip대로 각 노드에 설정해주었다.

- node1: 10.8.0.4
- node2: 10.8.0.5
- node3: 10.8.0.6

설정을 완료하고 각 노드에서 microk8s 를 재실행하면 정상적으로 INTERNAL-IP 부분이 바뀐것을 확인할 수 있다.

```sh
jonghoonpark@jonghoonpark:~$ kubectl get nodes -o wide
NAME           STATUS   ROLES    AGE   VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
jonghoonpark   Ready    <none>   2h    v1.31.0   10.8.0.4      <none>        Ubuntu 22.04.3 LTS   5.15.0-119-generic   containerd://1.6.28
oc1            Ready    <none>   2h    v1.31.0   10.8.0.5      <none>        Ubuntu 22.04.2 LTS   6.5.0-1026-oracle    containerd://1.6.28
oc2            Ready    <none>   2h    v1.31.0   10.8.0.6      <none>        Ubuntu 22.04.4 LTS   6.5.0-1027-oracle    containerd://1.6.28
```

# 마무리

이제 노드들 간의 통신이 정상적으로 된다. 각 노드에 별도의 pod을 띄우고 각각 정상 동작 되는것 까지도 확인하였다.

k8s에서의 네트워크 구성이 쉽지는 않다는 것을 알게 되었다. 내용에 다 적지는 않았지만 다양한 것들을 알 수 있게 되었다.

ip 구성시에 cluster 내부 ip 와 외부 ip를 혼동하지 않도록 주의한다.

## 추가 팁 : microk8s kubectl alias 설정하기

다음과 같이 kubectl alias를 설정하면 좀 더 편하게 사용할 수 있다.

```
sudo snap alias microk8s.kubectl kubectl
```

## 추가 팁 : microk8s restart 하기

```
sudo snap restart microk8s
```
