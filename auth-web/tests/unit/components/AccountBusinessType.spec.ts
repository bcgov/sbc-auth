import { createLocalVue, mount } from '@vue/test-utils'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import flushPromises from 'flush-promises'

document.body.setAttribute('data-app', 'true')

describe('AccountBusinessType.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('individual account type rendering', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    await wrapper.setData({ isLoading: false })
    expect(wrapper.find("[data-test='account-name']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeFalsy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeFalsy()
  })

  it('business account type rendering', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false
      },
      mocks: { $t
      }
    })
    await wrapper.setData({ isLoading: false, isBusinessAccount: true })
    wrapper.find("[data-test='radio-business-account-type']").trigger('click')
    await flushPromises()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeTruthy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeTruthy()
  })
})
