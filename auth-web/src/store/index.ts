import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({

  strict: process.env.NODE_ENV !== 'production',

  state: {
    entityNumber: '',
    passcode: ''

  },
  getters: {
    entityNumber: (state) => state.entityNumber,
    passcode: (state) => state.passcode
  },
  mutations: {
    entityNumber (state, entityNumber) {
      state.entityNumber = entityNumber
    },

    passcode (state, passcode) {
      state.passcode = passcode
    }
  },
  actions: {}
})
