import { Account, PaymentTypes } from '@/util/constants'
import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
import OrgModule from '@/store/modules/org'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PaymentMethodSelector.vue', () => {
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {},
        currentOrgType: Account.BASIC
      },
      actions: OrgModule.actions,
      mutations: OrgModule.mutations,
      getters: OrgModule.getters
    }

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapper = mount(PaymentMethodSelector, {
      store,
      localVue,
      vuetify
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('initial selection should be empty', () => {
    expect(wrapper.vm.$data.selectedPaymentMethod).toBeFalsy()
  })

  it('should render payment card', () => {
    expect(wrapper.find('.payment-card')).toBeTruthy()
  })

  it('should render payment page subtitle', () => {
    expect(wrapper.find('.payment-page-sub')).toBeTruthy()
  })

  it('should render payment page subtitle correctly', () => {
    expect(wrapper.find('.payment-page-sub').text()).toBe(wrapper.vm.pageSubTitle)
  })

  it('should select payment method correctly', () => {
    wrapper.vm.setSelectedPayment(PaymentTypes.CREDIT_CARD)
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(PaymentTypes.CREDIT_CARD)
  })
})
