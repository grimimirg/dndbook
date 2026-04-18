import { createI18n } from 'vue-i18n';
import { getAvailableLocales } from './config/locales';

const localeModules = import.meta.glob('./locales/*.yaml', { eager: true });

function loadMessages() {
  const availableLocales = getAvailableLocales();
  const messages = {};

  for (const locale of availableLocales) {
    const modulePath = `./locales/${locale}.yaml`;
    if (localeModules[modulePath]) {
      messages[locale] = localeModules[modulePath].default;
    } else {
      console.warn(`Locale file not found: ${modulePath}`);
    }
  }

  return messages;
}

export function createI18nInstance() {
  const messages = loadMessages();
  const availableLocales = getAvailableLocales();
  const savedLocale = localStorage.getItem('locale') || availableLocales[0] || 'en';

  return createI18n({
    legacy: false,
    locale: savedLocale,
    fallbackLocale: availableLocales[0] || 'en',
    messages
  });
}
