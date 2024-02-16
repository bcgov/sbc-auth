import { AccountStatus, Role } from '@/util/constants'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import AccountInfo from '@/components/auth/account-settings/account-info/AccountInfo.vue'
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
      }
    })
    expect(wrapper.find("[data-test='modal-suspend-account']").exists()).toBe(true)
    expect(wrapper.vm.isSuspensionReasonFormValid).toBeFalsy()

    wrapper.vm.selectedSuspensionReasonCode = 'Fraudulent'
    const stub = vi.fn().mockImplementation(() => { wrapper.vm.isSuspensionReasonFormValid = true })

    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.isSuspensionReasonFormValid).toBeTruthy()
  })
})
