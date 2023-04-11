import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import VueCompositionAPI from '@vue/composition-api'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'

// @ts-ignore
Vue.use(VueCompositionAPI)
Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ProductFeeViewEdit.vue', () => {
  const vuetify = new Vuetify({})
  const localVue = createLocalVue()

  const orgProductFeeCodes =
    [{ 'amount': 1.5, 'code': 'TRF01' }, { 'amount': 1, 'code': 'TRF02' }, { 'amount': 0, 'code': 'TRF04' }]
  const orgProduct =
    { 'applyFilingFees': true, 'id': 45, 'product': 'BUSINESS', 'serviceFeeCode': 'TRF01' }

  const wrapper = shallowMount(ProductFee, {
    localVue,
    vuetify,
    propsData: {
      orgProduct,
      orgProductFeeCodes
    }
  })
  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('Should have Service Fee and Statutory Fee', async () => {
    expect(wrapper.vm).toBeTruthy()
    await wrapper.setProps({
      orgProduct: { ...orgProduct },
      orgProductFeeCodes: orgProductFeeCodes.slice(0)
    })
    expect(wrapper.find("[data-test='apply-filing']").text()).toBe('Yes')
    expect(wrapper.find("[data-test='prod-filing']").text()).toBe('$ 1.50')
    await wrapper.setProps({
      orgProduct: { 'applyFilingFees': false, 'id': 45, 'product': 'BUSINESS', 'serviceFeeCode': 'TRF04' },
      orgProductFeeCodes: orgProductFeeCodes.slice(0)
    })
    expect(wrapper.find("[data-test='apply-filing']").text()).toBe('No')
    expect(wrapper.find("[data-test='prod-filing']").text()).toBe('$ 0.00')
  })
})
