
import ProductFeeSelector from '@/components/auth/common/ProductFeeSelector.vue'
import { shallowMount } from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ProductFeeSelector.vue', () => {
  const vuetify = new Vuetify({})

  const orgProductFeeCodes =
    [ { 'amount': 1.5, 'code': 'TRF01' }, { 'amount': 1, 'code': 'TRF02' } ]

  const wrapper = shallowMount(ProductFeeSelector, {
    // store,
    vuetify,
    propsData: {
      orgProductFeeCodes,
      productCode: 'BUSINESS'
    }
  })
  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })
})
