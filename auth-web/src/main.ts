import 'core-js/stable' // to polyfill ECMAScript features
import '@mdi/font/css/materialdesignicons.min.css' // icon library (https://materialdesignicons.com/)
import 'regenerator-runtime/runtime' // to use transpiled generator functions
import './registerServiceWorker'
import App from './App.vue'
import ConfigHelper from '@/util/config-helper'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import TokenService from 'sbc-common-components/src/services/token.services'
import Vue from 'vue'
import can from '@/directives/can'
import { getRoutes } from './routes/router'
import i18n from './plugins/i18n'
import router from './routes/index'
import store from './store'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false
Vue.prototype.$tokenService = new TokenService()

/**
 * The server side configs are necessary for app to work , since they are reference in templates and all
 *  Two ways , either reload Vue after we get the settings or load vue after we get the configs..going for second
 */
ConfigHelper.saveConfigToSessionStorage().then(async (data) => {
  // Initializing Launch Darkly services
  await LaunchDarklyService.init(ConfigHelper.getValue('LAUNCH_DARKLY_ENV_KEY'))
  await syncSession()
  renderVue()
}
)

async function syncSession () {
  await KeyCloakService.setKeycloakConfigUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`)

  // Initialize token service which will do a check-sso to initiate session
  let path = window.location.pathname
  let isSigningIn = path.includes('/signin') || path.includes('/signin-redirect') || path.includes('/signin-redirect-full')
  if (!isSigningIn) {
    debugger
    await Vue.prototype.$tokenService.init(null).catch(err => {
      if (err.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }
}

function renderVue () {
  new Vue({
    router,
    store,
    vuetify,
    i18n,
    render: (h) => h(App)
  }).$mount('#app')
  Vue.directive('can', can)
  router.addRoutes(getRoutes())
}
