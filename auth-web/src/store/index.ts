import Vuex, { StoreOptions } from 'vuex'
import BusinessModule from './modules/business'
import OrgModule from '@/store/modules/org'
import { RootState } from './types'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VuexPersistance from 'vuex-persist'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const vuexSession = new VuexPersistance<RootState>({
  storage: window.sessionStorage
})

const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  modules: {
    business: BusinessModule,
    user: UserModule,
    org: OrgModule
  },
  plugins: [vuexSession.plugin]
}

export default new Vuex.Store<RootState>(storeOptions)
