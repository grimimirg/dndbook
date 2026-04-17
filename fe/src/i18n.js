import { createI18n } from 'vue-i18n'
import yaml from 'js-yaml'

async function loadLocaleMessages() {
  const locales = ['en', 'it', 'de']
  const messages = {}

  for (const locale of locales) {
    const response = await fetch(`/src/locales/${locale}.yaml`)
    const yamlText = await response.text()
    messages[locale] = yaml.load(yamlText)
  }

  return messages
}

export async function createI18nInstance() {
  const messages = await loadLocaleMessages()
  const savedLocale = localStorage.getItem('locale') || 'en'

  return createI18n({
    legacy: false,
    locale: savedLocale,
    fallbackLocale: 'en',
    messages
  })
}
