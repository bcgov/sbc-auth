
import { mount, shallowMount } from '@vue/test-utils'
import PaymentReturnForm from '@/components/pay/PaymentReturnForm.vue'
import PaymentServices from '../../src/services/payment.services'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'

Vue.use(Vuetify)
Vue.use(VueRouter)

jest.mock('../../src/services/payment.services')

describe('PaymentReturnForm.vue', () => {
  it('renders page and service gets invoked', () => {
    PaymentServices.updateTransaction = jest.fn().mockResolvedValue({})
    const $t = () => 'Preparing your payments'
    const wrapper = shallowMount(PaymentReturnForm, {
      propsData: {
        paymentId: 'somepaymentId',
        transactionId: 'sometransactionId',
        receiptNum: 'somereceiptNum'
      },
      mocks: { $t }
    })

    expect(PaymentServices.updateTransaction).toBeCalledWith('somepaymentId', 'sometransactionId', 'somereceiptNum')
  })
  it('service is not invoked when no params are present', () => {
    PaymentServices.updateTransaction = jest.fn().mockResolvedValue({})

    let feeresponse = {}
    const $t = (payNoParams: string) => 'Incorrect configuration'
    const wrapper = shallowMount(PaymentReturnForm, {
      propsData: { },
      mocks: { $t }
    })
    expect(PaymentServices.updateTransaction).toBeCalledTimes(0)
    expect(wrapper.text()).toContain('Incorrect configuration')
  })

  it('renders page with error message when service fails', () => {
    let feeresponse = {}
    const $t = () => 'Preparing your payments'
    PaymentServices.updateTransaction = jest.fn().mockRejectedValue({})

    const wrapper = mount(PaymentReturnForm, {
      propsData: {
        paymentId: 'somepaymentId',
        transactionId: 'sometransactionId',
        receiptNum: 'somereceiptNum'
      },
      mocks: { $t }
    })
    expect(wrapper.html()).toContain('Preparing your payments')
  })
})
