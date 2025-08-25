import { useState, useMemo } from 'react';
import grafanaTheme from '../theme.js'; // ✅ import correto do export default

export default function useThemeMode() {
  const [mode, setMode] = useState('light');

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = useMemo(() => grafanaTheme(mode), [mode]);

  return { theme, mode, toggleColorMode };
}
