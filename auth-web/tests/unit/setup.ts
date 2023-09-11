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

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

setActivePinia(createPinia())
