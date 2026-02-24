/**
 * AsyncStorage 기반 저장소 서비스
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { Message, AppConfig } from '../types';

const KEYS = {
  AUTH_TOKEN: '@okxus/auth_token',
  BRIDGE_URL: '@okxus/bridge_url',
  CHAT_HISTORY: '@okxus/chat_history',
  SETTINGS: '@okxus/settings',
} as const;

const DEFAULT_CONFIG: AppConfig = {
  bridgeUrl: '',
  authToken: '',
  reconnectAttempts: 3,
  heartbeatInterval: 30000,
};

export const storage = {
  /** 인증 토큰 저장/로드 */
  async saveToken(token: string): Promise<void> {
    await AsyncStorage.setItem(KEYS.AUTH_TOKEN, token);
  },
  async loadToken(): Promise<string> {
    return (await AsyncStorage.getItem(KEYS.AUTH_TOKEN)) ?? '';
  },

  /** Bridge URL 저장/로드 */
  async saveUrl(url: string): Promise<void> {
    await AsyncStorage.setItem(KEYS.BRIDGE_URL, url);
  },
  async loadUrl(): Promise<string> {
    return (await AsyncStorage.getItem(KEYS.BRIDGE_URL)) ?? '';
  },

  /** 대화 기록 저장/로드 */
  async saveMessages(messages: Message[]): Promise<void> {
    await AsyncStorage.setItem(KEYS.CHAT_HISTORY, JSON.stringify(messages));
  },
  async loadMessages(): Promise<Message[]> {
    const raw = await AsyncStorage.getItem(KEYS.CHAT_HISTORY);
    if (!raw) return [];
    try {
      return JSON.parse(raw);
    } catch {
      return [];
    }
  },

  /** 앱 설정 저장/로드 */
  async saveConfig(config: AppConfig): Promise<void> {
    await AsyncStorage.setItem(KEYS.SETTINGS, JSON.stringify(config));
  },
  async loadConfig(): Promise<AppConfig> {
    const raw = await AsyncStorage.getItem(KEYS.SETTINGS);
    if (!raw) return DEFAULT_CONFIG;
    try {
      return { ...DEFAULT_CONFIG, ...JSON.parse(raw) };
    } catch {
      return DEFAULT_CONFIG;
    }
  },

  /** 전체 초기화 */
  async clear(): Promise<void> {
    await AsyncStorage.multiRemove(Object.values(KEYS));
  },
};
