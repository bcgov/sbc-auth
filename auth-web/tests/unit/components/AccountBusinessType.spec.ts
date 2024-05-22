import { createLocalVue, mount } from '@vue/test-utils'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import { AccountType } from '@/util/constants'
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
    await wrapper.setData({ isLoading: false, orgType: AccountType.INDIVIDUAL })
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
    await wrapper.setData({ isLoading: false, orgType: AccountType.BUSINESS })
    await wrapper.vm.handleAccountTypeChange(AccountType.BUSINESS)
    await flushPromises()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeTruthy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeTruthy()
  })

  it('renders the government agency radio button when not editing and not a current government org', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false,
        isEditAccount: false
      },
      mocks: { $t }
    })
    await wrapper.setData({ isLoading: false, isCurrentGovnOrg: false })
    expect(wrapper.find("[data-test='radio-government-account-type']").exists()).toBeTruthy()
  })

  it('does not render the government agency radio button when editing or a current government org', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false,
        isEditAccount: true
      },
      mocks: { $t }
    })
    await wrapper.setData({ isLoading: false, isCurrentGovnOrg: true })
    expect(wrapper.find("[data-test='radio-government-account-type']").exists()).toBeFalsy()
  })

  it('renders error message correctly', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: false,
        errorMessage: 'An error occurred'
      },
      mocks: { $t }
    })
    await wrapper.setData({ isLoading: false })
    expect(wrapper.find('.v-alert').text()).toBe('An error occurred')
  })

  it('renders correctly when govmAccount is true', async () => {
    const $t = () => ''
    wrapper = mount(AccountBusinessType, {
      localVue,
      vuetify,
      propsData: {
        govmAccount: true
      },
      mocks: { $t }
    })
    expect(wrapper.find("[data-test='account-name']").exists()).toBeTruthy()
    expect(wrapper.find("[data-test='input-branch-name']").isVisible()).toBeTruthy()
    expect(wrapper.find("[data-test='business-account-type-details']").exists()).toBeFalsy()
    expect(wrapper.find('legend.mb-3').text()).toBe('Enter Ministry Information for this account')
  })
})
