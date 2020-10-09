import { Wrapper, createLocalVue, mount } from '@vue/test-utils'
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

    const store = new Vuex.Store({
      state: {},
      strict: false
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

  it('should render both payment card types', () => {
    expect(wrapper.findAll('.payment-card').length).toBe(2)
  })

  it('should render both payment card types', () => {
    expect(wrapper.findAll('.payment-card').length).toBe(2)
  })

  it('should render payment card types correctly', () => {
    const paymentMethods = wrapper.vm.$data.paymentMethods
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
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.$data.paymentMethods[0].type)
  })

  it('should select payment method correctly', () => {
    wrapper.vm.selectPayment(wrapper.vm.$data.paymentMethods[0])
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.$data.paymentMethods[0].type)
  })

  it('should return the payment selected correctly', () => {
    const method1 = wrapper.vm.$data.paymentMethods[0]
    wrapper.vm.selectPayment(method1)
    expect(wrapper.vm.isPaymentSelected(method1)).toBe(true)
  })

  it('should return the payment selected correctly [negative]', () => {
    const method1 = wrapper.vm.$data.paymentMethods[0]
    const method2 = wrapper.vm.$data.paymentMethods[1]
    wrapper.vm.selectPayment(method1)
    expect(wrapper.vm.isPaymentSelected(method2)).toBe(false)
  })
})
