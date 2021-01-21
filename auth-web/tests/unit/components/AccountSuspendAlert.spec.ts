import { Wrapper, createLocalVue, shallowMount } from '@vue/test-utils'
import StaffActiveAccountsTable from '@/components/auth/common/AccountSuspendAlert.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('StaffActiveAccountsTable.vue', () => {
  let wrapper: Wrapper<StaffActiveAccountsTable>

  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const orgModule = {
      namespaced: true,
      state: {currentOrganization:{}},
      actions: {
        calculateFailedInvoices: jest.fn(() => {
        return {
            totalTransactionAmount: 10,
            totalAmountToPay: 20
        }}),
      }
    }

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    const $t = () => ''
    wrapper = shallowMount(StaffActiveAccountsTable, {
      store,
      localVue,
      vuetify,
      mocks: { $t }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })
  // TOFIX fix orgs undefiend
  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('Should have Alert', () => {
    expect(wrapper.find('.banner-info')).toBeTruthy()
  })
})
