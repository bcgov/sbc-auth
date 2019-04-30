
const state = {
  entityNumber: '',
  passcode: ''

}
const getters = {
  entityNumber: (state) => state.entityNumber,
  passcode: (state) => state.passcode
}
const mutations = {
  entityNumber (state, entityNumber) {
    state.entityNumber = entityNumber
  },

  passcode (state, passcode) {
    state.passcode = passcode
  }
}
const actions = {}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
