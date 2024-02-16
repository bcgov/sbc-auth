import { createLocalVue, mount } from '@vue/test-utils'
import PaymentReview from '@/components/auth/account-freeze/PaymentReview.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

describe('PaymentReview.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})

    wrapper = mount(PaymentReview, {
      localVue,
      vuetify,
      mixins: [Steppable]
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
