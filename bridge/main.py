"""OKXUS Bridge 메인 엔트리포인트

서버 시작 로직, config.json 로드, ngrok 연동을 담당한다.

사용법:
    python -m bridge.main
    또는
    python bridge/main.py
"""

import asyncio
import json
import logging
import signal
import sys
from pathlib import Path

from bridge.auth import Authenticator
from bridge.file_io import ensure_dirs
from bridge.server import BridgeServer

logger = logging.getLogger("bridge")

CONFIG_PATH = Path(__file__).parent / "config.json"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8765


def load_config() -> dict:
    """config.json에서 설정을 로드한다.

    파일이 없으면 기본값을 반환한다.

    Returns:
        설정 딕셔너리.
    """
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("설정 로드 완료: %s", CONFIG_PATH)
        return config

    logger.warning("config.json 없음 — 기본 설정 사용")
    return {
        "host": DEFAULT_HOST,
        "port": DEFAULT_PORT,
        "auth_token": "",
        "ngrok": {"enabled": False},
        "log_level": "INFO",
    }


def setup_logging(level: str = "INFO") -> None:
    """로깅을 설정한다."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def start_ngrok(port: int, ngrok_config: dict) -> str | None:
    """ngrok 터널을 시작하여 외부 접근 URL을 반환한다 (Req 7.1, 7.3).

    Args:
        port: 터널링할 로컬 포트.
        ngrok_config: ngrok 설정 딕셔너리 (authtoken, region 등).

    Returns:
        ngrok 공개 URL 문자열, 실패 시 None.
    """
    try:
        import ngrok  # pyngrok 대신 ngrok 공식 Python SDK

        authtoken = ngrok_config.get("authtoken", "")
        if not authtoken:
            logger.warning("ngrok authtoken이 설정되지 않았습니다.")
            print("[Bridge] ngrok authtoken 미설정 — 외부 접근 불가")
            return None

        listener = await ngrok.forward(
            port,
            authtoken=authtoken,
            domain=ngrok_config.get("domain"),
        )
        url = listener.url()
        logger.info("ngrok 터널 시작: %s → localhost:%d", url, port)
        print(f"[Bridge] ngrok 터널: {url}")
        # WSS URL 안내
        ws_url = url.replace("https://", "wss://").replace("http://", "ws://")
        print(f"[Bridge] WebSocket URL: {ws_url}")
        return url

    except ImportError:
        logger.warning("ngrok 패키지 미설치 — pip install ngrok")
        print("[Bridge] ngrok 패키지 미설치 — pip install ngrok")
        return None
    except Exception as e:
        logger.error("ngrok 시작 실패: %s", e)
        print(f"[Bridge] ngrok 시작 실패: {e}")
        return None


async def main() -> None:
    """Bridge 서버를 시작한다."""
    config = load_config()
    setup_logging(config.get("log_level", "INFO"))

    host = config.get("host", DEFAULT_HOST)
    port = config.get("port", DEFAULT_PORT)

    # 모듈 초기화
    token = config.get("auth_token", "")
    if token and token != "change-me-to-a-secure-token":
        auth = Authenticator(token=token)
    else:
        # 환경변수 또는 config.json 자동 로드
        try:
            auth = Authenticator()
        except ValueError as e:
            print(f"[Bridge] 인증 설정 오류: {e}")
            sys.exit(1)

    # 파일 기반 통신 디렉토리 생성
    ensure_dirs()
    print("[Bridge] 파일 기반 통신 모드 (inbox/outbox)")

    server = BridgeServer(authenticator=auth)

    # 서버 시작
    await server.start(host, port)

    # ngrok 터널 (선택)
    ngrok_config = config.get("ngrok", {})
    if ngrok_config.get("enabled", False):
        await start_ngrok(port, ngrok_config)
    else:
        print(f"[Bridge] 로컬 전용 모드 — ws://{host}:{port}")

    print("[Bridge] 준비 완료. Ctrl+C로 종료.")

    # 종료 시그널 대기
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        print("\n[Bridge] 종료 신호 수신...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            # Windows에서는 add_signal_handler 미지원
            pass

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()
        print("[Bridge] 종료 완료.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
