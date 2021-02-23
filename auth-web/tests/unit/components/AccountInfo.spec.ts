import { AccountStatus, Role } from '@/util/constants'
import { createLocalVue, shallowMount } from '@vue/test-utils'

import AccountInfo from '@/components/auth/account-settings/account-info/AccountInfo.vue'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountInfo.vue', () => {
  let wrapper: any
  let store: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'testOrg',
          statusCode: AccountStatus.ACTIVE,
          orgStatus: AccountStatus.ACTIVE
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
            orgStatus: AccountStatus.SUSPENDED
          }
        })
      },
      getters: OrgModule.getters
    }

    const userModule = {
      namespaced: true,
      state: {
        currentUser: {
          roles: [Role.Staff]
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

  it('Account status displayed properly', () => {
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
    expect(wrapper.vm.$store.state.org.currentOrganization.name).toBe('testOrg_suspended')
    expect(wrapper.find("[data-test='btn-suspend-account']").text()).toBe('Unsuspend Account')
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
})
