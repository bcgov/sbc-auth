import { Account, PaymentTypes } from '@/util/constants'
import { createLocalVue, mount } from '@vue/test-utils'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import Vuetify from 'vuetify'
import { useOrgStore } from '@/stores/org'

describe('PaymentMethodSelector.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})
    const orgStore = useOrgStore()
    orgStore.currentOrganization = { orgType: Account.BASIC } as any
    wrapper = mount(PaymentMethodSelector, {
      localVue,
      vuetify
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

  it('initial selection should be empty', () => {
    expect(wrapper.vm.$data.selectedPaymentMethod).toBeFalsy()
  })

  it('should render payment card', () => {
    expect(wrapper.find('.payment-card')).toBeTruthy()
  })

  it('should render payment page subtitle', () => {
    expect(wrapper.find('.payment-page-sub')).toBeTruthy()
  })

  it('should render payment page subtitle correctly', () => {
    expect(wrapper.find('.payment-page-sub').text()).toBe(wrapper.vm.pageSubTitle)
  })

  it('should select payment method correctly', () => {
    wrapper.vm.setSelectedPayment(PaymentTypes.CREDIT_CARD)
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(PaymentTypes.CREDIT_CARD)
  })

  it('should render payment page subtitle correctly', async () => {
    await wrapper.setProps({ readOnly: true })
    expect(wrapper.find('[data-test="save-button"]').text()).toBe('Submit')
  })
})
