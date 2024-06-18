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

  it('Renders elements', async () => {
    expect(wrapper.find('.balance-paid').exists()).toBe(true)
    expect(wrapper.find('[data-test="bcol-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="bcol-warning"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="error-payment-method"]').exists()).toBe(false)
  })
})
