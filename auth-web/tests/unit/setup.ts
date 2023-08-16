import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import VueRouter from 'vue-router'
import VueTheMask from 'vue-the-mask'
import Vuex from 'vuex'
import can from '@/directives/can'
import { install } from 'vue-demi'

Vue.use(VueCompositionAPI)
Vue.use(VueTheMask)
Vue.use(Vuex)
Vue.use(VueRouter)
Vue.directive('can', can)

// Need this so composition api works with vue-demi
install(Vue)
