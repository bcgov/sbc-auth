import { createLocalVue, shallowMount } from '@vue/test-utils'

import { AccountStatus } from '@/util/constants'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'
import can from '@/directives/can'
import flushPromises from 'flush-promises'

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
  sessionStorage['AUTH_API_CONFIG'] = JSON.stringify(config)

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
        setSelectedAccountType: vi.fn(),
        setCurrentOrganization: vi.fn(),
        setCurrentOrganizationType: vi.fn(),
        resetCurrentOrganisation: vi.fn(),
        setAccountTypeBeforeChange: vi.fn(),
        setAccessType: vi.fn(),
        setIsCurrentProductsPremiumOnly: vi.fn().mockImplementation(() => {
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
    vi.resetModules()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper.destroy()
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
    expect(wrapper.vm).toBeTruthy()
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

  it('enables basic type when non premium products are selected', async () => {
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
    await flushPromises()
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
