import Vuex, { StoreOptions } from 'vuex'
import BusinessModule from './modules/business'
import OrgModule from '@/store/modules/org'
import { RootState } from './types'
import StaffModule from '@/store/modules/staff'
import UserModule from '@/store/modules/user'
import Vue from 'vue'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

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
  },
  modules: {
    business: BusinessModule,
    user: UserModule,
    org: OrgModule,
    staff: StaffModule
  }
}

export default new Vuex.Store<RootState>(storeOptions)
