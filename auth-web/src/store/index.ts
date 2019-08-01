import Vue from 'vue'
import Vuex, { StoreOptions } from 'vuex'
import VuexPersistence from 'vuex-persist'
import { RootState } from './types'
import BusinessModule from './modules/business'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const vuexPersist = new VuexPersistence({
  key: 'vuex',
  storage: sessionStorage
})

const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  modules: {
    business: BusinessModule
  },
  plugins: [vuexPersist.plugin]
}

export default new Vuex.Store<RootState>(storeOptions)
