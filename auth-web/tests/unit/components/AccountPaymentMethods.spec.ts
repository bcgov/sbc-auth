import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountPaymentMethods from '@/components/auth/account-settings/payment/AccountPaymentMethods.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountPaymentMethods.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'test org'
        },
        currentOrgPaymentType: {
        },
        currentMembership: []
      },
      actions: {
        validatePADInfo: jest.fn(),
        getOrgPayments: jest.fn(),
        updateOrg: jest.fn()
      },
      mutations: {
        setCurrentOrganizationPaymentType: jest.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountPaymentMethods, {
        localVue,
        store,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({})
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
  })

  it('is a Vue instance', () => {
    expect(wrapper.isVueInstance()).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.find(AccountPaymentMethods).exists()).toBe(true)
  })
})
