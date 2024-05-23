import { AccessType, AccountStatus } from '@/util/constants'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import { useCodesStore, useOrgStore } from '@/stores'
import AccountDetails from '@/components/auth/account-settings/account-info/AccountDetails.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'

const vuetify = new Vuetify({})

document.body.setAttribute('data-app', 'true')

describe('AccountDetails.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.directive('can', can)
    const orgStore = useOrgStore()
    orgStore.currentOrganization = {
      name: 'testOrg',
      statusCode: AccountStatus.ACTIVE,
      orgStatus: AccountStatus.ACTIVE,
      accessType: AccessType.REGULAR,
      id: 1234
    } as any

    const codesStore = useCodesStore()
    codesStore.businessSizeCodes = [
      { code: '0-1', default: true, desc: '1 Employee' },
      { code: '2-5', default: false, desc: '2-5 Employees' }
    ]
    codesStore.businessTypeCodes = [
      { code: 'BIZ', default: false, desc: 'GENERAL BUSINESS' }
    ]

    codesStore.fetchAllBusinessTypeCodes = vi.fn().mockResolvedValue(null)
    codesStore.getBusinessSizeCodes = vi.fn().mockResolvedValue(null)
    codesStore.getBusinessTypeCodes = vi.fn().mockResolvedValue(null)
    await codesStore.fetchAllBusinessTypeCodes()
    await codesStore.getBusinessSizeCodes()
    await codesStore.getBusinessTypeCodes()

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
    await wrapper.setProps({ viewOnlyMode: true, nameChangeAllowed: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.accountTypeLabel).toBe('Business Type:')
    expect(wrapper.vm.accountSizeLabel).toBe('Business Size:')
    expect(wrapper.find('[data-test="btn-edit"]').exists()).toBe(true)
  })

  it('Hide edit icon when govn and update type label', async () => {
    const orgStore = useOrgStore()
    orgStore.currentOrganization.accessType = AccessType.GOVN
    await wrapper.setProps({ viewOnlyMode: true, nameChangeAllowed: true })
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.accountTypeLabel).toBe('Government Agency Type:')
    expect(wrapper.vm.accountSizeLabel).toBe('Government Agency Size:')
  })
})
