---
layout: "post"
title: "[Spring] WebRTC 와 Spring websocket 을 이용하여 구글 밋 처럼 카메라 스트리밍 하기"
description: "WebRTC와 Spring WebSocket을 활용하여 구글 밋과 유사한 카메라 스트리밍 서비스를 구현하는 방법을 소개합니\
  다. 이 포스트에서는 React(Next.js)로 프론트엔드를 구성하고, Spring WebSocket 서버를 통해 스트리머와 뷰어 간의 시그널\
  링 메시지를 전달하는 구조를 설명합니다. 코드를 통해 WebRTC 초기화, WebSocket 설정 및 스트리밍 기능을 구현하는 과정을 자세히 다\
  루며, 발생할 수 있는 이슈와 해결 방법도 공유합니다."
categories:
- "스터디-자바"
tags:
- "Java"
- "google meet"
- "Spring"
- "Spring Boot"
- "WebSocket"
- "WebRTC"
- "offer"
- "answer"
- "iceserver"
- "streaming"
- "streamer"
- "viewer"
- "live"
date: "2025-02-11 16:00:00 +0000"
toc: true
image:
  path: "/assets/thumbnails/2025-02-12-webrtc-with-spring-websocket.jpg"
---

# WebRTC 와 Spring websocket 을 이용하여 구글 밋 처럼 카메라 스트리밍 하기

구글 밋 처럼 웹 브라우저에서 웹 API를 이용하여 카메라 영상을 받아와 실시간으로 스트리밍 하는 서비스를 만들어보고자 하였다.

구현한 코드를 공유해본다.

## WebRTC

WebRTC에 대해서 간단하게 설명을 해보자면 웹 브라우저 간에 플러그인의 도움 없이 서로 통신할 수 있도록 설계된 API이다.

[WebRTC 코드 정리](http://www.gisdeveloper.co.kr/?p=13327)
개인적으로 이 블로그에 그려진 그림 자료가 FLOW 를 깔끔하게 그려둬서 쉽게 이해할 수 있었다.

이 사이에서 spring은, 두 서버를 직접 연결할 수 있도록 돕는 매개체 역할을 한다고 이해하면 된다.

## 프론트엔드 : react (next.js)

프론트엔드는 next.js 를 이용하여 구현하였다.

### streamer.tsx

```ts
"use client";

import React, { useEffect, useRef, useState } from "react";

const Streamer = () => {
  const [muted, setMuted] = useState(true);
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    const initWebSocket = () => {
      const ws = new WebSocket("ws://localhost:8080/ws");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleSignal(data);
      };

      ws.onerror = (error) => {
        console.error("WebSocket Error:", error);
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
      };

      socket.current = ws;
    };

    const initWebRTC = async () => {
      try {
        const pc = new RTCPeerConnection({
          iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
        });

        peerConnectionRef.current = pc;

        pc.onicecandidate = (event) => {
          if (event.candidate && socket.current) {
            socket.current.send(
              JSON.stringify({ type: "candidate", candidate: event.candidate })
            );
          }
        };

        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        stream.getTracks().forEach((track) => {
          pc.addTrack(track, stream);
        });

        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        if (socket.current) {
          socket.current.send(
            JSON.stringify({ type: "offer", sdp: offer.sdp })
          );
        }
      } catch (error) {
        console.error("WebRTC initialization failed:", error);
      }
    };

    initWebSocket();
    initWebRTC();

    return () => {
      // Clean up WebRTC
      if (peerConnectionRef.current) {
        peerConnectionRef.current.getSenders().forEach((sender) => {
          sender.track?.stop();
        });
        peerConnectionRef.current.close();
      }

      // Clean up WebSocket
      if (socket.current) {
        socket.current.close();
      }
    };
  }, []);

  const handleSignal = async (data: any) => {
    if (data.type === "answer") {
      if (peerConnectionRef.current) {
        await peerConnectionRef.current.setRemoteDescription({
          type: "answer",
          sdp: data.sdp,
        });
      }
    } else if (data.type === "candidate") {
      if (peerConnectionRef.current && data.candidate) {
        await peerConnectionRef.current.addIceCandidate(data.candidate);
      }
    }
  };

  return (
    <div>
      <div>
        <button onClick={() => setMuted(!muted)}>
          toggle muted(current: {muted ? "muted" : "unmuted"})
        </button>
      </div>
      <video ref={localVideoRef} autoPlay muted={muted} playsInline />;
    </div>
  );
};

export default Streamer;
```

### viewer.tsx

```ts
"use client";

import React, { useRef, useEffect, useState } from "react";

const Viewer = () => {
  const [muted, setMuted] = useState(true);
  const pc = useRef<RTCPeerConnection | null>(null);
  const socket = useRef<WebSocket | null>(null);
  const remoteVideoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    // WebSocket 초기화
    socket.current = new WebSocket("ws://localhost:8080/ws");

    socket.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "offer") {
        pc.current = new RTCPeerConnection({
          iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
        });

        pc.current.onicecandidate = (event) => {
          if (event.candidate && socket.current) {
            socket.current.send(
              JSON.stringify({ type: "candidate", candidate: event.candidate })
            );
          }
        };

        pc.current.ontrack = (event) => {
          if (remoteVideoRef.current && event.streams[0]) {
            remoteVideoRef.current.srcObject = event.streams[0];
          }
        };

        try {
          await pc.current.setRemoteDescription(
            new RTCSessionDescription(data)
          );
          const answer = await pc.current.createAnswer();
          await pc.current.setLocalDescription(answer);

          if (socket.current) {
            socket.current.send(JSON.stringify(answer));
          }
        } catch (error) {
          console.error("Error handling offer:", error);
        }
      } else if (data.type === "candidate") {
        try {
          await pc.current?.addIceCandidate(
            new RTCIceCandidate(data.candidate)
          );
        } catch (error) {
          console.error("Error adding ICE candidate:", error);
        }
      }
    };

    return () => {
      socket.current?.close();
      pc.current?.close();
    };
  }, []);

  return (
    <div>
      <div>
        <button onClick={() => setMuted(!muted)}>
          toggle muted(current: {muted ? "muted" : "unmuted"})
        </button>
      </div>
      <video ref={remoteVideoRef} autoPlay muted={muted} playsInline></video>
    </div>
  );
};

export default Viewer;
```

## Spring

Spring WebSocket 서버는 스트리머와 뷰어 간의 시그널링 메시지(offer, answer, ICE candidates)를 전달하는 중개 역할을 수행한다.

### WebSocketConfig.java

```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(new SignalHandler(), "/ws").setAllowedOrigins("*");
    }
}
```

### SignalHandler.java

```java
@Slf4j
public class SignalHandler extends TextWebSocketHandler {

    private final CopyOnWriteArrayList<WebSocketSession> sessions = new CopyOnWriteArrayList<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);
        log.debug("session added: {}", sessions);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        log.debug("message: {}", message);
        // Broadcast the received message to all connected clients
        for (WebSocketSession s : sessions) {
            if (s.isOpen() && !s.getId().equals(session.getId())) {
                log.debug("sendMessage to {}", s.getId());
                s.sendMessage(message);
            }
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session);
    }
}
```

## 결과물

`/` 로 접근시 스트리머(카메라 영상 정보를 제공하는 주체)로, `/viewer` 로 접근시 뷰어로 동작한다.

![demo](/assets/images/2025-02-12-webrtc-with-spring-websocket/demo.png)

왼쪽은 `/` 로 접근하였기 때문에 스트리머이다. 따라서 브라우저 주소창 옆에 동영상 아이콘이 나오고 있는걸 볼 수 있다.

음성도 전달된다.

## 이슈

### onicecandidate 가 트리거 되지 않는 이슈

setLocalDescription 전에 addTrack을 먼저 진행해야 한다. 그렇지 않으면 onicecandidate 가 트리거 되지 않는다.

[https://stackoverflow.com/a/58430313](https://stackoverflow.com/a/58430313) 를 참고하여 해결하였다.

### 동영상이 재생되지 않는 이슈

알 수 없는 이유로 동영상 재생이 계속 되다 안되다 하는 이슈가 있었다.

web rtc의 문제는 아니였고 브라우저에서 동영상 자동재생을 차단해서 발생된 일이였다. 콘솔에 에러도 남지 않아서 이 문제로 한참 헤맸다.

그래서 최초 실행시에는 동영상을 muted 로 처리하도록 하였다.

## 더 공부할 것

WebRTC에 대해서 많이 들어보았지만 직접 구현해보면서 더 알아볼 수 있었던 시간이였다.
이 구조는 1:1 으로만 가능하고 1:N 통신을 하고 싶다면 SFU 라는 키워드를 찾아봐야 한다고 한다.
SFU에 대해서 좀 더 공부해봐야할 것 같다.
