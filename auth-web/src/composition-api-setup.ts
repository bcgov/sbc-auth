import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import { getPiniaStore } from '@/stores'
Vue.use(VueCompositionAPI)
// Need to do this before Router gets hoisted.
getPiniaStore()
