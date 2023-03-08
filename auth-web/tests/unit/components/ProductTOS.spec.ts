import { createLocalVue, shallowMount } from '@vue/test-utils'
import ProductTOS from '@/components/auth/common/ProductTOS.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)

describe('ProductTOS.vue', () => {
  let wrapperFactory: any
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)

    const vuetify = new Vuetify({})

    const store = new Vuex.Store({
      state: {},
      strict: false

    })
    wrapperFactory = (propsData) => {
      return shallowMount(ProductTOS, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        },
        mocks: {
          $t: (mock) => mock
        }
      })
    }
    const props = {
      userName: 'user1',
      orgName: 'org 2',
      isTOSAlreadyAccepted: false,
      isApprovalFlow: true

    }
    wrapper = wrapperFactory(props)

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper).toBeTruthy()
  })

  it('renders the ProductTOS components properly ', () => {
    expect(wrapper.find(ProductTOS).exists()).toBe(true)
  })
  it('renders proper header content', () => {
    expect(wrapper.find('h4').text()).toBe('Terms of Service')
  })
})
