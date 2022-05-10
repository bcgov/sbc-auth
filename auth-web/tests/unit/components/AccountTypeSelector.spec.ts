import { createLocalVue, mount, shallowMount } from '@vue/test-utils'

import { AccountStatus } from '@/util/constants'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import OrgModule from '@/store/modules/org'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'

Vue.use(Vuetify)
Vue.use(VueRouter)

document.body.setAttribute('data-app', 'true')

describe('AccountTypeSelector.vue', () => {
  let wrapper: any
  let store: any
  let orgModule: any
  let userModule: any
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.directive('can', can)
  const vuetify = new Vuetify({})

  const config = {
    'VUE_APP_ROOT_API': 'https://localhost:8080/api/v1/11',
    'VUE_APP_COPS_REDIRECT_URL': 'https://coops-dev.pathfinder.gov.bc.ca/',
    'VUE_APP_PAY_ROOT_API': 'https://pay-api-dev.apps.silver.devops.gov.bc.ca/api/v1'
  }
  sessionStorage.__STORE__['AUTH_API_CONFIG'] = JSON.stringify(config)

  beforeEach(() => {
    orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'testOrg',
          statusCode: AccountStatus.ACTIVE,
          orgStatus: AccountStatus.ACTIVE
        },
        accountTypeBeforeChange: '',
        currentOrganizationType: '',
        isCurrentSelectedProductsPremiumOnly: true
      },
      mutations: {
        setSelectedAccountType: jest.fn(),
        setCurrentOrganization: jest.fn(),
        setCurrentOrganizationType: jest.fn(),
        resetCurrentOrganisation: jest.fn(),
        setAccountTypeBeforeChange: jest.fn(),
        setAccessType: jest.fn(),
        setIsCurrentProductsPremiumOnly: jest.fn().mockImplementation(() => {
          orgModule.state.isCurrentSelectedProductsPremiumOnly = false
        })
      }
    }

    userModule = {
      namespaced: true,
      state: {
        currentUser: {}
      },
      actions: {
      },
      mutations: {},
      getters: {}
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
    wrapper = shallowMount(AccountTypeSelector, {
      store,
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('disables basic type when premium products are selected', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      store,
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    expect(wrapper.find("[data-test='div-stepper-basic']").attributes('disabled')).toBeTruthy()
    expect(wrapper.find("[data-test='div-stepper-premium']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='badge-account-premium']").exists()).toBeTruthy()
  })

  it('enables basic type when non premium products are selected', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      store,
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    store.commit('org/setIsCurrentProductsPremiumOnly')
    expect(wrapper.find("[data-test='div-stepper-basic']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='div-stepper-premium']").attributes('disabled')).toBeFalsy()
    expect(wrapper.find("[data-test='badge-account-premium']").exists()).toBeFalsy()
  })

  it('Should set selectedAccountType as PREMIUM', () => {
    wrapper = shallowMount(AccountTypeSelector, {
      store,
      localVue,
      vuetify,
      stubs: {
        'ConfirmCancelButton': {
          template: `<div></div>`
        }
      },
      propsData: {
        isAccountChange: false
      }
    })
    store.commit('org/setCurrentOrganization', { currentOrganization: {
      name: 'testOrg2',
      statusCode: AccountStatus.ACTIVE,
      orgStatus: AccountStatus.ACTIVE,
      orgType: 'PREMIUM'
    } })

    expect(wrapper.vm.selectedAccountType).toEqual('PREMIUM')
  })
})
