"""pyautogui를 사용한 Kiro IDE 자동화 모듈

Kiro IDE 창 활성화, 클립보드를 통한 메시지 전송, 프로세스 실행 상태 확인을 담당한다.
"""

import logging
import subprocess
import time

import pyautogui
import pyperclip

logger = logging.getLogger(__name__)

# pyautogui 안전 설정
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


class KiroAutomation:
    """pyautogui를 사용한 Kiro IDE 제어

    Kiro IDE 창을 찾아 활성화하고, 클립보드를 통해 메시지를 붙여넣기하며,
    Kiro IDE 프로세스의 실행 상태를 확인한다.
    """

    KIRO_WINDOW_TITLE = "Kiro"
    KIRO_PROCESS_NAME = "Kiro"

    def activate_kiro_window(self) -> bool:
        """Kiro IDE 창을 찾아 활성화한다.

        pyautogui.getWindowsWithTitle()로 Kiro 창을 검색하고,
        찾은 창을 포커스 및 활성화한다.

        Returns:
            활성화 성공 시 True, 실패 시 False.
        """
        try:
            windows = pyautogui.getWindowsWithTitle(self.KIRO_WINDOW_TITLE)
            if not windows:
                logger.warning("Kiro IDE 창을 찾을 수 없습니다.")
                return False

            kiro_window = windows[0]

            # 최소화 상태이면 복원
            if kiro_window.isMinimized:
                kiro_window.restore()

            kiro_window.activate()
            time.sleep(0.5)

            logger.info("Kiro IDE 창 활성화 완료")
            return True
        except Exception as e:
            logger.error("Kiro IDE 창 활성화 실패: %s", e)
            return False

    def send_message(self, message: str) -> bool:
        """클립보드에 메시지를 복사한 후 Kiro IDE 채팅창에 붙여넣기 및 Enter 입력.

        1. Kiro IDE 창이 활성화되지 않은 상태이면 활성화한다 (Req 2.5).
        2. pyperclip으로 클립보드에 메시지를 복사한다 (Req 2.2).
        3. Ctrl+V로 붙여넣기 후 Enter 키를 입력한다 (Req 2.3).

        Args:
            message: Kiro IDE에 전송할 메시지 텍스트.

        Returns:
            전송 성공 시 True, 실패 시 False.
        """
        try:
            # Kiro 창 활성화 (Req 2.5)
            if not self.activate_kiro_window():
                logger.error("Kiro IDE 창 활성화 실패로 메시지 전송 불가")
                return False

            # 클립보드에 메시지 복사 (Req 2.2)
            pyperclip.copy(message)

            # Ctrl+V 붙여넣기 후 Enter (Req 2.3)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.3)
            pyautogui.press("enter")

            logger.info("메시지 전송 완료: %s", message[:50])
            return True
        except Exception as e:
            logger.error("메시지 전송 실패: %s", e)
            return False

    def is_kiro_running(self) -> bool:
        """Kiro IDE 프로세스가 실행 중인지 확인한다.

        Windows의 tasklist 명령어를 사용하여 Kiro 프로세스를 검색한다.

        Returns:
            Kiro IDE가 실행 중이면 True, 아니면 False (Req 5.4).
        """
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {self.KIRO_PROCESS_NAME}.exe"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return self.KIRO_PROCESS_NAME.lower() in result.stdout.lower()
        except Exception as e:
            logger.error("Kiro IDE 프로세스 확인 실패: %s", e)
            return False
