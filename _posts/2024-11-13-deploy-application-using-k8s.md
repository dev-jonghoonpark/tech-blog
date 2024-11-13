---
layout: post
title: "[k8s] 쿠버네티스로 어플리케이션 배포하기 (deployment, service, ingress, load balancer)"
categories: [스터디-인프라, 개발]
tags:
  [
    k8s,
    kubernetes,
    jenkins,
    docker,
    container,
    deployment,
    service,
    private registry,
    ingress,
    ingress controller,
    ingress class,
    load balancer,
    lb,
    metallb,
  ]
date: 2024-11-13 18:00:00 +0900
toc: true
---

이 글에서는 k8s (microk8s) 에서 어플리케이션를 배포해본 경험을 정리해본다.

틈틈이 테스트를 위한 환경을 온프레미스로 구축하고 있다.

처음으로 k8s에 어플리케이션을 배포하는 사람에게 도움이 되기를 바란다.

## 목표

오늘의 목표는 브라우저에서 `admin.jonghoonpark.com` 이라는 도메인에 접속했을 때 k8s로 배포된 어플리케이션에 접속이 되게 하는 것이다.

![plan](/assets/images/2024-11-13-deploy-react-project-using-k8s/plan.png)

## host 파일 수정

실제로 도메인을 연결해도 되지만 테스트 목적이기 떄문에 host를 수정하는 방향으로 진행하였다.
admin.jonghoonpark.com 이 10.8.0.4 를 바라보는것 처럼 되도록 세팅하였다.

ubuntu 에서는 `/etc/hosts` 파일을 수정하였고, mac에서는 [Gas Mask](https://github.com/2ndalpha/gasmask) 라는 프로그램을 사용하여 host 파일을 수정하였다. (오늘 처음 써봤는데 쉽게 사용할 수 있어서 좋았다.)

```
10.8.0.4 admin.jonghoonpark.com
```

## k8s에서 private registry에 접근하기 위한 설정

로컬에서 docker 이미지를 빌드하였고, 잘 동작하는 것을 확인하였다.

docker 이미지는 private registry 에 푸시하였다. (nexus 사용)

deployment 파일을 통해 pod에 어떤 docker 이미지를 사용할지 지정하게 된다. 따라서 관련 설정을 먼저 해둔다.

### private registry 에 접근하기 위한 secret 생성

[kubectl create secret docker-registry](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_create/kubectl_create_secret_docker-registry/)

private registry 에 접속하기 위한 정보를 secret으로 만들어 둔다. (docker-server 에는 포트 정보도 포함해야 한다. e.g. 10.8.0.4:32000)

```sh
kubectl create secret docker-registry NAME \
  --docker-server=host \
  --docker-username=user \
  --docker-password=password
```

secret을 만들때 docker-email 옵션이 필수였던 시절이 있었던것 같다. nexus 에는 계정 정보에 이메일이 따로 없어 생략하였는데 문제는 없었다. (k8s v1.31.2 버전 사용중)

### insecure registry 일 경우

insecure registry 일 경우, docker 쪽에서도 세팅이 필요하지만 microk8s 에서도 세팅이 필요하다.

microk8s 공식 문서 중 [How to work with a private registry](https://microk8s.io/docs/registry-private) 문서를 참고하여 세팅한다.

```sh
sudo mkdir -p /var/snap/microk8s/current/args/certs.d/10.8.0.4:32000
sudo vim /var/snap/microk8s/current/args/certs.d/10.8.0.4:32000/hosts.toml
```

```conf
# /var/snap/microk8s/current/args/certs.d/10.8.0.4:32000/hosts.toml
server = "http://10.8.0.4:32000"

[host."http://10.141.241.175:32000"]
capabilities = ["pull", "resolve"]
```

`10.8.0.4:32000` 부분을 자신의 registry 에 맞게 수정해주면 된다.

만약 insecure 관련 세팅이 제대로 되지 않았다면 `http: server gave HTTP response to HTTPS client` 와 같은 에러가 발생된다.

## deployment 설정

[deployment](https://kubernetes.io/ko/docs/concepts/workloads/controllers/deployment/) 는 파드에 대한 선언적 업데이트를 제공한다.

deployment 는 다음과 같이 작성하였다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-web-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: admin-web
  template:
    metadata:
      labels:
        app: admin-web
    spec:
      containers:
        - name: admin-web-container
          image: 10.8.0.4:32000/admin-web:latest
          ports:
            - containerPort: 5173
          resources:
            limits:
              memory: "2048Mi"
              cpu: "500m"
            requests:
              memory: "1024Mi"
              cpu: "500m"
      imagePullSecrets:
        - name: private-registry-secret
```

위에서 생성한 private registry 의 secret을 사용한다.

vite 기반 어플리케이션을 샘플로 사용하여 5173 포트를 사용하게 되었다. 상황에 맞게 포트와 리소스를 설정해주면 된다.

## service 설정

[service](https://kubernetes.io/ko/docs/concepts/services-networking/service/)는 파드 집합에서 실행중인 애플리케이션을 네트워크 서비스로 노출하는 추상화하는데 사용된다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: admin-web-service
spec:
  selector:
    app: admin-web
  ports:
    - protocol: TCP
      port: 5173
      targetPort: 5173
  type: ClusterIP
```

팟에서 5173 포트를 사용하였기 때문에 service 에서는 5173 포트를 사용하였다.
`targetPort` 가 pod의 port이고, `port` 가 서비스에서 노출할 port이다.

여기까지 따라했다면 아마 포트포워딩을 통해서 pod에 접근을 할 수는 있을 것이다.
이제 ingress 설정을 통해 포트포워딩 없이도 접근 가능한 상태로 만들어보자.

## ingress 설정

[ingress](https://kubernetes.io/ko/docs/concepts/services-networking/ingress/)는 쿠버네티스 API를 통해 정의한 규칙에 기반하여 트래픽을 다른 백엔드에 매핑할 수 있게 하는데 사용된다.

### ingress controller

클러스터 내의 인그레스가 작동하려면, **ingress controller** 가 실행되고 있어야 한다. 적어도 하나의 인그레스 컨트롤러를 선택하여 이를 클러스터 내에 설치해야한다.

#### nginx ingress

ingress controller 는 다양하게 구현되어 있다. 이 글에서는 **nginx ingress** 를 사용하였다.

다음 명령어로 설치할 수 있다.

```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

이후 아래와 같이 컨트롤러가 생성된 것을 확인할 수 있다. (아직 EXTERNAL-IP는 pending 상태이다.)

```sh
$ kubectl get svc -n ingress-nginx
NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller             LoadBalancer   10.152.183.69    <pending>     80:31118/TCP,443:30651/TCP
ingress-nginx-controller-admission   ClusterIP      10.152.183.179   <none>        443/TCP
```

### ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: admin-web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: admin.jonghoonpark.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-web-service
                port:
                  number: 5173
```

`admin.jonghoonpark.com` 도메인으로 들어오는 요청을 `admin-web-service` 서비스로 전달하도록 구성하였다.

### ingress class

인그레스를 처리하는 방식은 인그레스 컨트롤러에 따라 달라진다. 따라서 어떤 컨트롤러를 사용할 것인지 클래스 이름을 포함해줘야 한다.
여기서는 `ingressClassName: nginx` 를 통해 nginx 를 사용할 것이라고 명시해주었다.

다음과 같이 IngressClass 도 생성해준다.

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
spec:
  controller: k8s.io/ingress-nginx
```

ingress class 를 설정하는 것을 놓치면 아래와 같은 에러를 마주할 수 있다.

```sh
kubectl logs ingress-nginx-controller-546f9cf9bf-gtwn4 -n ingress-nginx
```

```
"Ignoring ingress because of error while validating ingress class" ingress="default/admin-web-ingress" error="ingress does not contain a valid IngressClass"
```

여기까지 설정을 잘 따라왔다고 해도 아직은 `admin.jonghoonpark.com` 으로 어플리케이션에는 접근하지 못한다. (아직 EXTERNAL-IP는 pending 상태이기 때문이다.) 이를 해결하기 위해 load balancer를 추가해줘야한다.

## load balancer 설정

마지막으로 load balancer를 설정해줘야 한다.

load balancer와 ingress는 서로 보완적인 역할을 수행한다.
load balancer의 개념이 ingress 와 혼동이 되기도 하는데 정리해보자면 다음과 같은 차이를 가지고 있다.

| 종류       | 특징                                   |
| ---------- | -------------------------------------- |
| 인그레스   | 애클러스터 내부에서 트래픽을 라우팅    |
| 로드밸런서 | 외부에서 트래픽을 받아 인그레스로 전달 |

### metallb

load balancer도 다양하게 구현되어 있다. 이 글에서는 [**metallb**](https://github.com/metallb/metallb) 를 사용하였다.

다음 명령어로 설치할 수 있다.

```sh
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.8/config/manifests/metallb-native.yaml
```

설치한 후에는 ip address pool을 설정해줘야 한다. 나는 다음과 같이 설정해주었다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: dev
  namespace: metallb-system
spec:
  addresses:
    - 10.8.0.4/32
```

address 에는 ingress controller 의 ip를 명시해주면 된다. (여기서는 한 ip 를 지정하였지만, 환경에 맞춰 여러 ip 범위를 지정할 수도 있다.)

apply 해보면 ingress-nginx-controller 에 EXTERNAL-IP가 연결된 것을 볼 수 있다.

```sh
$ kubectl get svc -n ingress-nginx
NAME                                 TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller             LoadBalancer   10.152.183.69    10.8.0.4      80:31118/TCP,443:30651/TCP
ingress-nginx-controller-admission   ClusterIP      10.152.183.179   <none>        443/TCP
```

## 마무리

여기까지 설정하였으면 처음 목표였던 `admin.jonghoonpark.com` 으로 애플리케이션에 접근할 수 있다.

## 기타

- 대부분의 내용은 k8s 공식 도큐먼트를 참고하였다.
- ingress 설정 후에도 연결이 되지 않을 경우에는 로그를 확인해보자. 바로 위에서 사용한대로 `kubectl logs` 명령어로 로그를 확인해볼 수 있다.
