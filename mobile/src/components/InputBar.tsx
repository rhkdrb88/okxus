/**
 * 하단 고정 입력창 + 전송 버튼
 */

import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { colors, fonts, spacing, borderRadius } from '../styles/theme';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export const InputBar: React.FC<Props> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        value={text}
        onChangeText={setText}
        placeholder="메시지 입력..."
        placeholderTextColor={colors.textMuted}
        multiline
        maxLength={4000}
        editable={!disabled}
        onSubmitEditing={handleSend}
        blurOnSubmit={false}
      />
      <TouchableOpacity
        style={[styles.sendBtn, (!text.trim() || disabled) && styles.sendBtnDisabled]}
        onPress={handleSend}
        disabled={!text.trim() || disabled}
        accessibilityLabel="전송"
        accessibilityRole="button"
      >
        <Text style={styles.sendText}>▶</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  input: {
    flex: 1,
    fontFamily: fonts.mono,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.background,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    maxHeight: 100,
  },
  sendBtn: {
    marginLeft: spacing.sm,
    width: 44,
    height: 44,
    borderRadius: borderRadius.full,
    backgroundColor: colors.neonCyan,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: {
    opacity: 0.3,
  },
  sendText: {
    fontSize: 18,
    color: colors.background,
  },
});
