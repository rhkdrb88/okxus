"""bridge/main.py 단위 테스트"""

import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bridge.main import load_config, setup_logging, start_ngrok, CONFIG_PATH


class TestLoadConfig:
    """config.json 로드 테스트"""

    def test_load_existing_config(self, tmp_path):
        """config.json이 존재하면 내용을 로드한다."""
        config_data = {"host": "127.0.0.1", "port": 9999, "auth_token": "test-token"}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        with patch("bridge.main.CONFIG_PATH", config_file):
            result = load_config()

        assert result["host"] == "127.0.0.1"
        assert result["port"] == 9999
        assert result["auth_token"] == "test-token"

    def test_load_missing_config_returns_defaults(self, tmp_path):
        """config.json이 없으면 기본값을 반환한다."""
        missing_path = tmp_path / "nonexistent.json"

        with patch("bridge.main.CONFIG_PATH", missing_path):
            result = load_config()

        assert result["host"] == "0.0.0.0"
        assert result["port"] == 8765
        assert result["ngrok"]["enabled"] is False


class TestSetupLogging:
    """로깅 설정 테스트"""

    def test_setup_logging_info(self):
        """INFO 레벨로 로깅을 설정한다."""
        import logging
        # basicConfig은 이미 설정된 경우 무시하므로 root 핸들러 초기화
        root = logging.getLogger()
        for h in root.handlers[:]:
            root.removeHandler(h)
        setup_logging("INFO")
        assert root.level == logging.INFO

    def test_setup_logging_debug(self):
        """DEBUG 레벨로 로깅을 설정한다."""
        import logging
        root = logging.getLogger()
        for h in root.handlers[:]:
            root.removeHandler(h)
        setup_logging("DEBUG")
        assert root.level == logging.DEBUG


class TestStartNgrok:
    """ngrok 터널 시작 테스트"""

    @pytest.mark.asyncio
    async def test_ngrok_no_authtoken(self):
        """authtoken이 없으면 None을 반환한다."""
        result = await start_ngrok(8765, {"authtoken": ""})
        assert result is None

    @pytest.mark.asyncio
    async def test_ngrok_import_error(self):
        """ngrok 패키지 미설치 시 None을 반환한다."""
        with patch.dict("sys.modules", {"ngrok": None}):
            result = await start_ngrok(8765, {"authtoken": "test-token"})
            assert result is None

    @pytest.mark.asyncio
    async def test_ngrok_success(self):
        """ngrok 터널 시작 성공 시 URL을 반환한다."""
        mock_listener = MagicMock()
        mock_listener.url.return_value = "https://abc123.ngrok.io"

        mock_ngrok = MagicMock()
        mock_ngrok.forward = AsyncMock(return_value=mock_listener)

        with patch.dict("sys.modules", {"ngrok": mock_ngrok}):
            result = await start_ngrok(8765, {"authtoken": "test-token"})
            assert result == "https://abc123.ngrok.io"
