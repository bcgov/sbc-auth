import 'core-js/stable' // to polyfill ECMAScript features
import '@mdi/font/css/materialdesignicons.min.css' // icon library (https://materialdesignicons.com/)
import 'regenerator-runtime/runtime' // to use transpiled generator functions
import './registerServiceWorker'
import App from './App.vue'
import ConfigHelper from '@/util/config-helper'
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
ConfigHelper.saveConfigToSessionStorage().then((data) => {
  renderVue()
}
)
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
