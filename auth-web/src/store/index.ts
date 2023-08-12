import Vuex, { StoreOptions } from 'vuex'

import ActvityLogModule from '@/store/modules/activityLog'
import BusinessModule from './modules/business'
import CodesModule from '@/store/modules/codes'
import OrgModule from '@/store/modules/org'
import { RootState } from './types'
import StaffModule from '@/store/modules/staff'
import TaskModule from '@/store/modules/task'
import UserModule from '@/store/modules/user'
import Vue from 'vue'

Vue.use(Vuex)

const debug = import.meta.env.NODE_ENV !== 'production'

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
    staff: StaffModule,
    codes: CodesModule,
    task: TaskModule,
    activity: ActvityLogModule
  }
}

export default new Vuex.Store<RootState>(storeOptions)
