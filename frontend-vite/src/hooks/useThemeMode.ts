import { useState, useMemo } from 'react';
import grafanaTheme from '../theme/theme';

export default function useThemeMode() {
  const [mode, setMode] = useState<'light' | 'dark'>('light');

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = useMemo(() => grafanaTheme(mode), [mode]);

  return { theme, mode, toggleColorMode };
}
