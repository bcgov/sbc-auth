import '@/composition-api-setup' // ensure this happens before any imports trigger use of composition-api
import Vue from 'vue'
import VueRouter from 'vue-router'
import VueTheMask from 'vue-the-mask'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(VueTheMask)
Vue.use(Vuex)
Vue.use(VueRouter)
Vue.directive('can', can)
