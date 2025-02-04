import { createLocalVue, mount } from '@vue/test-utils'

import { Account } from '@/util/constants'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'

describe('PaymentMethods.vue', () => {
  let wrapper: any
  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }

  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})
    localVue.directive('can', can)

    wrapper = mount(PaymentMethods, {
      localVue,
      vuetify,
      propsData: {
        currentOrgType: Account.PREMIUM
      }
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

  it('should render both payment card types', () => {
    expect(wrapper.findAll('.payment-card').length).toBe(4)
  })

  it('should render payment card types correctly', () => {
    const paymentMethods = wrapper.vm.filteredPaymentMethods
    const paymentTitles = wrapper.findAll('.payment-title')
    expect(paymentTitles.at(0).text()).toContain(paymentMethods[0].title)
    expect(paymentTitles.at(1).text()).toContain(paymentMethods[1].title)
    expect(paymentTitles.at(2).text()).toContain(paymentMethods[2].title)
    expect(paymentTitles.at(3).text()).toContain(paymentMethods[3].title)
  })

  it('should select payment card types correctly', async () => {
    const paymentCard1 = wrapper.findAll('.payment-card').at(0)
    const selectButton = paymentCard1.find('.v-radio')
    selectButton.trigger('click')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()
    expect(selectButton.attributes()['class']).toContain('v-item--active')
  })

  it('should set selectedPaymentMethod correctly', async () => {
    const paymentCard1 = wrapper.findAll('.payment-card').at(0)
    const selectButton = paymentCard1.find('.v-radio')
    selectButton.trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.filteredPaymentMethods[0].type)
  })

  it('should select payment method correctly', async () => {
    wrapper.vm.paymentMethodSelected(wrapper.vm.filteredPaymentMethods[0])
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$data.selectedPaymentMethod).toBe(wrapper.vm.filteredPaymentMethods[0].type)
  })

  it('should return the payment selected correctly', async () => {
    const method1 = wrapper.vm.filteredPaymentMethods[0]
    wrapper.vm.paymentMethodSelected(method1)
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentSelected(method1)).toBe(true)
  })

  it('should return the payment selected correctly [negative]', async () => {
    const method1 = wrapper.vm.filteredPaymentMethods[0]
    const method2 = wrapper.vm.filteredPaymentMethods[1]
    wrapper.vm.paymentMethodSelected(method1)
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.isPaymentSelected(method2)).toBe(false)
  })
})
