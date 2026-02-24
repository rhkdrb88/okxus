# OKXUS (OneHundred Kiro nexUS)

모바일 앱에서 집 PC의 Kiro IDE와 원격으로 대화하는 시스템

## 아키텍처

```
[모바일 앱] ←WebSocket(ngrok)→ [Bridge(Python)] ←pyautogui→ [Kiro IDE]
```

## 프로젝트 구조

```
okxus/
├── bridge/              # Python Bridge 서버
│   ├── __init__.py
│   ├── models.py        # 데이터 모델 (MessageType, ResponseType, etc.)
│   ├── auth.py          # 토큰 인증 모듈
│   ├── automation.py    # pyautogui Kiro IDE 자동화
│   ├── monitor.py       # Kiro 응답 모니터링
│   ├── server.py        # WebSocket 서버
│   ├── requirements.txt # Python 의존성
│   ├── test_auth.py     # 인증 테스트
│   ├── test_automation.py # 자동화 테스트
│   ├── test_monitor.py  # 모니터 테스트
│   └── test_server.py   # 서버 테스트
├── mobile/              # React Native 모바일 앱
│   ├── package.json
│   ├── tsconfig.json
│   └── src/types/       # TypeScript 타입 정의
│       ├── index.ts     # Message, ConnectionStatus, AppConfig, ChatSession
│       └── message.ts   # ClientMessage, ServerMessage, BridgeStatus, ErrorCode
└── .kiro/specs/okxus/   # 스펙 문서
    ├── requirements.md
    ├── design.md
    └── tasks.md
```

## 기술 스택

| 컴포넌트 | 기술 |
|---------|------|
| Bridge | Python 3.x, websockets, pyautogui, pyperclip |
| Mobile App | React Native, TypeScript |
| 테스트 | pytest, hypothesis (Python) / jest, fast-check (TS) |
| 외부 접근 | ngrok |

## Bridge 실행 방법

```bash
cd bridge
pip install -r requirements.txt
# config.json에 auth_token 설정 또는 환경변수 OKXUS_AUTH_TOKEN 설정
python main.py
```

## 테스트 실행

```bash
cd bridge
pip install -r requirements.txt
pytest -v
```

## UI 스타일

- 블랙 배경 (#0d1117) + 네온 컬러
- 네온 그린 (#39ff14) - Kiro 응답
- 네온 시안 (#00ffff) - 전송 버튼
- 네온 핑크 (#ff6ec7) - 사용자 메시지
- JetBrains Mono 폰트
- 앱 아이콘: 노란색 배경, 중앙 X, 동서남북 O/K/U/S
