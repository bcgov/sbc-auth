
import { mount, shallowMount } from '@vue/test-utils'
import PaymentReturnView from '@/views/pay/PaymentReturnView.vue'
import PaymentServices from '../../../src/services/payment.services'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
Vue.use(VueRouter)

vi.mock('../../../src/services/payment.services')

describe('PaymentReturnView.vue', () => {
  var ob = {
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1',
    'AUTH_API_URL': 'https://auth-api-post-dev.pathfinder.gov.bc.ca/api/v1',
    'LEGAL_API_URL': 'https://legal-api-dev.pathfinder.gov.bc.ca/api/v1',
    'VUE_APP_FLAVOR': 'post-mvp'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(ob)

  it('renders page and service gets invoked', () => {
    PaymentServices.updateTransaction = vi.fn().mockResolvedValue({})
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
    PaymentServices.updateTransaction = vi.fn().mockResolvedValue({})

    const $t = (payNoParams: string) => 'Incorrect configuration'
    const wrapper = shallowMount(PaymentReturnView, {
      propsData: { },
      mocks: { $t }
    })
    expect(PaymentServices.updateTransaction).toBeCalledTimes(0)
    // expect(wrapper.text()).toContain('Incorrect configuration')
  })

  it('renders page with error message when service fails', () => {
    const $t = () => 'Preparing your payments'
    PaymentServices.updateTransaction = vi.fn().mockRejectedValue({})

    const wrapper = mount(PaymentReturnView, {
      propsData: {
        paymentId: 'somepaymentId',
        transactionId: 'sometransactionId',
        payResponseUrl: 'someResponseUrl'
      },
      mocks: { $t }
    })
    // expect(wrapper.html()).toContain('Preparing your payments')
    expect(wrapper.find('.v-progress-circular')).toBeTruthy()
  })
})
