import { createLocalVue, shallowMount } from '@vue/test-utils'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import Vuex from 'vuex'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('AccountCreateBasic.vue', () => {
  let wrapper: any
  let wrapperFactory: any

  beforeEach(() => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueRouter)
    const router = new VueRouter()
    sessionStorage.__STORE__[SessionStorageKeys.LaunchDarklyFlags] = JSON.stringify({ 'payment-type-in-account-creation': true, 'auth-options-learn-more': true, 'enable-ltd-and-ulc-affiliate': true })
    const orgModule = {
      namespaced: true,
      state: {
        currentOrganization: {
          name: 'test org'
        },
        currentOrgAddress: {
        },
        currentMembership: [{
          membershipTypeCode: 'OWNER',
          membershipStatus: 'ACTIVE',
          user: { username: 'test' } }],
        pendingOrgMembers: []
      },
      actions: {
      },
      mutations: {
        setCurrentOrganizationAddress: jest.fn(),
        resetInvitations: jest.fn()
      }
    }

    const store = new Vuex.Store({
      strict: false,
      modules: {
        org: orgModule
      }
    })

    wrapperFactory = (propsData) => {
      return shallowMount(AccountCreateBasic, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {
          ...propsData
        }
      })
    }

    wrapper = wrapperFactory({ userProfile: {} })
  })

  afterEach(() => {
    jest.resetModules()
    jest.clearAllMocks()
    wrapper.destroy()
  })

  it('is a Vue instance', () => {
    expect(wrapper.vm).toBeTruthy()
  })

  it('renders the components properly and address is being shown', () => {
    expect(wrapper.find(AccountCreateBasic).exists()).toBe(true)
    expect(wrapper.find(BaseAddressForm).exists()).toBe(true)
    expect(wrapper.find('.save-btn').is('[disabled]')).toBe(true)
  })
})
