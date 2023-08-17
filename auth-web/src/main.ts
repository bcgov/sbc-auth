import './composition-api-setup' // ensure this happens before any imports trigger use of composition-api
import '@mdi/font/css/materialdesignicons.min.css' // icon library (https://materialdesignicons.com/)
import * as Sentry from '@sentry/vue'
import App from './App.vue'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import Hotjar from 'vue-hotjar'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
// eslint-disable-next-line sort-imports
import './routes/componentHooks'
import Vue from 'vue'
import VueSanitize from 'vue-sanitize-directive'
import Vuelidate from 'vuelidate'
import can from '@/directives/can'
import displayMode from '@/directives/displayMode'
import i18n from './plugins/i18n'
import router from './routes/index'
import store from './store'
import vuetify from './plugins/vuetify'

// eslint-disable-next-line sort-imports
import Search from 'fas-ui'
// eslint-disable-next-line sort-imports
import { LDFlags } from '@/util/constants'

Vue.config.productionTip = false
Vue.use(Vuelidate)
Vue.use(Search, { store, i18n })
Vue.use(VueSanitize)

/**
 * The server side configs are necessary for app to work , since they are reference in templates and all
 *  Two ways , either reload Vue after we get the settings or load vue after we get the configs..going for second
 */
ConfigHelper.saveConfigToSessionStorage().then(async () => {
  // Initializing Launch Darkly services
  await LaunchDarklyService.init(ConfigHelper.getLdClientId());
  // addressCompleteKey is for canada post address lookup, which is to be used in sbc-common-components
  (<any>window).addressCompleteKey = ConfigHelper.getAddressCompleteKey()

  if (LaunchDarklyService.getFlag(LDFlags.SentryEnable)) {
    // initialize Sentry
    console.info('Initializing Sentry...') // eslint-disable-line no-console
    Sentry.init({
      Vue,
      dsn: ConfigHelper.getSentryDsn()
    })
  }

  // initialize Hotjar
  const hotjarId = ConfigHelper.getHotjarId();
  (<any>window).hotJarId = hotjarId
  if (hotjarId) {
    console.info('Initializing Hotjar...') // eslint-disable-line no-console
    Vue.use(Hotjar, { id: hotjarId })
  }

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
    router,
    store,
    vuetify,
    i18n,
    render: (h) => h(App)
  }).$mount('#app')
  Vue.directive('can', can)
  Vue.directive('displayMode', displayMode)
}
