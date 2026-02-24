# Requirements Document

## Introduction

OKXUS(OneHundred Kiro nexUS)는 모바일 앱에서 집에 있는 Kiro IDE와 원격으로 대화할 수 있는 시스템입니다. ChatGPT 앱처럼 깔끔한 대화 UI로 어디서든 Kiro와 소통할 수 있으며, 브릿지 프로그램이 WebSocket을 통해 모바일과 Kiro IDE를 연결합니다.

## Glossary

- **Bridge**: 집 PC에서 실행되는 프로그램으로, WebSocket 서버 역할을 하며 모바일 앱과 Kiro IDE 사이의 메시지를 중계함
- **Mobile_App**: 사용자의 모바일 기기에서 실행되는 대화 UI 애플리케이션
- **Kiro_IDE**: 집 PC에서 실행 중인 Kiro IDE 채팅창
- **Message**: 사용자가 입력하거나 Kiro가 응답하는 텍스트 데이터
- **Session**: 모바일 앱과 브릿지 간의 WebSocket 연결 상태

## Requirements

### Requirement 1: WebSocket 서버 연결

**User Story:** As a 사용자, I want 모바일 앱에서 브릿지에 연결하고 싶다, so that 원격으로 Kiro와 대화할 수 있다.

#### Acceptance Criteria

1. WHEN Mobile_App이 연결 요청을 보내면, THE Bridge SHALL WebSocket 연결을 수립하고 연결 성공 메시지를 반환한다
2. WHILE Session이 활성 상태인 동안, THE Bridge SHALL 연결 상태를 유지하고 heartbeat를 교환한다
3. IF WebSocket 연결이 끊어지면, THEN THE Mobile_App SHALL 자동으로 재연결을 시도한다
4. IF 재연결이 3회 실패하면, THEN THE Mobile_App SHALL 사용자에게 연결 실패 알림을 표시한다

### Requirement 2: 메시지 전송 (모바일 → Kiro)

**User Story:** As a 사용자, I want 모바일 앱에서 메시지를 입력하여 Kiro에게 전송하고 싶다, so that 어디서든 Kiro와 대화할 수 있다.

#### Acceptance Criteria

1. WHEN 사용자가 Mobile_App에서 Message를 전송하면, THE Bridge SHALL 해당 Message를 수신한다
2. WHEN Bridge가 Message를 수신하면, THE Bridge SHALL 클립보드에 Message를 복사한다
3. WHEN 클립보드 복사가 완료되면, THE Bridge SHALL Kiro_IDE 채팅창에 Ctrl+V로 붙여넣기 후 Enter 키를 입력한다
4. WHEN 메시지 전송이 완료되면, THE Bridge SHALL Mobile_App에 전송 완료 확인을 반환한다
5. IF Kiro_IDE 창이 활성화되지 않은 상태이면, THEN THE Bridge SHALL Kiro_IDE 창을 활성화한 후 메시지를 입력한다

### Requirement 3: 응답 수신 (Kiro → 모바일)

**User Story:** As a 사용자, I want Kiro의 응답을 모바일 앱에서 확인하고 싶다, so that 대화 내용을 실시간으로 볼 수 있다.

#### Acceptance Criteria

1. WHILE Kiro_IDE가 응답을 생성하는 동안, THE Bridge SHALL 응답 상태를 모니터링한다
2. WHEN Kiro_IDE의 응답이 완료되면, THE Bridge SHALL 응답 텍스트를 읽어서 Mobile_App으로 전송한다
3. WHEN Mobile_App이 응답을 수신하면, THE Mobile_App SHALL 대화 UI에 응답을 표시한다
4. IF 응답 읽기에 실패하면, THEN THE Bridge SHALL 오류 메시지를 Mobile_App에 전송한다

### Requirement 4: 대화 UI

**User Story:** As a 사용자, I want ChatGPT 스타일의 깔끔한 대화 UI를 사용하고 싶다, so that 편리하게 대화할 수 있다.

#### Acceptance Criteria

1. THE Mobile_App SHALL 사용자 메시지와 Kiro 응답을 구분하여 표시한다
2. THE Mobile_App SHALL 대화 기록을 시간순으로 스크롤 가능한 목록으로 표시한다
3. WHEN 새 메시지가 도착하면, THE Mobile_App SHALL 자동으로 최신 메시지로 스크롤한다
4. WHILE Kiro_IDE가 응답을 생성하는 동안, THE Mobile_App SHALL 로딩 인디케이터를 표시한다
5. THE Mobile_App SHALL 메시지 입력창과 전송 버튼을 화면 하단에 고정 배치한다

### Requirement 5: 브릿지 상태 관리

**User Story:** As a 사용자, I want 브릿지의 상태를 확인하고 싶다, so that 연결 문제를 파악할 수 있다.

#### Acceptance Criteria

1. WHEN Bridge가 시작되면, THE Bridge SHALL WebSocket 서버를 지정된 포트에서 시작한다
2. THE Bridge SHALL 현재 연결 상태를 콘솔에 로그로 출력한다
3. WHEN Mobile_App이 상태 요청을 보내면, THE Bridge SHALL 현재 상태 정보를 반환한다
4. IF Kiro_IDE 프로세스가 실행 중이 아니면, THEN THE Bridge SHALL Mobile_App에 Kiro 미실행 상태를 알린다

### Requirement 6: 보안 및 인증

**User Story:** As a 사용자, I want 인증된 기기만 브릿지에 연결되도록 하고 싶다, so that 보안을 유지할 수 있다.

#### Acceptance Criteria

1. WHEN Mobile_App이 연결을 시도하면, THE Bridge SHALL 인증 토큰을 검증한다
2. IF 인증 토큰이 유효하지 않으면, THEN THE Bridge SHALL 연결을 거부하고 오류를 반환한다
3. THE Bridge SHALL 인증 토큰을 환경 변수 또는 설정 파일에서 읽어온다
4. THE Mobile_App SHALL 인증 토큰을 안전하게 저장한다

### Requirement 7: 외부 접근 설정

**User Story:** As a 사용자, I want 외부 네트워크에서 브릿지에 접근하고 싶다, so that 집 밖에서도 Kiro와 대화할 수 있다.

#### Acceptance Criteria

1. THE Bridge SHALL ngrok 또는 포트포워딩을 통한 외부 접근을 지원한다
2. WHEN 외부 URL이 설정되면, THE Mobile_App SHALL 해당 URL로 연결을 시도한다
3. THE Bridge SHALL HTTPS/WSS 보안 연결을 지원한다
