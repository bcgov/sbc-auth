import { castToVueI18n, createI18n } from 'vue-i18n-bridge'
import Vue from 'vue'
import VueI18n from 'vue-i18n'

export default {
  mock () {
    Vue.use(VueI18n, { bridge: true })

    const i18n = castToVueI18n(createI18n({
      legacy: false,
      locale: 'en',
      fallbackLocale: 'en',
      messages: {
        en: {
          msg: 'Test Message'
        }
      }
    }, VueI18n))

    return i18n
  }
}
