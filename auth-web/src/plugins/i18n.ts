import VueI18n, { LocaleMessages } from 'vue-i18n'
import { createI18n } from 'vue-i18n-composable'
import enLocals from '@/locales/en.json'

export default function initialize (vue) {
  vue.use(VueI18n)

  function loadLocaleMessages (): LocaleMessages {
    const messages: LocaleMessages = { en: {} }
    Object.keys(enLocals).forEach((key) => {
      messages['en'][key] = enLocals[key]
    })
    return messages
  }

  const i18n = createI18n({
    locale: import.meta.env.VUE_APP_I18N_LOCALE || 'en',
    fallbackLocale: import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
    messages: loadLocaleMessages()
  })
  return i18n
}
