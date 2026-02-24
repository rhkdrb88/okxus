"""토큰 기반 인증 모듈"""

import json
import os
from pathlib import Path


class Authenticator:
    """토큰 기반 인증

    환경변수(OKXUS_AUTH_TOKEN) 우선, 설정 파일(bridge/config.json) 폴백으로 토큰 로드.
    """

    def __init__(self, token: str | None = None):
        """토큰을 직접 전달하거나, 환경변수 또는 설정 파일에서 로드한다.

        Args:
            token: 직접 전달할 인증 토큰. None이면 환경변수/설정 파일에서 로드.
        """
        if token is not None:
            self._token = token
        else:
            self._token = self._load_token()

    def _load_token(self) -> str:
        """환경변수 → 설정 파일 순서로 토큰을 로드한다.

        Returns:
            로드된 토큰 문자열.

        Raises:
            ValueError: 토큰을 찾을 수 없는 경우.
        """
        # 1) 환경변수에서 로드
        env_token = os.environ.get("OKXUS_AUTH_TOKEN")
        if env_token:
            return env_token

        # 2) 설정 파일에서 로드
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            file_token = config.get("auth_token")
            if file_token:
                return file_token

        raise ValueError(
            "인증 토큰을 찾을 수 없습니다. "
            "OKXUS_AUTH_TOKEN 환경변수를 설정하거나 bridge/config.json에 auth_token을 추가하세요."
        )

    def validate(self, client_token: str) -> bool:
        """클라이언트 토큰을 검증한다.

        Args:
            client_token: 클라이언트가 전송한 인증 토큰.

        Returns:
            토큰이 유효하면 True, 아니면 False.
        """
        return client_token == self._token
