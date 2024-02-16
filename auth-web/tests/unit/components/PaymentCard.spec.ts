import { createLocalVue, mount } from '@vue/test-utils'
import PaymentCard from '@/components/pay/PaymentCard.vue'
import Vuetify from 'vuetify'

describe('PaymentCard.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    const paymentCardData = {
      totalBalanceDue: 50,
      payeeName: 'BC Reg',
      cfsAccountId: 1234,
      overCredit: true,
      partialCredit: false,
      creditBalance: 6,
      credit: 10,
      paymentId: 1
    }

    const $t = () => ''
    wrapper = mount(PaymentCard, {
      propsData: {
        paymentCardData
      },
      localVue,
      vuetify,
      mocks: { $t }
    })

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('Should Payment card div', () => {
    expect(wrapper.find('[data-test="div-bcol-payment-card"]')).toBeTruthy()
  })
})
