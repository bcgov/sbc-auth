import VueI18n, { LocaleMessages } from 'vue-i18n'
import { castToVueI18n, createI18n } from 'vue-i18n-bridge'
import Vue from 'vue'
import enLocals from '@/locales/en.json'
Vue.use(VueI18n, { bridge: true, legacy: false })

function loadLocaleMessages (): LocaleMessages {
  const locales = enLocals
  const messages: LocaleMessages = {}
  Object.keys(locales).forEach((key) => {
    const matched = key.match(/([A-Za-z0-9-_]+)\./i)
    if (matched?.length > 1) {
      const locale = matched[1]
      messages[locale] = locales[key]
    }
  })
  return messages
}

const i18n = castToVueI18n(createI18n({
  legacy: false,
  warnHtmlMessage: false,
  locale: import.meta.env.VUE_APP_I18N_LOCALE || 'en',
  fallbackLocale: import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE || 'en',
  globalInjection: true,
  messages: loadLocaleMessages()
}, VueI18n))

export default i18n
