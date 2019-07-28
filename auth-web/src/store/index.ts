import Vue from 'vue'
import Vuex, { StoreOptions } from 'vuex'
import { RootState } from './types'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'

const storeOptions: StoreOptions<RootState> = {
  strict: debug
}

export default new Vuex.Store<RootState>(storeOptions)
