"""inbox 폴더 감시 → Kiro 트리거 파일 생성

inbox/에 새 .json 파일이 생기면 감지하여
.kiro/triggers/ 폴더에 복사한다.
Kiro의 fileCreated hook이 .kiro/triggers/*.json을 감지하여 처리.
"""

import json
import logging
import shutil
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watcher] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

INBOX_DIR = Path(__file__).parent / "inbox"
TRIGGER_DIR = Path(__file__).resolve().parent.parent.parent / ".kiro" / "triggers"
POLL_INTERVAL = 2  # 초


def ensure_dirs() -> None:
    INBOX_DIR.mkdir(exist_ok=True)
    TRIGGER_DIR.mkdir(parents=True, exist_ok=True)


def poll_inbox() -> None:
    """inbox를 주기적으로 확인하고 트리거 파일을 생성한다."""
    ensure_dirs()
    logger.info("inbox 감시 시작: %s", INBOX_DIR)
    logger.info("트리거 디렉토리: %s", TRIGGER_DIR)
    print(f"[Watcher] inbox 감시 중... (매 {POLL_INTERVAL}초)")

    while True:
        try:
            for f in INBOX_DIR.glob("*.json"):
                if f.name == ".gitkeep":
                    continue

                trigger_path = TRIGGER_DIR / f.name
                if trigger_path.exists():
                    # 이미 트리거됨, 스킵
                    continue

                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    msg_id = data.get("id", f.stem)
                    content = data.get("content", "")
                    logger.info("새 메시지 감지: %s → %s", msg_id, content[:50])

                    # 트리거 파일 생성 (Kiro hook이 감지)
                    shutil.copy2(f, trigger_path)
                    logger.info("트리거 파일 생성: %s", trigger_path.name)
                    print(f"[Watcher] 메시지 전달: {msg_id}")
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("파일 읽기 실패: %s — %s", f.name, e)

        except Exception as e:
            logger.error("폴링 오류: %s", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        poll_inbox()
    except KeyboardInterrupt:
        print("\n[Watcher] 종료.")
