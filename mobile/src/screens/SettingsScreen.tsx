/**
 * 설정 화면 - Bridge URL, 인증 토큰 설정
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { storage } from '../services/storage';
import { wsService } from '../services/websocket';
import { colors, fonts, spacing, borderRadius } from '../styles/theme';

interface Props {
  onBack: () => void;
}

export const SettingsScreen: React.FC<Props> = ({ onBack }) => {
  const [url, setUrl] = useState('');
  const [token, setToken] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      setUrl(await storage.loadUrl());
      setToken(await storage.loadToken());
    })();
  }, []);

  const handleSave = async () => {
    if (!url.trim() || !token.trim()) {
      Alert.alert('입력 오류', 'URL과 토큰을 모두 입력해주세요.');
      return;
    }
    setSaving(true);
    try {
      await storage.saveUrl(url.trim());
      await storage.saveToken(token.trim());

      // 기존 연결 해제 후 재연결
      wsService.disconnect();
      await wsService.connect(url.trim(), token.trim());
      Alert.alert('성공', '연결 설정이 저장되었습니다.');
      onBack();
    } catch (e: any) {
      Alert.alert('연결 실패', e.message || '서버에 연결할 수 없습니다.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} accessibilityLabel="뒤로" accessibilityRole="button">
          <Text style={styles.backBtn}>← 뒤로</Text>
        </TouchableOpacity>
        <Text style={styles.title}>설정</Text>
        <View style={{ width: 60 }} />
      </View>

      <View style={styles.form}>
        <Text style={styles.label}>Bridge URL</Text>
        <TextInput
          style={styles.input}
          value={url}
          onChangeText={setUrl}
          placeholder="ws://192.168.0.10:8765 또는 wss://xxx.ngrok.io"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          autoCorrect={false}
        />

        <Text style={styles.label}>인증 토큰</Text>
        <TextInput
          style={styles.input}
          value={token}
          onChangeText={setToken}
          placeholder="Bridge config.json의 auth_token"
          placeholderTextColor={colors.textMuted}
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
        />

        <TouchableOpacity
          style={[styles.saveBtn, saving && styles.saveBtnDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveBtnText}>
            {saving ? '연결 중...' : '저장 및 연결'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backBtn: {
    color: colors.neonCyan,
    fontSize: 16,
  },
  title: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: 'bold',
  },
  form: {
    padding: spacing.xl,
  },
  label: {
    color: colors.textSecondary,
    fontFamily: fonts.mono,
    fontSize: 13,
    marginBottom: spacing.xs,
    marginTop: spacing.lg,
  },
  input: {
    fontFamily: fonts.mono,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  saveBtn: {
    marginTop: spacing.xl,
    paddingVertical: spacing.md,
    backgroundColor: colors.neonCyan,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  saveBtnDisabled: {
    opacity: 0.5,
  },
  saveBtnText: {
    color: colors.background,
    fontSize: 16,
    fontWeight: 'bold',
  },
});
