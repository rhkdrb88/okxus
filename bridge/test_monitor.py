"""ResponseMonitor 단위 테스트"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from bridge.models import ResponseType, ServerMessage
from bridge.monitor import ResponseMonitor


class TestIsResponding:
    """is_responding() 메서드 테스트"""

    def test_initially_false(self):
        """초기 상태에서 is_responding은 False"""
        monitor = ResponseMonitor()
        assert monitor.is_responding() is False

    @pytest.mark.asyncio
    async def test_true_while_waiting(self):
        """wait_for_response 실행 중에는 is_responding이 True"""
        monitor = ResponseMonitor()
        observed_states: list[bool] = []

        call_count = 0

        def fake_read():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                observed_states.append(monitor.is_responding())
                return "partial"
            return "partial"

        with patch.object(monitor, "_read_chat_text", side_effect=fake_read):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with patch.object(monitor, "STABLE_THRESHOLD", 0.05):
                    await monitor.wait_for_response(timeout=5)

        assert observed_states[0] is True

    @pytest.mark.asyncio
    async def test_false_after_completion(self):
        """wait_for_response 완료 후 is_responding은 False"""
        monitor = ResponseMonitor()

        with patch.object(monitor, "_read_chat_text", return_value="done"):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with patch.object(monitor, "STABLE_THRESHOLD", 0.05):
                    await monitor.wait_for_response(timeout=5)

        assert monitor.is_responding() is False


class TestWaitForResponse:
    """wait_for_response() 메서드 테스트"""

    @pytest.mark.asyncio
    async def test_returns_stable_text(self):
        """텍스트가 안정되면 해당 텍스트를 반환"""
        monitor = ResponseMonitor()

        with patch.object(monitor, "_read_chat_text", return_value="Kiro의 응답입니다"):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with patch.object(monitor, "STABLE_THRESHOLD", 0.05):
                    result = await monitor.wait_for_response(timeout=5)

        assert result == "Kiro의 응답입니다"

    @pytest.mark.asyncio
    async def test_waits_for_text_to_stabilize(self):
        """텍스트가 변화하다가 안정되면 최종 텍스트를 반환"""
        monitor = ResponseMonitor()
        # 처음 2번은 변화하고, 이후 계속 같은 값 반환
        changing = ["typing...", "typing... more"]
        call_count = 0

        def fake_read():
            nonlocal call_count
            if call_count < len(changing):
                text = changing[call_count]
                call_count += 1
                return text
            return "final answer"

        with patch.object(monitor, "_read_chat_text", side_effect=fake_read):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with patch.object(monitor, "STABLE_THRESHOLD", 0.05):
                    result = await monitor.wait_for_response(timeout=5)

        assert result == "final answer"

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """타임아웃 시 TimeoutError 발생"""
        monitor = ResponseMonitor()
        call_count = 0

        def changing_text():
            nonlocal call_count
            call_count += 1
            return f"changing {call_count}"

        with patch.object(monitor, "_read_chat_text", side_effect=changing_text):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with pytest.raises(TimeoutError, match="응답 대기 시간 초과"):
                    await monitor.wait_for_response(timeout=0.1)

    @pytest.mark.asyncio
    async def test_read_failure_raises_runtime_error(self):
        """텍스트 읽기 실패 시 RuntimeError 발생 (Req 3.4)"""
        monitor = ResponseMonitor()

        with patch.object(monitor, "_read_chat_text", return_value=None):
            with pytest.raises(RuntimeError, match="응답 텍스트 읽기 실패"):
                await monitor.wait_for_response(timeout=5)

    @pytest.mark.asyncio
    async def test_responding_false_after_timeout(self):
        """타임아웃 후에도 is_responding은 False로 복원"""
        monitor = ResponseMonitor()
        call_count = 0

        def changing_text():
            nonlocal call_count
            call_count += 1
            return f"changing {call_count}"

        with patch.object(monitor, "_read_chat_text", side_effect=changing_text):
            with patch.object(monitor, "POLL_INTERVAL", 0.01):
                with pytest.raises(TimeoutError):
                    await monitor.wait_for_response(timeout=0.1)

        assert monitor.is_responding() is False

    @pytest.mark.asyncio
    async def test_responding_false_after_read_failure(self):
        """읽기 실패 후에도 is_responding은 False로 복원"""
        monitor = ResponseMonitor()

        with patch.object(monitor, "_read_chat_text", return_value=None):
            with pytest.raises(RuntimeError):
                await monitor.wait_for_response(timeout=5)

        assert monitor.is_responding() is False


class TestCreateErrorMessage:
    """create_error_message() 메서드 테스트"""

    def test_creates_error_server_message(self):
        """오류 메시지가 올바른 ServerMessage 형식으로 생성됨 (Req 3.4)"""
        monitor = ResponseMonitor()
        msg = monitor.create_error_message("Response read timeout")

        assert isinstance(msg, ServerMessage)
        assert msg.type == ResponseType.ERROR
        assert msg.payload == {"error": "Response read timeout"}
        assert isinstance(msg.timestamp, float)

    def test_error_message_contains_description(self):
        """오류 설명이 payload에 포함됨"""
        monitor = ResponseMonitor()
        msg = monitor.create_error_message("채팅 텍스트 읽기 실패")

        assert msg.payload["error"] == "채팅 텍스트 읽기 실패"


class TestReadChatText:
    """_read_chat_text() 메서드 테스트"""

    @patch("bridge.monitor.pyperclip.copy")
    @patch("bridge.monitor.pyperclip.paste")
    @patch("bridge.monitor.pyautogui.hotkey")
    @patch("bridge.monitor.pyautogui.sleep")
    def test_reads_text_via_clipboard(self, mock_sleep, mock_hotkey, mock_paste, mock_copy):
        """Ctrl+A, Ctrl+C로 텍스트를 읽고 클립보드를 원복"""
        mock_paste.side_effect = ["original clipboard", "Kiro response text"]
        monitor = ResponseMonitor()

        result = monitor._read_chat_text()

        assert result == "Kiro response text"
        # 클립보드 원복 확인
        mock_copy.assert_called_once_with("original clipboard")

    @patch("bridge.monitor.pyperclip.paste", side_effect=Exception("clipboard error"))
    def test_returns_none_on_exception(self, _mock_paste):
        """예외 발생 시 None 반환"""
        monitor = ResponseMonitor()
        result = monitor._read_chat_text()
        assert result is None
