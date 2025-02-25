---
layout: post
title: "[k8s, kubernetes] 온프레미스 k8s에 리모트로 접속하기 (namespace, service account, role, rolebinding, secret, config)"
description: 온프레미스 Kubernetes 환경에 리모트로 접속하기 위한 과정으로, 네임스페이스 생성, 서비스 어카운트 및 역할(Role) 설정, 역할 바인딩(RoleBinding) 생성, 비밀(Secret) 생성, 그리고 kubeconfig 파일 작성 방법을 설명합니다. 이 글에서는 microk8s를 사용하여 서비스 어카운트를 인증 주체로 설정하고, dev 네임스페이스의 Pod에 대한 모든 권한을 부여하는 방법을 다룹니다. 최종적으로 생성된 kubeconfig 파일을 통해 원격 Kubernetes 클러스터에 안전하게 접속할 수 있습니다.
categories: [스터디-인프라, 개발]
tags:
  [
    k8s,
    kubernetes,
    microk8s,
    on-premises,
    connect,
    namespace,
    service account,
    sa,
    role,
    rolebinding,
    secret,
    config,
  ]
date: 2024-08-07 23:59:59 +0900
toc: true
---

테스트 서버에 k8s를 직접 구축해보고자 하고 있다.
k8s를 쓰는 법은 알지만, 구축하는 법에 대해서는 잘 모르기에 이번 기회를 통해 익혀보려고 한다.
아래 과정은 microk8s 로 진행하였다.

---

회사에서는 k8s를 사용할 때 openlens를 사용하고 있다. devops 분의 안내에 따라 발급받은 config 파일을 통해 remote k8s 환경에 접속할 수 있다.

나도 내 테스트 서버 환경에 이런식으로 환경을 구성하고 싶었다.

회사에 계신 devops 분께 질문드려보니 서비스 어카운트, 인증서 두 가지 방법을 추천해주셨고, 나는 서비스 어카운트 쪽이 더 좋을 것 같아서 이쪽으로 시작을 해보기로 했다.

## 네임스페이스 (namespace)

우선은 네임스페이스를 생성해주겠다.

> [네임스페이스](https://kubernetes.io/ko/docs/concepts/overview/working-with-objects/namespaces/) 는 단일 클러스터 내에서의 리소스 그룹 격리 메커니즘을 제공한다.

아래 명령어를 통해 현재 존재하는 네임스페이스들을 조회할 수 있다.

```bash
kubectl get namespaces
```

```bash
jonghoonpark@jonghoonpark:~$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   30h
kube-node-lease   Active   30h
kube-public       Active   30h
kube-system       Active   30h
```

아직은 별도의 네임스페이스가 생성되어 있지 않다. 목록에 있는것은 내가 생성하지 않은 기본으로 생성되어 있는 네임스페이스 들이다. 아래 명령어를 통해 dev 라는 네임 스페이스를 생성해주었다.

```bash
jonghoonpark@jonghoonpark:~$ kubectl create namespace dev
namespace/dev created
```

생성 후 다시 네임스페이스를 조회하면 `dev` 라는 네임 스페이스가 생성된 것을 볼 수 있다.

```bash
jonghoonpark@jonghoonpark:~$ kubectl get namespaces
NAME              STATUS   AGE
default           Active   30h
dev               Active   41s
kube-node-lease   Active   30h
kube-public       Active   30h
kube-system       Active   30h
```

만약 아래와 같은 에러가 나온다면 `~/.kube/config` 가 정상적으로 구성되었는지 확인해보자.

```bash
jonghoonpark@jonghoonpark:~$ kubectl get namespaces
E0807 08:18:07.610448 2401464 memcache.go:265] couldn't get current server API group list: Get "http://localhost:8080/api?timeout=32s": dial tcp 127.0.0.1:8080: connect: connection refused
```

## Service Account 생성 (SA)

일단 심플한 형태로 아래과 같이 `dev-manager-sa.yaml` 파일을 작성해주었다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dev-manager-sa
  namespace: default
```

여기서 namespace는 해당 service account를 어디에 생성할지에 대한 정보인데, 서비스 어카운트를 인증주체로 사용하려는 것이기 때문에 default에 생성하였다. 특정 namespace에 생성하였다고 다른 namespace에 접근하지 못하는 것은 아니고, 이후 role 설정을 통해 설정할 수 있다.

아래 명령어를 통해 작성한 YAML 파일로 Kubernetes 클러스터에 서비스 어카운트를 생성한다.

```bash
jonghoonpark@jonghoonpark:~/k8s/sa$ kubectl apply -f dev-manager-sa.yaml
serviceaccount/dev-manager-sa created
```

생성이 완료되었다면 get 명령어를 통해 조회해 볼 수 있다.

```bash
jonghoonpark@jonghoonpark:~/k8s/sa$ kubectl get serviceaccounts
NAME      SECRETS   AGE
default   0         32h
dev-manager-sa    0         14m
```

## Role 생성

위에서 만든 service account 로는 `dev` namespace 의 pod 들에 대해 모든 권한을 줘보겠다.

`dev-manager-role.yaml` 파일을 생성한다.

기본적인 verbs 에는 `get`, `list`, `watch`, `create`, `update`, `delete`, `deletecollection`, `patch`, `bind` 등이 있다고 한다.
일단 나는 모든 권한을 줄 예정이기 때문에 `*` 으로 설정하였다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: dev-manager-role
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["*"]
```

이후 apply 명령어를 통해 적용한다.

```bash
jonghoonpark@jonghoonpark:~/k8s$ kubectl apply -f dev-master-role.yaml
role.rbac.authorization.k8s.io/dev-manager-role created
```

이렇게 만들어진 Role 은 get 을 통해서 조회할 수 있다.

```bash
jonghoonpark@jonghoonpark:~/k8s$ kubectl get role
No resources found in default namespace.
jonghoonpark@jonghoonpark:~/k8s$ kubectl get role --namespace=dev
NAME               CREATED AT
dev-manager-role   2024-08-07T10:23:47Z
```

dev 스페이스에 생성되었기 때문에 default namespace 에서는 조회되지 않는 것을 볼 수 있다.

## RoleBinding 생성

RoleBinding 은 생성한 service 와 role을 연결시켜주는 역할을 한다.

`dev-manager-binding.yaml` 파일을 다음과 같이 만들어보겠다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-manager-rb
  namespace: dev
subjects:
  - kind: ServiceAccount
    name: dev-manager-sa
    namespace: dev
roleRef:
  kind: Role
  name: dev-manager-role
  apiGroup: rbac.authorization.k8s.io
```

마찬가지로 apply 명령어를 통해 적용한다.

```bash
jonghoonpark@jonghoonpark:~/k8s/rb$ kubectl apply -f dev-manager-rb.yaml
rolebinding.rbac.authorization.k8s.io/dev-manager-rb created
```

## Secret 생성

우선 서비스 어카운트에 대한 secret 을 생성해줘야한다.

다음과 같이 `dev-manager-sa-token.yaml` 을 만들어준 후 apply 를 통해 생성한다.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dev-manager-sa-token
  annotations:
    kubernetes.io/service-account.name: dev-manager-sa
type: kubernetes.io/service-account-token
```

```bash
jonghoonpark@jonghoonpark:~/k8s/secret$ kubectl apply -f dev-manager-sa-token.yaml
secret/dev-manager-sa-token created
```

secret이 만들어 진 후에는 token을 연결해줘야 한다. create token 명령어를 활용한다.

```bash
jonghoonpark@jonghoonpark:~/k8s/rb$ kubectl create token dev-manager-sa --bound-object-kind Secret --bound-object-name dev-manager-sa-token --duration=999999h | base64 -w 0
ZXlKaGJHY2lPaU...(생략)
```

## kubeconfig 파일 생성하기

모든 준비가 마무리 되었다.

다음은 kubeconfig 파일의 기본 구조이다.

```yaml
apiVersion: v1
kind: Config
clusters:
  - cluster:
      server: https://YOUR-CLUSTER-ADDRESS
      certificate-authority-data: YOUR-CA-DATA
    name: jonghoonpark-cluster
contexts:
  - context:
      cluster: jonghoonpark-cluster
      user: dev-manager-sa
    name: dev-manager-sa-context
current-context: dev-manager-sa-context
users:
  - name: dev-manager-sa
    user:
      token: YOUR-TOKEN
```

`YOUR-CLUSTER-ADDRESS` 와 `YOUR-TOKEN`, `YOUR-CA-DATA` 값을 상황에 맞게 채우면 된다. 각 변수에 대한 설명은 다음과 같다.

- `YOUR-CLUSTER-ADDRESS` : `kubectl cluster-info` 명령어를 입력하여 나오는 Kubernetes control plane 주소
- `YOUR-TOKEN`
  - `kubectl get secret dev-manager-sa-token -ojsonpath={.data.token} | base64 -d` 명령어로 확인 가능
- `YOUR-CA-DATA` : 클러스터의 CA 인증서를 Base64 인코딩한 값
  - `kubectl edit secret dev-manager-sa-token` 명령어를 통해서 확인하거나 admin config 를 통해서 확인 가능

생성된 kube config 파일을 접속하고자 하는 컴퓨터에 복사하고 사용하면 된다.

과정을 잘 따라왔으면 정상적으로 잘 동작할 것이다. 만약 정상적으로 설정되지 않았다면 아래와 같은 에러들이 발생될 수 있다.

```
error: You must be logged in to the server (Unauthorized)
```

```
Please enter Username:
```
