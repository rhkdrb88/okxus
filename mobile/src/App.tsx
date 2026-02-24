/**
 * OKXUS Mobile App - 메인 엔트리포인트
 */

import React, { useState } from 'react';
import { StatusBar } from 'react-native';
import { ChatScreen } from './screens/ChatScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { colors } from './styles/theme';

type Screen = 'chat' | 'settings';

const App: React.FC = () => {
  const [screen, setScreen] = useState<Screen>('chat');

  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor={colors.surface} />
      {screen === 'chat' ? (
        <ChatScreen onOpenSettings={() => setScreen('settings')} />
      ) : (
        <SettingsScreen onBack={() => setScreen('chat')} />
      )}
    </>
  );
};

export default App;
