import { createLocalVue, shallowMount } from '@vue/test-utils'
import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ProductFeeViewEdit.vue', () => {
  let wrapper: any
  const vuetify = new Vuetify({})
  const localVue = createLocalVue()

  const orgProductFeeCodes =
    [{ 'amount': 1.5, 'code': 'TRF01' }, { 'amount': 1, 'code': 'TRF02' }, { 'amount': 0, 'code': 'TRF04' }]
  const orgProduct =
    { 'applyFilingFees': true, 'id': 45, 'product': 'BUSINESS', 'serviceFeeCode': 'TRF01' }

  wrapper = shallowMount(ProductFee, {
    localVue,
    vuetify,
    propsData: {
      orgProduct,
      orgProductFeeCodes
    }
  })
  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
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
