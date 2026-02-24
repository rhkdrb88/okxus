"""파일 기반 Kiro IDE 통신 모듈

inbox/  - Bridge가 메시지를 쓰면 Kiro hook이 읽어감
outbox/ - Kiro가 응답을 쓰면 Bridge가 읽어감
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "inbox"
OUTBOX_DIR = BASE_DIR / "outbox"


def ensure_dirs() -> None:
    """inbox/outbox 디렉토리 생성."""
    INBOX_DIR.mkdir(exist_ok=True)
    OUTBOX_DIR.mkdir(exist_ok=True)


def write_message(message_id: str, content: str) -> Path:
    """inbox에 메시지 파일을 작성한다.

    Args:
        message_id: 고유 메시지 ID.
        content: 메시지 내용.

    Returns:
        작성된 파일 경로.
    """
    ensure_dirs()
    filepath = INBOX_DIR / f"{message_id}.json"
    data = {
        "id": message_id,
        "content": content,
        "timestamp": time.time(),
    }
    filepath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    logger.info("메시지 작성: %s", filepath.name)
    return filepath


async def wait_for_response(message_id: str, timeout: int = 120) -> str:
    """outbox에서 응답 파일이 생길 때까지 대기한다.

    Args:
        message_id: 대기할 메시지 ID.
        timeout: 최대 대기 시간 (초).

    Returns:
        응답 텍스트.

    Raises:
        TimeoutError: 시간 내 응답 없음.
    """
    ensure_dirs()
    response_path = OUTBOX_DIR / f"{message_id}.json"
    start = time.monotonic()

    while True:
        elapsed = time.monotonic() - start
        if elapsed >= timeout:
            raise TimeoutError(f"응답 대기 시간 초과 ({timeout}초)")

        if response_path.exists():
            try:
                data = json.loads(response_path.read_text(encoding="utf-8"))
                content = data.get("content", "")
                # 읽은 후 삭제
                response_path.unlink(missing_ok=True)
                logger.info("응답 수신: %s (%.1f초)", message_id, elapsed)
                return content
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("응답 파일 읽기 실패, 재시도: %s", e)

        await asyncio.sleep(1.0)


def cleanup_inbox(message_id: str) -> None:
    """처리 완료된 inbox 파일을 삭제한다."""
    filepath = INBOX_DIR / f"{message_id}.json"
    filepath.unlink(missing_ok=True)
