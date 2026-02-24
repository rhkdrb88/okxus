# Implementation Plan: OKXUS

## Overview

OKXUS 시스템을 Bridge(Python)와 Mobile App(React Native/TypeScript) 두 파트로 나누어 구현합니다. Bridge 핵심 로직부터 시작하여 Mobile App UI를 구축하고, 최종적으로 두 컴포넌트를 연결합니다. GitHub 레포: rhkdrb88/okxus

## Tasks

- [x] 1. 프로젝트 구조 및 기본 설정
  - [x] 1.1 Bridge 프로젝트 초기화
    - `bridge/` 디렉토리 생성
    - `bridge/requirements.txt` 작성 (websockets, pyautogui, pyperclip, hypothesis, pytest)
    - `bridge/__init__.py`, `bridge/models.py` 생성
    - `MessageType`, `ResponseType`, `ClientMessage`, `ServerMessage`, `BridgeStatus` 데이터 모델 구현
    - _Requirements: 2.2, 5.3_
  - [x] 1.2 Mobile App 프로젝트 초기화
    - React Native 프로젝트 생성 (`mobile/`)
    - TypeScript 설정
    - `src/types/index.ts` 생성 - `Message`, `MessageStatus`, `ConnectionStatus`, `AppConfig`, `ChatSession` 타입 정의
    - `src/types/message.ts` 생성 - `ClientMessage`, `ServerMessage`, `BridgeStatus`, `ErrorCode` 타입 정의
    - 의존성 설치: `fast-check`, `@react-native-async-storage/async-storage`
    - _Requirements: 4.1, 4.2_

- [ ] 2. Bridge 인증 모듈 구현
  - [x] 2.1 `bridge/auth.py` 구현
    - `Authenticator` 클래스 구현
    - 환경변수(`OKXUS_AUTH_TOKEN`) 또는 설정 파일(`bridge/config.json`)에서 토큰 로드
    - `validate(client_token: str) -> bool` 메서드 구현
    - _Requirements: 6.1, 6.2, 6.3_
  - [ ]* 2.2 Property 2 속성 테스트: 토큰 인증 정확성
    - **Property 2: 토큰 인증 정확성**
    - hypothesis를 사용하여 임의의 토큰 문자열에 대해 `validate(token) == (token == valid_token)` 검증
    - **Validates: Requirements 6.1, 6.2**

- [ ] 3. Bridge 자동화 모듈 구현
  - [x] 3.1 `bridge/automation.py` 구현
    - `KiroAutomation` 클래스 구현
    - `activate_kiro_window()`: Kiro IDE 창 찾기 및 활성화
    - `send_message(message: str)`: pyperclip으로 클립보드 복사 → pyautogui로 Ctrl+V, Enter
    - `is_kiro_running()`: Kiro IDE 프로세스 실행 상태 확인
    - _Requirements: 2.2, 2.3, 2.5, 5.4_
  - [ ]* 3.2 Property 1 속성 테스트: 클립보드 복사 라운드트립
    - **Property 1: 클립보드 복사 라운드트립**
    - hypothesis를 사용하여 임의의 문자열에 대해 클립보드 복사 후 읽기 값이 원본과 동일한지 검증
    - **Validates: Requirements 2.2**

- [ ] 4. Bridge 응답 모니터링 모듈 구현
  - [x] 4.1 `bridge/monitor.py` 구현
    - `ResponseMonitor` 클래스 구현
    - `wait_for_response(timeout: int = 60)`: Kiro IDE 응답 완료 대기 후 텍스트 반환
    - `is_responding()`: 현재 응답 생성 중인지 확인
    - 응답 읽기 실패 시 오류 메시지 생성
    - _Requirements: 3.1, 3.2, 3.4_
  - [ ]* 4.2 Property 9 속성 테스트: 오류 발생 시 오류 메시지 전송
    - **Property 9: 오류 발생 시 오류 메시지 전송**
    - hypothesis를 사용하여 오류 발생 시 `type: 'error'`와 오류 설명을 포함하는 ServerMessage가 생성되는지 검증
    - **Validates: Requirements 3.4**

- [ ] 5. Bridge WebSocket 서버 구현
  - [x] 5.1 `bridge/server.py` 구현
    - `BridgeServer` 클래스 구현
    - `start(host, port)`: WebSocket 서버 시작, 지정 포트 바인딩
    - `handle_connection(websocket)`: 연결 수립, 인증 검증, 메시지 라우팅
    - `broadcast(message)`: 연결된 클라이언트에 메시지 전송
    - heartbeat 교환 로직 구현
    - 연결 상태 콘솔 로그 출력
    - _Requirements: 1.1, 1.2, 2.1, 5.1, 5.2_
  - [ ]* 5.2 Property 5 속성 테스트: 상태 요청 응답 형식
    - **Property 5: 상태 요청 응답 형식**
    - hypothesis를 사용하여 상태 요청 시 `kiro_running`, `connected_clients`, `uptime` 필드를 포함하는 BridgeStatus 반환 검증
    - **Validates: Requirements 5.3**
  - [ ]* 5.3 Property 10 속성 테스트: WebSocket 메시지 전송 확인
    - **Property 10: WebSocket 메시지 전송 확인**
    - hypothesis를 사용하여 유효한 메시지 전송 시 `type: 'message_ack'`, `success: true` 응답 반환 검증
    - **Validates: Requirements 2.4**
  - [ ]* 5.4 Property 8 단위 테스트: Kiro 미실행 상태 감지
    - **Property 8: Kiro 미실행 상태 감지**
    - pytest를 사용하여 Kiro IDE 미실행 시 `kiro_running: false` 반환 검증
    - **Validates: Requirements 5.4**

- [ ] 6. Bridge 메인 엔트리포인트 및 설정
  - [~] 6.1 `bridge/main.py` 구현
    - 서버 시작 로직, 설정 로드, 모듈 연결
    - `bridge/config.json` 기본 설정 파일 생성 (포트, 토큰, ngrok 설정)
    - ngrok 터널 연동 지원 (외부 접근)
    - _Requirements: 5.1, 7.1, 7.3_

- [ ] 7. Checkpoint - Bridge 모듈 검증
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Mobile App 테마 및 공통 스타일 설정
  - [~] 8.1 앱 테마 및 폰트 설정
    - `src/styles/theme.ts` 생성
    - Kiro IDE 스타일 정의: 블랙 배경(#0d1117), 네온 그린(#39ff14), 네온 시안(#00ffff), 네온 핑크(#ff6ec7)
    - JetBrains Mono 폰트 설정
    - _Requirements: 추가요구사항 1, 4_
  - [~] 8.2 앱 아이콘 생성
    - 노란색 배경에 중앙 X, 동서남북에 O/K/U/S 글자 배치 아이콘 에셋 생성
    - _Requirements: 추가요구사항 3_

- [ ] 9. Mobile App WebSocket 서비스 구현
  - [~] 9.1 `src/services/websocket.ts` 구현
    - `WebSocketService` 구현: `connect`, `disconnect`, `sendMessage`, `onMessage`, `onStatusChange`
    - 인증 토큰 전송 로직
    - heartbeat 교환 로직
    - _Requirements: 1.1, 6.4_
  - [~] 9.2 자동 재연결 로직 구현
    - 연결 끊김 시 자동 재연결 (최대 3회)
    - 3회 실패 시 사용자에게 연결 실패 알림
    - 연결 상태 전이: disconnected → reconnecting → connected/error
    - _Requirements: 1.3, 1.4_
  - [ ]* 9.3 Property 6 단위 테스트: 연결 끊김 시 재연결 시도
    - **Property 6: 연결 끊김 시 재연결 시도**
    - jest를 사용하여 연결 끊김 시 상태가 'disconnected'에서 'reconnecting'으로 전이되는지 검증
    - **Validates: Requirements 1.3**

- [ ] 10. Mobile App 저장소 서비스 구현
  - [~] 10.1 `src/services/storage.ts` 구현
    - AsyncStorage를 사용한 토큰, URL, 대화 기록, 설정 저장/로드
    - 스토리지 키 상수 정의 (`@okxus/auth_token`, `@okxus/bridge_url`, `@okxus/chat_history`, `@okxus/settings`)
    - _Requirements: 6.4_

- [ ] 11. Mobile App 대화 UI 구현
  - [~] 11.1 `src/components/MessageBubble.tsx` 구현
    - 사용자 메시지: 네온 핑크(#ff6ec7) 스타일
    - Kiro 응답: 네온 그린(#39ff14) 스타일
    - JetBrains Mono 폰트 적용
    - _Requirements: 4.1, 추가요구사항 5_
  - [ ]* 11.2 Property 4 속성 테스트: 메시지 sender 구분 렌더링
    - **Property 4: 메시지 sender 구분 렌더링**
    - fast-check를 사용하여 sender가 'user'이면 네온 핑크, 'kiro'이면 네온 그린 스타일 적용 검증
    - **Validates: Requirements 4.1**
  - [~] 11.3 `src/components/ChatScreen.tsx` 구현
    - 블랙 배경(#0d1117) 메인 화면
    - 메시지 목록 FlatList (시간순 정렬, 스크롤 가능)
    - 새 메시지 도착 시 자동 스크롤
    - 로딩 인디케이터 (Kiro 응답 생성 중)
    - 승인 버튼 표시 로직 (Kiro가 승인 필요 작업 요청 시)
    - _Requirements: 4.2, 4.3, 4.4, 추가요구사항 2_
  - [ ]* 11.4 Property 3 속성 테스트: 메시지 시간순 정렬
    - **Property 3: 메시지 시간순 정렬**
    - fast-check를 사용하여 임의의 메시지 배열이 timestamp 기준 오름차순으로 정렬되어 표시되는지 검증
    - **Validates: Requirements 4.2**
  - [ ]* 11.5 Property 7 속성 테스트: 로딩 상태 인디케이터 표시
    - **Property 7: 로딩 상태 인디케이터 표시**
    - fast-check를 사용하여 `isKiroResponding`이 true일 때 로딩 인디케이터가 표시되는지 검증
    - **Validates: Requirements 4.4**
  - [~] 11.6 `src/components/InputBar.tsx` 구현
    - 하단 고정 입력창 + 전송 버튼
    - 네온 시안(#00ffff) 전송 버튼 스타일
    - _Requirements: 4.5_
  - [~] 11.7 `src/components/ConnectionStatus.tsx` 구현
    - 연결 상태 표시 컴포넌트 (connected/connecting/disconnected/error)
    - _Requirements: 5.3_

- [ ] 12. Checkpoint - Mobile App UI 검증
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Mobile App 설정 화면 및 네비게이션
  - [~] 13.1 설정 화면 구현
    - Bridge URL 입력
    - 인증 토큰 입력 및 저장
    - 외부 URL(ngrok) 설정
    - _Requirements: 6.4, 7.2_
  - [~] 13.2 앱 네비게이션 설정
    - 대화 화면 ↔ 설정 화면 네비게이션
    - 앱 시작 시 저장된 설정 로드 및 자동 연결
    - _Requirements: 7.2_

- [ ] 14. 전체 통합 및 연결
  - [~] 14.1 Mobile App과 Bridge 통합 연결
    - Mobile App에서 Bridge로 메시지 전송 → Kiro IDE 입력 전체 파이프라인 연결
    - Kiro IDE 응답 → Bridge → Mobile App 응답 수신 파이프라인 연결
    - 오류 처리 흐름 통합 (인증 실패, Kiro 미실행, 타임아웃 등)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3_
  - [ ]* 14.2 통합 테스트 작성
    - 메시지 전송 파이프라인 테스트 (Mock 기반)
    - 응답 수신 파이프라인 테스트 (Mock 기반)
    - 오류 시나리오 테스트
    - _Requirements: 2.1~2.5, 3.1~3.4_

- [ ] 15. Final checkpoint - 전체 시스템 검증
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Bridge는 Python, Mobile App은 TypeScript/React Native로 구현
- 각 태스크는 특정 요구사항을 참조하여 추적 가능
- Checkpoints에서 점진적 검증 수행
- Property 테스트는 보편적 정확성 속성을 검증하고, 단위 테스트는 특정 예시와 엣지 케이스를 검증
- GitHub 레포(rhkdrb88/okxus)에 커밋하여 다른 PC에서도 이어서 개발 가능
