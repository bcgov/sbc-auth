import './composition-api-setup' // ensure this happens before any imports trigger use of composition-api
import '@mdi/font/css/materialdesignicons.min.css' // icon library (https://materialdesignicons.com/)
import { PiniaVuePlugin, createPinia, setActivePinia } from 'pinia'
import App from './App.vue'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
// eslint-disable-next-line sort-imports
import './routes/componentHooks'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import VueGtag from 'vue-gtag'
import VueSanitize from 'vue-sanitize-directive'
import Vuelidate from 'vuelidate'
import can from '@/directives/can'
import displayMode from '@/directives/displayMode'
import initializeI18n from './plugins/i18n'
import router from './routes/index'
import vuetify from './plugins/vuetify'

Vue.use(VueCompositionAPI)
Vue.use(PiniaVuePlugin)
const pinia = createPinia()
setActivePinia(pinia)
Vue.config.productionTip = false
Vue.use(Vuelidate)
Vue.use(VueSanitize)

const i18n = initializeI18n(Vue)

if (import.meta.env.VUE_APP_GTAG_ID?.trim()) {
  Vue.use(VueGtag, {
    config: {
      id: import.meta.env.VUE_APP_GTAG_ID
    }
  }, router)
}

/**
 * The server side configs are necessary for app to work , since they are reference in templates and all
 *  Two ways , either reload Vue after we get the settings or load vue after we get the configs..going for second
 */
ConfigHelper.saveConfigToSessionStorage().then(async () => {
  // Initializing Launch Darkly services
  await LaunchDarklyService.init(ConfigHelper.getLdClientId());
  // addressCompleteKey is for canada post address lookup, which is to be used in sbc-common-components
  (<any>window).addressCompleteKey = ConfigHelper.getAddressCompleteKey()

  await syncSession()
  renderVue()
})

async function syncSession () {
  const keycloakConfig: any = {
    url: `${ConfigHelper.getKeycloakAuthUrl()}`,
    realm: `${ConfigHelper.getKeycloakRealm()}`,
    clientId: `${ConfigHelper.getKeycloakClientId()}`
  }

  await KeyCloakService.setKeycloakConfigUrl(keycloakConfig)

  // Initialize token service which will do a check-sso to initiate session
  if (!CommonUtils.isSigningIn() && !CommonUtils.isSigningOut()) {
    await KeyCloakService.initializeToken(null).then(() => {}).catch(err => {
      if (err?.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }
}
function renderVue () {
  new Vue({
    pinia,
    router,
    vuetify,
    i18n,
    render: (h) => h(App)
  }).$mount('#app')
  Vue.directive('can', can)
  Vue.directive('displayMode', displayMode)
}
