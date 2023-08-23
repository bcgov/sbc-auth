import { createLocalVue, shallowMount } from '@vue/test-utils'
import ProductFee from '@/components/auth/staff/review-task/ProductFee.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useOrgStore } from '@/store/org'

describe('PaymentInformation.vue', () => {
  let store: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  let wrapper: any
  const vuetify = new Vuetify({})

  beforeEach(() => {
    const orgStore = useOrgStore()
    orgStore.orgProductFeeCodes = [{ amount: 1.5, code: 'TRF01' }, { amount: 1, code: 'TRF02' }]
    orgStore.productList = [{ code: 'BCA', name: 'BC Assessment' }, { code: 'VS', name: 'Wills Registry' }] as any
    orgStore.currentAccountFees = []
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    wrapper = shallowMount(ProductFee, {
      store,
      vuetify
    })
    expect(wrapper.vm).toBeTruthy()
  })
})
