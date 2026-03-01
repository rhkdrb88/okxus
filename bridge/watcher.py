"""inbox 폴더 감시 → Kiro IDE 채팅에 자동 메시지 전송

inbox/에 새 .json 파일이 생기면 감지하여
Kiro IDE 채팅에 "inbox 확인" 메시지를 자동 입력한다.
promptSubmit hook이 트리거되어 Kiro가 inbox를 처리.

사용법:
    python okxus/bridge/watcher.py
"""

import json
import logging
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watcher] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

INBOX_DIR = Path(__file__).parent / "inbox"
POLL_INTERVAL = 3  # 초
KIRO_INPUT_DELAY = 0.5  # Kiro 포커스 후 입력 대기 (초)
COOLDOWN = 120  # 같은 메시지 재전송 방지 (초) — Kiro 처리 시간 고려

# 이미 트리거한 메시지 ID 추적
_triggered: dict[str, float] = {}


def ensure_dirs() -> None:
    INBOX_DIR.mkdir(exist_ok=True)


def send_to_kiro(message: str) -> bool:
    """Kiro IDE 채팅에 메시지를 자동 입력하고 Enter를 친다.

    Returns:
        성공 시 True, 실패 시 False.
    """
    try:
        from pywinauto import Desktop, keyboard

        desktop = Desktop(backend="uia")
        kiro = desktop.window(
            title_re=".*Kiro.*", class_name="Chrome_WidgetWin_1"
        )

        # Kiro 창 포커스
        kiro.set_focus()
        time.sleep(KIRO_INPUT_DELAY)

        # Ctrl+L → 채팅 입력란 포커스
        keyboard.send_keys("^l")
        time.sleep(0.3)

        # 텍스트 입력 + Enter
        keyboard.send_keys(message, with_spaces=True)
        time.sleep(0.1)
        keyboard.send_keys("{ENTER}")

        logger.info("Kiro 채팅에 메시지 전송: %s", message)
        return True

    except Exception as e:
        logger.error("Kiro 메시지 전송 실패: %s", e)
        return False


def poll_inbox() -> None:
    """inbox를 주기적으로 확인하고 Kiro에 알린다."""
    ensure_dirs()
    logger.info("inbox 감시 시작: %s", INBOX_DIR)
    print(f"[Watcher] inbox 감시 중... (매 {POLL_INTERVAL}초)")

    while True:
        try:
            for f in INBOX_DIR.glob("*.json"):
                if f.name == ".gitkeep":
                    continue

                msg_id = f.stem
                now = time.time()

                # 쿨다운 체크 — 같은 메시지를 반복 트리거하지 않음
                if msg_id in _triggered:
                    if now - _triggered[msg_id] < COOLDOWN:
                        continue

                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    content = data.get("content", "")
                    logger.info("새 메시지: %s → %s", msg_id, content[:50])
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("파일 읽기 실패: %s — %s", f.name, e)
                    continue

                # Kiro에 알림
                print(f"[Watcher] Kiro에 알림 전송: {msg_id}")
                if send_to_kiro("inbox 확인"):
                    _triggered[msg_id] = now
                    print(f"[Watcher] 전송 완료: {msg_id}")
                else:
                    print(f"[Watcher] 전송 실패: {msg_id} — 다음 폴링에서 재시도")

        except Exception as e:
            logger.error("폴링 오류: %s", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        poll_inbox()
    except KeyboardInterrupt:
        print("\n[Watcher] 종료.")
