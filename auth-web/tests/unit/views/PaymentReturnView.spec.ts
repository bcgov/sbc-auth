
import { mount, shallowMount } from '@vue/test-utils'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentServices from '../../../src/services/payment.services'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('../../../src/services/payment.services')

describe('PaymentReturnView.vue', () => {
  var ob = {
    'VUE_APP_COPS_REDIRECT_URL': 'http://localhost:8081',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_AUTH_ROOT_API': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_LEGAL_ROOT_API': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(ob)

  it('renders page and service gets invoked', () => {
    PaymentServices.updateTransaction = jest.fn().mockResolvedValue({})
    const $t = () => 'Preparing your payments'
    shallowMount(PaymentReturnView, {
      propsData: {
        paymentId: 'somepaymentId',
        transactionId: 'sometransactionId',
        payResponseUrl: 'someResponseUrl'
      },
      mocks: { $t }
    })

    expect(PaymentServices.updateTransaction).toBeCalledWith('somepaymentId', 'sometransactionId', 'someResponseUrl')
  })
  it('service is not invoked when no params are present', () => {
    PaymentServices.updateTransaction = jest.fn().mockResolvedValue({})

    const $t = (payNoParams: string) => 'Incorrect configuration'
    const wrapper = shallowMount(PaymentReturnView, {
      propsData: { },
      mocks: { $t }
    })
    expect(PaymentServices.updateTransaction).toBeCalledTimes(0)
    expect(wrapper.text()).toContain('Incorrect configuration')
  })

  it('renders page with error message when service fails', () => {
    const $t = () => 'Preparing your payments'
    PaymentServices.updateTransaction = jest.fn().mockRejectedValue({})

    const wrapper = mount(PaymentReturnView, {
      propsData: {
        paymentId: 'somepaymentId',
        transactionId: 'sometransactionId',
        payResponseUrl: 'someResponseUrl'
      },
      mocks: { $t }
    })
    expect(wrapper.html()).toContain('Preparing your payments')
  })
})
