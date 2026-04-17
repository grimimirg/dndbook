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

const savedLocale = localStorage.getItem('locale') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: {}
})

loadLocaleMessages().then(messages => {
  Object.keys(messages).forEach(locale => {
    i18n.global.setLocaleMessage(locale, messages[locale])
  })
})

export default i18n
