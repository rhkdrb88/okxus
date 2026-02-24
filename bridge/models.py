from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """클라이언트 → 서버 메시지 타입"""
    AUTH = "auth"
    MESSAGE = "message"
    STATUS_REQUEST = "status_request"
    HEARTBEAT = "heartbeat"


class ResponseType(Enum):
    """서버 → 클라이언트 응답 타입"""
    AUTH_RESULT = "auth_result"
    MESSAGE_ACK = "message_ack"
    KIRO_RESPONSE = "kiro_response"
    STATUS = "status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class ClientMessage:
    """클라이언트에서 서버로 전송되는 메시지"""
    type: MessageType
    payload: dict
    timestamp: float


@dataclass
class ServerMessage:
    """서버에서 클라이언트로 전송되는 메시지"""
    type: ResponseType
    payload: dict
    timestamp: float


@dataclass
class BridgeStatus:
    """브릿지 상태 정보"""
    kiro_running: bool
    connected_clients: int
    uptime: float
