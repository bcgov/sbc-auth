import { PiniaVuePlugin, createPinia } from 'pinia'
import Vuex, { StoreOptions } from 'vuex'

import { RootState } from './types'
import Vue from 'vue'

Vue.use(Vuex)

const debug = import.meta.env.NODE_ENV !== 'production'

// Remove with Vue 3.
const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  state: () => ({
    refreshKey: 0,
    loading: true
  }),
  getters: {
    loading: (state) => state.loading
  },
  mutations: {
    updateHeader (state) {
      state.refreshKey++
    },
    loadComplete (state) {
      state.loading = false
    }
  }
}

/**
 * Configures and returns Vuex Store. - We still need this for sbc-common-components.
 */
export function getVuexStore () {
  Vue.use(Vuex)

  return new Vuex.Store<RootState>(storeOptions)
}

/**
 * Configures and returns Pinia Store.
 */
export function getPiniaStore () {
  Vue.use(PiniaVuePlugin)

  return createPinia()
}
