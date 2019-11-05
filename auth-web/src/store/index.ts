import Vuex, { StoreOptions } from 'vuex'
import BusinessModule from './modules/business'
import OrgModule from '@/store/modules/org'
import { RootState } from './types'
import StatusModule from '@/store/modules/status'
import UserModule from '@/store/modules/user'
import Vue from 'vue'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  modules: {
    business: BusinessModule,
    statusmodule: StatusModule,
    user: UserModule,
    org: OrgModule
  }
}

export default new Vuex.Store<RootState>(storeOptions)
