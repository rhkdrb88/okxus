/**
 * OKXUS 앱 테마 - Kiro IDE 스타일 (블랙 배경 + 네온 컬러)
 */

export const colors = {
  /** 메인 배경 */
  background: '#0d1117',
  /** 약간 밝은 배경 (카드, 입력창) */
  surface: '#161b22',
  /** 테두리 */
  border: '#30363d',

  /** Kiro 응답 - 네온 그린 */
  neonGreen: '#39ff14',
  /** 전송 버튼 - 네온 시안 */
  neonCyan: '#00ffff',
  /** 사용자 메시지 - 네온 핑크 */
  neonPink: '#ff6ec7',
  /** 경고/오류 - 네온 레드 */
  neonRed: '#ff3131',
  /** 앱 아이콘/타이틀 - 노란 형광 */
  neonYellow: '#ccff00',

  /** 텍스트 */
  textPrimary: '#e6edf3',
  textSecondary: '#8b949e',
  textMuted: '#484f58',
} as const;

export const fonts = {
  mono: 'JetBrainsMono',
  monoRegular: 'JetBrainsMono-Regular',
  monoBold: 'JetBrainsMono-Bold',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
} as const;

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;
