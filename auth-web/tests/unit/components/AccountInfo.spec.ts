import { AccountStatus, Role } from '@/util/constants'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import AccountInfo from '@/components/auth/account-settings/account-info/AccountInfo.vue'
import CodesModule from '@/store/modules/codes'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountInfo.vue', () => {
  let wrapper: any
  let store: any
  let orgModule: any
  let userModule: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  const config = {
    'AUTH_API_URL': 'https://localhost:8080/api/v1/11',
    'PAY_API_URL': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'testOrg',
          statusCode: AccountStatus.ACTIVE,
          orgStatus: AccountStatus.ACTIVE,
          id: 1234
        },
        currentMembership: {},
        currentOrgAddress: {},
        permissions: ['CHANGE_ADDRESS', 'CHANGE_ORG_NAME', 'VIEW_ADDRESS', 'VIEW_ADMIN_CONTACT']
      },
      actions: {
        updateOrg: jest.fn(),
        syncAddress: jest.fn(),
        syncOrganization: jest.fn()
      },
      mutations: {
        setCurrentOrganizationAddress: jest.fn(),
        setCurrentOrganization: jest.fn().mockImplementation(() => {
          orgModule.state.currentOrganization = {
            name: 'testOrg_suspended',
            statusCode: AccountStatus.SUSPENDED,
            orgStatus: AccountStatus.SUSPENDED,
            id: 1234
          }
        })
      },
      getters: OrgModule.getters
    }

    userModule = {
      namespaced: true,
      state: {
        currentUser: {
          roles: [Role.Staff, Role.StaffSuspendAccounts]
        }
      },
      actions: UserModule.actions,
      mutations: UserModule.mutations,
      getters: UserModule.getters
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

    jest.resetModules()
    jest.clearAllMocks()
  })

  afterAll(() => {
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    wrapper = shallowMount(AccountInfo, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: jest.fn(() => {
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
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('suspend button click invokes showSuspendAccountDialog method', () => {
    wrapper = shallowMount(AccountInfo, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: jest.fn(() => {
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
    const stub = jest.fn()
    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.showSuspendAccountDialog).toBeCalled()
  })

  it('Account status and number displayed properly', async () => {
    wrapper = shallowMount(AccountInfo, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: jest.fn(() => {
          return {
            id: 1
          }
        })
      }
    })
    expect(wrapper.vm.$store.state.org.currentOrganization.name).toBe('testOrg')
    expect(wrapper.find("[data-test='btn-suspend-account']").text()).toBe('Suspend Account')
    store.commit('org/setCurrentOrganization')
    await flushPromises()
    expect(wrapper.vm.$store.state.org.currentOrganization.name).toBe('testOrg_suspended')
    expect(wrapper.find("[data-test='btn-suspend-account']").text()).toBe('Unsuspend Account')
    expect(wrapper.find("[data-test='div-account-number']").text()).toBe('1234')
  })

  it('Account Info color code', () => {
    wrapper = shallowMount(AccountInfo, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: jest.fn(() => {
          return {
            id: 1
          }
        })
      }
    })
    let statusColor = wrapper.vm.getStatusColor(store.state.org.currentOrganization.orgStatus)
    expect(statusColor).toBe('green')
    let getDialogStatusButtonColor = wrapper.vm.getDialogStatusButtonColor(store.state.org.currentOrganization.orgStatus)
    expect(getDialogStatusButtonColor).toBe('error')

    store.commit('org/setCurrentOrganization')

    statusColor = wrapper.vm.getStatusColor(store.state.org.currentOrganization.orgStatus)
    expect(statusColor).toBe('error')
    getDialogStatusButtonColor = wrapper.vm.getDialogStatusButtonColor(store.state.org.currentOrganization.orgStatus)
    expect(getDialogStatusButtonColor).toBe('green')
  })

  it('Suspension reason code enables suspend button', () => {
    const MyStub = {
      template: '<div />'
    }

    const codesModule = {
      namespaced: true,
      state: {
      },
      actions: CodesModule.actions,
      mutations: CodesModule.mutations,
      getters: CodesModule.getters
    }

    store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule,
        codes: codesModule
      }
    })

    wrapper = mount(AccountInfo, {
      store,
      localVue,
      vuetify,
      mixins: [Steppable],
      methods: {
        getAccountFromSession: jest.fn(() => {
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
    const stub = jest.fn().mockImplementation(() => { wrapper.vm.isSuspensionReasonFormValid = true })

    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.isSuspensionReasonFormValid).toBeTruthy()
  })
})
