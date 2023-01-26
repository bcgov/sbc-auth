import { createLocalVue, mount } from '@vue/test-utils'
import { Account } from '@/util/constants'
import OrgModule from '@/store/modules/org'
import PaymentReview from '@/components/auth/account-freeze/PaymentReview.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PaymentReview.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {}
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

    wrapper = mount(PaymentReview, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable]
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('should render payment method title', () => {
    expect(wrapper.find('h4').text()).toBe('Payment Method')
  })

  it('should set acknowledge false initially', () => {
    expect(wrapper.vm.isAcknowledged).toBe(false)
  })

  it('should render proceed and back buttons', () => {
    expect(wrapper.find('.v-btn').text('Proceed')).toBeTruthy()
    expect(wrapper.find('.v-btn').text('Back')).toBeTruthy()
  })

  it('should enable procced btn once acknowledged', async () => {
    expect(wrapper.find('.proceed-btn').props().disabled).toBe(true)
    wrapper.vm.isAcknowledged = true
    await flushPromises()
    expect(wrapper.find('.proceed-btn').props().disabled).toBe(false)
  })
})
