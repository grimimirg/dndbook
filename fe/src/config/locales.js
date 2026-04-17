/**
 * Mapping of locale codes to their display names
 * Add new languages here when creating new locale files
 */
export const LOCALE_NAMES = {
  en: 'English',
  it: 'Italiano',
  de: 'Deutsch',
  es: 'Español',
  fr: 'Français'
}

/**
 * Gets the list of available locales from environment variable
 * Configured in .env via VITE_AVAILABLE_LOCALES
 */
export function getAvailableLocales() {
  const localesEnv = import.meta.env.VITE_AVAILABLE_LOCALES || 'en,it,de'
  return localesEnv.split(',').map(locale => locale.trim())
}

/**
 * Gets the display name for a locale code
 * Falls back to uppercase locale code if not found in LOCALE_NAMES
 */
export function getLocaleName(localeCode) {
  return LOCALE_NAMES[localeCode] || localeCode.toUpperCase()
}
