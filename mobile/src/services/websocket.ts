/**
 * WebSocket 서비스 - Bridge 서버와의 통신 담당
 */

import { ConnectionStatus } from '../types';
import { ClientMessage, ServerMessage } from '../types/message';

export type MessageCallback = (message: ServerMessage) => void;
export type StatusCallback = (status: ConnectionStatus) => void;

const MAX_RECONNECT_ATTEMPTS = 3;
const HEARTBEAT_INTERVAL = 30_000; // 30초
const RECONNECT_DELAY = 2_000; // 2초

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url = '';
  private token = '';
  private status: ConnectionStatus = 'disconnected';
  private reconnectCount = 0;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private messageCallbacks: MessageCallback[] = [];
  private statusCallbacks: StatusCallback[] = [];

  /** 현재 연결 상태 */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /** Bridge 서버에 연결 (Req 1.1, 6.4) */
  async connect(url: string, token: string): Promise<void> {
    this.url = url;
    this.token = token;
    this.reconnectCount = 0;
    await this._connect();
  }

  /** 연결 해제 */
  disconnect(): void {
    this._clearHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this._setStatus('disconnected');
  }

  /** 메시지 전송 (Req 2.1) */
  sendMessage(content: string): void {
    if (!this.ws || this.status !== 'connected') return;
    const msg: ClientMessage = {
      type: 'message',
      payload: { content },
      timestamp: Date.now(),
    };
    this.ws.send(JSON.stringify(msg));
  }

  /** 상태 요청 */
  requestStatus(): void {
    if (!this.ws || this.status !== 'connected') return;
    const msg: ClientMessage = {
      type: 'status_request',
      payload: {},
      timestamp: Date.now(),
    };
    this.ws.send(JSON.stringify(msg));
  }

  /** 메시지 수신 콜백 등록 */
  onMessage(callback: MessageCallback): () => void {
    this.messageCallbacks.push(callback);
    return () => {
      this.messageCallbacks = this.messageCallbacks.filter(cb => cb !== callback);
    };
  }

  /** 연결 상태 변경 콜백 등록 */
  onStatusChange(callback: StatusCallback): () => void {
    this.statusCallbacks.push(callback);
    return () => {
      this.statusCallbacks = this.statusCallbacks.filter(cb => cb !== callback);
    };
  }

  // ── Internal ──────────────────────────────────────────

  private async _connect(): Promise<void> {
    this._setStatus('connecting');

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
      } catch {
        this._handleDisconnect();
        reject(new Error('WebSocket 생성 실패'));
        return;
      }

      this.ws.onopen = () => {
        // 인증 메시지 전송 (Req 6.1)
        const authMsg: ClientMessage = {
          type: 'auth',
          payload: { token: this.token },
          timestamp: Date.now(),
        };
        this.ws!.send(JSON.stringify(authMsg));
      };

      this.ws.onmessage = (event) => {
        try {
          const msg: ServerMessage = JSON.parse(event.data as string);
          if (msg.type === 'auth_result') {
            if (msg.payload.success) {
              this._setStatus('connected');
              this.reconnectCount = 0;
              this._startHeartbeat();
              resolve();
            } else {
              this._setStatus('error');
              reject(new Error(msg.payload.error || '인증 실패'));
            }
            return;
          }
          // heartbeat는 무시
          if (msg.type === 'heartbeat') return;
          // 나머지 메시지 콜백 전달
          this.messageCallbacks.forEach(cb => cb(msg));
        } catch {
          // JSON 파싱 실패 무시
        }
      };

      this.ws.onclose = () => {
        this._clearHeartbeat();
        if (this.status === 'connected' || this.status === 'connecting') {
          this._handleDisconnect();
        }
      };

      this.ws.onerror = () => {
        // onclose에서 처리
      };
    });
  }

  /** 재연결 로직 (Req 1.3, 1.4) */
  private _handleDisconnect(): void {
    this._clearHeartbeat();
    if (this.reconnectCount < MAX_RECONNECT_ATTEMPTS) {
      this.reconnectCount++;
      this._setStatus('reconnecting');
      setTimeout(() => this._connect().catch(() => {}), RECONNECT_DELAY);
    } else {
      this._setStatus('error');
    }
  }

  private _startHeartbeat(): void {
    this._clearHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.status === 'connected') {
        const msg: ClientMessage = {
          type: 'heartbeat',
          payload: {},
          timestamp: Date.now(),
        };
        this.ws.send(JSON.stringify(msg));
      }
    }, HEARTBEAT_INTERVAL);
  }

  private _clearHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private _setStatus(status: ConnectionStatus): void {
    this.status = status;
    this.statusCallbacks.forEach(cb => cb(status));
  }
}

/** 싱글톤 인스턴스 */
export const wsService = new WebSocketService();
