/**
 * OKXUS Mobile App - WebSocket Message Type Definitions
 */

/** 클라이언트 → 서버 메시지 */
export interface ClientMessage {
  type: 'auth' | 'message' | 'status_request' | 'heartbeat';
  payload: {
    token?: string;
    content?: string;
  };
  timestamp: number;
}

/** 서버 → 클라이언트 메시지 */
export interface ServerMessage {
  type:
    | 'auth_result'
    | 'message_ack'
    | 'kiro_response'
    | 'status'
    | 'error'
    | 'heartbeat';
  payload: {
    success?: boolean;
    content?: string;
    status?: BridgeStatus;
    error?: string;
  };
  timestamp: number;
}

/** Bridge 상태 정보 */
export interface BridgeStatus {
  kiro_running: boolean;
  connected_clients: number;
  uptime: number;
}

/** 오류 코드 */
export enum ErrorCode {
  AUTH_FAILED = 'AUTH_FAILED',
  KIRO_NOT_RUNNING = 'KIRO_NOT_RUNNING',
  CLIPBOARD_ERROR = 'CLIPBOARD_ERROR',
  WINDOW_ERROR = 'WINDOW_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN',
}
