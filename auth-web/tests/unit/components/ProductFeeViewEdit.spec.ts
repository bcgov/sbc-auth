
import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { shallowMount } from '@vue/test-utils'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ProductFeeViewEdit.vue', () => {
  let wrapper: any
  const vuetify = new Vuetify({})

  const orgProductFeeCodes =
    [ { 'amount': 1.5, 'code': 'TRF01' }, { 'amount': 1, 'code': 'TRF02' } ]
  const orgProduct =
    { 'applyFilingFees': true, 'id': 45, 'product': 'BUSINESS', 'serviceFeeCode': 'TRF01' }

  wrapper = shallowMount(ProductFee, {

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

  it('is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })

  it('Should have Service Fee and Statutory Fee', () => {
    expect(wrapper.find("[data-test='apply-filing']").text()).toBe('Yes')
    expect(wrapper.find("[data-test='prod-filing']").text()).toBe('$ 1.50')
  })
})
