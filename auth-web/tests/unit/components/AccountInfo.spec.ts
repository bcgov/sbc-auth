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
  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.directive('can', can)

    const vuetify = new Vuetify({})

    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: '',
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
        setCurrentOrganizationAddress: jest.fn()
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

    const store = new Vuex.Store({
      state: {},
      strict: false,
      modules: {
        org: orgModule,
        user: userModule
      }
    })

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

    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('suspend button click invokes showSuspendAccountDialog method', () => {
    const stub = jest.fn()
    wrapper.setMethods({ showSuspendAccountDialog: stub })
    wrapper.find('.suspend-account-btn').trigger('click')
    expect(wrapper.vm.showSuspendAccountDialog).toBeCalled()
  })
})
