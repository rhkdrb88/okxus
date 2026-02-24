"""WebSocket 서버 모듈 - 모바일 앱과의 통신 담당

BridgeServer는 WebSocket 서버를 시작하고, 클라이언트 연결을 처리하며,
인증 검증, 메시지 라우팅, heartbeat 교환을 수행한다.
"""

import asyncio
import json
import logging
import time

import websockets

from bridge.auth import Authenticator
from bridge.automation import KiroAutomation
from bridge.models import (
    BridgeStatus,
    MessageType,
    ResponseType,
    ServerMessage,
)
from bridge.monitor import ResponseMonitor

logger = logging.getLogger(__name__)


class BridgeServer:
    """WebSocket 서버 - 모바일 앱과의 통신 담당"""

    HEARTBEAT_INTERVAL = 30  # heartbeat 전송 간격 (초)

    def __init__(
        self,
        authenticator: Authenticator,
        automation: KiroAutomation | None = None,
        monitor: ResponseMonitor | None = None,
    ) -> None:
        self._auth = authenticator
        self._automation = automation or KiroAutomation()
        self._monitor = monitor or ResponseMonitor()
        self._clients: set[websockets.WebSocketServerProtocol] = set()
        self._authenticated: set[websockets.WebSocketServerProtocol] = set()
        self._start_time: float = 0.0
        self._server: websockets.WebSocketServer | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(self, host: str = "0.0.0.0", port: int = 8765) -> None:
        """WebSocket 서버를 시작한다 (Req 5.1).

        Args:
            host: 바인딩할 호스트 주소.
            port: 바인딩할 포트 번호.
        """
        self._start_time = time.time()
        self._server = await websockets.serve(
            self.handle_connection, host, port
        )
        logger.info("Bridge 서버 시작 — ws://%s:%s", host, port)
        print(f"[Bridge] 서버 시작 — ws://{host}:{port}")

    async def stop(self) -> None:
        """서버를 정상 종료한다."""
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            logger.info("Bridge 서버 종료")
            print("[Bridge] 서버 종료")

    async def handle_connection(
        self, websocket: websockets.WebSocketServerProtocol
    ) -> None:
        """클라이언트 연결을 처리한다 (Req 1.1, 2.1).

        연결 수립 후 인증을 검증하고, 인증 성공 시 메시지를 라우팅한다.
        """
        self._clients.add(websocket)
        remote = websocket.remote_address
        logger.info("클라이언트 연결: %s", remote)
        print(f"[Bridge] 클라이언트 연결: {remote}")
        self._log_status()

        heartbeat_task: asyncio.Task | None = None
        try:
            # 첫 메시지는 반드시 auth여야 한다
            if not await self._authenticate(websocket):
                return

            self._authenticated.add(websocket)
            logger.info("클라이언트 인증 성공: %s", remote)
            print(f"[Bridge] 클라이언트 인증 성공: {remote}")

            # heartbeat 태스크 시작 (Req 1.2)
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(websocket)
            )

            # 메시지 수신 루프
            async for raw in websocket:
                await self._route_message(websocket, raw)

        except websockets.ConnectionClosed:
            logger.info("클라이언트 연결 종료: %s", remote)
            print(f"[Bridge] 클라이언트 연결 종료: {remote}")
        except Exception as exc:
            logger.error("연결 처리 오류: %s", exc)
        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()
            self._clients.discard(websocket)
            self._authenticated.discard(websocket)
            self._log_status()

    async def broadcast(self, message: dict) -> None:
        """인증된 모든 클라이언트에 메시지를 전송한다.

        Args:
            message: 전송할 메시지 딕셔너리.
        """
        data = json.dumps(message)
        disconnected: list[websockets.WebSocketServerProtocol] = []
        for ws in self._authenticated:
            try:
                await ws.send(data)
            except websockets.ConnectionClosed:
                disconnected.append(ws)
        for ws in disconnected:
            self._clients.discard(ws)
            self._authenticated.discard(ws)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _authenticate(
        self, websocket: websockets.WebSocketServerProtocol
    ) -> bool:
        """첫 메시지로 인증을 수행한다 (Req 6.1, 6.2).

        Returns:
            인증 성공 시 True, 실패 시 False (연결 종료됨).
        """
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=10)
            msg = json.loads(raw)

            if msg.get("type") != MessageType.AUTH.value:
                await self._send(websocket, ResponseType.ERROR, {"error": "첫 메시지는 auth여야 합니다"})
                await websocket.close()
                return False

            token = msg.get("payload", {}).get("token", "")
            if self._auth.validate(token):
                await self._send(websocket, ResponseType.AUTH_RESULT, {"success": True})
                return True
            else:
                await self._send(websocket, ResponseType.AUTH_RESULT, {"success": False, "error": "Invalid token"})
                await websocket.close()
                return False

        except asyncio.TimeoutError:
            await self._send(websocket, ResponseType.ERROR, {"error": "인증 타임아웃"})
            await websocket.close()
            return False
        except (json.JSONDecodeError, Exception) as exc:
            logger.error("인증 처리 오류: %s", exc)
            await websocket.close()
            return False

    async def _route_message(
        self, websocket: websockets.WebSocketServerProtocol, raw: str
    ) -> None:
        """수신된 메시지를 타입에 따라 라우팅한다."""
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            await self._send(websocket, ResponseType.ERROR, {"error": "잘못된 JSON 형식"})
            return

        msg_type = msg.get("type")

        if msg_type == MessageType.HEARTBEAT.value:
            await self._handle_heartbeat(websocket)
        elif msg_type == MessageType.STATUS_REQUEST.value:
            await self._handle_status_request(websocket)
        elif msg_type == MessageType.MESSAGE.value:
            await self._handle_message(websocket, msg)
        else:
            await self._send(websocket, ResponseType.ERROR, {"error": f"알 수 없는 메시지 타입: {msg_type}"})

    async def _handle_heartbeat(
        self, websocket: websockets.WebSocketServerProtocol
    ) -> None:
        """heartbeat 메시지에 응답한다 (Req 1.2)."""
        await self._send(websocket, ResponseType.HEARTBEAT, {})

    async def _handle_status_request(
        self, websocket: websockets.WebSocketServerProtocol
    ) -> None:
        """상태 요청에 BridgeStatus를 반환한다 (Req 5.2)."""
        status = BridgeStatus(
            kiro_running=self._automation.is_kiro_running(),
            connected_clients=len(self._authenticated),
            uptime=time.time() - self._start_time,
        )
        await self._send(
            websocket,
            ResponseType.STATUS,
            {
                "status": {
                    "kiro_running": status.kiro_running,
                    "connected_clients": status.connected_clients,
                    "uptime": status.uptime,
                }
            },
        )

    async def _handle_message(
        self, websocket: websockets.WebSocketServerProtocol, msg: dict
    ) -> None:
        """메시지를 Kiro IDE에 전달하고 응답을 반환한다 (Req 2.1, 2.4)."""
        content = msg.get("payload", {}).get("content", "")
        if not content:
            await self._send(websocket, ResponseType.ERROR, {"error": "메시지 내용이 비어있습니다"})
            return

        # Kiro IDE에 메시지 전송
        success = self._automation.send_message(content)
        if not success:
            await self._send(websocket, ResponseType.ERROR, {"error": "Kiro IDE에 메시지 전송 실패"})
            return

        # 전송 완료 확인 (Req 2.4)
        await self._send(websocket, ResponseType.MESSAGE_ACK, {"success": True})

        # Kiro 응답 대기 및 전달
        try:
            response_text = await self._monitor.wait_for_response()
            await self._send(
                websocket,
                ResponseType.KIRO_RESPONSE,
                {"content": response_text},
            )
        except (TimeoutError, RuntimeError) as exc:
            error_msg = self._monitor.create_error_message(str(exc))
            await self._send(
                websocket,
                error_msg.type,
                error_msg.payload,
            )

    async def _heartbeat_loop(
        self, websocket: websockets.WebSocketServerProtocol
    ) -> None:
        """주기적으로 heartbeat를 전송한다 (Req 1.2)."""
        try:
            while True:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                await self._send(websocket, ResponseType.HEARTBEAT, {})
        except (asyncio.CancelledError, websockets.ConnectionClosed):
            pass

    async def _send(
        self,
        websocket: websockets.WebSocketServerProtocol,
        response_type: ResponseType,
        payload: dict,
    ) -> None:
        """ServerMessage를 JSON으로 직렬화하여 전송한다."""
        message = ServerMessage(
            type=response_type,
            payload=payload,
            timestamp=time.time(),
        )
        data = json.dumps({
            "type": message.type.value,
            "payload": message.payload,
            "timestamp": message.timestamp,
        })
        try:
            await websocket.send(data)
        except websockets.ConnectionClosed:
            pass

    def _log_status(self) -> None:
        """현재 연결 상태를 콘솔에 출력한다 (Req 5.2)."""
        total = len(self._clients)
        authed = len(self._authenticated)
        msg = f"[Bridge] 연결 상태 — 전체: {total}, 인증됨: {authed}"
        logger.info(msg)
        print(msg)
