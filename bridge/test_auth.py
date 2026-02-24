import json
import pytest
from unittest.mock import patch, mock_open
from bridge.auth import Authenticator


class TestDirectToken:
    def test_valid(self):
        auth = Authenticator(token='secret')
        assert auth.validate('secret') is True

    def test_invalid(self):
        auth = Authenticator(token='secret')
        assert auth.validate('wrong') is False

    def test_empty(self):
        auth = Authenticator(token='secret')
        assert auth.validate('') is False


class TestEnvVar:
    def test_loads_from_env(self, monkeypatch):
        monkeypatch.setenv('OKXUS_AUTH_TOKEN', 'env-tok')
        auth = Authenticator()
        assert auth.validate('env-tok') is True
        assert auth.validate('x') is False

    def test_env_priority(self, monkeypatch):
        monkeypatch.setenv('OKXUS_AUTH_TOKEN', 'env-tok')
        auth = Authenticator()
        assert auth.validate('env-tok') is True


class TestConfigFile:
    def test_loads_from_config(self, monkeypatch):
        monkeypatch.delenv('OKXUS_AUTH_TOKEN', raising=False)
        data = json.dumps({'auth_token': 'file-tok'})
        with patch('bridge.auth.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=data)):
                auth = Authenticator()
                assert auth.validate('file-tok') is True


class TestNoToken:
    def test_raises_no_config(self, monkeypatch):
        monkeypatch.delenv('OKXUS_AUTH_TOKEN', raising=False)
        with patch('bridge.auth.Path.exists', return_value=False):
            with pytest.raises(ValueError):
                Authenticator()

    def test_raises_missing_key(self, monkeypatch):
        monkeypatch.delenv('OKXUS_AUTH_TOKEN', raising=False)
        data = json.dumps({'port': 8765})
        with patch('bridge.auth.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=data)):
                with pytest.raises(ValueError):
                    Authenticator()
