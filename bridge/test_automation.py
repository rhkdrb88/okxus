"""KiroAutomation 단위 테스트"""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from bridge.automation import KiroAutomation


class TestIsKiroRunning:
    """is_kiro_running() 메서드 테스트"""

    def test_returns_true_when_kiro_process_found(self):
        """tasklist 출력에 Kiro.exe가 있으면 True 반환"""
        automation = KiroAutomation()
        fake_output = (
            "Image Name                     PID Session Name\n"
            "Kiro.exe                      1234 Console\n"
        )
        with patch("bridge.automation.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=fake_output)
            assert automation.is_kiro_running() is True

    def test_returns_false_when_kiro_process_not_found(self):
        """tasklist 출력에 Kiro.exe가 없으면 False 반환"""
        automation = KiroAutomation()
        fake_output = (
            "INFO: No tasks are running which match the specified criteria.\n"
        )
        with patch("bridge.automation.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=fake_output)
            assert automation.is_kiro_running() is False

    def test_returns_false_on_exception(self):
        """subprocess 실행 중 예외 발생 시 False 반환"""
        automation = KiroAutomation()
        with patch("bridge.automation.subprocess.run", side_effect=OSError("fail")):
            assert automation.is_kiro_running() is False


class TestActivateKiroWindow:
    """activate_kiro_window() 메서드 테스트"""

    def test_returns_false_when_no_window_found(self):
        """Kiro 창이 없으면 False 반환"""
        automation = KiroAutomation()
        with patch("bridge.automation.pyautogui.getWindowsWithTitle", return_value=[]):
            assert automation.activate_kiro_window() is False

    def test_returns_true_when_window_found_and_activated(self):
        """Kiro 창을 찾아 활성화하면 True 반환"""
        automation = KiroAutomation()
        mock_window = MagicMock()
        mock_window.isMinimized = False
        with patch(
            "bridge.automation.pyautogui.getWindowsWithTitle",
            return_value=[mock_window],
        ):
            with patch("bridge.automation.time.sleep"):
                assert automation.activate_kiro_window() is True
                mock_window.activate.assert_called_once()

    def test_restores_minimized_window(self):
        """최소화된 창은 복원 후 활성화"""
        automation = KiroAutomation()
        mock_window = MagicMock()
        mock_window.isMinimized = True
        with patch(
            "bridge.automation.pyautogui.getWindowsWithTitle",
            return_value=[mock_window],
        ):
            with patch("bridge.automation.time.sleep"):
                assert automation.activate_kiro_window() is True
                mock_window.restore.assert_called_once()
                mock_window.activate.assert_called_once()

    def test_returns_false_on_exception(self):
        """예외 발생 시 False 반환"""
        automation = KiroAutomation()
        with patch(
            "bridge.automation.pyautogui.getWindowsWithTitle",
            side_effect=Exception("fail"),
        ):
            assert automation.activate_kiro_window() is False


class TestSendMessage:
    """send_message() 메서드 테스트"""

    @patch("bridge.automation.time.sleep")
    @patch("bridge.automation.pyautogui.press")
    @patch("bridge.automation.pyautogui.hotkey")
    @patch("bridge.automation.pyperclip.copy")
    def test_sends_message_successfully(self, mock_copy, mock_hotkey, mock_press, _sleep):
        """메시지 전송 성공 시 True 반환, 클립보드 복사 → Ctrl+V → Enter 순서 확인"""
        automation = KiroAutomation()
        with patch.object(automation, "activate_kiro_window", return_value=True):
            result = automation.send_message("hello kiro")

        assert result is True
        mock_copy.assert_called_once_with("hello kiro")
        mock_hotkey.assert_called_once_with("ctrl", "v")
        mock_press.assert_called_once_with("enter")

    def test_returns_false_when_window_activation_fails(self):
        """창 활성화 실패 시 False 반환"""
        automation = KiroAutomation()
        with patch.object(automation, "activate_kiro_window", return_value=False):
            assert automation.send_message("test") is False

    @patch("bridge.automation.time.sleep")
    @patch("bridge.automation.pyperclip.copy", side_effect=Exception("clipboard error"))
    def test_returns_false_on_clipboard_error(self, _copy, _sleep):
        """클립보드 복사 실패 시 False 반환"""
        automation = KiroAutomation()
        with patch.object(automation, "activate_kiro_window", return_value=True):
            assert automation.send_message("test") is False
