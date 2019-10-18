import Vue from 'vue'
import Vuex, { StoreOptions } from 'vuex'
import { RootState } from './types'
import BusinessModule from './modules/business'
import PaymentModule from '@/store/modules/payment'
import UserModule from '@/store/modules/user'
import OrgModule from '@/store/modules/org'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const storeOptions: StoreOptions<RootState> = {
  strict: debug,
  modules: {
    business: BusinessModule,
    paymentmodule: PaymentModule,
    user: UserModule,
    org: OrgModule
  }
}

export default new Vuex.Store<RootState>(storeOptions)
