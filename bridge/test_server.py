"""BridgeServer 단위 테스트"""

import asyncio
import json
import time

import pytest
import pytest_asyncio
import websockets

from bridge.auth import Authenticator
from bridge.server import BridgeServer


TEST_TOKEN = "test-secret-token"
TEST_HOST = "127.0.0.1"
TEST_PORT = 9876


@pytest_asyncio.fixture
async def server():
    """테스트용 BridgeServer를 시작하고 종료한다."""
    auth = Authenticator(token=TEST_TOKEN)
    srv = BridgeServer(authenticator=auth)
    await srv.start(TEST_HOST, TEST_PORT)
    yield srv
    await srv.stop()


async def _connect_and_auth(token: str = TEST_TOKEN):
    """WebSocket 연결 후 인증을 수행하고 websocket을 반환한다."""
    ws = await websockets.connect(f"ws://{TEST_HOST}:{TEST_PORT}")
    auth_msg = json.dumps({
        "type": "auth",
        "payload": {"token": token},
        "timestamp": time.time(),
    })
    await ws.send(auth_msg)
    resp = json.loads(await ws.recv())
    return ws, resp


class TestStart:
    @pytest.mark.asyncio
    async def test_server_starts_and_accepts_connection(self, server):
        """서버가 시작되고 연결을 수락한다 (Req 5.1)."""
        ws, resp = await _connect_and_auth()
        assert resp["type"] == "auth_result"
        assert resp["payload"]["success"] is True
        await ws.close()


class TestAuthentication:
    @pytest.mark.asyncio
    async def test_valid_token_accepted(self, server):
        """유효한 토큰으로 인증 성공 (Req 6.1)."""
        ws, resp = await _connect_and_auth(TEST_TOKEN)
        assert resp["type"] == "auth_result"
        assert resp["payload"]["success"] is True
        await ws.close()

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, server):
        """무효한 토큰으로 인증 실패 (Req 6.2)."""
        ws, resp = await _connect_and_auth("wrong-token")
        assert resp["type"] == "auth_result"
        assert resp["payload"]["success"] is False
        # 서버가 연결을 종료해야 한다
        with pytest.raises(websockets.ConnectionClosed):
            await ws.recv()

    @pytest.mark.asyncio
    async def test_non_auth_first_message_rejected(self, server):
        """첫 메시지가 auth가 아니면 오류 반환."""
        ws = await websockets.connect(f"ws://{TEST_HOST}:{TEST_PORT}")
        msg = json.dumps({
            "type": "message",
            "payload": {"content": "hello"},
            "timestamp": time.time(),
        })
        await ws.send(msg)
        resp = json.loads(await ws.recv())
        assert resp["type"] == "error"
        await ws.close()


class TestHeartbeat:
    @pytest.mark.asyncio
    async def test_heartbeat_echo(self, server):
        """heartbeat 메시지에 heartbeat로 응답한다 (Req 1.2)."""
        ws, _ = await _connect_and_auth()
        hb = json.dumps({
            "type": "heartbeat",
            "payload": {},
            "timestamp": time.time(),
        })
        await ws.send(hb)
        resp = json.loads(await ws.recv())
        assert resp["type"] == "heartbeat"
        await ws.close()


class TestStatusRequest:
    @pytest.mark.asyncio
    async def test_status_response_fields(self, server):
        """상태 요청 시 kiro_running, connected_clients, uptime 필드 반환 (Req 5.2)."""
        ws, _ = await _connect_and_auth()
        req = json.dumps({
            "type": "status_request",
            "payload": {},
            "timestamp": time.time(),
        })
        await ws.send(req)
        resp = json.loads(await ws.recv())
        assert resp["type"] == "status"
        status = resp["payload"]["status"]
        assert "kiro_running" in status
        assert "connected_clients" in status
        assert "uptime" in status
        assert status["connected_clients"] >= 1
        assert status["uptime"] >= 0
        await ws.close()


class TestBroadcast:
    @pytest.mark.asyncio
    async def test_broadcast_to_authenticated_clients(self, server):
        """broadcast는 인증된 클라이언트에 메시지를 전송한다."""
        ws1, _ = await _connect_and_auth()
        ws2, _ = await _connect_and_auth()

        test_msg = {"type": "kiro_response", "payload": {"content": "hello"}, "timestamp": time.time()}
        await server.broadcast(test_msg)

        r1 = json.loads(await ws1.recv())
        r2 = json.loads(await ws2.recv())
        assert r1["payload"]["content"] == "hello"
        assert r2["payload"]["content"] == "hello"

        await ws1.close()
        await ws2.close()


class TestInvalidMessage:
    @pytest.mark.asyncio
    async def test_invalid_json(self, server):
        """잘못된 JSON 전송 시 오류 반환."""
        ws, _ = await _connect_and_auth()
        await ws.send("not-json{{{")
        resp = json.loads(await ws.recv())
        assert resp["type"] == "error"
        await ws.close()

    @pytest.mark.asyncio
    async def test_unknown_message_type(self, server):
        """알 수 없는 메시지 타입 전송 시 오류 반환."""
        ws, _ = await _connect_and_auth()
        msg = json.dumps({
            "type": "unknown_type",
            "payload": {},
            "timestamp": time.time(),
        })
        await ws.send(msg)
        resp = json.loads(await ws.recv())
        assert resp["type"] == "error"
        await ws.close()
