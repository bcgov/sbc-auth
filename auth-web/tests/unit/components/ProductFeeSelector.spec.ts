
import ProductFeeSelector from '@/components/auth/common/ProductFeeSelector.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import { shallowMount } from '@vue/test-utils'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ProductFeeSelector.vue', () => {
  let wrapper: any
  const vuetify = new Vuetify({})

  const orgProductFeeCodes =
    [ { 'amount': 1.5, 'code': 'TRF01' }, { 'amount': 1, 'code': 'TRF02' } ]

  wrapper = shallowMount(ProductFeeSelector, {
    // store,
    vuetify,
    propsData: {
      orgProductFeeCodes,
      productCode: 'BUSINESS'
    }
  })
  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
