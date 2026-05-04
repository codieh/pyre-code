'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { type Locale, type TranslationKey, translate, getProblemTitle } from '@/lib/i18n';

interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: TranslationKey, params?: Record<string, string | number>) => string;
  tProblem: (id: string) => string;
}

const LocaleContext = createContext<LocaleContextValue>({
  locale: 'en',
  setLocale: () => {},
  t: (key) => key,
  tProblem: (id) => id,
});

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en');

  useEffect(() => {
    const saved = localStorage.getItem('locale') as Locale | null;
    if (saved === 'en' || saved === 'zh') setLocaleState(saved);
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem('locale', l);
  };

  const t = (key: TranslationKey, params?: Record<string, string | number>) =>
    translate(locale, key, params);

  const tProblem = (id: string) => getProblemTitle(id, locale);

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t, tProblem }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocale() {
  return useContext(LocaleContext);
}
