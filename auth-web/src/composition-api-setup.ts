import ConfigHelper from './util/config-helper'
import Vue from 'vue'
import VueCompositionAPI from '@vue/composition-api'
import { getPiniaStore } from '@/stores'
Vue.use(VueCompositionAPI)
ConfigHelper.saveConfigToSessionStorage()
// Need to do this before Router gets hoisted.
getPiniaStore()
