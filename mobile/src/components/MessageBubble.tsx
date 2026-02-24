/**
 * 메시지 버블 컴포넌트
 * - 사용자: 네온 핑크 (#ff6ec7), 오른쪽 정렬
 * - Kiro: 네온 그린 (#39ff14), 왼쪽 정렬
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Message } from '../types';
import { colors, fonts, spacing, borderRadius } from '../styles/theme';

interface Props {
  message: Message;
}

export const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <View style={[styles.row, isUser ? styles.rowRight : styles.rowLeft]}>
      <View
        style={[
          styles.bubble,
          isUser ? styles.userBubble : styles.kiroBubble,
        ]}
      >
        <Text
          style={[
            styles.text,
            isUser ? styles.userText : styles.kiroText,
          ]}
        >
          {message.content}
        </Text>
        {message.status === 'error' && (
          <Text style={styles.errorHint}>전송 실패</Text>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  row: {
    marginVertical: spacing.xs,
    marginHorizontal: spacing.md,
  },
  rowRight: { alignItems: 'flex-end' },
  rowLeft: { alignItems: 'flex-start' },
  bubble: {
    maxWidth: '80%',
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.lg,
  },
  userBubble: {
    backgroundColor: 'rgba(255,110,199,0.15)',
    borderWidth: 1,
    borderColor: colors.neonPink,
  },
  kiroBubble: {
    backgroundColor: 'rgba(57,255,20,0.10)',
    borderWidth: 1,
    borderColor: colors.neonGreen,
  },
  text: {
    fontFamily: fonts.mono,
    fontSize: 14,
    lineHeight: 20,
  },
  userText: { color: colors.neonPink },
  kiroText: { color: colors.neonGreen },
  errorHint: {
    color: colors.neonRed,
    fontSize: 11,
    marginTop: spacing.xs,
  },
});
