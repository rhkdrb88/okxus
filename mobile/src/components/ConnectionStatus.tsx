/**
 * 연결 상태 표시 컴포넌트
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ConnectionStatus as Status } from '../types';
import { colors, fonts, spacing, borderRadius } from '../styles/theme';

interface Props {
  status: Status;
}

const STATUS_CONFIG: Record<Status, { label: string; color: string }> = {
  connected: { label: '연결됨', color: colors.neonGreen },
  connecting: { label: '연결 중...', color: colors.neonCyan },
  disconnected: { label: '연결 끊김', color: colors.textMuted },
  reconnecting: { label: '재연결 중...', color: colors.neonYellow },
  error: { label: '연결 실패', color: colors.neonRed },
};

export const ConnectionStatusBar: React.FC<Props> = ({ status }) => {
  const config = STATUS_CONFIG[status];

  return (
    <View style={styles.container}>
      <View style={[styles.dot, { backgroundColor: config.color }]} />
      <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    backgroundColor: colors.surface,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: borderRadius.full,
    marginRight: spacing.sm,
  },
  label: {
    fontFamily: fonts.mono,
    fontSize: 12,
  },
});
