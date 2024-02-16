import { createLocalVue, mount } from '@vue/test-utils'
import PaymentErrorMessage from '@/components/pay/common/PaymentErrorMessage.vue'
import Vuetify from 'vuetify'

describe('PaymentErrorMessage.vue', () => {
  let wrapper: any
  beforeEach(() => {
    const localVue = createLocalVue()
    const vuetify = new Vuetify({})

    const PaymentErrorMessageData = {
      errorType: 'PAYMENT_GENERIC_ERROR',
      backUrl: '',
      tryAgainURL: ''
    }

    const $t = () => ''
    wrapper = mount(PaymentErrorMessage, {
      propsData: {
        PaymentErrorMessageData
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
    expect(wrapper.find('[data-test="pay-error"]')).toBeTruthy()
  })
})
