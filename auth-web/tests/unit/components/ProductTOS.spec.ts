import { createLocalVue, shallowMount } from '@vue/test-utils'
import ProductTOS from '@/components/auth/common/ProductTOS.vue'
import Vuetify from 'vuetify'

describe('ProductTOS.vue', () => {
  let wrapperFactory: any
  let wrapper: any

  beforeEach(() => {
    const localVue = createLocalVue()

    const vuetify = new Vuetify({})

    wrapperFactory = (propsData) => {
      return shallowMount(ProductTOS, {
        localVue,
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

    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the ProductTOS components properly ', () => {
    expect(wrapper.findComponent(ProductTOS).exists()).toBe(true)
  })
  it('renders proper header content', () => {
    expect(wrapper.find('h4').text()).toBe('Terms of Service')
  })
})
