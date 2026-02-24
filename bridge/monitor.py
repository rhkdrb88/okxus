"""Kiro IDE 응답 모니터링 모듈

Kiro IDE가 응답을 생성하는 동안 상태를 모니터링하고,
응답이 완료되면 텍스트를 읽어서 반환한다.
"""

import asyncio
import logging
import time

import pyautogui
import pyperclip

from bridge.models import ResponseType, ServerMessage

logger = logging.getLogger(__name__)


class ResponseMonitor:
    """Kiro IDE 응답 모니터링

    Kiro IDE 채팅 영역의 텍스트 변화를 폴링 방식으로 감지하여
    응답 생성 중인지 판단하고, 응답이 완료되면 텍스트를 반환한다.
    """

    POLL_INTERVAL = 1.0  # 폴링 간격 (초)
    STABLE_THRESHOLD = 3.0  # 텍스트 변화 없이 안정된 것으로 판단하는 시간 (초)

    def __init__(self) -> None:
        self._responding = False
        self._last_snapshot: str | None = None
        self._last_change_time: float = 0.0

    def is_responding(self) -> bool:
        """현재 응답 생성 중인지 확인한다 (Req 3.1).

        Returns:
            응답 생성 중이면 True, 아니면 False.
        """
        return self._responding

    async def wait_for_response(self, timeout: int = 60) -> str:
        """응답 완료까지 대기 후 텍스트를 반환한다 (Req 3.1, 3.2).

        Kiro IDE 채팅 영역의 텍스트를 주기적으로 읽어서 변화를 감지한다.
        텍스트가 STABLE_THRESHOLD 동안 변하지 않으면 응답 완료로 판단한다.

        Args:
            timeout: 최대 대기 시간 (초). 기본값 60초.

        Returns:
            Kiro IDE의 응답 텍스트.

        Raises:
            TimeoutError: 지정된 시간 내에 응답이 완료되지 않은 경우.
            RuntimeError: 응답 텍스트 읽기에 실패한 경우 (Req 3.4).
        """
        self._responding = True
        self._last_snapshot = None
        self._last_change_time = time.monotonic()
        start_time = time.monotonic()

        try:
            while True:
                elapsed = time.monotonic() - start_time
                if elapsed >= timeout:
                    raise TimeoutError(
                        f"응답 대기 시간 초과 ({timeout}초)"
                    )

                snapshot = self._read_chat_text()

                if snapshot is None:
                    raise RuntimeError("응답 텍스트 읽기 실패")

                now = time.monotonic()

                if snapshot != self._last_snapshot:
                    # 텍스트가 변경됨 — 아직 응답 생성 중
                    self._last_snapshot = snapshot
                    self._last_change_time = now
                elif now - self._last_change_time >= self.STABLE_THRESHOLD:
                    # 텍스트가 안정됨 — 응답 완료
                    logger.info("응답 완료 감지 (%.1f초 경과)", elapsed)
                    return snapshot

                await asyncio.sleep(self.POLL_INTERVAL)
        finally:
            self._responding = False

    def _read_chat_text(self) -> str | None:
        """Kiro IDE 채팅 영역의 텍스트를 읽는다.

        Ctrl+A로 전체 선택 후 Ctrl+C로 클립보드에 복사하여 텍스트를 가져온다.

        Returns:
            읽은 텍스트 문자열, 실패 시 None.
        """
        try:
            # 기존 클립보드 내용 백업
            previous_clipboard = pyperclip.paste()

            # 전체 선택 후 복사
            pyautogui.hotkey("ctrl", "a")
            pyautogui.hotkey("ctrl", "c")
            # 클립보드 반영 대기
            pyautogui.sleep(0.2)

            text = pyperclip.paste()

            # 클립보드 원복
            pyperclip.copy(previous_clipboard)

            return text
        except Exception as e:
            logger.error("채팅 텍스트 읽기 실패: %s", e)
            return None

    def create_error_message(self, error: str) -> ServerMessage:
        """응답 읽기 실패 시 오류 ServerMessage를 생성한다 (Req 3.4).

        Args:
            error: 오류 설명 문자열.

        Returns:
            type이 ERROR이고 오류 설명을 포함하는 ServerMessage.
        """
        return ServerMessage(
            type=ResponseType.ERROR,
            payload={"error": error},
            timestamp=time.time(),
        )
