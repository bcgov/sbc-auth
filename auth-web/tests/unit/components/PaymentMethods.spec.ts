import { createLocalVue, mount } from '@vue/test-utils'

import { Account } from '@/util/constants'
import OrgModule from '@/store/modules/org'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('PaymentMethods.vue', () => {
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
    localVue.directive('can', can)

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

    wrapper = mount(PaymentMethods, {
      store,
      localVue,
      vuetify,
      propsData: {
        currentOrgType: Account.BASIC
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
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

  it('should render both payment card types', () => {
    expect(wrapper.findAll('.payment-card').length).toBe(2)
  })

  it('should render both payment card types', () => {
    expect(wrapper.findAll('.payment-card').length).toBe(2)
  })

  it('should render payment card types correctly', () => {
    const paymentMethods = wrapper.vm.allowedPaymentMethods
    const paymentCards = wrapper.findAll('.payment-card')
    expect(paymentCards.at(0).find('.payment-title').text()).toBe(paymentMethods[0].title)
    expect(paymentCards.at(1).find('.payment-title').text()).toBe(paymentMethods[1].title)
  })

  it('should select payment card types correctly', async () => {
    const paymentCard1 = wrapper.findAll('.payment-card').at(0)
    const selectButton = paymentCard1.find('.v-btn')
    expect(selectButton.text()).toBe('SELECT')
    selectButton.trigger('click')
    await wrapper.vm.$nextTick()
    expect(selectButton.text()).toBe('SELECTED')
  })

  it('should set selectedPaymentMethod correctly', async () => {
    const paymentCard1 = wrapper.findAll('.payment-card').at(0)
    const selectButton = paymentCard1.find('.v-btn')
    expect(selectButton.text()).toBe('SELECT')
    selectButton.trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.allowedPaymentMethods[0].type)
  })

  it('should select payment method correctly', () => {
    wrapper.vm.paymentMethodSelected(wrapper.vm.allowedPaymentMethods[0])
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.allowedPaymentMethods[0].type)
  })

  it('should return the payment selected correctly', () => {
    const method1 = wrapper.vm.allowedPaymentMethods[0]
    wrapper.vm.paymentMethodSelected(method1)
    expect(wrapper.vm.isPaymentSelected(method1)).toBe(true)
  })

  it('should return the payment selected correctly [negative]', () => {
    const method1 = wrapper.vm.allowedPaymentMethods[0]
    const method2 = wrapper.vm.allowedPaymentMethods[1]
    wrapper.vm.paymentMethodSelected(method1)
    expect(wrapper.vm.isPaymentSelected(method2)).toBe(false)
  })
})
