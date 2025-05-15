import { AccountStatus, Role } from '@/util/constants'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import AccountInfo from '@/components/auth/account-settings/account-info/AccountInfo.vue'
import OrgService from '@/services/org.services'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import Vuetify from 'vuetify'
import can from '@/directives/can'
import flushPromises from 'flush-promises'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

document.body.setAttribute('data-app', 'true')

describe('AccountInfo.vue', () => {
  let wrapper: any
  const localVue = createLocalVue()
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    orgStore.currentOrganization = {
      name: 'testOrg',
      statusCode: AccountStatus.ACTIVE,
      orgStatus: AccountStatus.ACTIVE,
      id: 1234
    } as any
    orgStore.currentMembership = {} as any
    orgStore.permissions = ['CHANGE_ADDRESS', 'CHANGE_ORG_NAME', 'VIEW_ADDRESS', 'VIEW_ADMIN_CONTACT']

    OrgService.getContactForOrg = vi.fn().mockResolvedValue({
      data: {
        contacts: []
      }
    })

    userStore.currentUser = {
      roles: [Role.Staff, Role.StaffSuspendAccounts]
    } as any
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      },
      stubs: {
        'v-btn': {
          template: `<button @click='$listeners.click'></button>`
        },
        ModalDialog: true
      }
    })
    expect(wrapper.vm).toBeTruthy()
  })

  it('suspend button click invokes showSuspendAccountDialog method', () => {
    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      },
      stubs: {
        'v-btn': {
          template: `<button @click='$listeners.click'></button>`
        },
        ModalDialog: true
      }
    })
    const stub = vi.fn()
    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.showSuspendAccountDialog).toBeCalled()
  })

  it('Account status and number displayed properly', async () => {
    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      }
    })
    const orgStore = useOrgStore()
    expect(orgStore.currentOrganization.name).toBe('testOrg')
    expect(wrapper.find("[data-test='btn-suspend-account']").text()).toBe('Suspend Account')
    orgStore.setCurrentOrganization({
      name: 'testOrg_suspended',
      statusCode: AccountStatus.SUSPENDED,
      orgStatus: AccountStatus.SUSPENDED,
      id: 1234
    })
    await flushPromises()

    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      }
    })
    expect(orgStore.currentOrganization.name).toBe('testOrg_suspended')
    expect(wrapper.find("[data-test='btn-suspend-account']").text()).toBe('Unsuspend Account')
    expect(wrapper.find("[data-test='div-account-number']").text()).toBe('1234')
  })

  it('Account Info color code', () => {
    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      }
    })
    const orgStore = useOrgStore()
    let statusColor = wrapper.vm.getStatusColor(orgStore.currentOrganization.orgStatus)
    expect(statusColor).toBe('green')
    let getDialogStatusButtonColor = wrapper.vm.getDialogStatusButtonColor(
      orgStore.currentOrganization.orgStatus)
    expect(getDialogStatusButtonColor).toBe('error')
    orgStore.setCurrentOrganization({
      name: 'testOrg_suspended',
      statusCode: AccountStatus.SUSPENDED,
      orgStatus: AccountStatus.SUSPENDED,
      id: 1234
    })
    statusColor = wrapper.vm.getStatusColor(orgStore.currentOrganization.orgStatus)
    expect(statusColor).toBe('error')
    getDialogStatusButtonColor = wrapper.vm.getDialogStatusButtonColor(orgStore.currentOrganization.orgStatus)
    expect(getDialogStatusButtonColor).toBe('green')
  })

  it('Suspension reason code enables suspend button', () => {
    const MyStub = {
      template: '<div />'
    }
    const $t = () => `test`
    
    wrapper = mount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => {
          return {
            id: 1
          }
        })
      },
      stubs: {
        'BaseAddressForm': MyStub,
        'OrgAdminContact': MyStub,
        'LinkedBCOLBanner': MyStub,
        'v-btn': {
          template: `<button @click='$listeners.click'></button>`
        }
      },
      mocks: { $t }
    })
    expect(wrapper.find("[data-test='modal-suspend-account']").exists()).toBe(true)
    expect(wrapper.vm.isSuspensionReasonFormValid).toBeFalsy()

    wrapper.vm.selectedSuspensionReasonCode = 'Fraudulent'
    const stub = vi.fn().mockImplementation(() => { wrapper.vm.isSuspensionReasonFormValid = true })

    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.isSuspensionReasonFormValid).toBeTruthy()
  })

  it('creates correct requestBody with businessSize and businessType', async () => {
    const orgStore = useOrgStore()
    const mockUpdateOrg = vi.fn()
    orgStore.updateOrg = mockUpdateOrg

    wrapper = shallowMount(AccountInfo, {
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: vi.fn(() => ({ id: 1 }))
      }
    })

    wrapper.setData({
      accountDetails: {
        name: 'New Name',
        branchName: 'New Branch',
        isBusinessAccount: true,
        businessSize: '1',
        businessType: 'CORPORATION'
      },
      currentOrganization: {
        name: 'Old Name',
        isBusinessAccount: false
      }
    })

    await wrapper.vm.updateDetails()

    expect(mockUpdateOrg).toHaveBeenCalledWith({
      name: 'New Name',
      branchName: 'New Branch',
      isBusinessAccount: true,
      businessSize: '1',
      businessType: 'CORPORATION'
    })

    wrapper.setData({
      accountDetails: {
        name: 'New Name 2',
        isBusinessAccount: false
      },
      currentOrganization: {
        name: 'New Name',
        branchName: 'New Branch',
        isBusinessAccount: true,
        businessSize: '1',
        businessType: 'CORPORATION'
      }
    })

    await wrapper.vm.updateDetails()

    expect(mockUpdateOrg).toHaveBeenCalledWith({
      name: 'New Name 2',
      isBusinessAccount: false
    })
  })
})
