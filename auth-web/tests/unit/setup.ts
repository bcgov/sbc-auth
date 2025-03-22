import '@/composition-api-setup' // ensure this happens before any imports trigger use of composition-api
import { createPinia, setActivePinia } from 'pinia'
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router'
import VueSanitize from 'vue-sanitize-directive'
import VueTheMask from 'vue-the-mask'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(VueTheMask)
Vue.use(Vuex)
Vue.use(VueRouter)
Vue.use(Vuetify)
Vue.use(VueI18n)
Vue.use(VueRouter)
Vue.use(VueSanitize)
Vue.directive('can', can)

// mock fix Error: Using the export keyword between a decorator and a class is not allowed. Please use `export @dec class` instead.
// remove this once when vuex-module-decorators removed from bcrs-shared-components
vi.mock('@bcrs-shared-components/base-address/BaseAddress.vue', () => ({
  default: {
    name: 'BaseAddress',
    template: '<div class="base-address-mock" />',
    props: ['editing', 'schema', 'address']
  }
}))

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

setActivePinia(createPinia())
