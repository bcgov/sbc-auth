import { AccountFee, AccountFeeDTO, OrgProduct, OrgProductFeeCode } from '@/models/Organization'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import ProductFee from '@/components/auth/staff/review-task/ProductFee.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('PaymentInformation.vue', () => {
  let store: any
  let orgModule: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.directive('can', can)
  let wrapper: any
  const vuetify = new Vuetify({})

  beforeEach(() => {
    orgModule = {
      namespaced: true,
      state: {
        orgProductFeeCodes: [{ amount: 1.5, code: 'TRF01' }, { amount: 1, code: 'TRF02' }],
        orgProducts: [{ code: 'BCA', name: 'BC Assessment' }, { code: 'VS', name: 'Wills Registry' }]
      }
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule
      }
    })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    wrapper = shallowMount(ProductFee, {
      store,
      vuetify
    })
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('validate properties', () => {
    wrapper = shallowMount(ProductFee, {
      store,
      vuetify,
      propsData: {
        tabNumber: 1,
        title: 'Product Fee'
      },
      mocks: {
        $t: (mock) => mock
      }
    })
    expect(wrapper.find('h2').text()).toBe('1. Product Fee')
  })
})
