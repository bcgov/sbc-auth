import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import { useCodesStore } from '@/stores'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('AccountDetails.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.directive('can', can)

    const codesStore = useCodesStore()
    codesStore.businessSizeCodes = [
      { code: '0-1', default: true, desc: '1 Employee' },
      { code: '2-5', default: false, desc: '2-5 Employees' }
    ]
    codesStore.businessTypeCodes = [
      { code: 'BIZ', default: false, desc: 'GENERAL BUSINESS' }
    ]
    // Remove in Vue 3
    codesStore.getBusinessSizeCodes = vi.fn()
    codesStore.getBusinessTypeCodes = vi.fn()
    wrapperFactory = propsData => {
      return shallowMount(AccountDetails, {
        localVue,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ accountDetails: {
      name: 'QQ COUNTERTOP',
      branchName: '22',
      businessType: 'BIZAC',
      businessSize: '0-1'
    },
    viewOnlyMode: false
    })
  })

  afterEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly ', () => {
    expect(wrapper.findComponent(AccountDetails).exists()).toBe(true)
  })

  it('renders proper header content', () => {
    expect(wrapper.find('[data-test="title"]').text()).toBe('Account Details')
  })

  it('Show edit icon when passing props', async () => {
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(false)
    await wrapper.setProps({ viewOnlyMode: true })
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(true)
  })
})
