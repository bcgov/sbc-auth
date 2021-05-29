import { createLocalVue, mount } from '@vue/test-utils'
import Product from '@/components/auth/common/Product.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

describe('Product.vue', () => {
  let wrapperFactory: any
  let wrapper: any
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }

  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false

    })
    wrapperFactory = (propsData) => {
      return mount(Product, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock,
          $te: (mock) => mock
        }
      })
    }
    const props = { productDetails: {
      'code': 'VS',
      'name': 'Wills Registry',
      'description': 'test',
      'url': 'url',
      'type': 'PARTNER',
      'mdiIcon': 'mdi-image-outline',
      'subscriptionStatus': ''
    } }
    wrapper = wrapperFactory(props)

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })
})
