import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import { getPiniaStore } from './store'

Vue.use(VueCompositionAPI)
// Need to do this before Router gets hoisted.
getPiniaStore()
