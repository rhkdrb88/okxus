/**
 * OKXUS Mobile App - Core Type Definitions
 */

/** 메시지 전송/수신 상태 */
export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'error';

/** WebSocket 연결 상태 */
export type ConnectionStatus =
  | 'connected'
  | 'connecting'
  | 'disconnected'
  | 'reconnecting'
  | 'error';

/** 대화 메시지 */
export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'kiro';
  timestamp: Date;
  status: MessageStatus;
}

/** 앱 설정 */
export interface AppConfig {
  bridgeUrl: string;
  authToken: string;
  reconnectAttempts: number;
  heartbeatInterval: number;
}

/** 대화 세션 상태 */
export interface ChatSession {
  messages: Message[];
  connectionStatus: ConnectionStatus;
  isKiroResponding: boolean;
}
