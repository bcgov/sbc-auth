import Vue from 'vue'
import Vuex, { StoreOptions } from 'vuex'
import VuexPersistence from 'vuex-persist'
import { RootState } from './types'
import BusinessModule from './modules/business'
import UserModule from './modules/user'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const vuexPersist = new VuexPersistence({
  key: 'AUTH_WEB',
  storage: sessionStorage
})

const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  modules: {
    business: BusinessModule,
    user: UserModule
  },
  plugins: [vuexPersist.plugin]
}

export default new Vuex.Store<RootState>(storeOptions)
