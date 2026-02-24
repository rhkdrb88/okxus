/**
 * Kiro 응답 대기 로딩 인디케이터
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, Animated, StyleSheet } from 'react-native';
import { colors, fonts, spacing } from '../styles/theme';

export const LoadingIndicator: React.FC = () => {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const anim = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 600, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.3, duration: 600, useNativeDriver: true }),
      ]),
    );
    anim.start();
    return () => anim.stop();
  }, [opacity]);

  return (
    <View style={styles.container}>
      <Animated.Text style={[styles.text, { opacity }]}>
        Kiro 응답 중...
      </Animated.Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
  },
  text: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.neonGreen,
  },
});
