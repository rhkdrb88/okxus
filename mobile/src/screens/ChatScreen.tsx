/**
 * 메인 대화 화면 - Kiro IDE 스타일
 */
import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  View, FlatList, StyleSheet, KeyboardAvoidingView,
  Platform, TouchableOpacity, Text, Keyboard,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Message, ConnectionStatus } from '../types';
import { ServerMessage } from '../types/message';
import { MessageBubble } from '../components/MessageBubble';
import { InputBar } from '../components/InputBar';
import { ConnectionStatusBar } from '../components/ConnectionStatus';
import { LoadingIndicator } from '../components/LoadingIndicator';
import { wsService } from '../services/websocket';
import { storage } from '../services/storage';
import { colors, spacing } from '../styles/theme';

interface Props { onOpenSettings: () => void; }

export const ChatScreen: React.FC<Props> = ({ onOpenSettings }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [isKiroResponding, setIsKiroResponding] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);
  const listRef = useRef<FlatList>(null);

  useEffect(() => {
    (async () => {
      const saved = await storage.loadMessages();
      if (saved.length) setMessages(saved);
      const url = await storage.loadUrl();
      const token = await storage.loadToken();
      if (url && token) {
        try { await wsService.connect(url, token); } catch { /* noop */ }
      }
    })();
  }, []);

  useEffect(() => {
    const unsubStatus = wsService.onStatusChange(setStatus);
    const unsubMsg = wsService.onMessage((msg: ServerMessage) => {
      if (msg.type === 'kiro_response' && msg.payload.content) {
        const kiroMsg: Message = {
          id: `kiro-${Date.now()}`, content: msg.payload.content,
          sender: 'kiro', timestamp: new Date(), status: 'delivered',
        };
        setMessages(prev => { const next = [...prev, kiroMsg]; storage.saveMessages(next); return next; });
        setIsKiroResponding(false);
        const t = msg.payload.content.toLowerCase();
        if (t.includes('승인') || t.includes('approve') || t.includes('confirm')) setPendingApproval(true);
      }
      if (msg.type === 'message_ack') {
        setMessages(prev => prev.map(m => (m.status === 'sending' ? { ...m, status: 'sent' } : m)));
        setIsKiroResponding(true);
      }
      if (msg.type === 'error') setIsKiroResponding(false);
    });
    return () => { unsubStatus(); unsubMsg(); };
  }, []);

  const handleSend = useCallback((text: string) => {
    const userMsg: Message = {
      id: `user-${Date.now()}`, content: text,
      sender: 'user', timestamp: new Date(), status: 'sending',
    };
    setMessages(prev => { const next = [...prev, userMsg]; storage.saveMessages(next); return next; });
    setPendingApproval(false);
    wsService.sendMessage(text);
  }, []);

  const handleApprove = useCallback(() => { handleSend('승인'); setPendingApproval(false); }, [handleSend]);

  const scrollToEnd = useCallback(() => {
    setTimeout(() => listRef.current?.scrollToEnd({ animated: true }), 100);
  }, []);
  useEffect(() => { scrollToEnd(); }, [messages, scrollToEnd]);

  // 키보드 올라올 때 스크롤
  useEffect(() => {
    const showSub = Keyboard.addListener('keyboardDidShow', () => scrollToEnd());
    return () => showSub.remove();
  }, [scrollToEnd]);

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      <View style={styles.header}>
        <Text style={styles.title}>OKXUS</Text>
        <TouchableOpacity onPress={onOpenSettings} accessibilityLabel="설정" accessibilityRole="button">
          <Text style={styles.settingsBtn}>⚙</Text>
        </TouchableOpacity>
      </View>
      <ConnectionStatusBar status={status} />
      <KeyboardAvoidingView style={styles.flex1} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <FlatList ref={listRef} data={messages} keyExtractor={item => item.id}
          renderItem={({ item }) => <MessageBubble message={item} />}
          style={styles.flex1} contentContainerStyle={styles.listContent}
          onContentSizeChange={scrollToEnd} />
        {isKiroResponding && <LoadingIndicator />}
        {pendingApproval && (
          <TouchableOpacity style={styles.approveBtn} onPress={handleApprove}>
            <Text style={styles.approveBtnText}>✓ 승인</Text>
          </TouchableOpacity>
        )}
        <InputBar onSend={handleSend} disabled={status !== 'connected'} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: spacing.lg, paddingVertical: spacing.md,
    backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  title: { color: colors.neonYellow, fontSize: 18, fontWeight: 'bold', letterSpacing: 2 },
  settingsBtn: { fontSize: 22, color: colors.textSecondary },
  flex1: { flex: 1 },
  listContent: { paddingVertical: spacing.sm },
  approveBtn: {
    marginHorizontal: spacing.lg, marginBottom: spacing.sm, paddingVertical: spacing.md,
    backgroundColor: 'rgba(0,255,255,0.15)', borderWidth: 1, borderColor: colors.neonCyan,
    borderRadius: 8, alignItems: 'center',
  },
  approveBtnText: { color: colors.neonCyan, fontSize: 16, fontWeight: 'bold' },
});
