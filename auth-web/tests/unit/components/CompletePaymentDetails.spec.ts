import { createLocalVue, mount } from '@vue/test-utils'
import CompletePaymentDetails from '@/components/pay/CompletePaymentDetails.vue'
import { PaymentTypes } from '@/util/constants'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

describe('CompletePaymentDetails.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})
  const $t = () => ''

  beforeEach(async () => {
    wrapper = mount(CompletePaymentDetails, {
      propsData: {
        orgId: '1234',
        paymentId: '1234',
        changePaymentType: PaymentTypes.BCOL
      },
      localVue,
      vuetify
    })
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    wrapper.destroy()
    sessionStorage.clear()

    vi.resetModules()
    vi.clearAllMocks()
  })

  const mountComponent = (paymentType: string) => {
    return mount(CompletePaymentDetails, {
      propsData: {
        orgId: '1234',
        paymentId: '1234',
        changePaymentType: paymentType,
        stepJumpTo: vi.fn()
      },
      localVue,
      vuetify,
      mocks: { $t }
    })
  }

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(CompletePaymentDetails, {
      localVue,
      vuetify,
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('Renders BCOL elements', async () => {
    wrapper = mountComponent(PaymentTypes.BCOL)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.balance-paid').exists()).toBe(true)
    expect(wrapper.find('[data-test="bcol-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="bcol-warning"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="error-payment-method"]').exists()).toBe(false)
  })

  it('Renders PAD elements', async () => {
    wrapper = mountComponent(PaymentTypes.PAD)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.balance-paid').exists()).toBe(true)
    expect(wrapper.find('h3').text()).toContain('Pre-authorized Debit')
    expect(wrapper.find('[data-test="error-payment-method"]').exists()).toBe(false)
  })
})
